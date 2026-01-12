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
            InlineKeyboardButton(
                f"{EMOJI['docker']} Docker Menu",
                callback_data="menu_docker"
            )
        ],
        [
            InlineKeyboardButton(f"{EMOJI['alert']} Alerts", callback_data="cmd_alerts"),
            InlineKeyboardButton(f"{EMOJI['help']} Help", callback_data="cmd_help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_docker_menu_keyboard() -> InlineKeyboardMarkup:
    """Get the Docker submenu inline keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(
                f"{EMOJI['docker']} Containers",
                callback_data="cmd_docker"
            ),
            InlineKeyboardButton(
                f"{EMOJI['chart']} Stats",
                callback_data="cmd_docker_stats"
            ),
        ],
        [
            InlineKeyboardButton("📋 Logs", callback_data="docker_logs_menu"),
            InlineKeyboardButton("🔄 Restart", callback_data="docker_restart_menu"),
        ],
        [
            InlineKeyboardButton("▶️ Start", callback_data="docker_start_menu"),
            InlineKeyboardButton("⏹️ Stop", callback_data="docker_stop_menu"),
        ],
        [
            InlineKeyboardButton(
                f"{EMOJI['back']} Back to Menu",
                callback_data="menu_main"
            )
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_container_action_keyboard(containers: list, action: str) -> InlineKeyboardMarkup:
    """
    Get keyboard with container buttons for a specific action.
    
    Args:
        containers: List of container info objects
        action: Action type (logs, restart, start, stop)
    """
    keyboard = []
    
    for container in containers[:10]:  # Limit to 10 containers
        status_emoji = "🟢" if container.status == "running" else "🔴"
        keyboard.append([
            InlineKeyboardButton(
                f"{status_emoji} {container.name[:20]}",
                callback_data=f"docker_{action}_{container.container_id}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(
            f"{EMOJI['back']} Back to Docker",
            callback_data="menu_docker"
        )
    ])
    
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


def get_back_to_docker_keyboard() -> InlineKeyboardMarkup:
    """Get a simple back to Docker menu keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(
                f"{EMOJI['back']} Back to Docker",
                callback_data="menu_docker"
            ),
            InlineKeyboardButton(
                f"{EMOJI['home']} Main Menu",
                callback_data="menu_main"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_confirmation_keyboard(action: str, container_id: str) -> InlineKeyboardMarkup:
    """Get confirmation keyboard for dangerous actions."""
    keyboard = [
        [
            InlineKeyboardButton(
                "✅ Confirm",
                callback_data=f"confirm_{action}_{container_id}"
            ),
            InlineKeyboardButton(
                "❌ Cancel",
                callback_data="menu_docker"
            )
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
