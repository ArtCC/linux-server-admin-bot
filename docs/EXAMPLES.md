# Examples and Usage Patterns

## Basic Usage Examples

### Getting System Status

**Command**: `/status`

**Response**:
```
ℹ️ System Status

🖥️ CPU Usage: ✅ 23.5%
└ Cores: 8

💾 Memory: ✅ 45.2%
└ 7.2GB / 16.0GB

💿 Disk: ✅ 68.5%
└ 685GB / 1000GB

🕐 Uptime: 5d 12h 34m
```

### Detailed CPU Information

**Command**: `/cpu`

**Response**:
- Text with detailed CPU metrics
- Chart showing:
  - Overall CPU gauge
  - Per-core usage bar chart

### Docker Container Management

**List containers**:
```
/docker
```

**View container stats**:
```
/docker_stats
```

**Restart a container**:
```
/docker_restart my-nginx
```

**View logs**:
```
/docker_logs my-nginx
```

## Advanced Usage Patterns

### Monitoring Multiple Servers

You can run multiple instances of the bot, one per server:

```bash
# Server 1
cd /opt/bot-server1
docker-compose up -d

# Server 2
cd /opt/bot-server2
docker-compose up -d
```

Each instance will monitor its host independently.

### Custom Alert Rules

Edit `.env` to customize thresholds:

```env
# Alert when CPU exceeds 90%
CPU_ALERT_THRESHOLD=90

# Alert when memory exceeds 85%
MEMORY_ALERT_THRESHOLD=85

# Alert when disk exceeds 95%
DISK_ALERT_THRESHOLD=95

# Check every 2 minutes
ALERT_CHECK_INTERVAL=120

# Wait 5 minutes between same alerts
ALERT_COOLDOWN=300
```

### Rate Limiting Configuration

Prevent abuse by adjusting rate limits:

```env
# Allow 20 commands
RATE_LIMIT_CALLS=20

# Per 60 seconds
RATE_LIMIT_PERIOD=60
```

### Multi-User Access

Add multiple users to whitelist:

```env
TELEGRAM_ALLOWED_USER_IDS=123456789,987654321,555444333
```

## Integration Examples

### Using with Cron Jobs

Monitor bot health with cron:

```bash
# Check bot is running every 5 minutes
*/5 * * * * docker ps | grep linux-server-admin-bot || docker-compose -f /path/to/docker-compose.yml up -d
```

### Integrating with Monitoring Tools

Export metrics for external monitoring:

```python
# Example: Export metrics to Prometheus (future feature)
from bot.services import SystemMonitor

monitor = SystemMonitor()
metrics = monitor.get_system_status()

# Export to Prometheus format
prometheus_metrics = f"""
# HELP cpu_usage_percent CPU usage percentage
# TYPE cpu_usage_percent gauge
cpu_usage_percent {metrics.cpu.percent}

# HELP memory_usage_percent Memory usage percentage  
# TYPE memory_usage_percent gauge
memory_usage_percent {metrics.memory.percent}
"""
```

### Webhook Integration

Receive alerts via webhook (future feature):

```python
# Example webhook endpoint
@app.post("/webhook/alert")
async def receive_alert(alert: Alert):
    # Process alert
    # Send to external service
    pass
```

## Command Chaining

While not directly supported, you can create custom scripts:

```bash
#!/bin/bash
# check_and_restart.sh

# Get container status
STATUS=$(docker inspect -f '{{.State.Status}}' my-nginx)

if [ "$STATUS" != "running" ]; then
    # Container is down, notify via bot
    # (Bot will detect via health monitor)
    docker start my-nginx
fi
```

## Automation Examples

### Auto-restart on High Memory

Create a systemd service that monitors and restarts:

```ini
[Unit]
Description=Auto-restart on high memory

[Service]
Type=simple
ExecStart=/usr/local/bin/memory-monitor.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

### Scheduled Reports

Use bot's scheduler for daily reports (extend health_monitor.py):

```python
# Add to health_monitor.py
def schedule_daily_report(self):
    self.scheduler.add_job(
        self.send_daily_report,
        trigger='cron',
        hour=9,
        minute=0,
    )

