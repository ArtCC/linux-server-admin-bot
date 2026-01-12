"""
Inline keyboard layouts for the bot.
"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import EMOJI


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get the main menu inline keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(
                f"{EMOJI['chart']} System Status",
                callback_data="cmd_status"
            )
        ],
        [
            InlineKeyboardButton(f"{EMOJI['cpu']} CPU", callback_data="cmd_cpu"),
            InlineKeyboardButton(f"{EMOJI['memory']} Memory", callback_data="cmd_memory"),
        ],
        [
            InlineKeyboardButton(f"{EMOJI['disk']} Disk", callback_data="cmd_disk"),
            InlineKeyboardButton(f"{EMOJI['network']} Network", callback_data="cmd_network"),
        ],
        [
            InlineKeyboardButton(f"{EMOJI['process']} Processes", callback_data="cmd_top"),
        ],
        [
            InlineKeyboardButton(f"{EMOJI['alert']} Alerts", callback_data="cmd_alerts"),
            InlineKeyboardButton(f"{EMOJI['help']} Help", callback_data="cmd_help"),
        ],
        [
            InlineKeyboardButton(f"{EMOJI['power']} Power Control", callback_data="menu_power"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_to_main_keyboard() -> InlineKeyboardMarkup:
    """Get a simple back to main menu keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(
                f"{EMOJI['back']} Back to Menu",
                callback_data="menu_main"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_power_menu_keyboard() -> InlineKeyboardMarkup:
    """Get the power control menu keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(
                f"{EMOJI['reboot']} Reboot Server",
                callback_data="cmd_reboot"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{EMOJI['shutdown']} Shutdown Server",
                callback_data="cmd_shutdown"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{EMOJI['back']} Back to Menu",
                callback_data="menu_main"
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_confirm_reboot_keyboard() -> InlineKeyboardMarkup:
    """Get confirmation keyboard for reboot."""
    keyboard = [
        [
            InlineKeyboardButton(
                f"{EMOJI['danger']} YES, REBOOT NOW",
                callback_data="confirm_reboot"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{EMOJI['cross']} Cancel",
                callback_data="menu_power"
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_confirm_shutdown_keyboard() -> InlineKeyboardMarkup:
    """Get confirmation keyboard for shutdown."""
    keyboard = [
        [
            InlineKeyboardButton(
                f"{EMOJI['danger']} YES, SHUTDOWN NOW",
                callback_data="confirm_shutdown"
            ),
        ],
        [
            InlineKeyboardButton(
                f"{EMOJI['cross']} Cancel",
                callback_data="menu_power"
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)
