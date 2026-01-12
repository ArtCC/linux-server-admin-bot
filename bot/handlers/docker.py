"""
Docker management command handlers.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from bot.services import DockerManager
from bot.utils import (
    chart_generator,
    escape_markdown,
    format_docker_containers,
    format_docker_stats,
    standard_handler,
)
from config import EMOJI, get_logger
from config.constants import MAX_CONTAINER_LOGS

logger = get_logger(__name__)


class DockerHandlers:
    """Handlers for Docker management commands."""

    def __init__(self, docker_manager: DockerManager) -> None:
        """
        Initialize Docker handlers.

        Args:
            docker_manager: Docker manager service
        """
        self.docker = docker_manager

    @standard_handler
    async def docker_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /docker command - list all containers.

        Args:
            update: Telegram update
            context: Bot context
        """
        try:
            containers = self.docker.list_containers(all_containers=True)
            message = format_docker_containers(containers)
            await update.message.reply_text(message, parse_mode="MarkdownV2")

        except Exception as e:
            logger.error(f"Error in docker_command: {e}")
            await update.message.reply_text(f"❌ Error listing containers: {str(e)}")

    @standard_handler
    async def docker_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /docker_stats command - show resource usage for running containers.

        Args:
            update: Telegram update
            context: Bot context
        """
        try:
            containers = self.docker.list_containers(all_containers=False)
            
            if not containers:
                await update.message.reply_text(f"{EMOJI['info']} No running containers found.")
                return

            # Collect stats for all running containers
            container_stats = {}
            detailed_messages = []

            for container in containers:
                try:
                    stats = self.docker.get_container_stats(container.id)
                    if stats:
                        container_stats[container.name] = {
                            "cpu": stats.cpu_percent,
                            "memory": stats.memory_percent,
                        }
                        # Store detailed message for later
                        detailed_messages.append(format_docker_stats(stats))
                except Exception as e:
                    logger.warning(f"Could not get stats for {container.name}: {e}")

            # Send chart if we have data
            if container_stats:
                chart_buf = chart_generator.generate_docker_stats_chart(container_stats)
                await update.message.reply_photo(
                    photo=chart_buf,
                    caption=f"{EMOJI['chart']} Docker Container Resources"
                )

                # Send detailed stats for each container
                for msg in detailed_messages[:5]:  # Limit to 5 containers
                    await update.message.reply_text(msg, parse_mode="MarkdownV2")
            else:
                await update.message.reply_text(f"{EMOJI['warning']} Could not retrieve container statistics.")

        except Exception as e:
            logger.error(f"Error in docker_stats_command: {e}")
            await update.message.reply_text(f"❌ Error getting Docker stats: {str(e)}")

    @standard_handler
    async def docker_logs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /docker_logs command - show logs from a container.

        Usage: /docker_logs <container_name_or_id>

        Args:
            update: Telegram update
            context: Bot context
        """
        if not context.args or len(context.args) == 0:
            containers = self.docker.list_containers(all_containers=False)
            if containers:
                names = [escape_markdown(c.name) for c in containers[:10]]
                await update.message.reply_text(
                    f"Usage: `/docker_logs <container>`\n\n"
                    f"Running containers:\n" + "\n".join(f"• {n}" for n in names),
                    parse_mode="MarkdownV2"
                )
            else:
                await update.message.reply_text("Usage: `/docker_logs <container>`", parse_mode="MarkdownV2")
            return

        container_id = context.args[0]

        try:
            logs = self.docker.get_container_logs(container_id, lines=MAX_CONTAINER_LOGS)
            
            # Split long logs into multiple messages
            max_length = 4000
            if len(logs) > max_length:
                logs = logs[-max_length:]
                logs = "...(truncated)...\n" + logs

            await update.message.reply_text(
                f"{EMOJI['container']} Logs for `{escape_markdown(container_id)}`:\n\n```\n{escape_markdown(logs)}\n```",
                parse_mode="MarkdownV2"
            )

        except Exception as e:
            logger.error(f"Error in docker_logs_command: {e}")
            await update.message.reply_text(f"❌ Error getting logs: {str(e)}")

    @standard_handler
    async def docker_restart_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /docker_restart command - restart a container.

        Usage: /docker_restart <container_name_or_id>

        Args:
            update: Telegram update
            context: Bot context
        """
        if not context.args or len(context.args) == 0:
            await update.message.reply_text(
                "Usage: `/docker_restart <container>`",
                parse_mode="MarkdownV2"
            )
            return

        container_id = context.args[0]

        try:
            success = self.docker.restart_container(container_id)
            
            if success:
                await update.message.reply_text(
                    f"{EMOJI['success']} Container `{escape_markdown(container_id)}` restarted successfully\\!",
                    parse_mode="MarkdownV2"
                )
            else:
                await update.message.reply_text(
                    f"{EMOJI['error']} Container `{escape_markdown(container_id)}` not found\\.",
                    parse_mode="MarkdownV2"
                )

        except Exception as e:
            logger.error(f"Error in docker_restart_command: {e}")
            await update.message.reply_text(f"❌ Error restarting container: {str(e)}")

    @standard_handler
    async def docker_stop_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /docker_stop command - stop a container.

        Usage: /docker_stop <container_name_or_id>

        Args:
            update: Telegram update
            context: Bot context
        """
        if not context.args or len(context.args) == 0:
            await update.message.reply_text(
                "Usage: `/docker_stop <container>`",
                parse_mode="MarkdownV2"
            )
            return

        container_id = context.args[0]

        try:
            success = self.docker.stop_container(container_id)
            
            if success:
                await update.message.reply_text(
                    f"{EMOJI['success']} Container `{escape_markdown(container_id)}` stopped successfully\\!",
                    parse_mode="MarkdownV2"
                )
            else:
                await update.message.reply_text(
                    f"{EMOJI['error']} Container `{escape_markdown(container_id)}` not found\\.",
                    parse_mode="MarkdownV2"
                )

        except Exception as e:
            logger.error(f"Error in docker_stop_command: {e}")
            await update.message.reply_text(f"❌ Error stopping container: {str(e)}")

    @standard_handler
    async def docker_start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /docker_start command - start a container.

        Usage: /docker_start <container_name_or_id>

        Args:
            update: Telegram update
            context: Bot context
        """
        if not context.args or len(context.args) == 0:
            await update.message.reply_text(
                "Usage: `/docker_start <container>`",
                parse_mode="MarkdownV2"
            )
            return

        container_id = context.args[0]

        try:
            success = self.docker.start_container(container_id)
            
            if success:
                await update.message.reply_text(
                    f"{EMOJI['success']} Container `{escape_markdown(container_id)}` started successfully\\!",
                    parse_mode="MarkdownV2"
                )
            else:
                await update.message.reply_text(
                    f"{EMOJI['error']} Container `{escape_markdown(container_id)}` not found\\.",
                    parse_mode="MarkdownV2"
                )

        except Exception as e:
            logger.error(f"Error in docker_start_command: {e}")
            await update.message.reply_text(f"❌ Error starting container: {str(e)}")
