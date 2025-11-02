# REE AI System Monitoring Service

Comprehensive monitoring and control dashboard for all REE AI microservices.

## 🎯 Features

### 1. **Service Control Dashboard**
- ✅ **Start/Stop/Restart** any service with one click
- 📊 **Real-time status** monitoring for all containers
- 🔍 **Health checks** with automatic detection
- 📈 **Resource metrics** (CPU, memory, network I/O)

### 2. **Log Viewer**
- 📋 **Real-time log streaming** via WebSocket
- 🔎 **Search and filter** logs by service
- 💾 **Recent logs** (configurable tail length)
- 🎨 **Syntax highlighting** for log levels (ERROR, WARNING, INFO, SUCCESS)

### 3. **Health Monitoring**
- 🏥 **Auto-check health endpoints** for all services
- 🔔 **Alert notifications** when services go down
- 📊 **Status dashboard** with service counts
- ⚡ **Real-time updates** via WebSocket

### 4. **Metrics Collection**
- 💻 **CPU usage** tracking per service
- 🧠 **Memory consumption** monitoring
- 🌐 **Network I/O** statistics (RX/TX bytes)
- 📈 **Visual progress bars** for resource usage

### 5. **Alert & Notification System**
- 📧 **Email notifications** for critical alerts
- 💬 **Slack integration** via webhooks
- 🔗 **Custom webhooks** for third-party tools
- ⚙️ **Configurable thresholds** for CPU, memory, health

### 6. **Modern Web UI**
- 🎨 **Beautiful dashboard** with Tailwind CSS
- ⚡ **Real-time updates** without page refresh
- 📱 **Responsive design** for mobile and desktop
- 🌙 **Clean, professional interface**

---

## 🚀 Quick Start

### 1. Start the Monitoring Service

```bash
# Start all services including monitoring
docker-compose --profile all up -d

# Or start only monitoring service
docker-compose up -d monitoring-service
```

### 2. Access the Dashboard

Open your browser and navigate to:

```
http://localhost:9999
```

### 3. Control Services

- Click **▶️ Start** to start a stopped service
- Click **⏹️ Stop** to stop a running service
- Click **🔄 Restart** to restart a service
- Click **📋 Logs** to view service logs in real-time

---

## 📖 Usage Guide

### Service Control

The dashboard shows all REE AI services with their current status:

| Status | Meaning | Color |
|--------|---------|-------|
| **running** | Service is operational | 🟢 Green |
| **stopped** | Service is not running | ⚫ Gray |
| **unhealthy** | Service health check failed | 🔴 Red |

**Control buttons:**
- **Start**: Launch a stopped service
- **Stop**: Gracefully stop a running service (10s timeout)
- **Restart**: Restart a service (stop + start)
- **Logs**: Open real-time log viewer

### Log Viewer

1. Click **📋 Logs** button on any service card
2. View recent logs (default: 100 lines)
3. Click **🔄 Refresh Logs** to update
4. Logs auto-highlight keywords:
   - 🔴 **ERROR** - Red
   - 🟡 **WARNING** - Yellow
   - 🔵 **INFO** - Blue
   - 🟢 **SUCCESS** - Green

### Real-time Updates

The dashboard automatically refreshes every 30 seconds via WebSocket:
- Service status changes
- Resource metrics updates
- Health check results
- Container statistics

### Alert Configuration

1. Click **⚙️ Configure** button in header
2. Navigate to **Alert Configuration** section
3. Click **+ Add Alert Rule**
4. Configure:
   - **Service**: Which service to monitor
   - **Alert Type**: health, cpu, memory, disk
   - **Threshold**: Alert trigger value
   - **Notification Channels**: email, slack, webhook

### Notification Channels

Configure notification channels in the settings panel:

**Email Notifications:**
```
📧 Email: admin@example.com
```

