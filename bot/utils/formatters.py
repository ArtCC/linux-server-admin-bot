"""
Text formatting utilities for Telegram messages.
"""
from datetime import datetime
from typing import List, Optional

from bot.models import (
    CPUMetrics,
    DiskMetrics,
    MemoryMetrics,
    ProcessInfo,
    SystemStatus,
)
from config.constants import EMOJI


def escape_markdown(text: str) -> str:
    """
    Escape special characters for Telegram MarkdownV2.

    Args:
        text: Text to escape

    Returns:
        Escaped text
    """
    special_chars = ["_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]
    for char in special_chars:
        text = text.replace(char, f"\\{char}")
    return text


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes to human-readable string.

    Args:
        bytes_value: Number of bytes

    Returns:
        Formatted string (e.g., "1.5 GB")
    """
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "2d 5h 30m")
    """
    days = int(seconds // 86400)
    hours = int((seconds % 86400) // 3600)
    minutes = int((seconds % 3600) // 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0 or not parts:
        parts.append(f"{minutes}m")
    
    return " ".join(parts)


def format_system_status(status: SystemStatus) -> str:
    """
    Format system status for Telegram message.

    Args:
        status: System status

    Returns:
        Formatted message in MarkdownV2
    """
    cpu_emoji = EMOJI["fire"] if status.cpu.percent > 80 else EMOJI["success"]
    mem_emoji = EMOJI["fire"] if status.memory.percent > 80 else EMOJI["success"]
    disk_emoji = EMOJI["fire"] if status.disk.percent > 80 else EMOJI["success"]
    
    message = (
        f"*{EMOJI['info']} System Status*\n\n"
        f"{EMOJI['cpu']} *CPU Usage:* {cpu_emoji} {escape_markdown(f'{status.cpu.percent:.1f}%')}\n"
        f"└ Cores: {escape_markdown(str(status.cpu.count))}\n\n"
        f"{EMOJI['memory']} *Memory:* {mem_emoji} {escape_markdown(f'{status.memory.percent:.1f}%')}\n"
        f"└ {escape_markdown(f'{status.memory.used_gb:.1f}GB')} / {escape_markdown(f'{status.memory.total_gb:.1f}GB')}\n\n"
        f"{EMOJI['disk']} *Disk:* {disk_emoji} {escape_markdown(f'{status.disk.percent:.1f}%')}\n"
        f"└ {escape_markdown(f'{status.disk.used_gb:.1f}GB')} / {escape_markdown(f'{status.disk.total_gb:.1f}GB')}\n\n"
        f"{EMOJI['clock']} *Uptime:* {escape_markdown(status.uptime_formatted)}\n"
    )
    
    return message


def format_cpu_metrics(metrics: CPUMetrics) -> str:
    """
    Format CPU metrics for Telegram message.

    Args:
        metrics: CPU metrics

    Returns:
        Formatted message in MarkdownV2
    """
    status_emoji = EMOJI["fire"] if metrics.percent > 80 else EMOJI["warning"] if metrics.percent > 60 else EMOJI["success"]
    
    message = (
        f"*{EMOJI['cpu']} CPU Information*\n\n"
        f"*Overall Usage:* {status_emoji} {escape_markdown(f'{metrics.percent:.1f}%')}\n"
        f"*CPU Cores:* {escape_markdown(str(metrics.count))}\n"
    )
    
    if metrics.frequency_current:
        message += f"*Frequency:* {escape_markdown(f'{metrics.frequency_current:.0f} MHz')}\n"
    
    if metrics.load_avg:
        load_str = f"{metrics.load_avg[0]:.2f}, {metrics.load_avg[1]:.2f}, {metrics.load_avg[2]:.2f}"
        message += f"*Load Average:* {escape_markdown(load_str)}\n"
    
    message += "\n*Per\\-CPU Usage:*\n"
    for i, usage in enumerate(metrics.per_cpu):
        bar = _create_progress_bar(usage, 100, length=10)
        message += f"CPU{i}: {escape_markdown(bar)} {escape_markdown(f'{usage:.1f}%')}\n"
    
    return message


def format_memory_metrics(metrics: MemoryMetrics) -> str:
    """
    Format memory metrics for Telegram message.

    Args:
        metrics: Memory metrics

    Returns:
        Formatted message in MarkdownV2
    """
    status_emoji = EMOJI["fire"] if metrics.percent > 80 else EMOJI["warning"] if metrics.percent > 60 else EMOJI["success"]
    bar = _create_progress_bar(metrics.percent, 100, length=15)
    
    message = (
        f"*{EMOJI['memory']} Memory Information*\n\n"
        f"*Usage:* {status_emoji} {escape_markdown(f'{metrics.percent:.1f}%')}\n"
        f"{escape_markdown(bar)}\n\n"
        f"*Total:* {escape_markdown(f'{metrics.total_gb:.2f} GB')}\n"
        f"*Used:* {escape_markdown(f'{metrics.used_gb:.2f} GB')}\n"
        f"*Available:* {escape_markdown(f'{metrics.available_gb:.2f} GB')}\n"
    )
    
    if metrics.swap_total > 0:
        message += (
            f"\n*Swap Usage:* {escape_markdown(f'{metrics.swap_percent:.1f}%')}\n"
            f"└ {escape_markdown(f'{metrics.swap_used / (1024**3):.2f} GB')} / "
            f"{escape_markdown(f'{metrics.swap_total / (1024**3):.2f} GB')}\n"
        )
    
    return message


def format_disk_metrics(metrics: DiskMetrics) -> str:
    """
    Format disk metrics for Telegram message.

    Args:
        metrics: Disk metrics

    Returns:
        Formatted message in MarkdownV2
    """
    status_emoji = EMOJI["fire"] if metrics.percent > 90 else EMOJI["warning"] if metrics.percent > 75 else EMOJI["success"]
    bar = _create_progress_bar(metrics.percent, 100, length=15)
    
    message = (
        f"*{EMOJI['disk']} Disk Information*\n\n"
        f"*Mount Point:* {escape_markdown(metrics.mount_point)}\n"
        f"*Usage:* {status_emoji} {escape_markdown(f'{metrics.percent:.1f}%')}\n"
        f"{escape_markdown(bar)}\n\n"
        f"*Total:* {escape_markdown(f'{metrics.total_gb:.2f} GB')}\n"
        f"*Used:* {escape_markdown(f'{metrics.used_gb:.2f} GB')}\n"
        f"*Free:* {escape_markdown(f'{metrics.free_gb:.2f} GB')}\n"
    )
    
    return message


def format_top_processes(processes: List[ProcessInfo]) -> str:
    """
    Format top processes for Telegram message.

    Args:
        processes: List of process information

    Returns:
        Formatted message in MarkdownV2
    """
    message = f"*{EMOJI['cpu']} Top Processes by CPU*\n\n"
    
    for i, proc in enumerate(processes, 1):
        message += (
            f"{i}\\. *{escape_markdown(proc.name[:30])}*\n"
            f"   CPU: {escape_markdown(f'{proc.cpu_percent:.1f}%')} \\| "
            f"MEM: {escape_markdown(f'{proc.memory_mb:.0f}MB')} \\| "
            f"PID: {escape_markdown(str(proc.pid))}\n"
        )
    
    return message


def _create_progress_bar(value: float, max_value: float, length: int = 10) -> str:
    """
    Create a text-based progress bar.

    Args:
        value: Current value
        max_value: Maximum value
        length: Bar length in characters

    Returns:
        Progress bar string
    """
    filled = int((value / max_value) * length)
    bar = "█" * filled + "░" * (length - filled)
    return bar
