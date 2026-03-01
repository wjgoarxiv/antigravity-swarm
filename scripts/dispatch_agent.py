# -*- coding: utf-8 -*-
"""
Antigravity Swarm Agent Dispatcher

Dispatches a sub-agent via Gemini CLI with:
- Streaming side-effect parsing (execute tags as they appear)
- Agent lifecycle management (run -> idle -> poll -> respond)
- Inter-agent messaging (SEND_MESSAGE, BROADCAST tags)
- Audit logging for all actions
- Mailbox polling for follow-up tasks
"""

import sys
import os
import re
import subprocess
import time
import json
import signal
import select
from typing import Optional

# Allow standalone execution: add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.core.config import get_gemini_path, SwarmConfig, ensure_dirs
from scripts.core.types import AgentStatus, MessageType, AgentIdentity
from scripts.core.mailbox import Mailbox
from scripts.core.audit import AuditLog


MAX_STREAM_BUFFER_CHARS = 262144
MAX_STREAM_TRIM_CHARS = 131072
MAX_TAG_CONTENT_CHARS = 1048576
MAX_MESSAGE_CHARS = 65536
REQUIRED_PROMPT_SECTIONS = (
    "1. TASK",
    "2. EXPECTED OUTCOME",
    "3. REQUIRED TOOLS",
    "4. MUST DO",
    "5. MUST NOT DO",
    "6. CONTEXT",
)


# ---------------------------------------------------------------------------
# Backward-compatible module-level function
# ---------------------------------------------------------------------------

def parse_and_execute_side_effects(output):
    """
    Parse agent output for special tags and execute side effects.

    Kept as a module-level function for backward compatibility.
    Supports: <<WRITE_FILE>>, <<RUN_COMMAND>>, <<SEND_MESSAGE>>, <<BROADCAST>>
    """
    # WRITE_FILE
    write_pattern = re.compile(r'<<WRITE_FILE path="([^"]+)">>(.*?)<<END_WRITE>>', re.DOTALL)
    for match in write_pattern.finditer(output):
        path = match.group(1)
        content = match.group(2).strip()
        if content.startswith('\n'):
            content = content[1:]
        if content.endswith('\n'):
            content = content[:-1]
        try:
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"[Shim] Successfully wrote to {path}")
        except Exception as e:
            print(f"[Shim] Error writing to {path}: {e}")

    # RUN_COMMAND
    run_pattern = re.compile(r'<<RUN_COMMAND>>(.*?)<<END_COMMAND>>', re.DOTALL)
    for match in run_pattern.finditer(output):
        command = match.group(1).strip()
        print(f"[Shim] Executing command: {command}")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            print(f"[Shim] Command Output:\n{result.stdout}")
            if result.stderr:
                print(f"[Shim] Command Error:\n{result.stderr}")
        except Exception as e:
            print(f"[Shim] Error executing command: {e}")


# ---------------------------------------------------------------------------
# Agent Lifecycle
# ---------------------------------------------------------------------------