**Slack Webhook:**
```
💬 Slack: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**Custom Webhook:**
```
🔗 Webhook: https://your-webhook.com/alerts
```

---

## 🏗️ Architecture

### Backend

**FastAPI Service** with the following components:

1. **Docker API Integration**
   - Uses `docker` Python SDK to control containers
   - Reads container stats, logs, and metadata
   - Executes start/stop/restart operations

2. **WebSocket Server**
   - Real-time updates to connected clients
   - Log streaming for active log viewers
   - Service status broadcasts

3. **Background Monitoring**
   - 30-second interval health checks
   - Automatic alert triggering
   - Metrics collection and aggregation

4. **REST API Endpoints**
   - `GET /api/services` - List all services
   - `POST /api/control` - Control service (start/stop/restart)
   - `GET /api/logs/{service_name}` - Get service logs
   - `GET /api/health/check` - Check all service health
   - `POST /api/alerts/config` - Configure alerts
   - `POST /api/notifications/channel` - Add notification channel

### Frontend

**Modern HTML/JavaScript** with:
- **Alpine.js** - Reactive data binding
- **Tailwind CSS** - Beautiful styling
- **Chart.js** - Metrics visualization (optional)
- **WebSocket** - Real-time updates

### Data Models

**ServiceStatus:**
```python
{
  "name": "postgres",
  "status": "running",
  "container_id": "abc123",
  "image": "postgres:15",
  "created": "2025-11-01T00:00:00Z",
  "health": "healthy",
  "ports": ["5432:5432"],
  "cpu_usage": 12.5,
  "memory_usage": 256.0,
  "network_rx": 1024000,
  "network_tx": 512000
}
```

**AlertConfig:**
```python
{
  "service_name": "postgres",
  "alert_type": "health",
  "threshold": 80.0,
  "notification_channels": ["email", "slack"],
  "enabled": true
}
```

---

## 🔧 Configuration

### Environment Variables

Set these in `.env` or docker-compose.yml:

```bash
# Monitoring service configuration
DEBUG=true
LOG_LEVEL=INFO
SERVICE_REGISTRY_URL=http://service-registry:8000

# Alert thresholds (optional)
CPU_ALERT_THRESHOLD=80
MEMORY_ALERT_THRESHOLD=1024
```

### Docker Socket Access

**Important:** The monitoring service requires access to Docker socket to control containers.

This is configured in `docker-compose.yml`:
```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock:ro
```

**Security Note:** Read-only (`:ro`) access is sufficient for monitoring. For production, consider using Docker API over TCP with TLS.

---

## 📊 API Reference

### List Services

```bash
GET /api/services
```

**Response:**
```json
[
  {
    "name": "postgres",
    "status": "running",
    "container_id": "abc123",
    "image": "postgres:15",
    "ports": ["5432:5432"],
    "cpu_usage": 12.5,
    "memory_usage": 256.0
  }
]
```

### Control Service

```bash
POST /api/control
Content-Type: application/json

{
  "service_name": "postgres",
  "action": "restart"
}
```

**Actions:** `start`, `stop`, `restart`

### Get Logs

```bash
GET /api/logs/postgres?tail=100
```

**Response:**
```json
{
  "service": "postgres",
  "logs": [
    "2025-11-01 10:00:00 INFO: Database started",
    "2025-11-01 10:00:01 INFO: Accepting connections"
  ]
}
```

### Check All Health

```bash
GET /api/health/check
```

**Response:**
```json
{
  "postgres": {
    "status": "healthy",
    "response": {"status": "healthy"}
  },
  "redis": {
    "status": "healthy",
    "response": {"status": "healthy"}
  }
}
```

---

## 🧪 Testing

### Manual Testing

1. **Start monitoring service:**
```bash
docker-compose up -d monitoring-service
```

2. **Check logs:**
```bash
docker-compose logs -f monitoring-service
```

3. **Access dashboard:**
```
http://localhost:9999
```

4. **Test service control:**
   - Stop a service via dashboard
   - Verify service stops
   - Start service again
   - Check logs update in real-time

### Automated Testing

```bash
# Test API endpoints
curl http://localhost:9999/api/services
curl http://localhost:9999/api/health/check

