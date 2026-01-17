"""
System monitoring service using psutil.
"""
import os
from datetime import datetime
from typing import List, Optional

import psutil

from bot.models import CPUMetrics, DiskMetrics, MemoryMetrics, NetworkMetrics, ProcessInfo, SystemStatus
from config import get_logger

logger = get_logger(__name__)


class SystemMonitor:
    """Service for monitoring system resources."""

    def __init__(self, proc_path: str = "/proc", sys_path: str = "/sys") -> None:
        """
        Initialize system monitor.

        Args:
            proc_path: Path to /proc directory
            sys_path: Path to /sys directory
        """
        # Use host paths if available (set via PSUTIL env vars in main.py)
        self.proc_path = os.environ.get("PSUTIL_PROCFS_PATH", proc_path)
        self.sys_path = os.environ.get("PSUTIL_SYSFS_PATH", sys_path)
        logger.info(f"SystemMonitor initialized (proc={self.proc_path}, sys={self.sys_path})")

    def get_cpu_metrics(self, interval: float = 1.0) -> CPUMetrics:
        """
        Get CPU usage metrics.

        Args:
            interval: Measurement interval in seconds

        Returns:
            CPU metrics
        """
        try:
            cpu_percent = psutil.cpu_percent(interval=interval)
            cpu_count = psutil.cpu_count()
            per_cpu = psutil.cpu_percent(interval=0.1, percpu=True)
            
            # CPU frequency (may not be available in all systems)
            try:
                freq = psutil.cpu_freq()
                freq_current = freq.current if freq else None
                freq_min = freq.min if freq else None
                freq_max = freq.max if freq else None
            except Exception:
                freq_current = freq_min = freq_max = None

            # Load average
            load_avg = psutil.getloadavg() if hasattr(psutil, "getloadavg") else None

            return CPUMetrics(
                percent=cpu_percent,
                count=cpu_count,
                per_cpu=per_cpu,
                frequency_current=freq_current,
                frequency_min=freq_min,
                frequency_max=freq_max,
                load_avg=load_avg,
            )
        except Exception as e:
            logger.error(f"Error getting CPU metrics: {e}")
            raise

    def get_memory_metrics(self) -> MemoryMetrics:
        """
        Get memory usage metrics.

        Returns:
            Memory metrics
        """
        try:
            mem = psutil.virtual_memory()
            swap = psutil.swap_memory()

            return MemoryMetrics(
                total=mem.total,
                available=mem.available,
                used=mem.used,
                percent=mem.percent,
                swap_total=swap.total,
                swap_used=swap.used,
                swap_percent=swap.percent,
            )
        except Exception as e:
            logger.error(f"Error getting memory metrics: {e}")
            raise

    def get_disk_metrics(self, mount_point: str = "/") -> DiskMetrics:
        """
        Get disk usage metrics.

        Args:
            mount_point: Disk mount point to check

        Returns:
            Disk metrics
        """
        try:
            disk = psutil.disk_usage(mount_point)

            return DiskMetrics(
                total=disk.total,
                used=disk.used,
                free=disk.free,
                percent=disk.percent,
                mount_point=mount_point,
            )
        except Exception as e:
            logger.error(f"Error getting disk metrics for {mount_point}: {e}")
            raise

    def get_network_metrics(self, interface: Optional[str] = None) -> List[NetworkMetrics]:
        """
        Get network interface metrics.

        Args:
            interface: Specific interface name, or None for all interfaces

        Returns:
            List of network metrics
        """
        try:
            net_io = psutil.net_io_counters(pernic=True)
            
            if interface and interface in net_io:
                stats = net_io[interface]
                return [
                    NetworkMetrics(
                        interface=interface,
                        bytes_sent=stats.bytes_sent,
                        bytes_recv=stats.bytes_recv,
                        packets_sent=stats.packets_sent,
                        packets_recv=stats.packets_recv,
                        errors_in=stats.errin,
                        errors_out=stats.errout,
                        drops_in=stats.dropin,
                        drops_out=stats.dropout,
                    )
                ]
            
            # Return all interfaces
            return [
                NetworkMetrics(
                    interface=iface,
                    bytes_sent=stats.bytes_sent,
                    bytes_recv=stats.bytes_recv,
                    packets_sent=stats.packets_sent,
                    packets_recv=stats.packets_recv,
                    errors_in=stats.errin,
                    errors_out=stats.errout,
                    drops_in=stats.dropin,
                    drops_out=stats.dropout,
                )
                for iface, stats in net_io.items()
            ]
        except Exception as e:
            logger.error(f"Error getting network metrics: {e}")
            raise

    def get_top_processes(self, limit: int = 10) -> List[ProcessInfo]:
        """
        Get top processes by CPU usage.

        Args:
            limit: Maximum number of processes to return

        Returns:
            List of process information
        """
        try:
            processes = []
            for proc in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent", "memory_info", "status", "username", "create_time"]):
                try:
                    info = proc.info
                    memory_mb = info["memory_info"].rss / (1024 * 1024) if info.get("memory_info") else 0
                    create_time = datetime.fromtimestamp(info["create_time"]) if info.get("create_time") else None
                    
                    processes.append(
                        ProcessInfo(
                            pid=info["pid"],
                            name=info["name"],
                            cpu_percent=info["cpu_percent"] or 0,
                            memory_percent=info["memory_percent"] or 0,
                            memory_mb=memory_mb,
                            status=info["status"],
                            username=info.get("username", ""),
                            create_time=create_time,
                        )
                    )
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Sort by CPU usage and return top N
            processes.sort(key=lambda x: x.cpu_percent, reverse=True)
            return processes[:limit]
        except Exception as e:
            logger.error(f"Error getting top processes: {e}")
            raise

    def get_system_status(self) -> SystemStatus:
        """
        Get overall system status.

        Returns:
            System status summary
        """
        try:
            cpu = self.get_cpu_metrics()
            memory = self.get_memory_metrics()
            disk = self.get_disk_metrics()
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime = (datetime.now() - boot_time).total_seconds()

            return SystemStatus(
                cpu=cpu,
                memory=memory,
                disk=disk,
                uptime_seconds=uptime,
                boot_time=boot_time,
            )
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            raise

    def get_temperature(self) -> Optional[dict]:
        """
        Get system temperature sensors (if available).

        Returns:
            Dictionary with temperature readings or None
        """
        try:
            if hasattr(psutil, "sensors_temperatures"):
                temps = psutil.sensors_temperatures()
                return temps if temps else None
            return None
        except Exception as e:
            logger.warning(f"Temperature sensors not available: {e}")
            return None

    def get_uptime_info(self) -> dict:
        """
        Get detailed uptime information.

        Returns:
            Dictionary with uptime details
        """
        try:
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            uptime_seconds = (datetime.now() - boot_time).total_seconds()
            
            # Calculate uptime components
            days = int(uptime_seconds // 86400)
            hours = int((uptime_seconds % 86400) // 3600)
            minutes = int((uptime_seconds % 3600) // 60)
            
            # Get logged in users count
            users = psutil.users()
            
            return {
                "boot_time": boot_time,
                "uptime_seconds": uptime_seconds,
                "days": days,
                "hours": hours,
                "minutes": minutes,
                "users_count": len(users),
                "users": [
                    {
                        "name": u.name,
                        "terminal": u.terminal or "N/A",
                        "host": u.host or "local",
                        "started": datetime.fromtimestamp(u.started),
                    }
                    for u in users
                ],
            }
        except Exception as e:
            logger.error(f"Error getting uptime info: {e}")
            raise

    def get_services_status(self, services: Optional[List[str]] = None) -> List[dict]:
        """
        Get status of systemd services.

        Args:
            services: List of service names to check. If None, checks common services.

        Returns:
            List of service status dictionaries
        """
        import subprocess
        
        if services is None:
            # Default list of common services to monitor
            services = [
                "docker",
                "nginx",
                "apache2",
                "mysql",
                "mariadb",
                "postgresql",
                "redis-server",
                "ssh",
                "cron",
                "fail2ban",
            ]
        
        results = []
        
        for service in services:
            try:
                # Check if service exists and get its status
                result = subprocess.run(
                    ["systemctl", "is-active", service],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                status = result.stdout.strip()
                
                # Get more details if service exists
                if status != "inactive" or result.returncode != 3:
                    # Service exists, get more info
                    detail_result = subprocess.run(
                        ["systemctl", "show", service, "--property=ActiveState,SubState,LoadState"],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    
                    props = {}
                    for line in detail_result.stdout.strip().split("\n"):
                        if "=" in line:
                            key, value = line.split("=", 1)
                            props[key] = value
                    
                    # Only add if service is loaded (exists)
                    if props.get("LoadState") == "loaded":
                        results.append({
                            "name": service,
                            "status": status,
                            "active_state": props.get("ActiveState", "unknown"),
                            "sub_state": props.get("SubState", "unknown"),
                            "is_running": status == "active",
                        })
            except subprocess.TimeoutExpired:
                logger.warning(f"Timeout checking service: {service}")
            except FileNotFoundError:
                # systemctl not available (non-systemd system)
                logger.warning("systemctl not available")
                break
            except Exception as e:
                logger.debug(f"Error checking service {service}: {e}")
        
        return results
