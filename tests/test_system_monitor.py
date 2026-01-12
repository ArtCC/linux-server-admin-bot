"""
Unit tests for SystemMonitor service.
"""
import pytest

from bot.services import SystemMonitor


@pytest.fixture
def system_monitor():
    """Create SystemMonitor instance for testing."""
    return SystemMonitor()


def test_get_cpu_metrics(system_monitor):
    """Test CPU metrics retrieval."""
    metrics = system_monitor.get_cpu_metrics(interval=0.1)
    
    assert metrics is not None
    assert 0 <= metrics.percent <= 100
    assert metrics.count > 0
    assert len(metrics.per_cpu) == metrics.count


def test_get_memory_metrics(system_monitor):
    """Test memory metrics retrieval."""
    metrics = system_monitor.get_memory_metrics()
    
    assert metrics is not None
    assert 0 <= metrics.percent <= 100
    assert metrics.total > 0
    assert metrics.used >= 0
    assert metrics.available >= 0
    assert metrics.total_gb > 0


def test_get_disk_metrics(system_monitor):
    """Test disk metrics retrieval."""
    metrics = system_monitor.get_disk_metrics("/")
    
    assert metrics is not None
    assert 0 <= metrics.percent <= 100
    assert metrics.total > 0
    assert metrics.used >= 0
    assert metrics.free >= 0
    assert metrics.mount_point == "/"


def test_get_top_processes(system_monitor):
    """Test top processes retrieval."""
    processes = system_monitor.get_top_processes(limit=5)
    
    assert processes is not None
    assert len(processes) <= 5
    assert len(processes) > 0
    
    # Check first process has required fields
    proc = processes[0]
    assert proc.pid > 0
    assert proc.name is not None
    assert proc.cpu_percent >= 0


def test_get_system_status(system_monitor):
    """Test system status retrieval."""
    status = system_monitor.get_system_status()
    
    assert status is not None
    assert status.cpu is not None
    assert status.memory is not None
    assert status.disk is not None
    assert status.uptime_seconds > 0
    assert status.boot_time is not None
