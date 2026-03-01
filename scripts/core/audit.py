import json
import time
import os
from typing import List, Optional

class AuditLog:
    """Append-only audit trail for all agent actions."""

    def __init__(self, mission_id: str = "default", audit_dir: str = ".swarm/audit"):
        self.audit_dir = audit_dir
        os.makedirs(audit_dir, exist_ok=True)
        self.log_file = os.path.join(audit_dir, f"mission-{mission_id}.jsonl")

    def record(self, agent_name: str, event_type: str, detail: str, metadata: Optional[dict] = None):
        """Record an audit event. Events: spawned, status_change, file_write, command_exec, message_sent, message_received, shutdown, error"""
        meta = metadata.copy() if metadata else {}
        if event_type == "error" and "failure_class" not in meta:
            text = f"{detail}".lower()
            if "config" in text or "yaml" in text:
                meta["failure_class"] = "config_error"
            elif "timeout" in text:
                meta["failure_class"] = "timeout_error"
            elif "mailbox" in text:
                meta["failure_class"] = "mailbox_error"
            elif "process exited" in text or "returncode" in text:
                meta["failure_class"] = "process_error"
            else:
                meta["failure_class"] = "unknown_error"

        entry = {
            "ts": time.time(),
            "agent": agent_name,
            "event": event_type,
            "detail": detail,
            "meta": meta
        }
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(entry) + "\n")
        except OSError:
            pass  # Don't let audit failures crash the system

    def read_all(self) -> List[dict]:
        entries = []
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            entries.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue
        return entries

    def read_for_agent(self, agent_name: str) -> List[dict]:
        return [e for e in self.read_all() if e.get("agent") == agent_name]

    def get_timeline(self, limit: int = 12) -> List[dict]:
        entries = self.read_all()
        if not entries:
            return []

        entries = sorted(entries, key=lambda e: e.get("ts", 0.0))
        if limit > 0:
            entries = entries[-limit:]

        timeline = []
        for e in entries:
            timeline.append({
                "ts": e.get("ts", 0.0),
                "agent": e.get("agent", "unknown"),
                "event": e.get("event", ""),
                "detail": e.get("detail", ""),
                "failure_class": e.get("meta", {}).get("failure_class", ""),
            })
        return timeline

    def get_summary(self) -> dict:
        """Get summary stats from audit trail."""
        entries = self.read_all()
        summary = {
            "total_events": len(entries),
            "file_writes": 0,
            "commands_run": 0,
            "messages_sent": 0,
            "errors": 0,
            "failure_classes": {},
            "agents": {},
            "files_modified": set(),
        }
        for e in entries:
            agent = e.get("agent", "unknown")
            event = e.get("event", "")
            if agent not in summary["agents"]:
                summary["agents"][agent] = {"events": 0, "file_writes": 0, "commands": 0, "messages": 0}
            summary["agents"][agent]["events"] += 1
            if event == "file_write":
                summary["file_writes"] += 1
                summary["agents"][agent]["file_writes"] += 1
                summary["files_modified"].add(e.get("detail", ""))
            elif event == "command_exec":
                summary["commands_run"] += 1
                summary["agents"][agent]["commands"] += 1
            elif event == "message_sent":
                summary["messages_sent"] += 1
                summary["agents"][agent]["messages"] += 1
            elif event == "error":
                summary["errors"] += 1
                failure_class = e.get("meta", {}).get("failure_class", "unknown_error")
                summary["failure_classes"][failure_class] = summary["failure_classes"].get(failure_class, 0) + 1
        summary["files_modified"] = list(summary["files_modified"])
        return summary
