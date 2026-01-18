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

            message = f"{EMOJI['network']} *NETWORK INTERFACES*\n\n"

            for net in networks:
                # Skip loopback
                if net.interface == "lo":
                    continue

                interface_name = escape_markdown(net.interface)
                message += (
                    f"*{interface_name}*\n"
                    f"  ↓ RX: {escape_markdown(f'{net.bytes_recv_mb:.2f}')} MB\n"
                    f"  ↑ TX: {escape_markdown(f'{net.bytes_sent_mb:.2f}')} MB\n"
                    f"  📦 Packets: {net.packets_recv} / {net.packets_sent}\n"
                    f"  ⚠️ Errors: {net.errors_in} / {net.errors_out}\n\n"
                )

            await update.message.reply_text(message, parse_mode="MarkdownV2")

        except Exception as e:
            logger.error(f"Error in network_command: {e}")
            await update.message.reply_text(f"❌ Error getting network information: {str(e)}")

    @standard_handler
    async def temp_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /temp command - show CPU/system temperatures.

        Args:
            update: Telegram update
            context: Bot context
        """
        try:
            temps = self.monitor.get_temperature()

            if not temps:
                await update.message.reply_text(
                    f"{EMOJI['warning']} No temperature sensors found\\.\n\n"
                    f"_This may happen if:_\n"
                    f"• Hardware has no sensors\n"
                    f"• Drivers are not installed\n"
                    f"• Container has no access to /sys",
                    parse_mode="MarkdownV2",
                )
                return

            message = f"{EMOJI['temp']} *SYSTEM TEMPERATURE*\n\n"

            for sensor_type, sensors in temps.items():
                sensor_name = escape_markdown(sensor_type.replace("_", " ").title())
                message += f"*{sensor_name}:*\n"

                for sensor in sensors:
                    label = escape_markdown(sensor.label or "Sensor")
                    current = sensor.current
                    high = sensor.high
                    critical = sensor.critical

                    # Determine status indicator based on temperature
                    if critical and current >= critical:
                        status = "🔴"
                    elif high and current >= high:
                        status = "🟡"
                    else:
                        status = "🟢"

                    temp_str = escape_markdown(f"{current:.1f}°C")
                    message += f"  {status} {label}: {temp_str}"

                    if high or critical:
                        limits = []
                        if high:
                            limits.append(f"max: {high:.0f}°C")
                        if critical:
                            limits.append(f"crit: {critical:.0f}°C")
                        limits_str = escape_markdown(f" ({', '.join(limits)})")
                        message += limits_str
                    message += "\n"

                message += "\n"

            await update.message.reply_text(message, parse_mode="MarkdownV2")

        except Exception as e:
            logger.error(f"Error in temp_command: {e}")
            await update.message.reply_text(f"❌ Error getting temperature: {str(e)}")

    @standard_handler
    async def uptime_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /uptime command - show system uptime and logged users.

        Args:
            update: Telegram update
            context: Bot context
        """
        try:
            info = self.monitor.get_uptime_info()

            boot_time_str = info["boot_time"].strftime("%d/%m/%Y %H:%M:%S")
            
            message = f"{EMOJI['clock']} *SYSTEM UPTIME*\n\n"
            
            uptime_parts = []
            if info["days"] > 0:
                uptime_parts.append(f"{info['days']} day{'s' if info['days'] != 1 else ''}")
            if info["hours"] > 0:
                uptime_parts.append(f"{info['hours']} hour{'s' if info['hours'] != 1 else ''}")
            uptime_parts.append(f"{info['minutes']} minute{'s' if info['minutes'] != 1 else ''}")
            
            uptime_str = escape_markdown(", ".join(uptime_parts))
            boot_str = escape_markdown(boot_time_str)
            
            message += f"⏱️ *Uptime:* {uptime_str}\n\n"
            message += f"🔄 *Last boot:* {boot_str}\n\n"
            
            # Users info
            message += f"👥 *Logged in users:* {info['users_count']}\n"
            
            if info["users"]:
                for user in info["users"][:5]:  # Limit to 5 users
                    user_name = escape_markdown(user["name"])
                    terminal = escape_markdown(user["terminal"])
                    since = escape_markdown(user["started"].strftime("%H:%M"))
                    message += f"  • {user_name} \\({terminal}\\) since {since}\n"
            
            await update.message.reply_text(message, parse_mode="MarkdownV2")

        except Exception as e:
            logger.error(f"Error in uptime_command: {e}")
            await update.message.reply_text(f"❌ Error getting uptime: {str(e)}")

    @standard_handler
    async def services_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /services command - show systemd services status.

        Args:
            update: Telegram update
            context: Bot context
        """
        try:
            services = self.monitor.get_services_status()

            if not services:
                await update.message.reply_text(
                    f"{EMOJI['warning']} No systemd services found\\.\n\n"
                    f"_This may happen if:_\n"
                    f"• System doesn't use systemd\n"
                    f"• No common services installed\n"
                    f"• systemctl is not available",
                    parse_mode="MarkdownV2",
                )
                return

            message = f"{EMOJI['services']} *SERVICES STATUS*\n\n"

            # Sort: running first, then stopped
            running = [s for s in services if s["is_running"]]
            stopped = [s for s in services if not s["is_running"]]

            if running:
                message += f"🟢 *Active \\({len(running)}\\):*\n"
                for svc in running:
                    name = escape_markdown(svc["name"])
                    sub = escape_markdown(svc["sub_state"])
                    message += f"  • {name} \\({sub}\\)\n"
                message += "\n"

            if stopped:
                message += f"🔴 *Inactive \\({len(stopped)}\\):*\n"
                for svc in stopped:
                    name = escape_markdown(svc["name"])
                    status = escape_markdown(svc["status"])
                    message += f"  • {name} \\({status}\\)\n"

            await update.message.reply_text(message, parse_mode="MarkdownV2")

        except Exception as e:
            logger.error(f"Error in services_command: {e}")
            await update.message.reply_text(f"❌ Error getting services: {str(e)}")
