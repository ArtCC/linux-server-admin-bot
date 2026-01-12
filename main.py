"""
Main application entry point.

Copyright 2026 Linux Server Admin Bot Contributors

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import asyncio
import signal
import sys
from typing import Optional

from telegram.ext import Application, CommandHandler

from bot.handlers import BasicHandlers, DockerHandlers, SystemHandlers
from bot.monitors import HealthMonitor
from bot.services import AlertManager, DockerManager, SystemMonitor
from config import get_logger, settings, setup_logging

logger = get_logger(__name__)


class BotApplication:
    """Main bot application."""

    def __init__(self) -> None:
        """Initialize bot application."""
        self.app: Optional[Application] = None
        self.system_monitor: Optional[SystemMonitor] = None
        self.docker_manager: Optional[DockerManager] = None
        self.alert_manager: Optional[AlertManager] = None
        self.health_monitor: Optional[HealthMonitor] = None
        
        # Handlers
        self.basic_handlers: Optional[BasicHandlers] = None
        self.system_handlers: Optional[SystemHandlers] = None
        self.docker_handlers: Optional[DockerHandlers] = None

    async def initialize(self) -> None:
        """Initialize all services and bot application."""
        logger.info("Initializing bot application...")

        # Initialize services
        self.system_monitor = SystemMonitor(
            proc_path=settings.host_proc_path,
            sys_path=settings.host_sys_path,
        )

        self.docker_manager = DockerManager(docker_host=settings.docker_host)

        self.alert_manager = AlertManager(
            cpu_threshold=settings.cpu_alert_threshold,
            memory_threshold=settings.memory_alert_threshold,
            disk_threshold=settings.disk_alert_threshold,
            cooldown_seconds=settings.alert_cooldown,
        )

        # Initialize bot application
        self.app = Application.builder().token(settings.telegram_bot_token).build()

        # Initialize handlers
        self.basic_handlers = BasicHandlers(self.alert_manager)
        self.system_handlers = SystemHandlers(self.system_monitor)
        self.docker_handlers = DockerHandlers(self.docker_manager)

        # Register command handlers
        self._register_handlers()

        # Initialize health monitor
        self.health_monitor = HealthMonitor(
            system_monitor=self.system_monitor,
            alert_manager=self.alert_manager,
            bot_app=self.app,
        )

        logger.info("Bot application initialized successfully")

    def _register_handlers(self) -> None:
        """Register all command handlers."""
        if not self.app:
            return

        # Basic commands
        self.app.add_handler(CommandHandler("start", self.basic_handlers.start_command))
        self.app.add_handler(CommandHandler("help", self.basic_handlers.help_command))
        self.app.add_handler(CommandHandler("alerts", self.basic_handlers.alerts_command))

        # System monitoring commands
        self.app.add_handler(CommandHandler("status", self.system_handlers.status_command))
        self.app.add_handler(CommandHandler("cpu", self.system_handlers.cpu_command))
        self.app.add_handler(CommandHandler("memory", self.system_handlers.memory_command))
        self.app.add_handler(CommandHandler("disk", self.system_handlers.disk_command))
        self.app.add_handler(CommandHandler("top", self.system_handlers.top_command))
        self.app.add_handler(CommandHandler("network", self.system_handlers.network_command))

        # Docker commands
        self.app.add_handler(CommandHandler("docker", self.docker_handlers.docker_command))
        self.app.add_handler(CommandHandler("docker_stats", self.docker_handlers.docker_stats_command))
        self.app.add_handler(CommandHandler("docker_logs", self.docker_handlers.docker_logs_command))
        self.app.add_handler(CommandHandler("docker_restart", self.docker_handlers.docker_restart_command))
        self.app.add_handler(CommandHandler("docker_stop", self.docker_handlers.docker_stop_command))
        self.app.add_handler(CommandHandler("docker_start", self.docker_handlers.docker_start_command))

        logger.info("All command handlers registered")

    async def start(self) -> None:
        """Start the bot application."""
        if not self.app:
            raise RuntimeError("Application not initialized")

        logger.info("Starting bot application...")

        # Start health monitor
        if self.health_monitor:
            self.health_monitor.start()

        # Start bot
        await self.app.initialize()
        await self.app.start()
        await self.app.updater.start_polling(drop_pending_updates=True)

        logger.info("Bot is running! Press Ctrl+C to stop.")

    async def stop(self) -> None:
        """Stop the bot application gracefully."""
        logger.info("Stopping bot application...")

        # Stop health monitor
        if self.health_monitor:
            self.health_monitor.stop()

        # Stop bot
        if self.app:
            await self.app.updater.stop()
            await self.app.stop()
            await self.app.shutdown()

        # Close Docker client
        if self.docker_manager:
            self.docker_manager.close()

        logger.info("Bot application stopped")

    async def run(self) -> None:
        """Run the bot application."""
        await self.initialize()
        await self.start()

        # Wait for termination signal
        stop_event = asyncio.Event()

        def signal_handler(sig: int, frame: any) -> None:
            """Handle termination signals."""
            logger.info(f"Received signal {sig}, shutting down...")
            stop_event.set()

        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Wait for stop event
        await stop_event.wait()

        # Cleanup
        await self.stop()


async def main() -> None:
    """Main entry point."""
    # Setup logging
    setup_logging()

    # Ensure required directories exist
    settings.ensure_directories()

    logger.info("=" * 60)
    logger.info("Linux Server Admin Bot starting...")
    logger.info(f"Allowed users: {settings.allowed_user_ids}")
    logger.info("=" * 60)

    # Create and run bot application
    bot_app = BotApplication()

    try:
        await bot_app.run()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Bot application terminated")


if __name__ == "__main__":
    asyncio.run(main())
