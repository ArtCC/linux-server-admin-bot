# Getting Started Guide

## Step 1: Create Your Telegram Bot

1. **Open Telegram** and search for [@BotFather](https://t.me/botfather)

2. **Start a chat** with BotFather and send `/newbot`

3. **Follow the prompts**:
   - Choose a name for your bot (e.g., "My Server Monitor")
   - Choose a username (must end in 'bot', e.g., "myserver_monitor_bot")

4. **Save your token**: BotFather will give you a token like:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```
   Keep this secret!

## Step 2: Get Your User ID

1. **Open Telegram** and search for [@userinfobot](https://t.me/userinfobot)

2. **Start a chat** with the bot

3. **Copy your ID**: The bot will show your user ID (e.g., `123456789`)

## Step 3: Clone and Configure

```bash
# Clone the repository
git clone https://github.com/artcc/linux-server-admin-bot.git
cd linux-server-admin-bot

# Run the setup script
./setup.sh
```

The setup script will:
- Check Docker installation
- Create `.env` file from template
- Open editor to configure your bot
- Build and start the bot

## Step 4: Configure Your Bot

Edit the `.env` file with your values:

```env
# Required: Your bot token from BotFather
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Required: Your Telegram user ID (comma-separated for multiple users)
TELEGRAM_ALLOWED_USER_IDS=123456789,987654321

# Optional: Alert thresholds (defaults shown)
CPU_ALERT_THRESHOLD=80
MEMORY_ALERT_THRESHOLD=80
DISK_ALERT_THRESHOLD=90

# Optional: Alert settings
ALERT_CHECK_INTERVAL=300  # Check every 5 minutes
ALERT_COOLDOWN=600        # Wait 10 minutes between same alerts

# Optional: Rate limiting
RATE_LIMIT_CALLS=10       # Max 10 calls
RATE_LIMIT_PERIOD=60      # Per 60 seconds

# Optional: Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
```

## Step 5: Start the Bot

### Using the setup script (recommended):
```bash
./setup.sh
```

### Manual start:
```bash
docker-compose up -d
```

### View logs:
```bash
docker-compose logs -f
```

## Step 6: Test Your Bot

1. **Open Telegram** and find your bot by username

2. **Start a chat** with your bot

3. **Send `/start`** - you should get a welcome message

4. **Try commands**:
   - `/status` - See overall system status
   - `/cpu` - View CPU usage with chart
   - `/docker` - List Docker containers
   - `/help` - See all available commands

## Common Issues

### Bot doesn't respond
- **Check logs**: `docker-compose logs -f`
- **Verify token**: Make sure `TELEGRAM_BOT_TOKEN` is correct
- **Check user ID**: Ensure your user ID is in `TELEGRAM_ALLOWED_USER_IDS`

### Permission denied for Docker
```bash
# Add your user to docker group
sudo usermod -aG docker $USER

# Restart Docker service
sudo systemctl restart docker

# Log out and log back in for changes to take effect
```

### Container fails to start
```bash
# Check Docker logs
docker-compose logs

# Verify .env file
cat .env

# Rebuild image
docker-compose build --no-cache
docker-compose up -d
```

### Can't access system metrics
- Make sure you're using `network_mode: host` in docker-compose.yml
- Verify volume mounts are correct
- Check Docker has permission to access host resources

## Next Steps

### Customize Alert Thresholds
Edit `.env` file and restart:
```bash
nano .env
docker-compose restart
```

### Add More Users
Add user IDs to `TELEGRAM_ALLOWED_USER_IDS` in `.env`:
```env
TELEGRAM_ALLOWED_USER_IDS=123456789,987654321,555666777
```

### View Detailed Logs
```bash
# Follow logs
docker-compose logs -f

# View specific number of lines
docker-compose logs --tail=100

# Save logs to file
docker-compose logs > bot-logs.txt
```

### Update the Bot
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d
```

### Stop the Bot
```bash
# Stop but keep containers
docker-compose stop

# Stop and remove containers
docker-compose down

# Stop and remove everything including volumes
docker-compose down -v
```

## Advanced Configuration

### Custom Docker Socket
If your Docker socket is in a different location:
```yaml
# docker-compose.yml
volumes:
  - /custom/path/docker.sock:/var/run/docker.sock:ro
```

### Custom Chart Settings
In `.env`:
```env
CHART_DPI=150              # Higher quality charts
CHART_FIGSIZE_WIDTH=12     # Wider charts
CHART_FIGSIZE_HEIGHT=8     # Taller charts
```

### Custom Monitoring Paths
If running in a non-standard environment:
```env
HOST_PROC_PATH=/custom/proc
HOST_SYS_PATH=/custom/sys
HOST_LOGS_PATH=/custom/logs
```

## Security Best Practices

1. **Keep your bot token secret** - Never commit it to Git
2. **Limit user access** - Only add trusted user IDs
3. **Use environment variables** - Never hardcode sensitive data
4. **Monitor logs** - Check for unauthorized access attempts
5. **Update regularly** - Keep dependencies and Docker images updated
6. **Use firewall rules** - Restrict network access to your server

## Getting Help

- **Documentation**: Check [README.md](../README.md)
- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Contributing**: Read [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Issues**: Open an issue on GitHub
- **Email**: your-email@example.com

## Quick Reference

### Essential Commands
```bash
# Start bot
docker-compose up -d

# View logs
docker-compose logs -f

# Restart bot
docker-compose restart

# Stop bot
docker-compose stop

# Update bot
git pull && docker-compose build && docker-compose up -d

# Check bot status
docker-compose ps
```

### Essential Bot Commands
- `/start` - Start the bot
- `/help` - Show help
- `/status` - System overview
- `/cpu` - CPU information
- `/memory` - Memory information
- `/disk` - Disk information
- `/docker` - List containers
- `/alerts` - Alert configuration

Enjoy your server monitoring bot! 🚀
