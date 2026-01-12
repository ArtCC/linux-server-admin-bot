# Architecture Documentation

## System Overview

The Linux Server Admin Bot is built with a clean, modular architecture following SOLID principles and separation of concerns.

## High-Level Architecture

```
┌─────────────────┐
│  Telegram API   │
└────────┬────────┘
         │
    ┌────▼─────┐
    │   Bot    │ (main.py)
    │ Application │
    └────┬─────┘
         │
    ┌────▼─────────────────────────────┐
    │         Handlers Layer           │
    │  (basic, system, docker)         │
    └────┬─────────────────────────────┘
         │
    ┌────▼─────────────────────────────┐
    │        Services Layer            │
    │  (SystemMonitor, DockerManager,  │
    │   AlertManager)                  │
    └────┬─────────────────────────────┘
         │
    ┌────▼─────────────────────────────┐
    │      External Resources          │
    │  (psutil, docker-py, filesystem) │
    └──────────────────────────────────┘
```

## Layer Descriptions

### 1. Handlers Layer (`bot/handlers/`)

**Responsibility**: Handle Telegram commands and user interactions

**Components**:
- `BasicHandlers`: /start, /help, /alerts
- `SystemHandlers`: System monitoring commands
- `DockerHandlers`: Docker management commands

**Key Features**:
- Decorated with authorization and rate limiting
- Input validation
- Error handling and user feedback
- Async/await for non-blocking operations

### 2. Services Layer (`bot/services/`)

**Responsibility**: Business logic and external API interactions

**Components**:
- `SystemMonitor`: psutil wrapper for system metrics
- `DockerManager`: Docker SDK wrapper for container management
- `AlertManager`: Alert detection and notification logic

**Key Features**:
- Pure business logic, no Telegram-specific code
- Testable in isolation
- Type-safe with dataclasses
- Error handling and logging

### 3. Models Layer (`bot/models/`)

**Responsibility**: Data structures and domain models

**Components**:
- Dataclasses for metrics (CPU, Memory, Disk, Network)
- Container information models
- Alert models

**Key Features**:
- Immutable data structures
- Type hints for all fields
- Property methods for computed values
- No business logic (pure data)

### 4. Utils Layer (`bot/utils/`)

**Responsibility**: Reusable utilities and helpers

**Components**:
- `decorators.py`: Authorization, rate limiting, logging
- `formatters.py`: Telegram message formatting
- `charts.py`: matplotlib chart generation

**Key Features**:
- Stateless functions
- Highly reusable
- Well-tested

### 5. Monitors Layer (`bot/monitors/`)

**Responsibility**: Background monitoring and scheduled tasks

**Components**:
- `HealthMonitor`: Periodic system health checks
- APScheduler integration

**Key Features**:
- Async background tasks
- Configurable intervals
- Alert broadcasting

### 6. Config Layer (`config/`)

**Responsibility**: Configuration management

**Components**:
- `settings.py`: Pydantic settings with validation
- `constants.py`: Application constants
- `logger.py`: Logging configuration

**Key Features**:
- Environment variable loading
- Type validation
- Centralized configuration

## Data Flow

### Command Execution Flow

```
1. User sends /cpu command
2. Telegram API → Bot Application
3. CommandHandler routes to SystemHandlers.cpu_command
4. Handler applies decorators:
   - authorized_only: Check user authorization
   - rate_limited: Check rate limit
   - typing_action: Show typing indicator
   - log_execution: Log command execution
   - error_handler: Catch and handle errors
5. Handler calls SystemMonitor.get_cpu_metrics()
6. SystemMonitor uses psutil to fetch metrics
7. Metrics returned as CPUMetrics dataclass
8. Handler formats metrics with formatters.format_cpu_metrics()
9. Handler generates chart with ChartGenerator
10. Handler sends text message and chart to user
11. Execution logged
```

### Alert Flow

