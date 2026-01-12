# Project Structure

```
linux-server-admin-bot/
│
├── 📁 bot/                         # Main bot package
│   ├── __init__.py
│   │
│   ├── 📁 handlers/                # Telegram command handlers
│   │   ├── __init__.py
│   │   ├── basic.py                # /start, /help, /alerts
│   │   ├── system.py               # System monitoring commands
│   │   └── docker.py               # Docker management commands
│   │
│   ├── 📁 services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── system_monitor.py      # System metrics collection (psutil)
│   │   ├── docker_manager.py      # Docker container management
│   │   └── alert_manager.py       # Alert detection and management
│   │
│   ├── 📁 monitors/                # Background monitoring tasks
│   │   ├── __init__.py
│   │   └── health_monitor.py      # Periodic health checks
│   │
│   ├── 📁 models/                  # Data models
│   │   ├── __init__.py
│   │   └── metrics.py              # Dataclasses for all metrics
│   │
│   └── 📁 utils/                   # Utilities and helpers
│       ├── __init__.py
│       ├── decorators.py           # Auth, rate limiting, logging
│       ├── formatters.py           # Message formatting for Telegram
│       └── charts.py               # Chart generation (matplotlib)
│
├── 📁 config/                      # Configuration management
│   ├── __init__.py
│   ├── settings.py                 # Pydantic settings with validation
│   ├── constants.py                # Application constants and enums
│   └── logger.py                   # Logging configuration
│
├── 📁 tests/                       # Unit and integration tests
│   ├── __init__.py
│   ├── conftest.py                 # pytest configuration and fixtures
│   ├── test_system_monitor.py     # System monitor tests
│   └── test_alert_manager.py      # Alert manager tests
│
├── 📁 docs/                        # Documentation
│   ├── ARCHITECTURE.md             # Architecture documentation
│   └── GETTING_STARTED.md          # Getting started guide
│
├── 📄 main.py                      # Application entry point
│
├── 📄 Dockerfile                   # Multi-stage Docker build
├── 📄 docker-compose.yml           # Docker Compose configuration
├── 📄 .dockerignore                # Docker build exclusions
│
├── 📄 requirements.txt             # Python dependencies
├── 📄 pyproject.toml               # Python project configuration
│
├── 📄 .env.example                 # Environment variables template
├── 📄 .gitignore                   # Git exclusions
│
├── 📄 README.md                    # Project README
├── 📄 CONTRIBUTING.md              # Contributing guidelines
├── 📄 LICENSE                      # MIT License
│
├── 📄 Makefile                     # Development commands
└── 📄 setup.sh                     # Quick setup script

📁 logs/                            # Application logs (created at runtime)
📁 charts/                          # Generated charts (created at runtime)
```

## Key Files Description

### Application Core
- **main.py**: Entry point, initializes and runs the bot
- **bot/__init__.py**: Bot package initialization

### Handlers
- **handlers/basic.py**: Basic commands (start, help, alerts)
- **handlers/system.py**: System monitoring commands
- **handlers/docker.py**: Docker container management commands

### Services (Business Logic)
- **services/system_monitor.py**: Wraps psutil for system metrics
- **services/docker_manager.py**: Wraps docker-py for container management
- **services/alert_manager.py**: Alert detection and notification logic

### Background Tasks
- **monitors/health_monitor.py**: Periodic system health checks with APScheduler

### Data Models
- **models/metrics.py**: Dataclasses for CPU, memory, disk, network, Docker stats

### Utilities
- **utils/decorators.py**: Authorization, rate limiting, logging decorators
- **utils/formatters.py**: Telegram MarkdownV2 message formatting
- **utils/charts.py**: matplotlib chart generation

### Configuration
- **config/settings.py**: Pydantic settings with environment variable loading
- **config/constants.py**: Application constants, emojis, commands
- **config/logger.py**: Structured logging setup

### Docker
- **Dockerfile**: Multi-stage build for optimized image size
- **docker-compose.yml**: Service definition with volumes and network config
- **.dockerignore**: Files to exclude from Docker build

### Testing
- **tests/conftest.py**: pytest fixtures and configuration
- **tests/test_*.py**: Unit tests for services

### Documentation
- **README.md**: Complete project documentation
- **CONTRIBUTING.md**: Contribution guidelines
- **docs/ARCHITECTURE.md**: Detailed architecture documentation
- **docs/GETTING_STARTED.md**: Step-by-step setup guide

### Development Tools
- **Makefile**: Common development commands
- **setup.sh**: Interactive setup script
- **requirements.txt**: Python dependencies
- **pyproject.toml**: Python project config (black, ruff, mypy, pytest)

## Module Dependencies

```
main.py
  ├─> bot.handlers (BasicHandlers, SystemHandlers, DockerHandlers)
  ├─> bot.services (SystemMonitor, DockerManager, AlertManager)
  ├─> bot.monitors (HealthMonitor)
  └─> config (settings, setup_logging)

handlers
  ├─> services (for data retrieval)
  ├─> utils (decorators, formatters, charts)
  └─> config (constants, logger)

services
  ├─> models (data structures)
  ├─> config (logger)
  └─> external libraries (psutil, docker)

monitors
  ├─> services (SystemMonitor, AlertManager)
  └─> telegram.ext (Application)
```

## File Count Summary

- **Python files**: 24
- **Configuration files**: 6
- **Docker files**: 3
- **Documentation files**: 4
- **Total**: 37+ files

## Lines of Code (Approximate)

- **Handlers**: ~600 lines
- **Services**: ~900 lines
- **Utils**: ~700 lines
- **Config**: ~400 lines
- **Models**: ~300 lines
- **Tests**: ~250 lines
- **Total**: ~3,150 lines of Python code

## Technology Stack

### Core
- Python 3.11+
- python-telegram-bot 21.0.1
- psutil 5.9.8
- docker-py 7.0.0

### Visualization
- matplotlib 3.8.3
- seaborn 0.13.2

### Configuration
- pydantic 2.6.1
- python-dotenv 1.0.1

### Scheduling
- APScheduler 3.10.4

### Development
- pytest 8.0.0
- black 24.1.1
- ruff 0.2.1
- mypy 1.8.0

### Deployment
- Docker
- Docker Compose
