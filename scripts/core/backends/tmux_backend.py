import subprocess
import shutil
import os
import time
import shlex
from typing import List, Optional, Any
from scripts.core.backends.base import SpawnBackend

COLOR_TO_TMUX = {
    "red": "red",
    "blue": "blue",
    "green": "green",
    "yellow": "yellow",
    "magenta": "magenta",
    "cyan": "cyan",
    "white": "white",
    "bright_red": "colour196"
}

class TmuxBackend(SpawnBackend):
    """Spawn agents as tmux panes with color-coded borders."""

    SESSION_NAME = "antigravity-swarm"

    def __init__(self):
        self.tmux_path: str = shutil.which("tmux") or ""
        if not self.tmux_path:
            raise RuntimeError("tmux not found. Install tmux or use 'thread' backend.")
        self._panes = {}  # agent_name -> pane_id
        self._session_created = False

    def _run_tmux(self, *args, capture=False):
        """Execute a tmux command."""
        cmd = [self.tmux_path] + list(args)
        if capture:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.stdout.strip()
        else:
            subprocess.run(cmd, capture_output=True)

    def _ensure_session(self):
        """Create tmux session if not already created."""
        if self._session_created:
            return

        # Kill existing session if any
        self._run_tmux("kill-session", "-t", self.SESSION_NAME)

        # Create new detached session
        self._run_tmux("new-session", "-d", "-s", self.SESSION_NAME, "-x", "220", "-y", "50")

        # Enable pane-border-status
        self._run_tmux("set-option", "-t", self.SESSION_NAME, "pane-border-status", "top")
        self._run_tmux("set-option", "-t", self.SESSION_NAME, "pane-border-format", " #{pane_title} ")

        self._session_created = True

    def spawn(self, agent_name: str, command: List[str], color: str = "white") -> str:
        """Spawn an agent in a new tmux pane."""
        self._ensure_session()

        # Create a new pane by splitting
        if self._panes:
            # Split from the first pane
            pane_id = self._run_tmux(
                "split-window", "-t", f"{self.SESSION_NAME}",
                "-h", "-P", "-F", "#{pane_id}",
                capture=True
            )
        else:
            # Use the initial pane
            pane_id = self._run_tmux(
                "list-panes", "-t", self.SESSION_NAME,
                "-F", "#{pane_id}",
                capture=True
            )
            pane_id = (pane_id or "").split('\n')[0]

        if pane_id:
            self._panes[agent_name] = pane_id

            # Set pane title
            self._run_tmux("select-pane", "-t", pane_id, "-T", agent_name)

            # Set border color
            tmux_color = COLOR_TO_TMUX.get(color, "white")
            self._run_tmux("select-pane", "-t", pane_id,
                          "-P", f"fg={tmux_color}")

            self._run_tmux("set-option", "-p", "-t", pane_id, "remain-on-exit", "on")

            # Send command to pane
            cmd_str = " ".join(shlex.quote(c) for c in command)
            wrapped_cmd = f"{cmd_str}; __ag_status=$?; exit $__ag_status"
            self._run_tmux("send-keys", "-t", pane_id, wrapped_cmd, "Enter")

            # Rebalance
            self.rebalance()

        return pane_id or ""

    def kill(self, agent_name: str):
        """Kill an agent's tmux pane."""
        pane_id = self._panes.get(agent_name)
        if pane_id:
            # Send Ctrl+C first for graceful shutdown
            self._run_tmux("send-keys", "-t", pane_id, "C-c", "")
            time.sleep(0.5)

            # Kill the pane
            self._run_tmux("kill-pane", "-t", pane_id)
            del self._panes[agent_name]

            if self._panes:
                self.rebalance()

    def is_alive(self, agent_name: str) -> bool:
        """Check if an agent's pane still exists."""
        pane_id = self._panes.get(agent_name)
        if not pane_id:
            return False

        result = self._run_tmux(
            "list-panes",
            "-t",
            self.SESSION_NAME,
            "-F",
            "#{pane_id} #{pane_dead}",
            capture=True,
        )
        for row in (result or "").splitlines():
            parts = row.split()
            if len(parts) >= 2 and parts[0] == pane_id:
                return parts[1] == "0"
        return False

    def is_alive_many(self, agent_names: List[str]) -> dict:
        result = self._run_tmux(
            "list-panes",
            "-t",
            self.SESSION_NAME,
            "-F",
            "#{pane_id} #{pane_dead}",
            capture=True,
        )
        pane_state = {}
        for row in (result or "").splitlines():
            parts = row.split()
            if len(parts) >= 2:
                pane_state[parts[0]] = parts[1] == "0"
        out = {}
        for name in agent_names:
            pane_id = self._panes.get(name)
            out[name] = bool(pane_id and pane_state.get(pane_id, False))
        return out

    def rebalance(self):
        """Rebalance panes in tiled layout."""
        if self._session_created:
            self._run_tmux("select-layout", "-t", self.SESSION_NAME, "tiled")

    def attach(self):
        """Attach to the tmux session."""
        subprocess.run([self.tmux_path, "attach-session", "-t", self.SESSION_NAME])

    def focus_pane(self, agent_name: str):
        """Focus a specific agent's pane."""
        pane_id = self._panes.get(agent_name)
        if pane_id:
            self._run_tmux("select-pane", "-t", pane_id)

    def cleanup(self):
        """Kill the entire tmux session."""
        if self._session_created:
            self._run_tmux("kill-session", "-t", self.SESSION_NAME)
            self._panes.clear()
            self._session_created = False

    def get_type(self) -> str:
        """Return backend type name."""
        return "tmux"

    def get_pane_id(self, agent_name: str) -> Optional[str]:
        """Get the tmux pane ID for an agent."""
        return self._panes.get(agent_name)

    def get_return_code(self, agent_name: str) -> Optional[int]:
        pane_id = self._panes.get(agent_name)
        if not pane_id:
            return None

        result = self._run_tmux(
            "list-panes",
            "-t",
            self.SESSION_NAME,
            "-F",
            "#{pane_id} #{pane_dead} #{pane_dead_status}",
            capture=True,
        )
        for row in (result or "").splitlines():
            parts = row.split()
            if len(parts) >= 3 and parts[0] == pane_id:
                if parts[1] != "1":
                    return None
                try:
                    return int(parts[2])
                except ValueError:
                    return None
        return None

    @staticmethod
    def is_available() -> bool:
        """Check if tmux backend is available."""
        return shutil.which("tmux") is not None and "TMUX" not in os.environ