```
1. APScheduler triggers HealthMonitor.check_system_health()
2. HealthMonitor fetches system metrics
3. HealthMonitor calls AlertManager.check_*_alert()
4. AlertManager compares metrics vs thresholds
5. If threshold exceeded and cooldown passed:
   - AlertManager creates Alert object
   - AlertManager calls registered callbacks
6. HealthMonitor receives alert callback
7. HealthMonitor formats alert message
8. HealthMonitor broadcasts to all registered chats
9. Alert logged
```

## Security Architecture

### Authentication
- Whitelist-based: Only configured user IDs can use the bot
- Checked at handler level via `@authorized_only` decorator
- User ID validation on every command

### Rate Limiting
- Per-user rate limiting
- Configurable limits (calls per period)
- Sliding window implementation
- Applied via `@rate_limited` decorator

### Docker Security
- Read-only socket mount
- No new privileges
- Non-root user in container
- Resource limits

### Logging & Auditing
- All commands logged with user ID
- Unauthorized access attempts logged
- Error logging with stack traces
- Structured logging format

## Scalability Considerations

### Current Design
- Single-instance bot
- In-memory state (rate limiting, alerts)
- Async/await for concurrency

### Future Scalability
- **Redis**: For distributed rate limiting and caching
- **PostgreSQL**: For persistent storage of metrics history
- **Message Queue**: For async task processing
- **Multi-server**: Support for managing multiple servers

## Testing Strategy

### Unit Tests
- Test individual services in isolation
- Mock external dependencies (psutil, Docker)
- Test error handling paths

### Integration Tests
- Test handler → service → external API flow
- Use test doubles for Telegram API
- Verify end-to-end functionality

### Test Coverage
- Minimum 80% coverage target
- Focus on critical paths
- Test edge cases and error conditions

## Performance Considerations

### Optimization Techniques
- Chart generation in memory (BytesIO)
- Lazy loading of metrics
- Caching for frequently accessed data
- Async operations to prevent blocking

### Resource Limits
- Docker memory limits
- Rate limiting to prevent abuse
- Configurable alert intervals
- Log rotation

## Monitoring & Observability

### Logging
- Structured logging with levels
- Colored console output
- File logging with rotation
- Request/response logging

### Metrics
- System metrics collection
- Docker stats monitoring
- Alert frequency tracking

### Health Checks
- Docker healthcheck endpoint
- Background task monitoring
- Service availability checks

## Deployment Architecture

### Docker Container
```
┌─────────────────────────────────────┐
│         Docker Container            │
│                                     │
│  ┌───────────────────────────────┐ │
│  │    Bot Application            │ │
│  │    (Python 3.11)              │ │
│  └───────────────────────────────┘ │
│                                     │
│  Volumes (Read-only):               │
│  • /var/run/docker.sock            │
│  • /proc → /host/proc              │
│  • /sys → /host/sys                │
│  • /var/log → /host/logs           │
│                                     │
└─────────────────────────────────────┘
         │
         ▼
   ┌────────────┐
   │ Host System│
   └────────────┘
```

### Network Mode
- Uses `host` network mode for better system monitoring
- Direct access to host network interfaces
- No port mapping needed

## Extension Points

### Adding New Commands
1. Create handler method in appropriate handler class
2. Apply standard decorators
3. Register in `BotApplication._register_handlers()`

### Adding New Metrics
1. Add dataclass to `bot/models/metrics.py`
2. Add service method to relevant service
3. Add formatter to `bot/utils/formatters.py`
4. Create handler in appropriate handler class

### Adding New Alert Types
1. Add to `AlertType` enum in `config/constants.py`
2. Add check method to `AlertManager`
3. Add to health monitor checks

## Future Architecture Considerations

### Microservices
- Separate monitoring service
- Separate alert service
- API gateway pattern

### Event-Driven
- Event bus for alert propagation
- Webhook support for integrations
- Real-time metric streaming

### Multi-Tenancy
- Support multiple servers per user
- Server configuration management
- Per-server alert rules
