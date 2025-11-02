"""
System Monitoring Service
Provides comprehensive monitoring and control for all REE AI services.

Features:
- Service control (start/stop/restart) via Docker API
- Real-time log streaming via WebSocket
- Health monitoring and metrics collection
- Alert and notification system
- Web UI dashboard
"""
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

import docker
from docker.errors import DockerException, NotFound, APIError
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

from core.base_service import BaseService
from shared.utils.logger import setup_logger, LogEmoji
from shared.config import settings


# ============================================================
# MODELS
# ============================================================

class ServiceControl(BaseModel):
    """Request model for service control operations."""
    service_name: str
    action: str  # start, stop, restart


class ServiceStatus(BaseModel):
    """Service status information."""
    name: str
    status: str  # running, stopped, unhealthy, unknown
    container_id: Optional[str] = None
    image: str
    created: str
    health: Optional[str] = None
    ports: List[str] = []
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    network_rx: Optional[int] = None
    network_tx: Optional[int] = None


class AlertConfig(BaseModel):
    """Alert configuration."""
    service_name: str
    alert_type: str  # health, cpu, memory, disk
    threshold: float
    notification_channels: List[str]  # email, slack, webhook
    enabled: bool = True


class NotificationChannel(BaseModel):
    """Notification channel configuration."""
    channel_type: str  # email, slack, webhook
    config: Dict[str, Any]
    enabled: bool = True


# ============================================================
# CONNECTION MANAGER
# ============================================================

class ConnectionManager:
    """Manages WebSocket connections for real-time updates."""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.logger = setup_logger("websocket_manager")

    async def connect(self, websocket: WebSocket):
        """Accept new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.logger.info(f"{LogEmoji.SUCCESS} New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        self.logger.info(f"{LogEmoji.WARNING} WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients."""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Failed to send message: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for conn in disconnected:
            self.disconnect(conn)


# ============================================================
# MONITORING SERVICE
# ============================================================

