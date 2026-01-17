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
            InlineKeyboardButton(f"{EMOJI['temp']} Temperature", callback_data="cmd_temp"),
        ],
        [
            InlineKeyboardButton(f"{EMOJI['clock']} Uptime", callback_data="cmd_uptime"),
            InlineKeyboardButton(f"{EMOJI['services']} Services", callback_data="cmd_services"),
        ],
        [
            InlineKeyboardButton(f"{EMOJI['alert']} Alerts", callback_data="cmd_alerts"),
            InlineKeyboardButton(f"{EMOJI['help']} Help", callback_data="cmd_help"),
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
