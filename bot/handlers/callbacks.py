"""
Callback query handlers for inline keyboard buttons.
"""
from telegram import Update
from telegram.ext import ContextTypes

from bot.services import AlertManager, SystemMonitor
from bot.utils import (
    chart_generator,
    escape_markdown,
    format_cpu_metrics,
    format_disk_metrics,
    format_memory_metrics,
    format_system_status,
    format_top_processes,
    get_back_to_main_keyboard,
    get_main_menu_keyboard,
)
from config import EMOJI, get_logger, settings

logger = get_logger(__name__)


class CallbackHandlers:
    """Handlers for inline keyboard callback queries."""

    def __init__(
        self,
        system_monitor: SystemMonitor,
        alert_manager: AlertManager,
    ) -> None:
        """
        Initialize callback handlers.

        Args:
            system_monitor: System monitor service
            alert_manager: Alert manager service
        """
        self.system_monitor = system_monitor
        self.alert_manager = alert_manager

    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Main callback handler that routes to specific handlers.

        Args:
            update: Telegram update
            context: Bot context
        """
        query = update.callback_query
        await query.answer()

        user = update.effective_user
        if not user or user.id not in settings.allowed_user_ids:
            await query.edit_message_text("🔒 Access denied.")
            return

        data = query.data
        logger.info(f"Callback from user {user.id}: {data}")

        try:
            # Menu navigation
            if data == "menu_main":
                await self._show_main_menu(query)

            # System commands
            elif data == "cmd_status":
                await self._handle_status(query)
            elif data == "cmd_cpu":
                await self._handle_cpu(query, context)
            elif data == "cmd_memory":
                await self._handle_memory(query, context)
            elif data == "cmd_disk":
                await self._handle_disk(query)
            elif data == "cmd_network":
                await self._handle_network(query)
            elif data == "cmd_top":
                await self._handle_top(query, context)
            elif data == "cmd_temp":
                await self._handle_temp(query)
            elif data == "cmd_uptime":
                await self._handle_uptime(query)
            elif data == "cmd_services":
                await self._handle_services(query)
            elif data == "cmd_alerts":
                await self._handle_alerts(query)
            elif data == "cmd_help":
                await self._handle_help(query)

            else:
                await query.edit_message_text(f"Unknown action: {data}")

        except Exception as e:
            logger.error(f"Error handling callback {data}: {e}")
            await query.edit_message_text(
                f"❌ Error: {str(e)[:200]}",
                reply_markup=get_back_to_main_keyboard()
            )

    async def _show_main_menu(self, query) -> None:
        """Show the main menu."""
        message = (
            f"{EMOJI['rocket']} *Linux Server Admin Bot*\n\n"
            f"Welcome\\! Select an option below:\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{EMOJI['chart']} *System Monitoring*\n"
            f"Monitor CPU, Memory, Disk, Network\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        # If coming from a photo message, delete and send new message
        if query.message.photo:
            await query.message.delete()
            await query.message.chat.send_message(
                message,
                parse_mode="MarkdownV2",
                reply_markup=get_main_menu_keyboard()
            )
        else:
            await query.edit_message_text(
                message,
                parse_mode="MarkdownV2",
                reply_markup=get_main_menu_keyboard()
            )

    async def _handle_status(self, query) -> None:
        """Handle system status callback."""
        status = self.system_monitor.get_system_status()
        message = format_system_status(status)
        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_back_to_main_keyboard()
        )

    async def _handle_cpu(self, query, context) -> None:
        """Handle CPU callback."""
        cpu = self.system_monitor.get_cpu_metrics()
        message = format_cpu_metrics(cpu)
        
        # Generate chart
        chart_buf = chart_generator.generate_cpu_chart(cpu.percent, cpu.per_cpu)
        
        # Send new message with photo (can't edit to photo)
        await query.message.delete()
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=chart_buf,
            caption=message,
            parse_mode="MarkdownV2",
            reply_markup=get_back_to_main_keyboard()
        )

    async def _handle_memory(self, query, context) -> None:
        """Handle memory callback."""
        memory = self.system_monitor.get_memory_metrics()
        message = format_memory_metrics(memory)
        
        # Generate chart
        chart_buf = chart_generator.generate_memory_chart(
            memory.total_gb, memory.used_gb, memory.available_gb, memory.percent
        )
        
        await query.message.delete()
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=chart_buf,
            caption=message,
            parse_mode="MarkdownV2",
            reply_markup=get_back_to_main_keyboard()
        )

    async def _handle_disk(self, query) -> None:
        """Handle disk callback."""
        disks = self.system_monitor.get_disk_metrics()
        message = format_disk_metrics(disks)
        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_back_to_main_keyboard()
        )

    async def _handle_network(self, query) -> None:
        """Handle network callback."""
        networks = self.system_monitor.get_network_metrics()
        
        if not networks:
            await query.edit_message_text(
                "No network interfaces found.",
                reply_markup=get_back_to_main_keyboard()
            )
            return

        message = f"*{EMOJI['network']} Network Interfaces*\n\n"

        for net in networks:
            if net.interface == "lo":
                continue
            
            interface_name = escape_markdown(net.interface)
            message += (
                f"*{interface_name}*\n"
                f"└ RX: {escape_markdown(f'{net.bytes_recv_mb:.2f}')} MB\n"
                f"└ TX: {escape_markdown(f'{net.bytes_sent_mb:.2f}')} MB\n"
                f"└ Packets: {net.packets_recv} / {net.packets_sent}\n\n"
            )

        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_back_to_main_keyboard()
        )

    async def _handle_top(self, query, context) -> None:
        """Handle top processes callback."""
        processes = self.system_monitor.get_top_processes(limit=10)
        message = format_top_processes(processes)
        
        # Generate chart
        processes_data = [
            {"name": p.name, "cpu_percent": p.cpu_percent} for p in processes
        ]
        chart_buf = chart_generator.generate_process_chart(processes_data)
        
        await query.message.delete()
        await context.bot.send_photo(
            chat_id=query.message.chat_id,
            photo=chart_buf,
            caption=message,
            parse_mode="MarkdownV2",
            reply_markup=get_back_to_main_keyboard()
        )

    async def _handle_alerts(self, query) -> None:
        """Handle alerts callback."""
        active_alerts = self.alert_manager.get_active_alerts()
        
        message = (
            f"*{EMOJI['alert']} Alert Configuration*\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{EMOJI['cpu']} CPU Threshold: *{settings.cpu_alert_threshold}%*\n"
            f"{EMOJI['memory']} Memory Threshold: *{settings.memory_alert_threshold}%*\n"
            f"{EMOJI['disk']} Disk Threshold: *{settings.disk_alert_threshold}%*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        )
        
        if active_alerts:
            message += f"*Active Alerts:* {len(active_alerts)}\n"
            for alert in active_alerts[:5]:
                message += f"⚠️ {escape_markdown(alert.message)}\n"
        else:
            message += f"{EMOJI['success']} No active alerts"

        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_back_to_main_keyboard()
        )

    async def _handle_help(self, query) -> None:
        """Handle help callback."""
        message = f"*{EMOJI['help']} Available Commands*\n\n"
        
        message += "*📊 System Monitoring*\n"
        message += "`/status` \\- System overview\n"
        message += "`/cpu` \\- CPU information\n"
        message += "`/memory` \\- Memory usage\n"
        message += "`/disk` \\- Disk usage\n"
        message += "`/network` \\- Network stats\n"
        message += "`/top` \\- Top processes\n"
        message += "`/temp` \\- System temperature\n"
        message += "`/uptime` \\- System uptime\n"
        message += "`/services` \\- Services status\n\n"
        
        message += "*🔔 Alerts*\n"
        message += "`/alerts` \\- Alert configuration\n\n"
        
        message += "*ℹ️ Info*\n"
        message += "`/author` \\- Bot author\n\n"
        
        message += "_Use the menu buttons for easier navigation\\!_"

        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_back_to_main_keyboard()
        )

    async def _handle_temp(self, query) -> None:
        """Handle temperature callback."""
        temps = self.system_monitor.get_temperature()

        if not temps:
            message = (
                f"{EMOJI['warning']} No temperature sensors found\\.\n\n"
                f"_This may happen if:_\n"
                f"• Hardware has no sensors\n"
                f"• Drivers are not installed\n"
                f"• Container has no access to /sys"
            )
            await query.edit_message_text(
                message,
                parse_mode="MarkdownV2",
                reply_markup=get_back_to_main_keyboard()
            )
            return

        message = f"*{EMOJI['temp']} System Temperature*\n\n"

        for sensor_type, sensors in temps.items():
            sensor_name = escape_markdown(sensor_type.replace("_", " ").title())
            message += f"*{sensor_name}:*\n"

            for sensor in sensors:
                label = escape_markdown(sensor.label or "Sensor")
                current = sensor.current
                high = sensor.high
                critical = sensor.critical

                if critical and current >= critical:
                    status = EMOJI["error"]
                elif high and current >= high:
                    status = EMOJI["warning"]
                else:
                    status = EMOJI["success"]

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

        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_back_to_main_keyboard()
        )

    async def _handle_uptime(self, query) -> None:
        """Handle uptime callback."""
        info = self.system_monitor.get_uptime_info()

        boot_time_str = info["boot_time"].strftime("%d/%m/%Y %H:%M:%S")
        
        message = f"*{EMOJI['clock']} System Uptime*\n\n"
        message += f"*Uptime:*\n"
        
        uptime_parts = []
        if info["days"] > 0:
            uptime_parts.append(f"{info['days']} day{'s' if info['days'] != 1 else ''}")
        if info["hours"] > 0:
            uptime_parts.append(f"{info['hours']} hour{'s' if info['hours'] != 1 else ''}")
        uptime_parts.append(f"{info['minutes']} minute{'s' if info['minutes'] != 1 else ''}")
        
        uptime_str = escape_markdown(", ".join(uptime_parts))
        boot_str = escape_markdown(boot_time_str)
        
        message += f"└ {uptime_str}\n\n"
        message += f"*Last boot:*\n└ {boot_str}\n\n"
        
        message += f"*Logged in users:* {info['users_count']}\n"
        
        if info["users"]:
            for user in info["users"][:5]:
                user_name = escape_markdown(user["name"])
                terminal = escape_markdown(user["terminal"])
                since = escape_markdown(user["started"].strftime("%H:%M"))
                message += f"  • {user_name} \\({terminal}\\) since {since}\n"
        
        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_back_to_main_keyboard()
        )

    async def _handle_services(self, query) -> None:
        """Handle services callback."""
        services = self.system_monitor.get_services_status()

        if not services:
            message = (
                f"{EMOJI['warning']} No systemd services found\\.\n\n"
                f"_This may happen if:_\n"
                f"• System doesn't use systemd\n"
                f"• No common services installed\n"
                f"• systemctl is not available"
            )
            await query.edit_message_text(
                message,
                parse_mode="MarkdownV2",
                reply_markup=get_back_to_main_keyboard()
            )
            return

        message = f"*{EMOJI['services']} Services Status*\n\n"

        running = [s for s in services if s["is_running"]]
        stopped = [s for s in services if not s["is_running"]]

        if running:
            message += f"*{EMOJI['success']} Active:*\n"
            for svc in running:
                name = escape_markdown(svc["name"])
                sub = escape_markdown(svc["sub_state"])
                message += f"  • {name} \\({sub}\\)\n"
            message += "\n"

        if stopped:
            message += f"*{EMOJI['error']} Inactive:*\n"
            for svc in stopped:
                name = escape_markdown(svc["name"])
                status = escape_markdown(svc["status"])
                message += f"  • {name} \\({status}\\)\n"

        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_back_to_main_keyboard()
        )
