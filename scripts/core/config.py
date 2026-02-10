# -*- coding: utf-8 -*-
"""
Antigravity Swarm Configuration Module
Single source of truth for all configuration constants and settings.
"""

import os
import shutil
import yaml
from dataclasses import dataclass, field, asdict
from typing import Dict

# Directory constants
STATE_DIR = ".swarm"
MAILBOX_DIR = ".swarm/mailboxes"
AUDIT_DIR = ".swarm/audit"
MISSIONS_DIR = ".swarm/missions"


def get_gemini_path():
    """
    Locate the Gemini CLI executable.

    Returns:
        str: Path to gemini executable, or None if not found
    """
    # First check GEMINI_PATH environment variable
    path = os.environ.get("GEMINI_PATH")
    if path and os.path.isfile(path) and os.access(path, os.X_OK):
        return path

    # Fall back to PATH search
    path = shutil.which("gemini")
    if path:
        return path

    return None


def ensure_dirs():
    """Create all required .swarm subdirectories."""
    directories = [
        STATE_DIR,
        MAILBOX_DIR,
        AUDIT_DIR,
        MISSIONS_DIR,
    ]
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


@dataclass
class SwarmConfig:
    """
    Swarm configuration loaded from swarm-config.yaml.
    """
    backend: str = "auto"              # auto | tmux | thread
    default_model: str = "auto-gemini-3"
    max_parallel: int = 5
    poll_interval_ms: int = 1000
    permission_mode: str = "auto"      # auto | ask | deny
    audit_enabled: bool = True
    tui_refresh_rate: int = 10
    compaction_threshold: int = 50
    presets: Dict = field(default_factory=dict)

    @classmethod
    def load(cls, path="swarm-config.yaml"):
        """
        Load configuration from YAML file.

        Args:
            path: Path to config file

        Returns:
            SwarmConfig instance with loaded values
        """
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f) or {}
            # Filter to only known fields
            valid = {k: v for k, v in data.items() if k in cls.__dataclass_fields__}
            return cls(**valid)
        return cls()

    def save(self, path="swarm-config.yaml"):
        """
        Save configuration to YAML file.

        Args:
            path: Path to config file
        """
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(asdict(self), f, default_flow_style=False)