class AgentLifecycle:
    """Manages the full lifecycle of an agent: run, idle, poll, respond."""

    def __init__(self, identity: AgentIdentity, mailbox: Mailbox, audit: AuditLog, config: SwarmConfig):
        self.identity = identity
        self.mailbox = mailbox
        self.audit = audit
        self.config = config
        self.status = AgentStatus.PENDING

    # -- Public API ---------------------------------------------------------

    def run(
        self,
        initial_task: str,
        gemini_path: str,
        model: str,
        log_file: Optional[str] = None,
        exit_on_idle: bool = False,
    ):
        """Full lifecycle: execute task, enter idle, poll inbox, handle messages."""
        self.status = AgentStatus.RUNNING
        self.audit.record(self.identity.name, "status_change", "running")

        # Execute the initial task
        self._execute_task(initial_task, gemini_path, model, log_file)

        if exit_on_idle:
            self.status = AgentStatus.COMPLETED
            self.audit.record(self.identity.name, "status_change", "completed")
            self._notify_leader("__AGENT_COMPLETED__: initial_task")
            return

        # Enter idle state and poll for messages
        self.status = AgentStatus.IDLE
        self.audit.record(self.identity.name, "status_change", "idle")
        self._notify_leader("Task completed. Entering idle state.")

        # Poll loop
        poll_interval = self.config.poll_interval_ms / 1000.0
        try:
            idle_timeout_seconds = float(os.environ.get("AG_SWARM_AGENT_IDLE_TIMEOUT_SECONDS", "120"))
        except ValueError:
            idle_timeout_seconds = 120.0
        idle_timeout_seconds = max(0.0, idle_timeout_seconds)
        idle_started_at = time.time()
        last_cleanup = time.time()
        while self.status == AgentStatus.IDLE:
            self.mailbox.write_heartbeat()
            messages = self.mailbox.poll()
            if messages:
                idle_started_at = time.time()
            for msg in messages:
                self.audit.record(
                    self.identity.name, "message_received",
                    f"from {msg.sender}", {"type": msg.msg_type},
                )
                if msg.msg_type == MessageType.SHUTDOWN_REQUEST.value:
                    self._handle_shutdown(msg)
                    return
                elif msg.msg_type in (MessageType.DIRECT.value, MessageType.BROADCAST.value):
                    self.status = AgentStatus.RUNNING
                    self.audit.record(
                        self.identity.name, "status_change",
                        "running (new task from message)",
                    )
                    self._execute_task(msg.content, gemini_path, model, log_file)
                    self.status = AgentStatus.IDLE
                    self.audit.record(self.identity.name, "status_change", "idle")
                    self._notify_leader(f"Follow-up task from {msg.sender} completed.")

            if idle_timeout_seconds > 0 and (time.time() - idle_started_at) >= idle_timeout_seconds:
                self.status = AgentStatus.COMPLETED
                self.audit.record(
                    self.identity.name,
                    "status_change",
                    "completed (idle_timeout)",
                )
                self._notify_leader("__AGENT_COMPLETED__: idle_timeout")
                return

            now = time.time()
            if now - last_cleanup >= 300:
                try:
                    self.mailbox.cleanup_processed(max_age_seconds=86400)
                except Exception as e:
                    self.audit.record(
                        self.identity.name,
                        "error",
                        "mailbox_cleanup_failed",
                        {"detail": str(e)[:200]},
                    )
                last_cleanup = now
            time.sleep(poll_interval)

    # -- Task execution -----------------------------------------------------

    def _execute_task(self, task: str, gemini_path: str, model: str, log_file: Optional[str] = None):
        """Execute a single task via Gemini subprocess with streaming parse."""
        shim_instruction = self._build_shim_instruction()
        contracted_task = self._ensure_prompt_contract(task)
        full_prompt = f"{shim_instruction}{contracted_task}"

        cmd = [
            gemini_path,
            "--model",
            model,
            "--prompt",
            full_prompt,
            "--output-format",
            "text",
        ]
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            encoding='utf-8',
        )

        buffer = ""
        log_handle = None
        if log_file:
            os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
            log_handle = open(log_file, 'a', encoding='utf-8')

        stdout = process.stdout
        stderr = process.stderr
        try:
            task_timeout_seconds = float(os.environ.get("AG_SWARM_TASK_TIMEOUT_SECONDS", "240"))
        except ValueError:
            task_timeout_seconds = 240.0
        task_timeout_seconds = max(0.0, task_timeout_seconds)
        task_started_at = time.time()

        try:
            while True:
                if task_timeout_seconds > 0 and (time.time() - task_started_at) >= task_timeout_seconds:
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        process.kill()
                    self.audit.record(
                        self.identity.name,
                        "error",
                        "task_execution_timeout",
                        {"timeout_seconds": round(task_timeout_seconds, 2), "failure_class": "timeout_error"},
                    )
                    break

                if stdout is None:
                    break

                ready, _, _ = select.select([stdout], [], [], 0.2)
                if not ready:
                    if process.poll() is not None:
                        break
                    continue

                line = stdout.readline()
                if not line:
                    if process.poll() is not None:
                        break
                    continue

                if line:
                    print(line.strip())
                    if log_handle:
                        log_handle.write(line)
                        log_handle.flush()
                    buffer += line
                    # Stream-parse: execute any complete tag pairs immediately
                    buffer = self._parse_streaming(buffer)

                    if len(buffer) > MAX_STREAM_BUFFER_CHARS:
                        cut_idx = buffer.rfind("<<", -MAX_STREAM_TRIM_CHARS)
                        if cut_idx == -1:
                            cut_idx = len(buffer) - MAX_STREAM_TRIM_CHARS
                        dropped = cut_idx if cut_idx > 0 else 0
                        if dropped > 0:
                            self.audit.record(
                                self.identity.name,
                                "warning",
                                "stream_buffer_trimmed",
                                {"dropped_chars": dropped},
                            )
                            buffer = buffer[cut_idx:]

            # Final parse for any remaining complete tags
            tail = self._parse_streaming(buffer, final=True)
            if tail.strip():
                self.audit.record(
                    self.identity.name,
                    "warning",
                    "stream_tail_unparsed",
                    {"tail_chars": len(tail)},
                )

            if process.returncode != 0:
                stderr_output = stderr.read() if stderr else ""
                self.audit.record(
                    self.identity.name, "error",
                    f"Process exited with code {process.returncode}",
                    {"stderr": stderr_output[:500] if stderr_output else ""},
                )
        finally:
            if log_handle:
                log_handle.close()

    # -- Shim instruction ---------------------------------------------------

    def _build_shim_instruction(self) -> str:
        """Build the shim instruction including message tags."""
        return (
            "You are a sub-agent working in the Antigravity IDE. "
            "Your environment lacks native writing tools, but I have a shim layer to help you. "
            "To perform actions, you MUST use the following syntax PRECISELY:\n\n"
            "1. TO WRITE A FILE:\n"
            '<<WRITE_FILE path="path/to/file.ext">>\n'
            "File content goes here...\n"
            "<<END_WRITE>>\n\n"
            "2. TO RUN A SHELL COMMAND:\n"
            "<<RUN_COMMAND>>\n"
            "ls -la\n"
            "<<END_COMMAND>>\n\n"
            "3. TO SEND A MESSAGE TO ANOTHER AGENT:\n"
            '<<SEND_MESSAGE to="agent_name">>\n'
            "Your message here...\n"
            "<<END_MESSAGE>>\n\n"
            "4. TO BROADCAST A MESSAGE TO ALL AGENTS:\n"
            "<<BROADCAST>>\n"
            "Your message here...\n"
            "<<END_BROADCAST>>\n\n"
            "Now, perform the following task:\n"
        )

    def _ensure_prompt_contract(self, task_text: str) -> str:
        if all(section in task_text for section in REQUIRED_PROMPT_SECTIONS):
            return task_text

        return (
            "1. TASK\n"
            f"{task_text}\n\n"
            "2. EXPECTED OUTCOME\n"
            "Deliver concrete outputs and verification notes.\n\n"
            "3. REQUIRED TOOLS\n"
            "Use only necessary tools and report key tool outcomes.\n\n"
            "4. MUST DO\n"
            "Preserve existing behavior and validate before completion.\n\n"
            "5. MUST NOT DO\n"
            "No destructive actions and no fabricated results.\n\n"
            "6. CONTEXT\n"
            f"Agent: {self.identity.name}. Team: {self.identity.team_name}."
        )

    # -- Streaming side-effect parser ---------------------------------------

    def _parse_streaming(self, buffer: str, final: bool = False) -> str:
        """Parse and execute side effects from the streaming buffer.

        Matches complete tag pairs, executes them immediately, and removes
        them from the buffer.  Incomplete (partial) tags are left in the
        buffer so they can be completed by subsequent lines.

        Args:
            buffer: Accumulated stdout text
            final:  If True this is the last call; log a warning for
                    any orphaned opening tags remaining.

        Returns:
            Remaining unparsed buffer content.
        """
        # -- WRITE_FILE -----------------------------------------------------
        write_pat = re.compile(
            r'<<WRITE_FILE path="([^"]+)">>(.*?)<<END_WRITE>>', re.DOTALL,
        )
        for match in write_pat.finditer(buffer):
            path = match.group(1)
            content = match.group(2).strip()
            if len(content) > MAX_TAG_CONTENT_CHARS:
                self.audit.record(
                    self.identity.name,
                    "error",
                    "write_file_payload_too_large",
                    {"path": path, "size": len(content)},
                )
                continue
            if content.startswith('\n'):
                content = content[1:]
            if content.endswith('\n'):
                content = content[:-1]
            try:
                os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"[Shim] Successfully wrote to {path}")
                self.audit.record(
                    self.identity.name, "file_write", path,
                    {"size": len(content)},
                )
            except Exception as e:
                print(f"[Shim] Error writing to {path}: {e}")
                self.audit.record(
                    self.identity.name, "error",
                    f"File write failed: {path}: {e}",
                )
        buffer = write_pat.sub('', buffer)

        # -- RUN_COMMAND ----------------------------------------------------
        run_pat = re.compile(
            r'<<RUN_COMMAND>>(.*?)<<END_COMMAND>>', re.DOTALL,
        )
        for match in run_pat.finditer(buffer):
            command = match.group(1).strip()
            if len(command) > MAX_TAG_CONTENT_CHARS:
                self.audit.record(
                    self.identity.name,
                    "error",
                    "run_command_payload_too_large",
                    {"size": len(command)},
                )
                continue
            print(f"[Shim] Executing command: {command}")
            try:
                result = subprocess.run(
                    command, shell=True, capture_output=True, text=True,
                )
                print(f"[Shim] Command Output:\n{result.stdout}")
                if result.stderr:
                    print(f"[Shim] Command Error:\n{result.stderr}")
                self.audit.record(
                    self.identity.name, "command_exec", command,
                    {"exit_code": result.returncode},
                )
            except Exception as e:
                print(f"[Shim] Error executing command: {e}")
                self.audit.record(
                    self.identity.name, "error",
                    f"Command failed: {command}: {e}",
                )
        buffer = run_pat.sub('', buffer)

        # -- SEND_MESSAGE ---------------------------------------------------
        msg_pat = re.compile(
            r'<<SEND_MESSAGE to="([^"]+)">>(.*?)<<END_MESSAGE>>', re.DOTALL,
        )
        for match in msg_pat.finditer(buffer):
            recipient = match.group(1)
            content = match.group(2).strip()
            if len(content) > MAX_MESSAGE_CHARS:
                self.audit.record(
                    self.identity.name,
                    "error",
                    "direct_message_too_large",
                    {"to": recipient, "size": len(content)},
                )
                continue
            try:
                self.mailbox.send(recipient, MessageType.DIRECT, content)
                print(f"[Shim] Sent message to {recipient}")
                self.audit.record(
                    self.identity.name, "message_sent",
                    f"\u2192{recipient}", {"preview": content[:50]},
                )
            except Exception as e:
                print(f"[Shim] Error sending message to {recipient}: {e}")
                self.audit.record(
                    self.identity.name, "error",
                    f"Message send failed \u2192{recipient}: {e}",
                )
        buffer = msg_pat.sub('', buffer)

        # -- BROADCAST ------------------------------------------------------
        bcast_pat = re.compile(
            r'<<BROADCAST>>(.*?)<<END_BROADCAST>>', re.DOTALL,
        )
        for match in bcast_pat.finditer(buffer):
            content = match.group(1).strip()
            if len(content) > MAX_MESSAGE_CHARS:
                self.audit.record(
                    self.identity.name,
                    "error",
                    "broadcast_message_too_large",
                    {"size": len(content)},
                )
                continue
            all_agents = self._discover_team_agents()
            if all_agents:
                self.mailbox.broadcast(all_agents, MessageType.BROADCAST, content)
                sent_count = len([a for a in all_agents if a != self.identity.name])
                print(f"[Shim] Broadcast sent to {sent_count} agents")
                self.audit.record(
                    self.identity.name, "message_sent",
                    "\u2192ALL", {"preview": content[:50]},
                )
            else:
                print("[Shim] Broadcast skipped: no team agents discovered")
        buffer = bcast_pat.sub('', buffer)

        if final:
            orphan_markers = [
                "<<WRITE_FILE", "<<RUN_COMMAND>>", "<<SEND_MESSAGE", "<<BROADCAST>>"
            ]
            orphaned = [m for m in orphan_markers if m in buffer]
            if orphaned:
                self.audit.record(
                    self.identity.name,
                    "warning",
                    "stream_orphan_tags",
                    {"markers": orphaned, "tail_chars": len(buffer)},
                )

        return buffer

    # -- Helpers ------------------------------------------------------------

    def _discover_team_agents(self) -> list:
        """Read team config to discover all agent names."""
        team_config_path = os.path.join(".swarm", "config.json")
        if os.path.exists(team_config_path):
            try:
                with open(team_config_path, 'r', encoding='utf-8') as f:
                    tc = json.load(f)
                return [m["name"] for m in tc.get("members", [])]
            except (json.JSONDecodeError, OSError, KeyError):
                pass
        return []

    def _notify_leader(self, content: str):
        """Send a status update to the leader."""
        try:
            self.mailbox.send("leader", MessageType.STATUS_UPDATE, content)
        except Exception:
            pass  # Don't crash if leader mailbox doesn't exist yet

    def _handle_shutdown(self, msg):
        """Handle a shutdown request."""
        self.status = AgentStatus.SHUTDOWN
        self.audit.record(
            self.identity.name, "shutdown",
            f"Requested by {msg.sender}",
        )
        try:
            self.mailbox.send(
                msg.sender, MessageType.SHUTDOWN_RESPONSE,
                "Shutdown acknowledged.",
            )
        except Exception:
            pass
        print(f"[{self.identity.name}] Shutting down.")


