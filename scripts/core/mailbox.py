"""File-based mailbox for inter-agent communication.

Each agent has its own inbox directory. Messages are individual JSON files
to avoid locking issues. Atomic writes via temp+rename pattern.
"""

import os
import json
import time
import uuid
import glob
import tempfile
from typing import List, Optional

from scripts.core.types import Message, MessageType


class Mailbox:
    """File-based mailbox for inter-agent communication."""

    def __init__(self, agent_name: str, base_dir: str = ".swarm/mailboxes"):
        """Initialize mailbox for an agent.

        Args:
            agent_name: Name of the agent owning this mailbox
            base_dir: Base directory for all mailboxes
        """
        self.agent_name = agent_name
        self.inbox_dir = os.path.join(base_dir, agent_name, "inbox")
        self.processed_dir = os.path.join(base_dir, agent_name, "processed")
        self.base_dir = base_dir
        os.makedirs(self.inbox_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)

    def send(self, recipient: str, msg_type: MessageType, content: str, metadata: dict = None) -> Message:
        """Send a message to another agent's inbox.

        Uses atomic write via temp+rename to prevent corruption.

        Args:
            recipient: Name of the recipient agent
            msg_type: Type of message (MessageType enum or string)
            content: Message content
            metadata: Optional metadata dictionary

        Returns:
            Message: The sent message object
        """
        msg = Message(
            msg_id=str(uuid.uuid4())[:8],
            sender=self.agent_name,
            recipient=recipient,
            msg_type=msg_type.value if isinstance(msg_type, MessageType) else msg_type,
            content=content,
            timestamp=time.time(),
            metadata=metadata or {}
        )
        target_inbox = os.path.join(self.base_dir, recipient, "inbox")
        os.makedirs(target_inbox, exist_ok=True)

        filename = f"{int(time.time() * 1000)}-{msg.msg_id}.json"
        filepath = os.path.join(target_inbox, filename)

        # Atomic write: write to temp file then rename
        fd, tmp_path = tempfile.mkstemp(dir=target_inbox, suffix=".tmp")
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(msg.to_dict(), f)
            os.rename(tmp_path, filepath)
        except Exception:
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
            raise
        return msg

    def broadcast(self, all_agents: List[str], msg_type: MessageType, content: str, metadata: dict = None) -> List[Message]:
        """Send a message to all agents except self.

        Args:
            all_agents: List of all agent names
            msg_type: Type of message
            content: Message content
            metadata: Optional metadata dictionary

        Returns:
            List[Message]: List of sent messages
        """
        messages = []
        for agent in all_agents:
            if agent != self.agent_name:
                msg = self.send(agent, msg_type, content, metadata)
                messages.append(msg)
        return messages

    def poll(self) -> List[Message]:
        """Read all unprocessed messages from inbox, move to processed.

        Returns:
            List[Message]: List of messages, sorted by timestamp
        """
        messages = []
        pattern = os.path.join(self.inbox_dir, "*.json")
        for filepath in sorted(glob.glob(pattern)):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                msg = Message.from_dict(data)
                messages.append(msg)
                # Move to processed
                processed_path = os.path.join(self.processed_dir, os.path.basename(filepath))
                os.rename(filepath, processed_path)
            except (json.JSONDecodeError, OSError, KeyError) as e:
                # Skip corrupted/missing files
                continue
        return messages

    def has_messages(self) -> bool:
        """Quick check if there are unread messages.

        Returns:
            bool: True if unread messages exist
        """
        pattern = os.path.join(self.inbox_dir, "*.json")
        return len(glob.glob(pattern)) > 0

    def write_heartbeat(self):
        """Write a heartbeat timestamp file for this agent."""
        heartbeat_path = os.path.join(self.base_dir, self.agent_name, "heartbeat")
        os.makedirs(os.path.dirname(heartbeat_path), exist_ok=True)
        try:
            with open(heartbeat_path, 'w') as f:
                f.write(str(time.time()))
        except OSError:
            pass

    def read_heartbeat(self, agent_name: str) -> Optional[float]:
        """Read another agent's heartbeat timestamp.

        Args:
            agent_name: Name of the agent to check

        Returns:
            Optional[float]: Timestamp of last heartbeat, or None if not available
        """
        heartbeat_path = os.path.join(self.base_dir, agent_name, "heartbeat")
        if os.path.exists(heartbeat_path):
            try:
                with open(heartbeat_path, 'r') as f:
                    return float(f.read().strip())
            except (ValueError, OSError):
                pass
        return None

    def cleanup_processed(self, max_age_seconds: int = 3600):
        """Remove processed messages older than max_age_seconds.

        Args:
            max_age_seconds: Maximum age in seconds (default: 1 hour)
        """
        pattern = os.path.join(self.processed_dir, "*.json")
        now = time.time()
        for filepath in glob.glob(pattern):
            try:
                if now - os.path.getmtime(filepath) > max_age_seconds:
                    os.unlink(filepath)
            except OSError:
                continue

    def get_message_count(self) -> dict:
        """Get counts of sent and received messages.

        Returns:
            dict: Dictionary with 'unread' and 'processed' counts
        """
        inbox_count = len(glob.glob(os.path.join(self.inbox_dir, "*.json")))
        processed_count = len(glob.glob(os.path.join(self.processed_dir, "*.json")))
        return {"unread": inbox_count, "processed": processed_count}


def get_all_messages(base_dir: str = ".swarm/mailboxes") -> List[Message]:
    """Read all processed messages from all agents (for Messages View in TUI).

    Args:
        base_dir: Base directory for all mailboxes

    Returns:
        List[Message]: All processed messages, sorted by timestamp
    """
    messages = []
    if not os.path.exists(base_dir):
        return messages

    try:
        for agent_dir in os.listdir(base_dir):
            processed_dir = os.path.join(base_dir, agent_dir, "processed")
            if not os.path.isdir(processed_dir):
                continue
            for filepath in glob.glob(os.path.join(processed_dir, "*.json")):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    messages.append(Message.from_dict(data))
                except (json.JSONDecodeError, OSError, KeyError):
                    continue
    except OSError:
        pass

    messages.sort(key=lambda m: m.timestamp)
    return messages
