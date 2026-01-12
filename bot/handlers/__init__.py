"""Bot handlers package."""
from bot.handlers.basic import BasicHandlers
from bot.handlers.callbacks import CallbackHandlers
from bot.handlers.system import SystemHandlers

__all__ = ["BasicHandlers", "CallbackHandlers", "SystemHandlers"]
