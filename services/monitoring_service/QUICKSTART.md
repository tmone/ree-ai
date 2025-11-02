# Monitoring Service - Quick Start Guide

## 🚀 Start in 3 Steps

### 1. Start the Service

```bash
# Start with all other services
docker-compose --profile all up -d

# Or start standalone
docker-compose up -d monitoring-service
```

### 2. Access Dashboard

Open browser: **http://localhost:9999**

### 3. Control Services

- Click **▶️ Start** to start services
- Click **⏹️ Stop** to stop services
- Click **🔄 Restart** to restart services
- Click **📋 Logs** to view real-time logs

---

## 📊 Dashboard Overview

| Section | Description |
|---------|-------------|
| **Summary Cards** | Running/Stopped/Unhealthy counts, Average CPU |
| **Service Grid** | All services with status, controls, and metrics |
| **Log Viewer** | Real-time log streaming with syntax highlighting |
| **Configuration** | Alert rules and notification channels |

---

## 🔔 Quick Alert Setup

1. Click **⚙️ Configure** button
2. Add alert rule:
   - Service: postgres
   - Type: health
   - Notifications: email, slack
3. Configure notification channels:
   - Email: admin@example.com
   - Slack: https://hooks.slack.com/services/...

---

## 🐛 Troubleshooting

**Service won't start?**
```bash
docker logs ree-ai-monitoring-service
```

**Can't access dashboard?**
- Check port 9999 is not in use: `lsof -i :9999`
- Verify service is running: `docker ps | grep monitoring`

**WebSocket disconnected?**
- Refresh browser page
- Check monitoring service logs

---

## 📚 Full Documentation

See [README.md](./README.md) for complete guide.

---

**Dashboard URL:** http://localhost:9999 🎯
