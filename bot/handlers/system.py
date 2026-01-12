"""
System monitoring command handlers.
"""
from telegram import Update
from telegram.ext import ContextTypes

from bot.services import SystemMonitor
from bot.utils import (
    chart_generator,
    escape_markdown,
    format_cpu_metrics,
    format_disk_metrics,
    format_memory_metrics,
    format_system_status,
    format_top_processes,
    standard_handler,
)
from config import EMOJI, get_logger, settings
from config.constants import MAX_PROCESS_COUNT

logger = get_logger(__name__)


class SystemHandlers:
    """Handlers for system monitoring commands."""

    def __init__(self, monitor: SystemMonitor) -> None:
        """
        Initialize system handlers.

        Args:
            monitor: System monitor service
        """
        self.monitor = monitor

    @standard_handler
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /status command - show overall system status.

        Args:
            update: Telegram update
            context: Bot context
        """
        try:
            status = self.monitor.get_system_status()
            message = format_system_status(status)
            await update.message.reply_text(message, parse_mode="MarkdownV2")
        except Exception as e:
            logger.error(f"Error in status_command: {e}")
            await update.message.reply_text(f"❌ Error getting system status: {str(e)}")

    @standard_handler
    async def cpu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /cpu command - show detailed CPU information with chart.

        Args:
            update: Telegram update
            context: Bot context
        """
        try:
            # Get CPU metrics
            metrics = self.monitor.get_cpu_metrics(interval=1.0)

            # Send text message
            message = format_cpu_metrics(metrics)
            await update.message.reply_text(message, parse_mode="MarkdownV2")

            # Generate and send chart
            chart_buf = chart_generator.generate_cpu_chart(
                cpu_percent=metrics.percent,
                per_cpu=metrics.per_cpu,
            )
            await update.message.reply_photo(photo=chart_buf, caption=f"{EMOJI['chart']} CPU Usage Chart")

        except Exception as e:
            logger.error(f"Error in cpu_command: {e}")
            await update.message.reply_text(f"❌ Error getting CPU information: {str(e)}")

    @standard_handler
    async def memory_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /memory command - show detailed memory information with chart.

        Args:
            update: Telegram update
            context: Bot context
        """
        try:
            # Get memory metrics
            metrics = self.monitor.get_memory_metrics()

            # Send text message
            message = format_memory_metrics(metrics)
            await update.message.reply_text(message, parse_mode="MarkdownV2")

            # Generate and send chart
            chart_buf = chart_generator.generate_memory_chart(
                total_gb=metrics.total_gb,
                used_gb=metrics.used_gb,
                available_gb=metrics.available_gb,
                percent=metrics.percent,
            )
            await update.message.reply_photo(photo=chart_buf, caption=f"{EMOJI['chart']} Memory Usage Chart")

        except Exception as e:
            logger.error(f"Error in memory_command: {e}")
            await update.message.reply_text(f"❌ Error getting memory information: {str(e)}")

    @standard_handler
    async def disk_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /disk command - show detailed disk information with chart.

        Args:
            update: Telegram update
            context: Bot context
        """
        try:
            # Get disk metrics
            metrics = self.monitor.get_disk_metrics()

            # Send text message
            message = format_disk_metrics(metrics)
            await update.message.reply_text(message, parse_mode="MarkdownV2")

            # Generate and send chart
            chart_buf = chart_generator.generate_disk_chart(
                total_gb=metrics.total_gb,
                used_gb=metrics.used_gb,
                free_gb=metrics.free_gb,
                percent=metrics.percent,
            )
            await update.message.reply_photo(photo=chart_buf, caption=f"{EMOJI['chart']} Disk Usage Chart")

        except Exception as e:
            logger.error(f"Error in disk_command: {e}")
            await update.message.reply_text(f"❌ Error getting disk information: {str(e)}")

    @standard_handler
    async def top_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /top command - show top processes by CPU usage.

        Args:
            update: Telegram update
            context: Bot context
        """
        try:
            # Get top processes
            processes = self.monitor.get_top_processes(limit=MAX_PROCESS_COUNT)

            # Send text message
            message = format_top_processes(processes)
            await update.message.reply_text(message, parse_mode="MarkdownV2")

            # Generate and send chart
            processes_data = [
                {"name": p.name, "cpu_percent": p.cpu_percent} for p in processes
            ]
            chart_buf = chart_generator.generate_process_chart(processes_data)
            await update.message.reply_photo(photo=chart_buf, caption=f"{EMOJI['chart']} Top Processes")

        except Exception as e:
            logger.error(f"Error in top_command: {e}")
            await update.message.reply_text(f"❌ Error getting process information: {str(e)}")

    @standard_handler
    async def network_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /network command - show network interface information.

        Args:
            update: Telegram update
            context: Bot context
        """
        try:
            # Get network metrics
            networks = self.monitor.get_network_metrics()

            if not networks:
                await update.message.reply_text("No network interfaces found.")
                return

            message = f"*{EMOJI['network']} Network Interfaces*\n\n"

            for net in networks:
                # Skip loopback
                if net.interface == "lo":
                    continue

                interface_name = escape_markdown(net.interface)
                message += (
                    f"*{interface_name}*\n"
                    f"└ RX: {escape_markdown(f'{net.bytes_recv_mb:.2f}')} MB\n"
                    f"└ TX: {escape_markdown(f'{net.bytes_sent_mb:.2f}')} MB\n"
                    f"└ Packets: {net.packets_recv} / {net.packets_sent}\n"
                    f"└ Errors: {net.errors_in} / {net.errors_out}\n\n"
                )

            await update.message.reply_text(message, parse_mode="MarkdownV2")

        except Exception as e:
            logger.error(f"Error in network_command: {e}")
            await update.message.reply_text(f"❌ Error getting network information: {str(e)}")
