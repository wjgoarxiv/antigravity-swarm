# -*- coding: utf-8 -*-
"""
Antigravity Swarm Type Definitions
Agent identity, status, and message types.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional, Dict

# Color palette for agent visualization
COLOR_PALETTE = ["red", "blue", "green", "yellow", "magenta", "cyan", "white", "bright_red"]


class AgentStatus(Enum):
    """Agent execution status."""
    PENDING = "pending"
    RUNNING = "running"
    IDLE = "idle"
    COMPLETED = "completed"
    FAILED = "failed"
    SHUTDOWN = "shutdown"


class MessageType(Enum):
    """Message types for agent communication."""
    DIRECT = "direct"
    BROADCAST = "broadcast"
    STATUS_UPDATE = "status_update"
    FINDING = "finding"
    SHUTDOWN_REQUEST = "shutdown_request"
    SHUTDOWN_RESPONSE = "shutdown_response"
    PERMISSION_REQUEST = "permission_request"
    PERMISSION_RESPONSE = "permission_response"


@dataclass
class AgentIdentity:
    """
    Agent identity and state information.
    """
    name: str
    agent_id: str = ""
    team_name: str = "default"
    color: str = "white"
    model: str = "auto-gemini-3"
    mode: str = "parallel"
    status: str = "pending"
    pid: Optional[int] = None
    tmux_pane: Optional[str] = None
    start_time: float = 0.0
    heartbeat: float = 0.0

    def __post_init__(self):
        if not self.agent_id:
            self.agent_id = f"{self.name.lower()}@{self.team_name}"

    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass
class Message:
    """
    Agent communication message.
    """
    msg_id: str
    sender: str
    recipient: str
    msg_type: str
    content: str
    timestamp: float
    metadata: Dict = field(default_factory=dict)

    def to_dict(self):
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


def assign_color(index: int) -> str:
    """
    Assign a color from the palette based on index.

    Args:
        index: Agent index

    Returns:
        Color name from palette
    """
    return COLOR_PALETTE[index % len(COLOR_PALETTE)]


def make_agent_id(name: str, team_name: str) -> str:
    """
    Create a standardized agent ID.

    Args:
        name: Agent name
        team_name: Team name

    Returns:
        Agent ID in format "name@team"
    """
    return f"{name.lower()}@{team_name}"
