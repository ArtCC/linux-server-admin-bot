"""
Configuration settings using Pydantic for validation and type safety.
"""
from pathlib import Path
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Telegram Configuration
    telegram_bot_token: str = Field(..., description="Telegram Bot API Token")
    telegram_allowed_user_ids: str = Field(
        ..., description="Comma-separated list of allowed user IDs"
    )

    # Alert Thresholds
    cpu_alert_threshold: int = Field(
        default=80, ge=1, le=100, description="CPU usage alert threshold (%)"
    )
    memory_alert_threshold: int = Field(
        default=80, ge=1, le=100, description="Memory usage alert threshold (%)"
    )
    disk_alert_threshold: int = Field(
        default=90, ge=1, le=100, description="Disk usage alert threshold (%)"
    )

    # Alert Settings
    alert_check_interval: int = Field(
        default=300, ge=60, description="Alert check interval in seconds"
    )
    alert_cooldown: int = Field(
        default=600, ge=60, description="Alert cooldown period in seconds"
    )

    # Rate Limiting
    rate_limit_calls: int = Field(default=10, ge=1, description="Max calls per period")
    rate_limit_period: int = Field(default=60, ge=1, description="Rate limit period in seconds")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="logs/bot.log", description="Log file path")

    # Docker Settings
    docker_host: str = Field(
        default="unix:///var/run/docker.sock", description="Docker host socket"
    )

    # System Monitoring Paths
    host_proc_path: str = Field(default="/host/proc", description="Host /proc mount path")
    host_sys_path: str = Field(default="/host/sys", description="Host /sys mount path")
    host_logs_path: str = Field(default="/host/logs", description="Host /var/log mount path")

    # Charts Configuration
    chart_dpi: int = Field(default=100, ge=50, le=300, description="Chart DPI")
    chart_figsize_width: int = Field(default=10, ge=5, le=20, description="Chart width")
    chart_figsize_height: int = Field(default=6, ge=4, le=15, description="Chart height")

    @field_validator("telegram_allowed_user_ids")
    @classmethod
    def validate_user_ids(cls, v: str) -> str:
        """Validate that user IDs are comma-separated integers."""
        try:
            user_ids = [int(uid.strip()) for uid in v.split(",")]
            if not user_ids:
                raise ValueError("At least one user ID must be provided")
            return v
        except ValueError as e:
            raise ValueError(f"Invalid user IDs format: {e}") from e

    @property
    def allowed_user_ids(self) -> List[int]:
        """Get list of allowed user IDs as integers."""
        return [int(uid.strip()) for uid in self.telegram_allowed_user_ids.split(",")]

    @property
    def chart_figsize(self) -> tuple[int, int]:
        """Get chart figure size as tuple."""
        return (self.chart_figsize_width, self.chart_figsize_height)

    def ensure_directories(self) -> None:
        """Ensure required directories exist."""
        log_dir = Path(self.log_file).parent
        log_dir.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
