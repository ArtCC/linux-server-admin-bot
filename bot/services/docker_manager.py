"""
Docker management service.
"""
from datetime import datetime
from typing import Dict, List, Optional

import docker
from docker.errors import DockerException, NotFound
from docker.models.containers import Container

from bot.models import DockerContainerInfo, DockerContainerStats
from config import get_logger
from config.constants import ContainerStatus

logger = get_logger(__name__)

# Docker socket path - always use local socket
DOCKER_SOCKET = "unix:///var/run/docker.sock"


class DockerManager:
    """Service for managing Docker containers."""

    def __init__(self) -> None:
        """
        Initialize Docker manager.
        Always uses local Docker socket.
        """
        try:
            # Explicitly create client with socket URL
            self.client = docker.DockerClient(base_url=DOCKER_SOCKET)
            self.client.ping()
            logger.info(f"Docker client initialized successfully: {DOCKER_SOCKET}")
        except DockerException as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise

    def list_containers(self, all_containers: bool = True) -> List[DockerContainerInfo]:
        """
        List Docker containers.

        Args:
            all_containers: Include stopped containers

        Returns:
            List of container information
        """
        try:
            containers = self.client.containers.list(all=all_containers)
            return [self._container_to_info(container) for container in containers]
        except DockerException as e:
            logger.error(f"Error listing containers: {e}")
            raise

    def get_container(self, container_id: str) -> Optional[DockerContainerInfo]:
        """
        Get information about a specific container.

        Args:
            container_id: Container ID or name

        Returns:
            Container information or None if not found
        """
        try:
            container = self.client.containers.get(container_id)
            return self._container_to_info(container)
        except NotFound:
            logger.warning(f"Container not found: {container_id}")
            return None
        except DockerException as e:
            logger.error(f"Error getting container {container_id}: {e}")
            raise

    def get_container_stats(self, container_id: str) -> Optional[DockerContainerStats]:
        """
        Get resource usage statistics for a container.

        Args:
            container_id: Container ID or name

        Returns:
            Container statistics or None if not found
        """
        try:
            container = self.client.containers.get(container_id)
            stats = container.stats(stream=False)

            # Calculate CPU percentage
            cpu_delta = stats["cpu_stats"]["cpu_usage"]["total_usage"] - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            system_delta = stats["cpu_stats"]["system_cpu_usage"] - stats["precpu_stats"]["system_cpu_usage"]
            
            # Handle percpu_usage being None or missing
            percpu_usage = stats["cpu_stats"]["cpu_usage"].get("percpu_usage")
            num_cpus = len(percpu_usage) if percpu_usage else stats["cpu_stats"].get("online_cpus", 1)
            cpu_percent = (cpu_delta / system_delta) * num_cpus * 100.0 if system_delta > 0 else 0.0

            # Memory stats
            memory_usage = stats["memory_stats"].get("usage", 0)
            memory_limit = stats["memory_stats"].get("limit", 1)
            memory_percent = (memory_usage / memory_limit) * 100.0 if memory_limit > 0 else 0.0

            # Network stats
            networks = stats.get("networks", {})
            network_rx = sum(net.get("rx_bytes", 0) for net in networks.values()) / (1024 * 1024)
            network_tx = sum(net.get("tx_bytes", 0) for net in networks.values()) / (1024 * 1024)

            # Block I/O stats
            blkio_stats = stats.get("blkio_stats", {}).get("io_service_bytes_recursive") or []
            block_read = sum(item.get("value", 0) for item in blkio_stats if item.get("op") == "Read") / (1024 * 1024) if blkio_stats else 0
            block_write = sum(item.get("value", 0) for item in blkio_stats if item.get("op") == "Write") / (1024 * 1024) if blkio_stats else 0

            return DockerContainerStats(
                container_id=container.short_id,
                container_name=container.name,
                cpu_percent=round(cpu_percent, 2),
                memory_usage_mb=round(memory_usage / (1024 * 1024), 2),
                memory_limit_mb=round(memory_limit / (1024 * 1024), 2),
                memory_percent=round(memory_percent, 2),
                network_rx_mb=round(network_rx, 2),
                network_tx_mb=round(network_tx, 2),
                block_read_mb=round(block_read, 2),
                block_write_mb=round(block_write, 2),
            )
        except NotFound:
            logger.warning(f"Container not found: {container_id}")
            return None
        except DockerException as e:
            logger.error(f"Error getting stats for container {container_id}: {e}")
            raise

    def get_container_logs(self, container_id: str, lines: int = 50) -> str:
        """
        Get logs from a container.

        Args:
            container_id: Container ID or name
            lines: Number of log lines to retrieve

        Returns:
            Container logs as string
        """
        try:
            container = self.client.containers.get(container_id)
            logs = container.logs(tail=lines, timestamps=True).decode("utf-8", errors="replace")
            return logs
        except NotFound:
            logger.warning(f"Container not found: {container_id}")
            return f"Container {container_id} not found"
        except DockerException as e:
            logger.error(f"Error getting logs for container {container_id}: {e}")
            raise

    def restart_container(self, container_id: str, timeout: int = 10) -> bool:
        """
        Restart a container.

        Args:
            container_id: Container ID or name
            timeout: Timeout in seconds

        Returns:
            True if successful
        """
        try:
            container = self.client.containers.get(container_id)
            container.restart(timeout=timeout)
            logger.info(f"Container restarted: {container_id}")
            return True
        except NotFound:
            logger.warning(f"Container not found: {container_id}")
            return False
        except DockerException as e:
            logger.error(f"Error restarting container {container_id}: {e}")
            raise

    def stop_container(self, container_id: str, timeout: int = 10) -> bool:
        """
        Stop a container.

        Args:
            container_id: Container ID or name
            timeout: Timeout in seconds

        Returns:
            True if successful
        """
        try:
            container = self.client.containers.get(container_id)
            container.stop(timeout=timeout)
            logger.info(f"Container stopped: {container_id}")
            return True
        except NotFound:
            logger.warning(f"Container not found: {container_id}")
            return False
        except DockerException as e:
            logger.error(f"Error stopping container {container_id}: {e}")
            raise

    def start_container(self, container_id: str) -> bool:
        """
        Start a container.

        Args:
            container_id: Container ID or name

        Returns:
            True if successful
        """
        try:
            container = self.client.containers.get(container_id)
            container.start()
            logger.info(f"Container started: {container_id}")
            return True
        except NotFound:
            logger.warning(f"Container not found: {container_id}")
            return False
        except DockerException as e:
            logger.error(f"Error starting container {container_id}: {e}")
            raise

    def _container_to_info(self, container: Container) -> DockerContainerInfo:
        """
        Convert Docker container to info model.

        Args:
            container: Docker container object

        Returns:
            Container information model
        """
        # Map Docker status to our enum
        status_map = {
            "running": ContainerStatus.RUNNING,
            "exited": ContainerStatus.EXITED,
            "paused": ContainerStatus.PAUSED,
            "restarting": ContainerStatus.RESTARTING,
            "dead": ContainerStatus.DEAD,
        }
        
        status_str = container.status.lower()
        status = status_map.get(status_str, ContainerStatus.STOPPED)

        # Parse created time
        created_str = container.attrs.get("Created", "")
        try:
            created = datetime.fromisoformat(created_str.replace("Z", "+00:00"))
        except Exception:
            created = datetime.now()

        return DockerContainerInfo(
            id=container.id,
            name=container.name,
            image=container.image.tags[0] if container.image.tags else container.image.short_id,
            status=status,
            state=container.status,
            created=created,
            ports=container.ports,
            labels=container.labels,
        )

    def close(self) -> None:
        """Close Docker client connection."""
        try:
            self.client.close()
            logger.info("Docker client closed")
        except Exception as e:
            logger.error(f"Error closing Docker client: {e}")
