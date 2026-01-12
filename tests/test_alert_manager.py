"""
Unit tests for AlertManager service.
"""
import pytest
from datetime import datetime

from bot.models import CPUMetrics, MemoryMetrics, DiskMetrics
from bot.services import AlertManager
from config.constants import AlertType


@pytest.fixture
def alert_manager():
    """Create AlertManager instance for testing."""
    return AlertManager(
        cpu_threshold=80.0,
        memory_threshold=80.0,
        disk_threshold=90.0,
        cooldown_seconds=60,
    )


def test_check_cpu_alert_below_threshold(alert_manager):
    """Test CPU alert when below threshold."""
    metrics = CPUMetrics(
        percent=50.0,
        count=4,
        per_cpu=[50.0, 50.0, 50.0, 50.0],
    )
    
    alert = alert_manager.check_cpu_alert(metrics)
    assert alert is None


def test_check_cpu_alert_above_threshold(alert_manager):
    """Test CPU alert when above threshold."""
    metrics = CPUMetrics(
        percent=85.0,
        count=4,
        per_cpu=[85.0, 85.0, 85.0, 85.0],
    )
    
    alert = alert_manager.check_cpu_alert(metrics)
    assert alert is not None
    assert alert.alert_type == AlertType.CPU
    assert alert.metric_value == 85.0
    assert alert.threshold == 80.0


def test_check_memory_alert_below_threshold(alert_manager):
    """Test memory alert when below threshold."""
    metrics = MemoryMetrics(
        total=16 * (1024 ** 3),
        available=10 * (1024 ** 3),
        used=6 * (1024 ** 3),
        percent=37.5,
    )
    
    alert = alert_manager.check_memory_alert(metrics)
    assert alert is None


def test_check_memory_alert_above_threshold(alert_manager):
    """Test memory alert when above threshold."""
    metrics = MemoryMetrics(
        total=16 * (1024 ** 3),
        available=2 * (1024 ** 3),
        used=14 * (1024 ** 3),
        percent=87.5,
    )
    
    alert = alert_manager.check_memory_alert(metrics)
    assert alert is not None
    assert alert.alert_type == AlertType.MEMORY
    assert alert.metric_value == 87.5


def test_create_custom_alert(alert_manager):
    """Test custom alert creation."""
    alert = alert_manager.create_custom_alert(
        title="Test Alert",
        message="This is a test",
        severity="warning",
    )
    
    assert alert is not None
    assert alert.title == "Test Alert"
    assert alert.message == "This is a test"
    assert alert.severity == "warning"


def test_get_active_alerts(alert_manager):
    """Test getting active alerts."""
    # Create a custom alert
    alert_manager.create_custom_alert("Test", "Test message", "info")
    
    active_alerts = alert_manager.get_active_alerts()
    assert len(active_alerts) > 0


def test_acknowledge_alert(alert_manager):
    """Test acknowledging an alert."""
    alert = alert_manager.create_custom_alert("Test", "Test message", "info")
    
    alert_manager.acknowledge_alert(alert)
    assert alert.acknowledged is True


def test_alert_cooldown(alert_manager):
    """Test alert cooldown period."""
    metrics = CPUMetrics(
        percent=85.0,
        count=4,
        per_cpu=[85.0, 85.0, 85.0, 85.0],
    )
    
    # First alert should be created
    alert1 = alert_manager.check_cpu_alert(metrics)
    assert alert1 is not None
    
    # Second alert immediately after should be None (cooldown)
    alert2 = alert_manager.check_cpu_alert(metrics)
    assert alert2 is None