# ---------------------------------------------------------------------------
# CLI argument helpers
# ---------------------------------------------------------------------------

def _extract_arg(args: list, flag: str):
    """Extract a flag value from args list, removing both flag and value.

    Args:
        args: Mutable list of CLI arguments
        flag: Flag name (e.g. '--model')

    Returns:
        The value string, or None if flag not present.
    """
    if flag in args:
        idx = args.index(flag)
        if idx + 1 < len(args):
            value = args[idx + 1]
            del args[idx:idx + 2]
            return value
    return None


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    reconfigure = getattr(sys.stdout, 'reconfigure', None)
    if callable(reconfigure):
        reconfigure(encoding='utf-8')

    if len(sys.argv) < 2:
        print("Usage: python3 dispatch_agent.py <task_description> [options]")
        print("Options:")
        print("  --log-file <path>    Log file path")
        print("  --model <name>       Model name (default: auto-gemini-3)")
        print("  --agent-id <id>      Agent identity (e.g., oracle@mission)")
        print("  --team-dir <dir>     Team directory (default: .swarm)")
        print("  --exit-on-idle       Exit after initial task (no idle poll loop)")
        print("  --watch              Stream raw output to stdout")
        sys.exit(1)

    # Parse arguments
    args = sys.argv[1:]

    log_file = _extract_arg(args, "--log-file")
    model_name = _extract_arg(args, "--model") or "auto-gemini-3"
    agent_id_str = _extract_arg(args, "--agent-id")
    team_dir = _extract_arg(args, "--team-dir") or ".swarm"

    # --watch is a boolean flag (no value)
    watch_mode = "--watch" in args
    if watch_mode:
        args.remove("--watch")

    exit_on_idle = "--exit-on-idle" in args
    if exit_on_idle:
        args.remove("--exit-on-idle")

    task = " ".join(args)

    if not task.strip():
        print("[Dispatch][Hook:PreRunValidation] FAILED (empty_task)")
        sys.exit(1)

    # Resolve Gemini CLI
    gemini_path = get_gemini_path()
    if not gemini_path:
        print("Error: 'gemini' executable not found.")
        print(
            "Please resolve this by:\n"
            "1. Installing gemini CLI.\n"
            "2. Ensuring it is in your PATH.\n"
            "3. Or setting GEMINI_PATH environment variable."
        )
        sys.exit(1)

    # Load config and ensure directories
    config = SwarmConfig.load()
    ensure_dirs()

    # Build agent identity
    if agent_id_str and "@" in agent_id_str:
        name, team = agent_id_str.split("@", 1)
    else:
        name = agent_id_str or "agent"
        team = "default"

    if "@" in name or "@" in team:
        print("[Dispatch][Hook:PreRunValidation] FAILED (invalid_identity_format)")
        sys.exit(1)

    identity = AgentIdentity(name=name, team_name=team)

    # Set up mailbox and audit
    mailbox_base = os.path.join(team_dir, "mailboxes")
    audit_base = os.path.join(team_dir, "audit")

    mailbox = Mailbox(name, base_dir=mailbox_base)
    audit = AuditLog(team, audit_dir=audit_base)

    audit.record(name, "spawned", f"Task: {task[:100]}", {"model": model_name})

    print(f"[Shim] Dispatching task to sub-agent ({model_name}): {task}")

    # Run with lifecycle
    lifecycle = AgentLifecycle(identity, mailbox, audit, config)

    def _signal_handler(signum, _frame):
        lifecycle.status = AgentStatus.FAILED
        audit.record(
            name,
            "error",
            "dispatcher_interrupted",
            {"signal": int(signum), "failure_class": "interrupted"},
        )
        try:
            mailbox.send("leader", MessageType.STATUS_UPDATE, f"Interrupted by signal {signum}.")
        except Exception:
            pass
        raise SystemExit(1)

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    lifecycle.run(task, gemini_path, model_name, log_file, exit_on_idle=exit_on_idle)

    # Exit based on final status
    if lifecycle.status == AgentStatus.FAILED:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
