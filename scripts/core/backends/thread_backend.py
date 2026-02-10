import subprocess
import threading
import sys
from typing import List, Optional, Any
from scripts.core.backends.base import SpawnBackend

class ThreadBackend(SpawnBackend):
    """Spawn agents as threads running subprocesses."""

    def __init__(self):
        self._agents = {}  # agent_name -> {"thread": Thread, "process": Popen}

    def spawn(self, agent_name: str, command: List[str], color: str = "white") -> threading.Thread:
        """Spawn an agent process in a thread."""
        process = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        def wait_for_process():
            process.wait()

        thread = threading.Thread(target=wait_for_process, daemon=True)
        thread.start()

        self._agents[agent_name] = {
            "thread": thread,
            "process": process,
            "pid": process.pid
        }
        return thread

    def kill(self, agent_name: str):
        """Terminate an agent's process."""
        agent = self._agents.get(agent_name)
        if agent and agent["process"].poll() is None:
            agent["process"].terminate()
            try:
                agent["process"].wait(timeout=5)
            except subprocess.TimeoutExpired:
                agent["process"].kill()

    def is_alive(self, agent_name: str) -> bool:
        """Check if an agent is still running."""
        agent = self._agents.get(agent_name)
        if agent:
            return agent["process"].poll() is None
        return False

    def get_pid(self, agent_name: str) -> Optional[int]:
        """Get the process ID of an agent."""
        agent = self._agents.get(agent_name)
        if agent:
            return agent["pid"]
        return None

    def get_return_code(self, agent_name: str) -> Optional[int]:
        """Get the return code of a completed agent process."""
        agent = self._agents.get(agent_name)
        if agent:
            return agent["process"].returncode
        return None

    def cleanup(self):
        """Kill all agent processes and cleanup resources."""
        for name in list(self._agents.keys()):
            self.kill(name)
        self._agents.clear()

    def get_type(self) -> str:
        """Return backend type name."""
        return "thread"
