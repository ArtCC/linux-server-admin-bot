"""
Chart generation utilities using matplotlib.
"""
import io
from typing import Dict, List, Optional, Tuple

import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns

from config import get_logger, settings
from config.constants import CHART_COLORS, ChartType

# Use non-interactive backend
matplotlib.use("Agg")

logger = get_logger(__name__)

# Set style
sns.set_style("whitegrid")
plt.rcParams["figure.facecolor"] = "white"


class ChartGenerator:
    """Generate charts for system metrics."""

    def __init__(self, dpi: int = 100, figsize: Tuple[int, int] = (10, 6)) -> None:
        """
        Initialize chart generator.

        Args:
            dpi: Chart resolution
            figsize: Figure size as (width, height)
        """
        self.dpi = dpi
        self.figsize = figsize

    def generate_cpu_chart(
        self, 
        cpu_percent: float, 
        per_cpu: List[float],
        title: str = "CPU Usage"
    ) -> io.BytesIO:
        """
        Generate CPU usage chart.

        Args:
            cpu_percent: Overall CPU percentage
            per_cpu: Per-CPU percentages
            title: Chart title

        Returns:
            BytesIO buffer containing PNG image
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize, dpi=self.dpi)
        
        # Overall CPU gauge
        self._draw_gauge(ax1, cpu_percent, "Overall CPU", CHART_COLORS["cpu"])
        
        # Per-CPU bar chart
        cpu_labels = [f"CPU{i}" for i in range(len(per_cpu))]
        colors = [CHART_COLORS["danger"] if p > 80 else CHART_COLORS["warning"] if p > 60 else CHART_COLORS["success"] for p in per_cpu]
        ax2.barh(cpu_labels, per_cpu, color=colors)
        ax2.set_xlabel("Usage (%)")
        ax2.set_title("Per-CPU Usage")
        ax2.set_xlim(0, 100)
        
        plt.tight_layout()
        return self._fig_to_bytes(fig)

    def generate_memory_chart(
        self,
        total_gb: float,
        used_gb: float,
        available_gb: float,
        percent: float,
    ) -> io.BytesIO:
        """
        Generate memory usage chart.

        Args:
            total_gb: Total memory in GB
            used_gb: Used memory in GB
            available_gb: Available memory in GB
            percent: Usage percentage

        Returns:
            BytesIO buffer containing PNG image
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize, dpi=self.dpi)
        
        # Memory gauge
        self._draw_gauge(ax1, percent, "Memory Usage", CHART_COLORS["memory"])
        
        # Memory breakdown pie chart
        sizes = [used_gb, available_gb]
        labels = [f"Used\n{used_gb:.1f}GB", f"Available\n{available_gb:.1f}GB"]
        colors = [CHART_COLORS["memory"], CHART_COLORS["success"]]
        ax2.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
        ax2.set_title(f"Total: {total_gb:.1f}GB")
        
        plt.tight_layout()
        return self._fig_to_bytes(fig)

    def generate_disk_chart(
        self,
        total_gb: float,
        used_gb: float,
        free_gb: float,
        percent: float,
    ) -> io.BytesIO:
        """
        Generate disk usage chart.

        Args:
            total_gb: Total disk space in GB
            used_gb: Used disk space in GB
            free_gb: Free disk space in GB
            percent: Usage percentage

        Returns:
            BytesIO buffer containing PNG image
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.figsize, dpi=self.dpi)
        
        # Disk gauge
        self._draw_gauge(ax1, percent, "Disk Usage", CHART_COLORS["disk"])
        
        # Disk breakdown bar chart
        categories = ["Used", "Free"]
        values = [used_gb, free_gb]
        colors = [CHART_COLORS["disk"], CHART_COLORS["success"]]
        ax2.bar(categories, values, color=colors)
        ax2.set_ylabel("Space (GB)")
        ax2.set_title(f"Total: {total_gb:.1f}GB")
        
        # Add value labels on bars
        for i, v in enumerate(values):
            ax2.text(i, v, f"{v:.1f}GB", ha="center", va="bottom")
        
        plt.tight_layout()
        return self._fig_to_bytes(fig)

    def generate_process_chart(
        self,
        processes: List[Dict[str, any]],
        top_n: int = 10,
    ) -> io.BytesIO:
        """
        Generate top processes chart.

        Args:
            processes: List of process dicts with 'name' and 'cpu_percent'
            top_n: Number of top processes to show

        Returns:
            BytesIO buffer containing PNG image
        """
        processes = processes[:top_n]
        
        fig, ax = plt.subplots(figsize=self.figsize, dpi=self.dpi)
        
        names = [p["name"][:20] for p in processes]  # Truncate long names
        cpu_values = [p["cpu_percent"] for p in processes]
        
        colors = [CHART_COLORS["danger"] if v > 50 else CHART_COLORS["warning"] if v > 25 else CHART_COLORS["cpu"] for v in cpu_values]
        
        ax.barh(names, cpu_values, color=colors)
        ax.set_xlabel("CPU Usage (%)")
        ax.set_title(f"Top {len(processes)} Processes by CPU")
        ax.invert_yaxis()
        
        plt.tight_layout()
        return self._fig_to_bytes(fig)

    def _draw_gauge(
        self,
        ax: plt.Axes,
        value: float,
        title: str,
        color: str,
    ) -> None:
        """
        Draw a gauge chart.

        Args:
            ax: Matplotlib axes
            value: Value to display (0-100)
            title: Gauge title
            color: Gauge color
        """
        # Determine color based on value
        if value > 90:
            gauge_color = CHART_COLORS["danger"]
        elif value > 75:
            gauge_color = CHART_COLORS["warning"]
        else:
            gauge_color = CHART_COLORS["success"]
        
        # Draw pie chart as gauge
        sizes = [value, 100 - value]
        colors = [gauge_color, "#e0e0e0"]
        ax.pie(
            sizes,
            colors=colors,
            startangle=90,
            counterclock=False,
            wedgeprops=dict(width=0.3),
        )
        
        # Add text in center
        ax.text(0, 0, f"{value:.1f}%", ha="center", va="center", fontsize=24, fontweight="bold")
        ax.set_title(title)

    def _fig_to_bytes(self, fig: plt.Figure) -> io.BytesIO:
        """
        Convert matplotlib figure to BytesIO.

        Args:
            fig: Matplotlib figure

        Returns:
            BytesIO buffer containing PNG image
        """
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=self.dpi, bbox_inches="tight")
        buf.seek(0)
        plt.close(fig)
        return buf

    def _create_empty_chart(self, message: str) -> io.BytesIO:
        """
        Create an empty chart with a message.

        Args:
            message: Message to display

        Returns:
            BytesIO buffer containing PNG image
        """
        fig, ax = plt.subplots(figsize=(8, 6), dpi=self.dpi)
        ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=16)
        ax.axis("off")
        return self._fig_to_bytes(fig)


# Global instance
chart_generator = ChartGenerator(dpi=settings.chart_dpi, figsize=settings.chart_figsize)
