"""
Background monitoring and alert scheduler.
"""
import asyncio
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from telegram.ext import Application

from bot.services import AlertManager, SystemMonitor
from bot.utils import escape_markdown
from config import EMOJI, get_logger, settings

logger = get_logger(__name__)


class HealthMonitor:
    """Background health monitoring service."""

    def __init__(
        self,
        system_monitor: SystemMonitor,
        alert_manager: AlertManager,
        bot_app: Application,
    ) -> None:
        """
        Initialize health monitor.

        Args:
            system_monitor: System monitor service
            alert_manager: Alert manager service
            bot_app: Telegram bot application
        """
        self.system_monitor = system_monitor
        self.alert_manager = alert_manager
        self.bot_app = bot_app
        self.scheduler: Optional[AsyncIOScheduler] = None
        self._alert_chat_ids: set[int] = set()

        logger.info("HealthMonitor initialized")

    def register_alert_chat(self, chat_id: int) -> None:
        """
        Register a chat to receive alerts.

        Args:
            chat_id: Telegram chat ID
        """
        self._alert_chat_ids.add(chat_id)
        logger.info(f"Registered alert chat: {chat_id}")

    def unregister_alert_chat(self, chat_id: int) -> None:
        """
        Unregister a chat from receiving alerts.

        Args:
            chat_id: Telegram chat ID
        """
        self._alert_chat_ids.discard(chat_id)
        logger.info(f"Unregistered alert chat: {chat_id}")

    async def check_system_health(self) -> None:
        """Check system health and trigger alerts if needed."""
        try:
            logger.debug("Checking system health...")

            # Get metrics
            cpu_metrics = self.system_monitor.get_cpu_metrics(interval=0.5)
            memory_metrics = self.system_monitor.get_memory_metrics()
            disk_metrics = self.system_monitor.get_disk_metrics()

            # Check for alerts
            alerts = []
            
            cpu_alert = self.alert_manager.check_cpu_alert(cpu_metrics)
            if cpu_alert:
                alerts.append(cpu_alert)

            memory_alert = self.alert_manager.check_memory_alert(memory_metrics)
            if memory_alert:
                alerts.append(memory_alert)

            disk_alert = self.alert_manager.check_disk_alert(disk_metrics)
            if disk_alert:
                alerts.append(disk_alert)

            # Send alerts to registered chats
            for alert in alerts:
                await self._send_alert_to_chats(alert)

            logger.debug("System health check completed")

        except Exception as e:
            logger.error(f"Error checking system health: {e}", exc_info=True)

    async def _send_alert_to_chats(self, alert: any) -> None:
        """
        Send alert to all registered chats.

        Args:
            alert: Alert object
        """
        if not self._alert_chat_ids:
            logger.warning("No chats registered for alerts")
            return

        # Format alert message
        severity_emoji = {
            "info": EMOJI["info"],
            "warning": EMOJI["warning"],
            "critical": EMOJI["error"],
        }
        
        emoji = severity_emoji.get(alert.severity, EMOJI["warning"])
        
        message = (
            f"{emoji} *ALERT: {escape_markdown(alert.title)}*\n\n"
            f"{escape_markdown(alert.message)}\n\n"
            f"Threshold: {escape_markdown(f'{alert.threshold:.1f}%')}\n"
            f"Current: {escape_markdown(f'{alert.metric_value:.1f}%')}\n"
            f"Severity: {escape_markdown(alert.severity.upper())}"
        )

        # Send to all registered chats
        for chat_id in self._alert_chat_ids:
            try:
                await self.bot_app.bot.send_message(
                    chat_id=chat_id,
                    text=message,
                    parse_mode="MarkdownV2",
                )
                logger.info(f"Alert sent to chat {chat_id}: {alert.title}")
            except Exception as e:
                logger.error(f"Failed to send alert to chat {chat_id}: {e}")

    def start(self) -> None:
        """Start the health monitoring scheduler."""
        if self.scheduler and self.scheduler.running:
            logger.warning("Health monitor already running")
            return

        self.scheduler = AsyncIOScheduler()
        
        # Schedule health check
        self.scheduler.add_job(
            self.check_system_health,
            trigger=IntervalTrigger(seconds=settings.alert_check_interval),
            id="health_check",
            name="System Health Check",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info(f"Health monitor started (interval: {settings.alert_check_interval}s)")

        # Register all allowed users for alerts
        for user_id in settings.allowed_user_ids:
            self.register_alert_chat(user_id)

    def stop(self) -> None:
        """Stop the health monitoring scheduler."""
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Health monitor stopped")
        else:
            logger.warning("Health monitor not running")
