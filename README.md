# 🤖 Linux Server Admin Bot

<p align="left">
  <img src="https://github.com/ArtCC/linux-server-admin-bot/blob/main/assets/linux-server-admin-bot.png" alt="Linux Server Admin Bot" width="175"/>
</p>

[![Python Version](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](Dockerfile)

Telegram bot for monitoring and managing Ubuntu servers with Docker support. Monitor system resources, manage Docker containers, and receive automated alerts - all from Telegram.

## ✨ Features

### 📊 System Monitoring
- **CPU**: Real-time usage, per-core breakdown, frequency, load average
- **Memory**: RAM and swap usage with detailed breakdown
- **Disk**: Space usage across mount points
- **Network**: Interface statistics, traffic monitoring
- **Processes**: Top CPU-consuming processes
- **Temperature**: System sensors (if available)

### 🐳 Docker Management
- List all containers with status
- View resource usage per container
- Start/Stop/Restart containers
- View container logs
- Real-time statistics with charts

### 📈 Visualizations
- Beautiful matplotlib charts for all metrics
- CPU usage per core
- Memory distribution pie charts
- Disk usage visualization
- Docker container resource graphs

### 🔔 Automated Alerts
- Configurable thresholds for CPU, RAM, and disk
- Automatic notifications when limits exceeded
- Smart cooldown to prevent spam
- Alert severity levels (info, warning, critical)

### 🔒 Security
- User whitelist authentication
- Rate limiting per user
- Comprehensive logging
- Docker security best practices

## 🚀 Quick Start

### Prerequisites
- Ubuntu server (18.04+)
- Docker and Docker Compose
- Telegram Bot Token ([create one](https://t.me/botfather))
- Your Telegram User ID ([get it](https://t.me/userinfobot))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/artcc/linux-server-admin-bot.git
cd linux-server-admin-bot
```

2. **Configure environment**
```bash
cp .env.example .env
nano .env
```

Edit `.env` with your values:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_ALLOWED_USER_IDS=123456789,987654321

CPU_ALERT_THRESHOLD=80
MEMORY_ALERT_THRESHOLD=80
DISK_ALERT_THRESHOLD=90
```

3. **Create logs directory with correct permissions**
```bash
mkdir -p logs
sudo chown -R 1000:1000 logs
sudo chmod -R 775 logs
```

4. **Build and run with Docker Compose**
```bash
docker-compose up -d
```

5. **Check logs**
```bash
docker-compose logs -f
```

6. **Start chatting with your bot on Telegram!**

## 📖 Usage

### Available Commands

#### Basic
- `/start` - Welcome message and bot info
- `/help` - Show all available commands
- `/status` - Overall system status summary

#### System Monitoring
- `/cpu` - Detailed CPU information with chart
- `/memory` - Memory usage with visualization
- `/disk` - Disk space usage
- `/top` - Top processes by CPU usage
- `/network` - Network interface statistics

#### Docker Management
- `/docker` - List all containers
- `/docker_stats` - Resource usage per container
- `/docker_logs <container>` - View container logs
- `/docker_restart <container>` - Restart a container
- `/docker_stop <container>` - Stop a container
- `/docker_start <container>` - Start a container

#### Alerts
- `/alerts` - View alert configuration and active alerts

## 🏗️ Architecture

```
linux-server-admin-bot/
├── bot/
│   ├── handlers/          # Command handlers
│   │   ├── basic.py      # Start, help, alerts
│   │   ├── system.py     # System monitoring commands
│   │   └── docker.py     # Docker management commands
│   ├── services/          # Business logic
│   │   ├── system_monitor.py    # psutil wrapper
│   │   ├── docker_manager.py    # Docker SDK wrapper
│   │   └── alert_manager.py     # Alert system
│   ├── monitors/          # Background tasks
│   │   └── health_monitor.py    # Periodic health checks
│   ├── models/            # Data models
│   │   └── metrics.py    # Dataclasses for metrics
│   └── utils/             # Utilities
│       ├── decorators.py # Auth, rate limiting, logging
│       ├── formatters.py # Message formatting
│       └── charts.py     # Chart generation
├── config/                # Configuration
│   ├── settings.py       # Pydantic settings
│   ├── constants.py      # Constants and enums
│   └── logger.py         # Logging setup
├── tests/                 # Unit tests
├── docs/                  # Documentation
├── main.py               # Application entry point
├── Dockerfile            # Multi-stage Docker build
├── docker-compose.yml    # Docker Compose config
└── requirements.txt      # Python dependencies
```

### Design Principles
- **Separation of Concerns**: Clear separation between handlers, services, and utilities
- **Type Safety**: Full type hints and Pydantic validation
- **Testability**: Dependency injection and comprehensive tests
- **Security**: Authorization, rate limiting, and audit logging
- **Observability**: Structured logging and error handling
- **Scalability**: Async/await patterns for concurrent operations

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `TELEGRAM_BOT_TOKEN` | Telegram Bot API token | ✅ Yes | - |
| `TELEGRAM_ALLOWED_USER_IDS` | Comma-separated user IDs | ✅ Yes | - |
| `CPU_ALERT_THRESHOLD` | CPU usage alert threshold (%) | ❌ No | 80 |
| `MEMORY_ALERT_THRESHOLD` | Memory usage alert threshold (%) | ❌ No | 80 |
| `DISK_ALERT_THRESHOLD` | Disk usage alert threshold (%) | ❌ No | 90 |
| `ALERT_CHECK_INTERVAL` | Alert check interval (seconds) | ❌ No | 300 |
| `ALERT_COOLDOWN` | Alert cooldown period (seconds) | ❌ No | 600 |
| `RATE_LIMIT_CALLS` | Max calls per period | ❌ No | 10 |
| `RATE_LIMIT_PERIOD` | Rate limit period (seconds) | ❌ No | 60 |
| `LOG_LEVEL` | Logging level | ❌ No | INFO |

### Docker Volumes

The bot requires access to host system resources:

```yaml
volumes:
  - /var/run/docker.sock:/var/run/docker.sock:ro  # Docker management
  - /proc:/host/proc:ro                            # System metrics
  - /sys:/host/sys:ro                              # System information
  - /var/log:/host/logs:ro                         # System logs (optional)
```

## 🎨 Bot Avatar

You can use the official bot avatar for your own instance:

<p align="left">
  <img src="https://github.com/ArtCC/linux-server-admin-bot/blob/main/assets/linux-server-admin-bot.png" alt="Bot Avatar" width="200"/>
</p>

**Download**: [linux-server-admin-bot.png](https://github.com/ArtCC/linux-server-admin-bot/blob/main/assets/linux-server-admin-bot.png)

To set this image as your bot's profile picture:
1. Download the image from the link above
2. Open [@BotFather](https://t.me/botfather) on Telegram
3. Send `/setuserpic`
4. Select your bot
5. Upload the downloaded image

## 🧪 Development

### Local Setup

1. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run locally**
```bash
python main.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=bot --cov-report=html

# Run specific test file
pytest tests/test_system_monitor.py
```

### Code Quality

```bash
# Format code
black .

# Lint code
ruff check .

# Type checking
mypy bot/ config/
```

## 🐛 Troubleshooting

### Bot doesn't respond
- Check logs: `docker-compose logs -f`
- Verify bot token is correct
- Ensure your user ID is in `TELEGRAM_ALLOWED_USER_IDS`

### Docker permission errors
- User must be in `docker` group: `sudo usermod -aG docker $USER`
- Restart Docker service: `sudo systemctl restart docker`

### High memory usage
- Adjust resource limits in `docker-compose.yml`
- Increase alert check interval
- Reduce chart DPI in settings

### Temperature sensors not working
- Install `lm-sensors`: `sudo apt install lm-sensors`
- Run sensor detection: `sudo sensors-detect`

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Telegram Bot framework
- [psutil](https://github.com/giampaolo/psutil) - System monitoring
- [docker-py](https://github.com/docker/docker-py) - Docker SDK
- [matplotlib](https://matplotlib.org/) - Visualization library

## 📧 Support

For support, open an issue on GitHub.

## 📝 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ for system administrators

<p align="left">
  <sub>100% built with GitHub Copilot (Claude Sonnet 4.5)</sub><br>
  <sub>Arturo Carretero Calvo — 2026</sub>
</p>