class MonitoringService(BaseService):
    """
    System Monitoring Service.

    Provides real-time monitoring, control, and alerting for all REE AI services.
    """

    def __init__(self):
        super().__init__(
            name="monitoring_service",
            version="1.0.0",
            capabilities=["monitoring", "service_control", "alerting", "logging"],
            port=8080
        )

        # Docker client
        try:
            self.docker_client = docker.from_env()
            self.logger.info(f"{LogEmoji.SUCCESS} Connected to Docker daemon")
        except DockerException as e:
            self.logger.error(f"{LogEmoji.ERROR} Failed to connect to Docker: {e}")
            self.docker_client = None

        # WebSocket manager
        self.ws_manager = ConnectionManager()

        # Alert configurations (in-memory for MVP, should use DB for production)
        self.alert_configs: Dict[str, AlertConfig] = {}
        self.notification_channels: Dict[str, NotificationChannel] = {}

        # Background tasks
        self.monitoring_task = None

    def setup_routes(self):
        """Setup custom routes for monitoring service."""

        # ============================================================
        # WEB UI ROUTES
        # ============================================================

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard():
            """Serve main dashboard HTML."""
            return FileResponse("services/monitoring_service/templates/dashboard.html")

        # Mount static files
        self.app.mount("/static", StaticFiles(directory="services/monitoring_service/static"), name="static")

        # ============================================================
        # API ROUTES - SERVICE CONTROL
        # ============================================================

        @self.app.get("/api/services")
        async def list_services() -> List[ServiceStatus]:
            """List all REE AI services with their status."""
            if not self.docker_client:
                raise HTTPException(status_code=500, detail="Docker client not available")

            services = []
            try:
                # Get all containers with ree-ai label
                containers = self.docker_client.containers.list(
                    all=True,
                    filters={"label": "com.docker.compose.project=ree-ai"}
                )

                for container in containers:
                    try:
                        # Get container stats (non-blocking)
                        stats = None
                        try:
                            stats = container.stats(stream=False)
                        except:
                            pass

                        # Parse stats
                        cpu_usage = None
                        memory_usage = None
                        network_rx = None
                        network_tx = None

                        if stats:
                            # CPU percentage
                            cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - \
                                       stats['precpu_stats']['cpu_usage']['total_usage']
                            system_delta = stats['cpu_stats']['system_cpu_usage'] - \
                                          stats['precpu_stats']['system_cpu_usage']
                            if system_delta > 0:
                                cpu_usage = (cpu_delta / system_delta) * 100.0

                            # Memory usage in MB
                            if 'usage' in stats['memory_stats']:
                                memory_usage = stats['memory_stats']['usage'] / (1024 * 1024)

                            # Network I/O
                            if 'networks' in stats:
                                network_rx = sum(net['rx_bytes'] for net in stats['networks'].values())
                                network_tx = sum(net['tx_bytes'] for net in stats['networks'].values())

                        # Get health status
                        health = None
                        if container.attrs.get('State', {}).get('Health'):
                            health = container.attrs['State']['Health']['Status']

                        # Get ports
                        ports = []
                        if container.ports:
                            for container_port, host_bindings in container.ports.items():
                                if host_bindings:
                                    for binding in host_bindings:
                                        ports.append(f"{binding['HostPort']}:{container_port}")

                        service_status = ServiceStatus(
                            name=container.name.replace("ree-ai-", ""),
                            status=container.status,
                            container_id=container.id[:12],
                            image=container.image.tags[0] if container.image.tags else "unknown",
                            created=container.attrs['Created'],
                            health=health,
                            ports=ports,
                            cpu_usage=cpu_usage,
                            memory_usage=memory_usage,
                            network_rx=network_rx,
                            network_tx=network_tx
                        )
                        services.append(service_status)

                    except Exception as e:
                        self.logger.error(f"{LogEmoji.ERROR} Error getting container info: {e}")

                return services

            except DockerException as e:
                self.logger.error(f"{LogEmoji.ERROR} Docker API error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/control")
        async def control_service(request: ServiceControl):
            """Control service (start/stop/restart)."""
            if not self.docker_client:
                raise HTTPException(status_code=500, detail="Docker client not available")

            try:
                container_name = f"ree-ai-{request.service_name}"
                container = self.docker_client.containers.get(container_name)

                if request.action == "start":
                    container.start()
                    self.logger.info(f"{LogEmoji.SUCCESS} Started {request.service_name}")
                elif request.action == "stop":
                    container.stop(timeout=10)
                    self.logger.info(f"{LogEmoji.WARNING} Stopped {request.service_name}")
                elif request.action == "restart":
                    container.restart(timeout=10)
                    self.logger.info(f"{LogEmoji.SUCCESS} Restarted {request.service_name}")
                else:
                    raise HTTPException(status_code=400, detail=f"Invalid action: {request.action}")

                # Broadcast update to all WebSocket clients
                await self.ws_manager.broadcast({
                    "type": "service_update",
                    "service": request.service_name,
                    "action": request.action,
                    "timestamp": datetime.utcnow().isoformat()
                })

                return {"status": "success", "message": f"{request.action} {request.service_name}"}

            except NotFound:
                raise HTTPException(status_code=404, detail=f"Service not found: {request.service_name}")
            except APIError as e:
                self.logger.error(f"{LogEmoji.ERROR} Docker API error: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/logs/{service_name}")
        async def get_logs(service_name: str, tail: int = 100):
            """Get recent logs from a service."""
            if not self.docker_client:
                raise HTTPException(status_code=500, detail="Docker client not available")

            try:
                container_name = f"ree-ai-{service_name}"
                container = self.docker_client.containers.get(container_name)
                logs = container.logs(tail=tail, timestamps=True).decode('utf-8')

                return {
                    "service": service_name,
                    "logs": logs.split('\n')
                }

            except NotFound:
                raise HTTPException(status_code=404, detail=f"Service not found: {service_name}")
            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Error getting logs: {e}")
                raise HTTPException(status_code=500, detail=str(e))

        # ============================================================
        # WEBSOCKET ROUTES - REAL-TIME UPDATES
        # ============================================================

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket endpoint for real-time updates."""
            await self.ws_manager.connect(websocket)

            try:
                while True:
                    # Receive message from client
                    data = await websocket.receive_json()

                    # Handle different message types
                    if data.get("type") == "subscribe_logs":
                        # Stream logs for specific service
                        service_name = data.get("service_name")
                        await self._stream_logs(websocket, service_name)

                    elif data.get("type") == "ping":
                        # Heartbeat
                        await websocket.send_json({"type": "pong"})

            except WebSocketDisconnect:
                self.ws_manager.disconnect(websocket)
            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} WebSocket error: {e}")
                self.ws_manager.disconnect(websocket)

        # ============================================================
        # API ROUTES - HEALTH MONITORING
        # ============================================================

        @self.app.get("/api/health/check")
        async def check_all_health():
            """Check health of all services."""
            health_results = {}

            services = await list_services()

            for service in services:
                # Check if service has health endpoint
                if service.status == "running":
                    try:
                        # Try standard health endpoint
                        async with httpx.AsyncClient(timeout=5.0) as client:
                            port = service.ports[0].split(':')[0] if service.ports else None
                            if port:
                                response = await client.get(f"http://localhost:{port}/health")
                                if response.status_code == 200:
                                    health_results[service.name] = {
                                        "status": "healthy",
                                        "response": response.json()
                                    }
                                else:
                                    health_results[service.name] = {
                                        "status": "unhealthy",
                                        "error": f"HTTP {response.status_code}"
                                    }
                    except Exception as e:
                        health_results[service.name] = {
                            "status": "unhealthy",
                            "error": str(e)
                        }
                else:
                    health_results[service.name] = {
                        "status": "stopped"
                    }

            return health_results

        # ============================================================
        # API ROUTES - ALERTS & NOTIFICATIONS
        # ============================================================

        @self.app.post("/api/alerts/config")
        async def add_alert_config(config: AlertConfig):
            """Add or update alert configuration."""
            self.alert_configs[f"{config.service_name}_{config.alert_type}"] = config
            self.logger.info(f"{LogEmoji.SUCCESS} Alert config added: {config.service_name} - {config.alert_type}")
            return {"status": "success"}

        @self.app.get("/api/alerts/config")
        async def list_alert_configs():
            """List all alert configurations."""
            return list(self.alert_configs.values())

        @self.app.post("/api/notifications/channel")
        async def add_notification_channel(channel: NotificationChannel):
            """Add notification channel."""
            self.notification_channels[channel.channel_type] = channel
            self.logger.info(f"{LogEmoji.SUCCESS} Notification channel added: {channel.channel_type}")
            return {"status": "success"}

        @self.app.get("/api/notifications/channels")
        async def list_notification_channels():
            """List all notification channels."""
            return list(self.notification_channels.values())

    async def _stream_logs(self, websocket: WebSocket, service_name: str):
        """Stream logs for a specific service via WebSocket."""
        if not self.docker_client:
            return

        try:
            container_name = f"ree-ai-{service_name}"
            container = self.docker_client.containers.get(container_name)

            # Stream logs
            for log_line in container.logs(stream=True, follow=True, tail=50):
                await websocket.send_json({
                    "type": "log",
                    "service": service_name,
                    "message": log_line.decode('utf-8').strip(),
                    "timestamp": datetime.utcnow().isoformat()
                })

        except Exception as e:
            self.logger.error(f"{LogEmoji.ERROR} Error streaming logs: {e}")

    async def on_startup(self):
        """Service startup logic."""
        await super().on_startup()

        # Start background monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        self.logger.info(f"{LogEmoji.SUCCESS} Started background monitoring")

    async def on_shutdown(self):
        """Service shutdown logic."""
        # Cancel monitoring task
        if self.monitoring_task:
            self.monitoring_task.cancel()

        # Close Docker client
        if self.docker_client:
            self.docker_client.close()

        await super().on_shutdown()

    async def _monitoring_loop(self):
        """Background task to monitor services and trigger alerts."""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds

                # Get all services
                services = await self._get_services_internal()

                # Check alerts
                for service in services:
                    await self._check_alerts(service)

                # Broadcast status update to WebSocket clients
                await self.ws_manager.broadcast({
                    "type": "status_update",
                    "services": [s.dict() for s in services],
                    "timestamp": datetime.utcnow().isoformat()
                })

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"{LogEmoji.ERROR} Monitoring loop error: {e}")

    async def _get_services_internal(self) -> List[ServiceStatus]:
        """Internal method to get services (for background tasks)."""
        if not self.docker_client:
            return []

        services = []
        try:
            containers = self.docker_client.containers.list(
                all=True,
                filters={"label": "com.docker.compose.project=ree-ai"}
            )

            for container in containers:
                try:
                    service_status = ServiceStatus(
                        name=container.name.replace("ree-ai-", ""),
                        status=container.status,
                        container_id=container.id[:12],
                        image=container.image.tags[0] if container.image.tags else "unknown",
                        created=container.attrs['Created'],
                        health=container.attrs.get('State', {}).get('Health', {}).get('Status'),
                        ports=[]
                    )
                    services.append(service_status)
                except:
                    pass

        except:
            pass

        return services

    async def _check_alerts(self, service: ServiceStatus):
        """Check if service triggers any alerts."""
        # Check health alerts
        health_key = f"{service.name}_health"
        if health_key in self.alert_configs:
            config = self.alert_configs[health_key]
            if config.enabled and service.status != "running":
                await self._send_notification(
                    f"ALERT: Service {service.name} is {service.status}",
                    config.notification_channels
                )

        # Check CPU alerts
        cpu_key = f"{service.name}_cpu"
        if cpu_key in self.alert_configs and service.cpu_usage:
            config = self.alert_configs[cpu_key]
            if config.enabled and service.cpu_usage > config.threshold:
                await self._send_notification(
                    f"ALERT: Service {service.name} CPU usage {service.cpu_usage:.1f}% exceeds threshold {config.threshold}%",
                    config.notification_channels
                )

        # Check memory alerts
        memory_key = f"{service.name}_memory"
        if memory_key in self.alert_configs and service.memory_usage:
            config = self.alert_configs[memory_key]
            if config.enabled and service.memory_usage > config.threshold:
                await self._send_notification(
                    f"ALERT: Service {service.name} memory usage {service.memory_usage:.1f}MB exceeds threshold {config.threshold}MB",
                    config.notification_channels
                )

    async def _send_notification(self, message: str, channels: List[str]):
        """Send notification to configured channels."""
        self.logger.warning(f"{LogEmoji.WARNING} {message}")

        for channel_type in channels:
            if channel_type in self.notification_channels:
                channel = self.notification_channels[channel_type]
                if not channel.enabled:
                    continue

                try:
                    if channel_type == "webhook":
                        # Send webhook
                        async with httpx.AsyncClient() as client:
                            await client.post(
                                channel.config.get("url"),
                                json={"message": message, "timestamp": datetime.utcnow().isoformat()}
                            )
                    elif channel_type == "slack":
                        # Send Slack message
                        async with httpx.AsyncClient() as client:
                            await client.post(
                                channel.config.get("webhook_url"),
                                json={"text": message}
                            )
                    # Add more notification types as needed

                except Exception as e:
                    self.logger.error(f"{LogEmoji.ERROR} Failed to send notification to {channel_type}: {e}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    service = MonitoringService()
    service.run()
