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
    cpu_indicator = _get_status_indicator(status.cpu.percent)
    mem_indicator = _get_status_indicator(status.memory.percent)
    disk_indicator = _get_status_indicator(status.disk.percent, 75, 90)
    
    cpu_bar = _create_progress_bar(status.cpu.percent, 100, 10)
    mem_bar = _create_progress_bar(status.memory.percent, 100, 10)
    disk_bar = _create_progress_bar(status.disk.percent, 100, 10)
    
    header = _format_header(f"{EMOJI['chart']} *SYSTEM STATUS*")
    
    message = (
        f"{escape_markdown(header)}\n\n"
        f"{EMOJI['cpu']} *CPU*\n"
        f"{escape_markdown(cpu_bar)} {escape_markdown(f'{status.cpu.percent:.1f}%')} {cpu_indicator}\n"
        f"└ Cores: {escape_markdown(str(status.cpu.count))}\n\n"
        f"{EMOJI['memory']} *Memory*\n"
        f"{escape_markdown(mem_bar)} {escape_markdown(f'{status.memory.percent:.1f}%')} {mem_indicator}\n"
        f"└ {escape_markdown(f'{status.memory.used_gb:.1f}GB')} / {escape_markdown(f'{status.memory.total_gb:.1f}GB')}\n\n"
        f"{EMOJI['disk']} *Disk*\n"
        f"{escape_markdown(disk_bar)} {escape_markdown(f'{status.disk.percent:.1f}%')} {disk_indicator}\n"
        f"└ {escape_markdown(f'{status.disk.used_gb:.1f}GB')} / {escape_markdown(f'{status.disk.total_gb:.1f}GB')}\n\n"
        f"{escape_markdown(_format_section_divider())}\n"
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
    status_indicator = _get_status_indicator(metrics.percent)
    overall_bar = _create_progress_bar(metrics.percent, 100, 12)
    
    header = _format_header(f"{EMOJI['cpu']} *CPU INFORMATION*")
    
    message = f"{escape_markdown(header)}\n\n"
    message += f"*Overall Usage*\n"
    message += f"{escape_markdown(overall_bar)} {escape_markdown(f'{metrics.percent:.1f}%')} {status_indicator}\n\n"
    message += f"*Cores:* {escape_markdown(str(metrics.count))}\n"
    
    if metrics.frequency_current:
        message += f"*Frequency:* {escape_markdown(f'{metrics.frequency_current:.0f} MHz')}\n"
    
    if metrics.load_avg:
        load_str = f"{metrics.load_avg[0]:.2f}, {metrics.load_avg[1]:.2f}, {metrics.load_avg[2]:.2f}"
        message += f"*Load Average:* {escape_markdown(load_str)}\n"
    
    message += f"\n{escape_markdown(_format_section_divider())}\n"
    message += "*Per\\-Core Usage*\n\n"
    
    for i, usage in enumerate(metrics.per_cpu):
        bar = _create_progress_bar(usage, 100, length=8)
        indicator = _get_status_indicator(usage)
        message += f"CPU{i}: {escape_markdown(bar)} {escape_markdown(f'{usage:.1f}%')} {indicator}\n"
    
    return message


def format_memory_metrics(metrics: MemoryMetrics) -> str:
    """
    Format memory metrics for Telegram message.

    Args:
        metrics: Memory metrics

    Returns:
        Formatted message in MarkdownV2
    """
    status_indicator = _get_status_indicator(metrics.percent)
    bar = _create_progress_bar(metrics.percent, 100, length=12)
    
    header = _format_header(f"{EMOJI['memory']} *MEMORY INFORMATION*")
    
    message = f"{escape_markdown(header)}\n\n"
    message += f"*Usage*\n"
    message += f"{escape_markdown(bar)} {escape_markdown(f'{metrics.percent:.1f}%')} {status_indicator}\n\n"
    message += f"*Total:* {escape_markdown(f'{metrics.total_gb:.2f} GB')}\n"
    message += f"*Used:* {escape_markdown(f'{metrics.used_gb:.2f} GB')}\n"
    message += f"*Available:* {escape_markdown(f'{metrics.available_gb:.2f} GB')}\n"
    
    if metrics.swap_total > 0:
        swap_indicator = _get_status_indicator(metrics.swap_percent)
        swap_bar = _create_progress_bar(metrics.swap_percent, 100, length=12)
        message += f"\n{escape_markdown(_format_section_divider())}\n"
        message += f"*Swap*\n"
        message += f"{escape_markdown(swap_bar)} {escape_markdown(f'{metrics.swap_percent:.1f}%')} {swap_indicator}\n"
        message += f"└ {escape_markdown(f'{metrics.swap_used / (1024**3):.2f} GB')} / {escape_markdown(f'{metrics.swap_total / (1024**3):.2f} GB')}\n"
    
    return message


def format_disk_metrics(metrics: DiskMetrics) -> str:
    """
    Format disk metrics for Telegram message.

    Args:
        metrics: Disk metrics

    Returns:
        Formatted message in MarkdownV2
    """
    status_indicator = _get_status_indicator(metrics.percent, 75, 90)
    bar = _create_progress_bar(metrics.percent, 100, length=12)
    
    header = _format_header(f"{EMOJI['disk']} *DISK INFORMATION*")
    
    message = f"{escape_markdown(header)}\n\n"
    message += f"*Mount Point:* {escape_markdown(metrics.mount_point)}\n\n"
    message += f"*Usage*\n"
    message += f"{escape_markdown(bar)} {escape_markdown(f'{metrics.percent:.1f}%')} {status_indicator}\n\n"
    message += f"*Total:* {escape_markdown(f'{metrics.total_gb:.2f} GB')}\n"
    message += f"*Used:* {escape_markdown(f'{metrics.used_gb:.2f} GB')}\n"
    message += f"*Free:* {escape_markdown(f'{metrics.free_gb:.2f} GB')}\n"
    
    return message


def format_top_processes(processes: List[ProcessInfo]) -> str:
    """
    Format top processes for Telegram message.

    Args:
        processes: List of process information

    Returns:
        Formatted message in MarkdownV2
    """
    header = _format_header(f"{EMOJI['process']} *TOP PROCESSES*")
    
    message = f"{escape_markdown(header)}\n\n"
    
    for i, proc in enumerate(processes, 1):
        cpu_indicator = _get_status_indicator(proc.cpu_percent)
        message += (
            f"*{i}\\. {escape_markdown(proc.name[:25])}*\n"
            f"   {cpu_indicator} CPU: {escape_markdown(f'{proc.cpu_percent:.1f}%')} │ "
            f"MEM: {escape_markdown(f'{proc.memory_mb:.0f}MB')} │ "
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
    return f"[{bar}]"


def _get_status_indicator(percent: float, warning_threshold: int = 60, critical_threshold: int = 80) -> str:
    """
    Get a colored status indicator based on percentage.

    Args:
        percent: Current percentage value
        warning_threshold: Threshold for warning (yellow)
        critical_threshold: Threshold for critical (red)

    Returns:
        Status emoji (🟢, 🟡, or 🔴)
    """
    if percent >= critical_threshold:
        return "🔴"
    elif percent >= warning_threshold:
        return "🟡"
    else:
        return "🟢"


def _format_header(title: str) -> str:
    """
    Format a header with decorative lines.

    Args:
        title: Header title text

    Returns:
        Formatted header string
    """
    return f"━━━━━━━━━━━━━━━━━━━━━━\n{title}\n━━━━━━━━━━━━━━━━━━━━━━"


def _format_section_divider() -> str:
    """Get a section divider line."""
    return "────────────────────"