async def send_daily_report(self):
    status = self.system_monitor.get_system_status()
    message = format_daily_report(status)
    # Send to all registered chats
```

## API Usage Examples (for developers)

### Programmatic Access

```python
from bot.services import SystemMonitor, DockerManager

# Initialize services
system = SystemMonitor()
docker = DockerManager()

# Get metrics
cpu = system.get_cpu_metrics()
memory = system.get_memory_metrics()
containers = docker.list_containers()

# Process data
print(f"CPU: {cpu.percent}%")
print(f"Memory: {memory.percent}%")
print(f"Containers: {len(containers)}")
```

### Custom Handlers

Add your own commands:

```python
# bot/handlers/custom.py
from bot.utils import standard_handler

class CustomHandlers:
    @standard_handler
    async def my_command(self, update, context):
        """Handle /my_command"""
        # Your logic here
        await update.message.reply_text("Custom response")

# Register in main.py
app.add_handler(CommandHandler("my_command", custom_handlers.my_command))
```

### Custom Alerts

Create custom alert conditions:

```python
# In health_monitor.py
async def check_custom_conditions(self):
    # Your custom logic
    if some_condition:
        alert = self.alert_manager.create_custom_alert(
            title="Custom Alert",
            message="Something happened!",
            severity="warning"
        )
        await self._send_alert_to_chats(alert)
```

## Best Practices

### 1. Regular Backups

Backup your configuration:
```bash
# Backup .env file
cp .env .env.backup

# Backup logs
tar -czf logs-backup-$(date +%Y%m%d).tar.gz logs/
```

### 2. Log Rotation

Configure log rotation in `.env`:
```env
LOG_FILE=logs/bot.log
```

And set up logrotate:
```
/path/to/logs/bot.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 botuser botuser
}
```

### 3. Security Hardening

- Keep bot token secret
- Regularly update dependencies
- Monitor logs for suspicious activity
- Use strong firewall rules
- Limit Docker socket access

### 4. Performance Optimization

- Adjust alert check intervals based on your needs
- Reduce chart DPI for faster generation
- Use resource limits in docker-compose.yml
- Monitor bot's own resource usage

### 5. Monitoring the Monitor

Set up external monitoring for the bot itself:

```bash
# Healthcheck script
#!/bin/bash
if ! docker ps | grep -q linux-server-admin-bot; then
    echo "Bot is down!" | mail -s "Bot Alert" admin@example.com
fi
```

## Troubleshooting Examples

### Debug Mode

Enable debug logging:
```env
LOG_LEVEL=DEBUG
```

### Test Alert System

Temporarily lower thresholds to test alerts:
```env
CPU_ALERT_THRESHOLD=10
MEMORY_ALERT_THRESHOLD=10
```

### Check Permissions

```bash
# Verify Docker socket permissions
ls -l /var/run/docker.sock

# Verify mounted volumes
docker inspect linux-server-admin-bot | grep -A 20 Mounts
```

## Future Enhancement Ideas

### 1. Database Integration
```python
# Store metrics history
from sqlalchemy import create_engine

engine = create_engine('sqlite:///metrics.db')
# Store historical data for trends
```

### 2. Web Dashboard
```python
# FastAPI dashboard
from fastapi import FastAPI

app = FastAPI()

@app.get("/api/metrics")
async def get_metrics():
    return system_monitor.get_system_status()
```

### 3. Notification Channels
```python
# Support multiple notification methods
class NotificationManager:
    async def send(self, alert, channels=['telegram', 'email', 'slack']):
        for channel in channels:
            await self._send_via_channel(alert, channel)
```

### 4. Machine Learning Alerts
```python
# Predict resource usage
from sklearn.ensemble import RandomForestRegressor

def predict_cpu_usage(historical_data):
    model = RandomForestRegressor()
    # Train on historical data
    # Predict future usage
    pass
```

## Community Contributions

Share your custom commands, integrations, or use cases with the community!

Example community extensions:
- SSL certificate expiration monitoring
- Database connection monitoring  
- Custom service health checks
- Integration with other tools (Grafana, Prometheus, etc.)

---

For more examples, check the [GitHub repository](https://github.com/yourusername/linux-server-admin-bot) or join our community discussions!
