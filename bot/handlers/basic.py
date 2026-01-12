"""
Basic command handlers (start, help, alerts).
"""
from telegram import Update
from telegram.ext import ContextTypes

from bot.services import AlertManager
from bot.utils import escape_markdown, standard_handler
from config import COMMANDS, EMOJI, get_logger

logger = get_logger(__name__)


class BasicHandlers:
    """Handlers for basic bot commands."""

    def __init__(self, alert_manager: AlertManager) -> None:
        """
        Initialize basic handlers.

        Args:
            alert_manager: Alert manager service
        """
        self.alert_manager = alert_manager

    @standard_handler
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /start command - welcome message.

        Args:
            update: Telegram update
            context: Bot context
        """
        user = update.effective_user
        
        welcome_message = (
            f"{EMOJI['rocket']} *Linux Server Admin Bot*\n\n"
            f"Welcome, {escape_markdown(user.first_name)}\\!\n\n"
            f"This bot helps you monitor and manage your Ubuntu server\\.\n\n"
            f"Use /help to see available commands\\."
        )
        
        await update.message.reply_text(welcome_message, parse_mode="MarkdownV2")

    @standard_handler
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /help command - show available commands.

        Args:
            update: Telegram update
            context: Bot context
        """
        help_text = f"*{EMOJI['info']} Available Commands*\n\n"
        
        # Group commands by category
        basic_cmds = ["/start", "/help", "/status"]
        system_cmds = ["/cpu", "/memory", "/disk", "/top", "/network"]
        docker_cmds = ["/docker", "/docker_stats", "/docker_logs", "/docker_restart", "/docker_stop", "/docker_start"]
        alert_cmds = ["/alerts"]
        
        help_text += "*Basic Commands:*\n"
        for cmd in basic_cmds:
            if cmd in COMMANDS:
                help_text += f"`{cmd}` \\- {escape_markdown(COMMANDS[cmd])}\n"
        
        help_text += "\n*System Monitoring:*\n"
        for cmd in system_cmds:
            if cmd in COMMANDS:
                help_text += f"`{cmd}` \\- {escape_markdown(COMMANDS[cmd])}\n"
        
        help_text += "\n*Docker Management:*\n"
        for cmd in docker_cmds:
            if cmd in COMMANDS:
                help_text += f"`{cmd}` \\- {escape_markdown(COMMANDS[cmd])}\n"
        
        help_text += "\n*Alerts:*\n"
        for cmd in alert_cmds:
            if cmd in COMMANDS:
                help_text += f"`{cmd}` \\- {escape_markdown(COMMANDS[cmd])}\n"
        
        await update.message.reply_text(help_text, parse_mode="MarkdownV2")

    @standard_handler
    async def alerts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Handle /alerts command - show alert configuration and active alerts.

        Args:
            update: Telegram update
            context: Bot context
        """
        try:
            active_alerts = self.alert_manager.get_active_alerts()
            summary = self.alert_manager.get_alert_summary()
            
            message = f"*{EMOJI['warning']} Alert Configuration*\n\n"
            message += f"*Thresholds:*\n"
            message += f"• CPU: {escape_markdown(str(self.alert_manager.cpu_threshold))}%\n"
            message += f"• Memory: {escape_markdown(str(self.alert_manager.memory_threshold))}%\n"
            message += f"• Disk: {escape_markdown(str(self.alert_manager.disk_threshold))}%\n"
            message += f"• Cooldown: {escape_markdown(str(self.alert_manager.cooldown_seconds // 60))} minutes\n\n"
            
            if active_alerts:
                message += f"*Active Alerts:* {len(active_alerts)}\n"
                for severity, count in summary.items():
                    emoji_map = {"info": EMOJI["info"], "warning": EMOJI["warning"], "critical": EMOJI["error"]}
                    message += f"{emoji_map.get(severity, EMOJI['info'])} {escape_markdown(severity.title())}: {count}\n"
                
                message += "\n"
                for alert in active_alerts[:5]:  # Show up to 5 alerts
                    message += f"• {escape_markdown(alert.title)}: {escape_markdown(f'{alert.metric_value:.1f}%')}\n"
            else:
                message += f"{EMOJI['success']} No active alerts\\."
            
            await update.message.reply_text(message, parse_mode="MarkdownV2")

        except Exception as e:
            logger.error(f"Error in alerts_command: {e}")
            await update.message.reply_text(f"❌ Error getting alerts: {str(e)}")
