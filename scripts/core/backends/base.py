from abc import ABC, abstractmethod
from typing import List, Optional, Any

class SpawnBackend(ABC):
    """Abstract backend for spawning agent processes."""

    @abstractmethod
    def spawn(self, agent_name: str, command: List[str], color: str = "white") -> Any:
        """Spawn an agent process. Returns a handle (thread, pane_id, etc.)."""
        ...

    @abstractmethod
    def kill(self, agent_name: str):
        """Kill an agent's process."""
        ...

    @abstractmethod
    def is_alive(self, agent_name: str) -> bool:
        """Check if an agent is still running."""
        ...

    @abstractmethod
    def cleanup(self):
        """Cleanup all resources on shutdown."""
        ...

    @abstractmethod
    def get_type(self) -> str:
        """Return backend type name."""
        ...