# Test service control
curl -X POST http://localhost:9999/api/control \
  -H "Content-Type: application/json" \
  -d '{"service_name": "postgres", "action": "restart"}'
```

---

## 🔒 Security Considerations

### Production Deployment

1. **Authentication Required**
   - Add JWT authentication for API endpoints
   - Protect dashboard with login page
   - Use HTTPS for all connections

2. **Docker Socket Security**
   - Use Docker API over TCP with TLS
   - Limit container permissions
   - Run monitoring service as non-root user

3. **Rate Limiting**
   - Add rate limiting for control operations
   - Prevent abuse of start/stop/restart actions

4. **Audit Logging**
   - Log all control operations
   - Track who started/stopped services
   - Store audit logs in database

### Recommended Production Setup

```yaml
monitoring-service:
  environment:
    - ENABLE_AUTH=true
    - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    - DOCKER_HOST=tcp://docker-proxy:2376
    - DOCKER_TLS_VERIFY=1
    - DOCKER_CERT_PATH=/certs
  volumes:
    - /path/to/certs:/certs:ro
```

---

## 🐛 Troubleshooting

### Issue: "Docker client not available"

**Solution:**
```bash
# Check Docker socket is mounted
docker exec ree-ai-monitoring-service ls -la /var/run/docker.sock

# Verify Docker socket permissions
ls -la /var/run/docker.sock
```

### Issue: "Failed to control service"

**Solution:**
- Check service exists: `docker ps -a | grep ree-ai-{service_name}`
- Check Docker socket permissions
- Review monitoring service logs: `docker logs ree-ai-monitoring-service`

### Issue: "WebSocket disconnected"

**Solution:**
- Refresh browser page
- Check monitoring service is running
- Verify network connectivity
- Check browser console for errors

### Issue: "Logs not showing"

**Solution:**
```bash
# Verify container has logs
docker logs ree-ai-{service_name}

# Check monitoring service can access Docker API
docker exec ree-ai-monitoring-service python -c "import docker; print(docker.from_env().version())"
```

---

## 🚀 Advanced Features

### Custom Alerts

Create custom alert rules via API:

```python
import requests

alert_config = {
    "service_name": "postgres",
    "alert_type": "cpu",
    "threshold": 80.0,
    "notification_channels": ["slack"],
    "enabled": True
}

response = requests.post(
    "http://localhost:9999/api/alerts/config",
    json=alert_config
)
```

### Slack Integration

Configure Slack webhook:

```python
slack_channel = {
    "channel_type": "slack",
    "config": {
        "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    },
    "enabled": True
}

response = requests.post(
    "http://localhost:9999/api/notifications/channel",
    json=slack_channel
)
```

### Custom Webhooks

Send alerts to custom webhooks:

```python
webhook_channel = {
    "channel_type": "webhook",
    "config": {
        "url": "https://your-webhook.com/alerts",
        "headers": {"Authorization": "Bearer YOUR_TOKEN"}
    },
    "enabled": True
}
```

---

## 📚 Related Documentation

- **Project Overview**: `../../CLAUDE.md`
- **Architecture Guide**: `../../COMPLETE_FRAMEWORK_SUMMARY.md`
- **Quick Start**: `../../QUICKSTART_COMPLETE.md`
- **Testing Guide**: `../../TESTING.md`

---

## 🤝 Contributing

When adding new monitoring features:

1. Update backend API in `main.py`
2. Update frontend UI in `templates/dashboard.html`
3. Add tests for new endpoints
4. Update this README with new features
5. Follow CLAUDE.md guidelines (English code, Vietnamese responses)

---

## 📝 License

Part of the REE AI platform. See project root for license information.

---

**Built with ❤️ for REE AI Platform**

Dashboard URL: http://localhost:9999 🎯
