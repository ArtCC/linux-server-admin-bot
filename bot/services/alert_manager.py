"""
Alert management service.
"""
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional

from bot.models import Alert, CPUMetrics, DiskMetrics, MemoryMetrics
from config import get_logger
from config.constants import AlertType

logger = get_logger(__name__)


class AlertManager:
    """Service for managing system alerts."""

    def __init__(
        self,
        cpu_threshold: float = 80.0,
        memory_threshold: float = 80.0,
        disk_threshold: float = 90.0,
        cooldown_seconds: int = 600,
    ) -> None:
        """
        Initialize alert manager.

        Args:
            cpu_threshold: CPU usage percentage threshold
            memory_threshold: Memory usage percentage threshold
            disk_threshold: Disk usage percentage threshold
            cooldown_seconds: Cooldown period between same alerts
        """
        self.cpu_threshold = cpu_threshold
        self.memory_threshold = memory_threshold
        self.disk_threshold = disk_threshold
        self.cooldown_seconds = cooldown_seconds

        # Track last alert time for each type
        self._last_alert_time: Dict[AlertType, datetime] = {}
        
        # Store active alerts
        self._active_alerts: List[Alert] = []
        
        # Alert callbacks
        self._callbacks: List[Callable[[Alert], None]] = []

        logger.info(
            f"AlertManager initialized - CPU: {cpu_threshold}%, "
            f"Memory: {memory_threshold}%, Disk: {disk_threshold}%"
        )

    def register_callback(self, callback: Callable[[Alert], None]) -> None:
        """
        Register a callback to be called when alerts are triggered.

        Args:
            callback: Function to call with Alert object
        """
        self._callbacks.append(callback)
        logger.info(f"Alert callback registered: {callback.__name__}")

    def check_cpu_alert(self, metrics: CPUMetrics) -> Optional[Alert]:
        """
        Check if CPU usage exceeds threshold.

        Args:
            metrics: CPU metrics

        Returns:
            Alert if threshold exceeded, None otherwise
        """
        if metrics.percent > self.cpu_threshold:
            if self._can_send_alert(AlertType.CPU):
                severity = "critical" if metrics.percent > 95 else "warning"
                alert = Alert(
                    alert_type=AlertType.CPU,
                    title="High CPU Usage",
                    message=f"CPU usage is at {metrics.percent:.1f}%",
                    severity=severity,
                    metric_value=metrics.percent,
                    threshold=self.cpu_threshold,
                )
                self._trigger_alert(alert)
                return alert
        return None

    def check_memory_alert(self, metrics: MemoryMetrics) -> Optional[Alert]:
        """
        Check if memory usage exceeds threshold.

        Args:
            metrics: Memory metrics

        Returns:
            Alert if threshold exceeded, None otherwise
        """
        if metrics.percent > self.memory_threshold:
            if self._can_send_alert(AlertType.MEMORY):
                severity = "critical" if metrics.percent > 95 else "warning"
                alert = Alert(
                    alert_type=AlertType.MEMORY,
                    title="High Memory Usage",
                    message=f"Memory usage is at {metrics.percent:.1f}% ({metrics.used_gb:.1f}GB / {metrics.total_gb:.1f}GB)",
                    severity=severity,
                    metric_value=metrics.percent,
                    threshold=self.memory_threshold,
                )
                self._trigger_alert(alert)
                return alert
        return None

    def check_disk_alert(self, metrics: DiskMetrics) -> Optional[Alert]:
        """
        Check if disk usage exceeds threshold.

        Args:
            metrics: Disk metrics

        Returns:
            Alert if threshold exceeded, None otherwise
        """
        if metrics.percent > self.disk_threshold:
            if self._can_send_alert(AlertType.DISK):
                severity = "critical" if metrics.percent > 95 else "warning"
                alert = Alert(
                    alert_type=AlertType.DISK,
                    title="High Disk Usage",
                    message=f"Disk usage is at {metrics.percent:.1f}% ({metrics.used_gb:.1f}GB / {metrics.total_gb:.1f}GB) on {metrics.mount_point}",
                    severity=severity,
                    metric_value=metrics.percent,
                    threshold=self.disk_threshold,
                )
                self._trigger_alert(alert)
                return alert
        return None

    def create_custom_alert(
        self,
        title: str,
        message: str,
        severity: str = "info",
        alert_type: AlertType = AlertType.CUSTOM,
    ) -> Alert:
        """
        Create a custom alert.

        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity (info, warning, critical)
            alert_type: Type of alert

        Returns:
            Created alert
        """
        alert = Alert(
            alert_type=alert_type,
            title=title,
            message=message,
            severity=severity,
            metric_value=0.0,
            threshold=0.0,
        )
        self._trigger_alert(alert)
        return alert

    def get_active_alerts(self) -> List[Alert]:
        """
        Get list of active alerts.

        Returns:
            List of active alerts
        """
        return self._active_alerts.copy()

    def acknowledge_alert(self, alert: Alert) -> None:
        """
        Acknowledge an alert.

        Args:
            alert: Alert to acknowledge
        """
        alert.acknowledged = True
        if alert in self._active_alerts:
            self._active_alerts.remove(alert)
        logger.info(f"Alert acknowledged: {alert.title}")

    def clear_alerts(self, alert_type: Optional[AlertType] = None) -> None:
        """
        Clear alerts.

        Args:
            alert_type: Type of alerts to clear, or None to clear all
        """
        if alert_type:
            self._active_alerts = [a for a in self._active_alerts if a.alert_type != alert_type]
            logger.info(f"Cleared alerts of type: {alert_type}")
        else:
            self._active_alerts.clear()
            logger.info("All alerts cleared")

    def _can_send_alert(self, alert_type: AlertType) -> bool:
        """
        Check if enough time has passed since last alert of this type.

        Args:
            alert_type: Type of alert

        Returns:
            True if alert can be sent
        """
        last_time = self._last_alert_time.get(alert_type)
        if last_time is None:
            return True
        
        time_since_last = datetime.now() - last_time
        return time_since_last.total_seconds() >= self.cooldown_seconds

    def _trigger_alert(self, alert: Alert) -> None:
        """
        Trigger an alert and call callbacks.

        Args:
            alert: Alert to trigger
        """
        self._last_alert_time[alert.alert_type] = datetime.now()
        self._active_alerts.append(alert)
        
        logger.warning(f"Alert triggered: {alert}")
        
        # Call all registered callbacks
        for callback in self._callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error calling alert callback {callback.__name__}: {e}")

    def get_alert_summary(self) -> Dict[str, int]:
        """
        Get summary of alerts by severity.

        Returns:
            Dictionary with alert counts by severity
        """
        summary = defaultdict(int)
        for alert in self._active_alerts:
            if not alert.acknowledged:
                summary[alert.severity] += 1
        return dict(summary)
