"""
Application constants and enums.
"""
from enum import Enum


class AlertType(str, Enum):
    """Types of system alerts."""

    CPU = "cpu"
    MEMORY = "memory"
    DISK = "disk"
    DOCKER = "docker"
    CUSTOM = "custom"


class ContainerStatus(str, Enum):
    """Docker container statuses."""

    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    RESTARTING = "restarting"
    EXITED = "exited"
    DEAD = "dead"


class ChartType(str, Enum):
    """Types of charts that can be generated."""

    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    HORIZONTAL_BAR = "hbar"


# Emoji constants for better UX
EMOJI = {
    "cpu": "🖥️",
    "memory": "💾",
    "disk": "💿",
    "network": "🌐",
    "docker": "🐳",
    "container": "📦",
    "warning": "⚠️",
    "error": "❌",
    "success": "✅",
    "info": "ℹ️",
    "chart": "📊",
    "fire": "🔥",
    "check": "✔️",
    "cross": "✖️",
    "arrow_up": "⬆️",
    "arrow_down": "⬇️",
    "clock": "🕐",
    "lock": "🔒",
    "rocket": "🚀",
    "back": "⬅️",
    "home": "🏠",
    "help": "❓",
    "alert": "🔔",
    "process": "⚙️",
    "settings": "⚙️",
    "refresh": "🔄",
    "play": "▶️",
    "stop": "⏹️",
    "logs": "📋",
}

# Command descriptions for bot menu
COMMANDS = {
    "/start": "Iniciar el bot y mostrar información de bienvenida",
    "/help": "Mostrar ayuda y lista de comandos disponibles",
    "/status": "Estado general del sistema (CPU, RAM, Disco)",
    "/cpu": "Información detallada de CPU con gráfico",
    "/memory": "Información detallada de memoria RAM",
    "/disk": "Información de uso de disco",
    "/top": "Procesos top por uso de CPU",
    "/docker": "Listar contenedores Docker",
    "/docker_stats": "Estadísticas de recursos por contenedor",
    "/docker_logs": "Ver logs de un contenedor",
    "/docker_restart": "Reiniciar un contenedor",
    "/docker_stop": "Detener un contenedor",
    "/docker_start": "Iniciar un contenedor",
    "/alerts": "Ver configuración de alertas",
    "/network": "Información de red y puertos abiertos",
}

# System metrics refresh rates (seconds)
REFRESH_RATES = {
    "cpu": 1,
    "memory": 2,
    "disk": 5,
    "network": 2,
}

# Chart colors palette
CHART_COLORS = {
    "primary": "#3498db",
    "success": "#2ecc71",
    "warning": "#f39c12",
    "danger": "#e74c3c",
    "info": "#1abc9c",
    "cpu": "#3498db",
    "memory": "#9b59b6",
    "disk": "#e67e22",
    "network": "#1abc9c",
}

# Format strings
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M:%S"

# Limits
MAX_LOG_LINES = 100
MAX_PROCESS_COUNT = 10
MAX_CONTAINER_LOGS = 50
