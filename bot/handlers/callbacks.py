"""
Callback query handlers for inline keyboard buttons.
"""
from typing import Optional

from telegram import Update
from telegram.ext import ContextTypes

from bot.services import AlertManager, DockerManager, SystemMonitor
from bot.utils import (
    chart_generator,
    escape_markdown,
    format_cpu_metrics,
    format_disk_metrics,
    format_docker_containers,
    format_docker_stats,
    format_memory_metrics,
    format_system_status,
    format_top_processes,
    get_back_to_docker_keyboard,
    get_back_to_main_keyboard,
    get_container_action_keyboard,
    get_docker_menu_keyboard,
    get_main_menu_keyboard,
)
from config import COMMANDS, EMOJI, get_logger, settings

logger = get_logger(__name__)


class CallbackHandlers:
    """Handlers for inline keyboard callback queries."""

    def __init__(
        self,
        system_monitor: SystemMonitor,
        alert_manager: AlertManager,
        docker_manager: Optional[DockerManager] = None,
    ) -> None:
        """
        Initialize callback handlers.

        Args:
            system_monitor: System monitor service
            alert_manager: Alert manager service
            docker_manager: Docker manager service (optional)
        """
        self.system_monitor = system_monitor
        self.alert_manager = alert_manager
        self.docker_manager = docker_manager

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
            elif data == "menu_docker":
                await self._show_docker_menu(query)

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

            # Docker commands
            elif data == "cmd_docker":
                await self._handle_docker_list(query)
            elif data == "cmd_docker_stats":
                await self._handle_docker_stats(query)

            # Docker action menus
            elif data == "docker_logs_menu":
                await self._show_container_menu(query, "logs")
            elif data == "docker_restart_menu":
                await self._show_container_menu(query, "restart")
            elif data == "docker_start_menu":
                await self._show_container_menu(query, "start")
            elif data == "docker_stop_menu":
                await self._show_container_menu(query, "stop")

            # Docker actions on containers
            elif data.startswith("docker_logs_"):
                container_id = data.replace("docker_logs_", "")
                await self._handle_container_logs(query, container_id)
            elif data.startswith("docker_restart_"):
                container_id = data.replace("docker_restart_", "")
                await self._handle_container_restart(query, container_id)
            elif data.startswith("docker_start_"):
                container_id = data.replace("docker_start_", "")
                await self._handle_container_start(query, container_id)
            elif data.startswith("docker_stop_"):
                container_id = data.replace("docker_stop_", "")
                await self._handle_container_stop(query, container_id)

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
            f"Monitor CPU, Memory, Disk, Network\n\n"
            f"{EMOJI['docker']} *Docker Management*\n"
            f"Manage your containers\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_main_menu_keyboard()
        )

    async def _show_docker_menu(self, query) -> None:
        """Show the Docker submenu."""
        if not self.docker_manager:
            await query.edit_message_text(
                f"{EMOJI['warning']} Docker is not available on this system.",
                reply_markup=get_back_to_main_keyboard()
            )
            return

        message = (
            f"{EMOJI['docker']} *Docker Management*\n\n"
            f"Select an action:\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📦 *Containers* \\- List all containers\n"
            f"📊 *Stats* \\- Resource usage\n"
            f"📋 *Logs* \\- View container logs\n"
            f"🔄 *Restart* \\- Restart container\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━"
        )
        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_docker_menu_keyboard()
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
        chart_buf = chart_generator.generate_cpu_chart(cpu)
        
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
        chart_buf = chart_generator.generate_memory_chart(memory)
        
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
        
        message += "*🐳 Docker*\n"
        message += "`/docker` \\- List containers\n"
        message += "`/docker\\_stats` \\- Container stats\n\n"
        
        message += "*🔔 Alerts*\n"
        message += "`/alerts` \\- Alert configuration\n\n"
        
        message += "_Use the menu buttons for easier navigation\\!_"

        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_back_to_main_keyboard()
        )

    async def _handle_docker_list(self, query) -> None:
        """Handle Docker containers list callback."""
        if not self.docker_manager:
            await query.edit_message_text(
                f"{EMOJI['warning']} Docker is not available.",
                reply_markup=get_back_to_main_keyboard()
            )
            return

        containers = self.docker_manager.list_containers()
        message = format_docker_containers(containers)
        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_back_to_docker_keyboard()
        )

    async def _handle_docker_stats(self, query) -> None:
        """Handle Docker stats callback."""
        if not self.docker_manager:
            await query.edit_message_text(
                f"{EMOJI['warning']} Docker is not available.",
                reply_markup=get_back_to_main_keyboard()
            )
            return

        containers = self.docker_manager.list_containers()
        running = [c for c in containers if c.status == "running"]
        
        if not running:
            await query.edit_message_text(
                f"{EMOJI['info']} No running containers.",
                reply_markup=get_back_to_docker_keyboard()
            )
            return

        stats = []
        for container in running[:5]:
            stat = self.docker_manager.get_container_stats(container.container_id)
            if stat:
                stats.append(stat)

        message = format_docker_stats(stats)
        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_back_to_docker_keyboard()
        )

    async def _show_container_menu(self, query, action: str) -> None:
        """Show container selection menu for an action."""
        if not self.docker_manager:
            await query.edit_message_text(
                f"{EMOJI['warning']} Docker is not available.",
                reply_markup=get_back_to_main_keyboard()
            )
            return

        containers = self.docker_manager.list_containers()
        
        if not containers:
            await query.edit_message_text(
                f"{EMOJI['info']} No containers found.",
                reply_markup=get_back_to_docker_keyboard()
            )
            return

        action_text = {
            "logs": "view logs",
            "restart": "restart",
            "start": "start",
            "stop": "stop",
        }

        message = (
            f"*Select container to {action_text.get(action, action)}:*\n\n"
            f"🟢 Running  🔴 Stopped"
        )
        
        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_container_action_keyboard(containers, action)
        )

    async def _handle_container_logs(self, query, container_id: str) -> None:
        """Handle container logs callback."""
        if not self.docker_manager:
            return

        logs = self.docker_manager.get_container_logs(container_id, lines=30)
        
        # Truncate and escape
        if len(logs) > 3000:
            logs = logs[-3000:]
        
        logs_escaped = escape_markdown(logs)
        message = f"*📋 Container Logs*\n\n```\n{logs_escaped}\n```"
        
        # If message too long, just show last part
        if len(message) > 4000:
            message = f"*📋 Container Logs \\(truncated\\)*\n\n```\n{logs_escaped[-3500:]}\n```"

        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_back_to_docker_keyboard()
        )

    async def _handle_container_restart(self, query, container_id: str) -> None:
        """Handle container restart callback."""
        if not self.docker_manager:
            return

        success = self.docker_manager.restart_container(container_id)
        
        if success:
            message = f"{EMOJI['success']} Container restarted successfully\\!"
        else:
            message = f"{EMOJI['error']} Failed to restart container"

        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_back_to_docker_keyboard()
        )

    async def _handle_container_start(self, query, container_id: str) -> None:
        """Handle container start callback."""
        if not self.docker_manager:
            return

        success = self.docker_manager.start_container(container_id)
        
        if success:
            message = f"{EMOJI['success']} Container started successfully\\!"
        else:
            message = f"{EMOJI['error']} Failed to start container"

        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_back_to_docker_keyboard()
        )

    async def _handle_container_stop(self, query, container_id: str) -> None:
        """Handle container stop callback."""
        if not self.docker_manager:
            return

        success = self.docker_manager.stop_container(container_id)
        
        if success:
            message = f"{EMOJI['success']} Container stopped successfully\\!"
        else:
            message = f"{EMOJI['error']} Failed to stop container"

        await query.edit_message_text(
            message,
            parse_mode="MarkdownV2",
            reply_markup=get_back_to_docker_keyboard()
        )
