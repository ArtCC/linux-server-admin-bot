"""
Callback query handlers for inline keyboard buttons.
"""
import subprocess

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
    get_confirm_reboot_keyboard,
    get_confirm_shutdown_keyboard,
    get_main_menu_keyboard,
    get_power_menu_keyboard,
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
            elif data == "menu_power":
                await self._show_power_menu(query)

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
            elif data == "cmd_alerts":
                await self._handle_alerts(query)
            elif data == "cmd_help":
                await self._handle_help(query)

            # Power control commands
            elif data == "cmd_reboot":
                await self._handle_reboot_request(query)
            elif data == "cmd_shutdown":
                await self._handle_shutdown_request(query)
            elif data == "confirm_reboot":
                await self._handle_confirm_reboot(query)
            elif data == "confirm_shutdown":
                await self._handle_confirm_shutdown(query)

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
        message += "`/top` \\- Top processes\n\n"
        
        message += "*🔔 Alerts*\n"
        message += "`/alerts` \\- Alert configuration\n\n"
        
        message += "*⚡ Power Control*\n"
        message += "`/reboot` \\- Reboot server\n"
        message += "`/shutdown` \\- Shutdown server\n\n"
        
        message += "_Use the menu buttons for easier navigation\\!_"

        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_back_to_main_keyboard()
        )

    async def _show_power_menu(self, query) -> None:
        """Show the power control menu."""
        message = (
            f"{EMOJI['power']} *Power Control*\n\n"
            f"⚠️ *Warning:* These actions will affect the server\\!\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{EMOJI['reboot']} *Reboot* \\- Restart the server\n"
            f"{EMOJI['shutdown']} *Shutdown* \\- Power off the server\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"_Select an option carefully\\._"
        )
        
        if query.message.photo:
            await query.message.delete()
            await query.message.chat.send_message(
                message,
                parse_mode="MarkdownV2",
                reply_markup=get_power_menu_keyboard()
            )
        else:
            await query.edit_message_text(
                message,
                parse_mode="MarkdownV2",
                reply_markup=get_power_menu_keyboard()
            )

    async def _handle_reboot_request(self, query) -> None:
        """Handle reboot request - show confirmation."""
        message = (
            f"{EMOJI['danger']} *REBOOT CONFIRMATION*\n\n"
            f"You are about to *REBOOT* the server\\.\n\n"
            f"⚠️ This will:\n"
            f"• Disconnect all active sessions\n"
            f"• Stop all running services\n"
            f"• Restart the operating system\n\n"
            f"_Are you absolutely sure\\?_"
        )
        
        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_confirm_reboot_keyboard()
        )

    async def _handle_shutdown_request(self, query) -> None:
        """Handle shutdown request - show confirmation."""
        message = (
            f"{EMOJI['danger']} *SHUTDOWN CONFIRMATION*\n\n"
            f"You are about to *SHUTDOWN* the server\\.\n\n"
            f"⚠️ This will:\n"
            f"• Disconnect all active sessions\n"
            f"• Stop all running services\n"
            f"• Power off the server completely\n"
            f"• Require physical access to restart\\!\n\n"
            f"_Are you absolutely sure\\?_"
        )
        
        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_confirm_shutdown_keyboard()
        )

    async def _handle_confirm_reboot(self, query) -> None:
        """Execute server reboot."""
        user = query.from_user
        logger.warning(f"SERVER REBOOT initiated by user {user.id} ({user.username})")
        
        await query.edit_message_text(
            f"{EMOJI['reboot']} *Rebooting server\\.\\.\\.*\n\n"
            f"The server will restart now\\.\n"
            f"Bot will be back online shortly\\.",
            parse_mode="MarkdownV2"
        )
        
        try:
            # Execute reboot command on host using nsenter
            # nsenter -t 1 enters the namespace of PID 1 (init/systemd on host)
            subprocess.Popen(
                ["nsenter", "-t", "1", "-m", "-u", "-i", "-n", "--", "shutdown", "-r", "now"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            logger.error(f"Failed to execute reboot: {e}")
            await query.edit_message_text(
                f"{EMOJI['error']} *Reboot Failed*\n\n"
                f"Error: {escape_markdown(str(e))}",
                parse_mode="MarkdownV2",
                reply_markup=get_power_menu_keyboard()
            )

    async def _handle_confirm_shutdown(self, query) -> None:
        """Execute server shutdown."""
        user = query.from_user
        logger.warning(f"SERVER SHUTDOWN initiated by user {user.id} ({user.username})")
        
        await query.edit_message_text(
            f"{EMOJI['shutdown']} *Shutting down server\\.\\.\\.*\n\n"
            f"The server will power off now\\.\n"
            f"Physical access required to restart\\.",
            parse_mode="MarkdownV2"
        )
        
        try:
            # Execute shutdown command on host using nsenter
            # nsenter -t 1 enters the namespace of PID 1 (init/systemd on host)
            subprocess.Popen(
                ["nsenter", "-t", "1", "-m", "-u", "-i", "-n", "--", "shutdown", "-h", "now"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        except Exception as e:
            logger.error(f"Failed to execute shutdown: {e}")
            await query.edit_message_text(
                f"{EMOJI['error']} *Shutdown Failed*\n\n"
                f"Error: {escape_markdown(str(e))}",
                parse_mode="MarkdownV2",
                reply_markup=get_power_menu_keyboard()
            )
