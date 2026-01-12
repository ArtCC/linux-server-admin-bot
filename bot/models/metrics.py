"""
Data models for system metrics, alerts, and responses.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional

from config.constants import AlertType, ContainerStatus


@dataclass
class CPUMetrics:
    """CPU usage metrics."""

    percent: float
    count: int
    per_cpu: List[float]
    frequency_current: Optional[float] = None
    frequency_min: Optional[float] = None
    frequency_max: Optional[float] = None
    load_avg: Optional[tuple[float, float, float]] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class MemoryMetrics:
    """Memory usage metrics."""

    total: int  # bytes
    available: int  # bytes
    used: int  # bytes
    percent: float
    swap_total: int = 0
    swap_used: int = 0
    swap_percent: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def total_gb(self) -> float:
        """Total memory in GB."""
        return self.total / (1024**3)

    @property
    def used_gb(self) -> float:
        """Used memory in GB."""
        return self.used / (1024**3)

    @property
    def available_gb(self) -> float:
        """Available memory in GB."""
        return self.available / (1024**3)


@dataclass
class DiskMetrics:
    """Disk usage metrics."""

    total: int  # bytes
    used: int  # bytes
    free: int  # bytes
    percent: float
    mount_point: str = "/"
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def total_gb(self) -> float:
        """Total disk space in GB."""
        return self.total / (1024**3)

    @property
    def used_gb(self) -> float:
        """Used disk space in GB."""
        return self.used / (1024**3)

    @property
    def free_gb(self) -> float:
        """Free disk space in GB."""
        return self.free / (1024**3)


@dataclass
class NetworkMetrics:
    """Network interface metrics."""

    interface: str
    bytes_sent: int
    bytes_recv: int
    packets_sent: int
    packets_recv: int
    errors_in: int = 0
    errors_out: int = 0
    drops_in: int = 0
    drops_out: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def bytes_sent_mb(self) -> float:
        """Bytes sent in MB."""
        return self.bytes_sent / (1024**2)

    @property
    def bytes_recv_mb(self) -> float:
        """Bytes received in MB."""
        return self.bytes_recv / (1024**2)


@dataclass
class ProcessInfo:
    """Process information."""

    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    status: str
    username: str = ""
    create_time: Optional[datetime] = None


@dataclass
class DockerContainerInfo:
    """Docker container information."""

    id: str
    name: str
    image: str
    status: ContainerStatus
    state: str
    created: datetime
    ports: Dict[str, List[Dict[str, str]]] = field(default_factory=dict)
    labels: Dict[str, str] = field(default_factory=dict)

    @property
    def short_id(self) -> str:
        """Get short container ID."""
        return self.id[:12]


@dataclass
class DockerContainerStats:
    """Docker container resource usage statistics."""

    container_id: str
    container_name: str
    cpu_percent: float
    memory_usage_mb: float
    memory_limit_mb: float
    memory_percent: float
    network_rx_mb: float
    network_tx_mb: float
    block_read_mb: float
    block_write_mb: float
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Alert:
    """System alert."""

    alert_type: AlertType
    title: str
    message: str
    severity: str  # info, warning, critical
    metric_value: float
    threshold: float
    timestamp: datetime = field(default_factory=datetime.now)
    acknowledged: bool = False

    def __str__(self) -> str:
        """String representation of alert."""
        return f"[{self.severity.upper()}] {self.title}: {self.message}"


@dataclass
class SystemStatus:
    """Overall system status summary."""

    cpu: CPUMetrics
    memory: MemoryMetrics
    disk: DiskMetrics
    uptime_seconds: float
    boot_time: datetime
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def uptime_formatted(self) -> str:
        """Get formatted uptime string."""
        days = int(self.uptime_seconds // 86400)
        hours = int((self.uptime_seconds % 86400) // 3600)
        minutes = int((self.uptime_seconds % 3600) // 60)
        return f"{days}d {hours}h {minutes}m"
