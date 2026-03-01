# -*- coding: utf-8 -*-
"""
Antigravity Swarm Orchestrator

Manages multi-agent execution with:
- Backend abstraction (tmux / thread)
- Inter-agent mailbox messaging
- Interactive keyboard controls
- Three TUI views: Dashboard, Messages, Agent Detail
- Mission lifecycle and audit logging

Inspired by "Oh-My-Opencode" (https://github.com/code-yeongyu/oh-my-opencode)
Adopts the "Manus Protocol" for state management and TUI visualization.
"""

import yaml
import sys
import subprocess
import threading
import time
import os
import json
import random
import select
import termios
import tty
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich import box

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.core.config import get_gemini_path, SwarmConfig, ensure_dirs, STATE_DIR
from scripts.core.types import AgentStatus, AgentIdentity, MessageType, assign_color
from scripts.core.mailbox import Mailbox, get_all_messages
from scripts.core.audit import AuditLog
from scripts.core.mission import MissionState
from scripts.core.backends import get_backend
from scripts.reporter import generate_report

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CONFIG_FILE = "subagents.yaml"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DISPATCH_SCRIPT = os.path.join(SCRIPT_DIR, "dispatch_agent.py")
SPINNERS = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
REQUIRED_PROMPT_SECTIONS = (
    "1. TASK",
    "2. EXPECTED OUTCOME",
    "3. REQUIRED TOOLS",
    "4. MUST DO",
    "5. MUST NOT DO",
    "6. CONTEXT",
)


# ---------------------------------------------------------------------------
# TUI View Modes
# ---------------------------------------------------------------------------

class ViewMode:
    DASHBOARD = 0
    MESSAGES = 1
    DETAIL = 2


# ---------------------------------------------------------------------------
# Keyboard Listener
# ---------------------------------------------------------------------------

class KeyboardListener:
    """Non-blocking keyboard listener (daemon thread + termios raw mode)."""

    def __init__(self):
        self._queue = []
        self._running = False
        self._thread = None
        self._old_settings = None

    def start(self):
        if not sys.stdin.isatty():
            return
        self._running = True
        self._old_settings = termios.tcgetattr(sys.stdin)
        self._thread = threading.Thread(target=self._listen, daemon=True)
        self._thread.start()

    def _listen(self):
        try:
            tty.setcbreak(sys.stdin.fileno())
            while self._running:
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    ch = sys.stdin.read(1)
                    if ch == '\x1b':  # Escape sequence
                        if select.select([sys.stdin], [], [], 0.05)[0]:
                            ch2 = sys.stdin.read(1)
                            if ch2 in ('[', 'O'):
                                ch3 = sys.stdin.read(1)
                                if ch3 == 'A':
                                    self._queue.append('up')
                                elif ch3 == 'B':
                                    self._queue.append('down')
                                else:
                                    self._queue.append('esc')
                            else:
                                self._queue.append('esc')
                        else:
                            self._queue.append('esc')
                    elif ch == '\t':
                        self._queue.append('tab')
                    elif ch == '\n' or ch == '\r':
                        self._queue.append('enter')
                    elif ch == '?':
                        self._queue.append('?')
                    else:
                        self._queue.append(ch)
        except Exception:
            pass
        finally:
            if self._old_settings:
                try:
                    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_settings)
                except Exception:
                    pass

    def get_key(self):
        if self._queue:
            return self._queue.pop(0)
        return None

    def stop(self):
        self._running = False
        if self._old_settings:
            try:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, self._old_settings)
            except Exception:
                pass


# ---------------------------------------------------------------------------
# SubAgentRunner
# ---------------------------------------------------------------------------

class SubAgentRunner:
    """Manages state and execution tracking for an individual sub-agent."""

    def __init__(self, name, prompt, color, model="auto-gemini-3", mode="parallel",
                 demo_mode=False, team_name="default"):
        self.name = name
        self.prompt = prompt
        self.color = color
        self.model = model
        self.mode = mode  # parallel, serial, validator
        self.status = AgentStatus.PENDING.value
        self.log_file = f"logs/{name.lower().replace(' ', '_')}.log"
        self.last_log = ""
        self.is_running = False
        self.log_handle = None
        self.demo_mode = demo_mode
        self.start_time = None
        self.end_time = None
        self.msg_count = {"sent": 0, "recv": 0}
        self.backend_info = "-"
        self.team_name = team_name
        self.last_progress_at = time.time()
        self.last_heartbeat_at = 0.0
        self.retry_count = 0
        self.failure_reason = "pending"
        self.retryable = False
        self.stop_mode = "none"
        self.stop_requested_at = 0.0
        self.saw_completion_signal = False
        self.identity = AgentIdentity(
            name=name, team_name=team_name, color=color, model=model, mode=mode
        )

        os.makedirs("logs", exist_ok=True)

    def build_command(self):
        """Build the dispatch command with new CLI flags."""
        agent_id = f"{self.name.lower()}@{self.team_name}"
        cmd = [
            sys.executable, DISPATCH_SCRIPT,
            self.prompt,
            "--log-file", self.log_file,
            "--model", self.model,
            "--agent-id", agent_id,
            "--team-dir", STATE_DIR,
        ]
        if self.mode in ("serial", "validator"):
            cmd.append("--exit-on-idle")
        return cmd

    def run(self):
        """Run agent (threaded entry point for demo mode)."""
        self.is_running = True
        self.status = AgentStatus.RUNNING.value
        self.start_time = time.time()

        if self.demo_mode:
            self._run_demo()
        else:
            self._run_real()

        self.end_time = time.time()
        self.is_running = False
        if self.log_handle:
            self.log_handle.close()

    def _run_demo(self):
        """Simulates agent execution for TUI testing."""
        steps = [
            "Initializing agent context...",
            "Reading task_plan.md...",
            "Analyzing requirements...",
            "Thinking...",
            "Generating solution code...",
            "Writing to file...",
            "Verifying output...",
            "Finalizing..."
        ]

        for step in steps:
            self.last_log = step
            self.last_progress_at = time.time()
            time.sleep(random.uniform(0.5, 1.5))

        demo_fail_rate = 0.0
        env_fail_rate = os.environ.get("AG_SWARM_DEMO_FAIL_RATE")
        if env_fail_rate:
            try:
                demo_fail_rate = max(0.0, min(1.0, float(env_fail_rate)))
            except ValueError:
                demo_fail_rate = 0.0

        if random.random() >= demo_fail_rate:
            self.status = AgentStatus.COMPLETED.value
            self.last_log = "Task completed successfully."
        else:
            self.status = AgentStatus.FAILED.value
            self.last_log = "Error: Simulated failure."

    def _run_real(self):
        """Run via dispatch_agent.py subprocess (used when backend is not available)."""
        cmd = self.build_command()

        try:
            self.process = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

            while self.process.poll() is None:
                self._read_new_logs()
                time.sleep(0.1)

            self.status = (
                AgentStatus.COMPLETED.value
                if self.process.returncode == 0
                else AgentStatus.FAILED.value
            )
            self._read_new_logs()

        except Exception as e:
            self.status = AgentStatus.FAILED.value
            self.last_log = f"Error: {str(e)}"

    def _read_new_logs(self):
        """Poll the log file for the latest line."""
        if not self.log_handle:
            if os.path.exists(self.log_file):
                try:
                    self.log_handle = open(
                        self.log_file, 'r', encoding='utf-8', errors='replace'
                    )
                except Exception:
                    pass

        if self.log_handle:
            try:
                lines = self.log_handle.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    if last_line:
                        self.last_log = last_line
                        self.last_progress_at = time.time()
            except Exception:
                pass

    def get_duration(self):
        """Return elapsed time as a formatted string."""
        if self.start_time:
            end = self.end_time if self.end_time else time.time()
            return f"{end - self.start_time:.1f}s"
        return "-"


# ---------------------------------------------------------------------------
# TUI Render Functions
# ---------------------------------------------------------------------------

def render_dashboard(runners, spinner_idx, selected_idx, backend, show_help):
    """Render the main dashboard view with agent table, activity, and keybinds.

    Returns a Layout renderable.
    """
    spinner_char = SPINNERS[spinner_idx % len(SPINNERS)]

    # --- Header ---
    header = Panel(
        Align.center(
            "[bold magenta]✨ Antigravity Swarm Mission Control ✨[/bold magenta]"
        ),
        box=box.HEAVY,
        style="white on black",
    )

    # --- Agent Table ---
    table = Table(box=box.ROUNDED, expand=True, highlight=True)
    table.add_column("Agent", style="bold white")
    table.add_column("Role", style="dim")
    table.add_column("Status", justify="center")
    table.add_column("Time", justify="right")
    table.add_column("Msgs", justify="center")
    table.add_column("Backend", style="dim")

    active_log = "Waiting for agents..."
    active_agent = "System"

    for idx, runner in enumerate(runners):
        # Status display
        if runner.status == AgentStatus.RUNNING.value:
            status_style = "bold yellow"
            status_icon = spinner_char
            active_log = runner.last_log
            active_agent = runner.name
        elif runner.status == AgentStatus.COMPLETED.value:
            status_style = "bold green"
            status_icon = "✔"
        elif runner.status == AgentStatus.FAILED.value:
            status_style = "bold red"
            status_icon = "✘"
        elif runner.status == AgentStatus.IDLE.value:
            status_style = "bold blue"
            status_icon = "◉"
        elif runner.status == AgentStatus.SHUTDOWN.value:
            status_style = "dim"
            status_icon = "⏻"
        else:  # PENDING
            status_style = "dim"
            status_icon = "•"

        status_text = f"[{status_style}]{status_icon} {runner.status}[/{status_style}]"

        # Messages column
        msg_parts = []
        if runner.msg_count["sent"] > 0:
            msg_parts.append(f"{runner.msg_count['sent']}↑")
        if runner.msg_count["recv"] > 0:
            msg_parts.append(f"{runner.msg_count['recv']}↓")
        msg_text = " ".join(msg_parts) if msg_parts else "-"

        # Selection highlight
        name_prefix = "▶ " if idx == selected_idx else "● "
        name_style = "bold reverse" if idx == selected_idx else ""
        agent_name = f"[{runner.color}]{name_prefix}{runner.name}[/{runner.color}]"
        if idx == selected_idx:
            agent_name = f"[{name_style}]{agent_name}[/{name_style}]" if name_style else agent_name

        table.add_row(
            agent_name,
            runner.mode,
            status_text,
            runner.get_duration(),
            msg_text,
            runner.backend_info,
        )

    # --- Activity Panel ---
    log_content = Text()
    log_content.append(f"Agent: {active_agent}\n", style="bold cyan")
    log_content.append(f"Action: {active_log}", style="white")

    activity_panel = Panel(
        Align.center(log_content, vertical="middle"),
        title="Live Activity",
        border_style="blue",
        box=box.ROUNDED,
    )

    # --- Footer (keybinds) ---
    footer_text = Text.assemble(
        (" [Tab] ", "bold white on dark_blue"), ("View  ", "dim"),
        (" [w,s] ", "bold white on dark_blue"), ("Select  ", "dim"),
        (" [Enter] ", "bold white on dark_blue"), ("Detail  ", "dim"),
        (" [k] ", "bold white on dark_blue"), ("Kill  ", "dim"),
        (" [x] ", "bold white on dark_blue"), ("Shutdown  ", "dim"),
        (" [q] ", "bold white on dark_blue"), ("Quit  ", "dim"),
        (" [?] ", "bold white on dark_blue"), ("Help", "dim"),
    )
    footer = Panel(Align.center(footer_text), box=box.SIMPLE, style="dim")

    # --- Help Overlay ---
    if show_help:
        help_text = Text()
        help_text.append("Keyboard Controls\n\n", style="bold underline cyan")
        help_text.append("  Tab       ", style="bold white")
        help_text.append("Cycle views (Dashboard / Messages / Detail)\n", style="dim")
        help_text.append("  w / s      ", style="bold white")
        help_text.append("Navigate agent list\n", style="dim")
        help_text.append("  Enter     ", style="bold white")
        help_text.append("Show selected agent detail\n", style="dim")
        help_text.append("  k         ", style="bold white")
        help_text.append("Kill selected agent\n", style="dim")
        help_text.append("  x         ", style="bold white")
        help_text.append("Send shutdown request to selected agent\n", style="dim")
        help_text.append("  q         ", style="bold white")
        help_text.append("Quit (shutdown all agents)\n", style="dim")
        help_text.append("  Esc       ", style="bold white")
        help_text.append("Back to dashboard\n", style="dim")
        help_text.append("  ?         ", style="bold white")
        help_text.append("Toggle this help\n", style="dim")

        help_panel = Panel(
            Align.center(help_text, vertical="middle"),
            title="Help",
            border_style="bright_yellow",
            box=box.DOUBLE,
            width=60,
            height=16,
        )
        # Overlay: return help panel instead of full layout
        layout = Layout()
        layout.split_column(
            Layout(header, size=3),
            Layout(name="body"),
            Layout(footer, size=3),
        )
        layout["body"].split_row(
            Layout(table, ratio=2),
            Layout(help_panel, ratio=1),
        )
        return layout

    # --- Standard Layout ---
    layout = Layout()
    layout.split_column(
        Layout(header, size=3),
        Layout(name="body"),
        Layout(footer, size=3),
    )
    layout["body"].split_column(
        Layout(table, name="table", ratio=3),
        Layout(activity_panel, name="activity", size=5),
    )
    return layout


def render_messages_view(messages=None):
    """Render the messages view showing all inter-agent communication.

    Returns a Panel renderable.
    """
    if messages is None:
        messages = get_all_messages()

    content = Text()
    content.append("Inter-Agent Messages\n\n", style="bold underline cyan")

    if not messages:
        content.append("  No messages exchanged yet.\n", style="dim italic")
    else:
        for msg in messages[-50:]:  # Show last 50 messages
            ts = time.strftime("%H:%M:%S", time.localtime(msg.timestamp))
            content.append(f"  [{ts}] ", style="dim")
            content.append(f"{msg.sender}", style="bold cyan")
            content.append(" → ", style="dim")
            content.append(f"{msg.recipient}", style="bold green")
            content.append(f" ({msg.msg_type})", style="dim yellow")
            content.append(f"\n    {msg.content[:120]}\n\n", style="white")

    footer_hint = Text.assemble(
        ("\n [Tab] ", "bold white on dark_blue"), ("Next View  ", "dim"),
        (" [Esc] ", "bold white on dark_blue"), ("Dashboard", "dim"),
    )
    content.append_text(footer_hint)

    return Panel(
        content,
        title="Messages",
        border_style="green",
        box=box.ROUNDED,
    )


def read_log_tail(log_file, max_lines=20, max_bytes=65536):
    if not os.path.exists(log_file):
        return []

    try:
        with open(log_file, 'rb') as f:
            f.seek(0, os.SEEK_END)
            size = f.tell()
            read_size = min(size, max_bytes)
            f.seek(size - read_size, os.SEEK_SET)
            chunk = f.read(read_size)

        text = chunk.decode('utf-8', errors='replace')
        lines = text.splitlines()
        return lines[-max_lines:] if len(lines) > max_lines else lines
    except Exception:
        return []


def render_detail_view(runner, all_msgs=None, log_tail=None):
    """Render the detail view for a single agent.

    Shows identity, status, duration, log tail, and message history.
    Returns a Panel renderable.
    """
    content = Text()

    # -- Header info --
    content.append(f"Agent: {runner.name}\n", style=f"bold {runner.color}")
    content.append(f"  Status:   {runner.status}\n", style="white")
    content.append(f"  Mode:     {runner.mode}\n", style="dim")
    content.append(f"  Model:    {runner.model}\n", style="dim")
    content.append(f"  Duration: {runner.get_duration()}\n", style="white")
    content.append(f"  Backend:  {runner.backend_info}\n", style="dim")
    content.append(f"  Messages: {runner.msg_count['sent']} sent, "
                   f"{runner.msg_count['recv']} received\n", style="dim")
    content.append(f"  Agent ID: {runner.identity.agent_id}\n", style="dim")
    content.append("\n")

    # -- Log tail --
    content.append("Log Output (last 20 lines)\n", style="bold underline cyan")
    if os.path.exists(runner.log_file):
        if log_tail is None:
            log_tail = read_log_tail(runner.log_file, max_lines=20)
        if log_tail:
            for line in log_tail:
                content.append(f"  {line.rstrip()}\n", style="white")
        else:
            content.append("  [Could not read log file]\n", style="dim italic")
    else:
        content.append("  [No log file yet]\n", style="dim italic")

    content.append("\n")

    # -- Message history for this agent --
    content.append("Message History\n", style="bold underline cyan")
    if all_msgs is None:
        all_msgs = get_all_messages()
    agent_msgs = [
        m for m in all_msgs
        if m.sender == runner.name or m.recipient == runner.name
    ]
    if not agent_msgs:
        content.append("  [No messages]\n", style="dim italic")
    else:
        for msg in agent_msgs[-10:]:
            ts = time.strftime("%H:%M:%S", time.localtime(msg.timestamp))
            direction = "→" if msg.sender == runner.name else "←"
            other = msg.recipient if msg.sender == runner.name else msg.sender
            content.append(f"  [{ts}] {direction} {other}: ", style="dim")
            content.append(f"{msg.content[:100]}\n", style="white")

    footer_hint = Text.assemble(
        ("\n [Tab] ", "bold white on dark_blue"), ("Next View  ", "dim"),
        (" [Esc] ", "bold white on dark_blue"), ("Dashboard", "dim"),
    )
    content.append_text(footer_hint)

    return Panel(
        content,
        title=f"Agent Detail: {runner.name}",
        border_style=runner.color,
        box=box.ROUNDED,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    # Fix encoding (Windows CP949 / etc.)
    reconfigure = getattr(sys.stdout, 'reconfigure', None)
    if callable(reconfigure):
        reconfigure(encoding='utf-8')

    demo_mode = "--demo" in sys.argv
    resume_mode = "--resume" in sys.argv
    cleanup_stale_mode = "--cleanup-stale" in sys.argv

    mission_id_override = None
    if "--mission-id" in sys.argv:
        try:
            idx = sys.argv.index("--mission-id")
            mission_id_override = sys.argv[idx + 1] if idx + 1 < len(sys.argv) else None
        except Exception:
            mission_id_override = None

    if demo_mode:
        print("[Orchestrator] Running in DEMO MODE (Simulated Execution)")

    def fail_with_hook(stage, code, detail):
        print(f"[Orchestrator][Hook:{stage}] FAILED ({code})")
        print(f"  {detail}")
        sys.exit(1)

    def validate_config_data(data):
        errors = []
        if not isinstance(data, dict):
            return ["config_not_object"]
        subagents = data.get("subagents")
        if not isinstance(subagents, list) or not subagents:
            return ["missing_subagents"]

        has_validator = False
        for i, agent in enumerate(subagents):
            if not isinstance(agent, dict):
                errors.append(f"agent_{i}_not_object")
                continue
            for key in ("name", "prompt", "mode", "model"):
                if key not in agent:
                    errors.append(f"agent_{i}_missing_{key}")
            if agent.get("name") == "Quality_Validator":
                has_validator = True

            prompt = str(agent.get("prompt", ""))
            for section in REQUIRED_PROMPT_SECTIONS:
                if section not in prompt:
                    errors.append(f"agent_{i}_prompt_missing_section:{section}")

        if not has_validator:
            errors.append("missing_quality_validator")
        return errors

    # Load swarm config
    config = SwarmConfig.load()
    ensure_dirs()

    # Backend selection
    backend = get_backend(config)

    # Resume logic
    mission = None
    try:
        resume_stale_seconds = float(os.environ.get("AG_SWARM_RESUME_STALE_SECONDS", "1800"))
    except ValueError:
        resume_stale_seconds = 1800.0
    resume_stale_seconds = max(0.0, resume_stale_seconds)

    if resume_mode:
        mission = MissionState.load(mission_id_override) if mission_id_override else MissionState.latest()
        if not mission or not mission.is_resumable():
            print("[Orchestrator] No resumable mission found.")
            sys.exit(1)
        if mission.is_stale(resume_stale_seconds):
            mission.mark_failed("stale_resume_timeout")
            print("[Orchestrator] Latest mission is stale and was marked failed.")
            sys.exit(1)
        print(f"[Orchestrator] Resuming mission: {mission.description}")
        mission.attempt += 1
        mission.save()

    if cleanup_stale_mode:
        latest = MissionState.load(mission_id_override) if mission_id_override else MissionState.latest()
        if not latest:
            print("[Orchestrator] No mission found for stale cleanup.")
            return
        if latest.is_resumable() and latest.is_stale(resume_stale_seconds):
            latest.mark_failed("stale_cleanup")
            print(f"[Orchestrator] Marked stale mission as failed: {latest.mission_id}")
        else:
            print("[Orchestrator] No stale resumable mission to clean.")
        return

    # Read config file
    if not os.path.exists(CONFIG_FILE) and not demo_mode:
        fail_with_hook("PreRunValidation", "missing_config", f"{CONFIG_FILE} not found")

    if demo_mode:
        config_data = {
            'mission': 'Demo Swarm Mission',
            'subagents': [
                {'name': 'Architect', 'color': 'magenta', 'prompt': '', 'mode': 'parallel',
                 'model': 'gemini-2.5-pro'},
                {'name': 'Engineer', 'color': 'cyan', 'prompt': '', 'mode': 'parallel',
                 'model': 'gemini-2.5-flash'},
                {'name': 'Researcher', 'color': 'yellow', 'prompt': '', 'mode': 'parallel',
                 'model': 'gemini-2.5-pro'},
                {'name': 'Tester', 'color': 'green', 'prompt': '', 'mode': 'serial',
                 'model': 'gemini-2.5-flash'},
                {'name': 'Quality_Validator', 'color': 'bright_red', 'prompt': '', 'mode': 'validator',
                 'model': 'gemini-2.5-pro'},
            ]
        }
        manus_context = ""
    else:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)

        validation_errors = validate_config_data(config_data)
        if validation_errors:
            fail_with_hook(
                "PreRunValidation",
                "invalid_subagent_config",
                ", ".join(validation_errors[:8]),
            )

        # Manus Protocol: Context Injection
        manus_context = "\n\n[SHARED STATE]"
        for f_name in ["task_plan.md", "findings.md", "progress.md"]:
            if os.path.exists(f_name):
                with open(f_name, 'r', encoding='utf-8') as fh:
                    manus_context += f"\n--- {f_name} ---\n{fh.read()}"

        manus_context += "\n[END SHARED STATE]\n"
        manus_context += (
            "Instructions: Read shared state. "
            "Update findings.md/progress.md. "
            "Use <<SEND_MESSAGE>> and <<BROADCAST>> to communicate."
        )

    # Create mission state
    if not resume_mode or mission is None:
        mission = MissionState.create(
            config_data.get('mission', 'Swarm Mission')
        )
        mission.status = "running"

    team_name = mission.team_name if mission else "default"

    # Build runners categorised by execution mode
    runners = []
    parallel_runners = []
    serial_runners = []
    validator_runners = []

    for i, agent_cfg in enumerate(config_data.get('subagents', [])):
        full_prompt = agent_cfg.get('prompt', '') + manus_context
        name = agent_cfg['name']
        mode = agent_cfg.get('mode', 'parallel')
        color = agent_cfg.get('color', assign_color(i))

        if name == 'Quality_Validator':
            mode = 'validator'

        runner = SubAgentRunner(
            name=name,
            prompt=full_prompt,
            color=color,
            model=agent_cfg.get('model', config.default_model),
            mode=mode,
            demo_mode=demo_mode,
            team_name=team_name,
        )

        if mode == 'validator':
            validator_runners.append(runner)
        elif mode == 'serial':
            serial_runners.append(runner)
        else:
            parallel_runners.append(runner)

    runners = parallel_runners + serial_runners + validator_runners

    # Generate .swarm/config.json team config
    team_config = {
        "name": team_name,
        "created_at": time.time(),
        "leader": "leader",
        "members": [
            {
                "agent_id": f"{r.name.lower()}@{team_name}",
                "name": r.name,
                "color": r.color,
                "model": r.model,
                "mode": r.mode,
                "status": "pending",
            }
            for r in runners
        ],
        "settings": {
            "backend": backend.get_type(),
            "poll_interval_ms": config.poll_interval_ms,
        },
    }
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(os.path.join(STATE_DIR, "config.json"), 'w') as f:
        json.dump(team_config, f, indent=2)

    # Save mission agents
    mission.agents = [
        {"name": r.name, "mode": r.mode, "color": r.color, "status": "pending"}
        for r in runners
    ]
    mission.save()

    # Leader mailbox for receiving status updates
    leader_mailbox = Mailbox("leader")
    audit = AuditLog(mission.mission_id)

    # Print plan summary
    print()
    print(f"[Orchestrator] Mission: {mission.description}")
    print(f"[Orchestrator] Backend: {backend.get_type()}")
    print(f"[Orchestrator] Agents:  {len(runners)}")
    for r in runners:
        print(f"  ● {r.name} ({r.mode}, {r.model})")
    print()

    # Confirmation prompt
    if "--yes" not in sys.argv and not demo_mode:
        try:
            confirm = input("[Plan Mode] Execute this team? [y/N]: ").strip().lower()
            if confirm != 'y':
                print("[Orchestrator] Execution cancelled.")
                return
        except EOFError:
            print("[Orchestrator] No input stream. Assuming --yes.")

    # Start keyboard listener
    keyboard = KeyboardListener()
    keyboard.start()

    # TUI state
    current_view = ViewMode.DASHBOARD
    selected_idx = 0
    show_help = False
    quit_requested = False

    try:
        max_retries = int(os.environ.get("AG_SWARM_MAX_RETRIES", "1"))
    except ValueError:
        max_retries = 1
    max_retries = max(0, min(max_retries, 5))

    try:
        watchdog_timeout = float(os.environ.get("AG_SWARM_WATCHDOG_SECONDS", "90"))
    except ValueError:
        watchdog_timeout = 90.0
    watchdog_timeout = max(10.0, watchdog_timeout)

    try:
        retry_cooldown = float(os.environ.get("AG_SWARM_RETRY_COOLDOWN_SECONDS", "0.3"))
    except ValueError:
        retry_cooldown = 0.3
    retry_cooldown = max(0.0, retry_cooldown)

    try:
        hard_timeout_seconds = float(os.environ.get("AG_SWARM_HARD_TIMEOUT_SECONDS", "0"))
    except ValueError:
        hard_timeout_seconds = 0.0
    hard_timeout_seconds = max(0.0, hard_timeout_seconds)

    try:
        watchdog_grace = float(os.environ.get("AG_SWARM_WATCHDOG_GRACE_SECONDS", "15"))
    except ValueError:
        watchdog_grace = 15.0
    watchdog_grace = max(3.0, watchdog_grace)

    console = Console()

    def spawn_runner(r):
        if demo_mode:
            t = threading.Thread(target=r.run, daemon=True)
            t.start()
            r.backend_info = "demo"
            return t

        cmd = r.build_command()
        handle = backend.spawn(r.name, cmd, r.color)
        r.backend_info = (
            f"{backend.get_type()} {handle}" if handle else backend.get_type()
        )
        r.is_running = True
        r.status = AgentStatus.RUNNING.value
        r.start_time = time.time()
        r.last_progress_at = time.time()
        r.last_heartbeat_at = 0.0
        r.failure_reason = ""
        r.retryable = False
        r.stop_mode = "none"
        r.stop_requested_at = 0.0
        r.saw_completion_signal = False
        audit.record(
            r.name,
            "spawned",
            f"mode={r.mode}",
            {"backend": backend.get_type(), "retry": r.retry_count},
        )
        mission.update_agent_status(r.name, AgentStatus.RUNNING.value)
        return handle

    def maybe_retry_runner(r):
        if quit_requested or demo_mode:
            return False
        if r.status != AgentStatus.FAILED.value:
            return False
        if not r.retryable:
            return False
        if r.retry_count >= max_retries:
            return False

        liveness_cache.pop(r.name, None)
        try:
            backend.kill(r.name)
        except Exception:
            pass

        r.retry_count += 1
        time.sleep(retry_cooldown)
        audit.record(
            r.name,
            "status_change",
            "retrying",
            {"attempt": r.retry_count, "reason": r.failure_reason},
        )
        spawn_runner(r)
        return True

    def apply_watchdog(active_runners):
        if demo_mode:
            return
        now = time.time()
        for r in active_runners:
            if not r.is_running:
                continue
            if r.mode in ("serial", "validator"):
                continue
            idle_for = now - r.last_progress_at
            if idle_for >= watchdog_timeout:
                if r.stop_mode == "watchdog_soft_shutdown":
                    if now - r.stop_requested_at >= watchdog_grace:
                        r.is_running = False
                        r.end_time = now
                        r.status = AgentStatus.FAILED.value
                        r.failure_reason = "watchdog_timeout"
                        r.retryable = True
                        audit.record(
                            r.name,
                            "error",
                            "watchdog_no_progress_timeout",
                            {"idle_seconds": round(idle_for, 2), "failure_class": "timeout_error"},
                        )
                        mission.update_agent_status(r.name, r.status)
                    continue

                r.stop_mode = "watchdog_soft_shutdown"
                r.stop_requested_at = now
                try:
                    leader_mailbox.send(
                        r.name,
                        MessageType.SHUTDOWN_REQUEST,
                        "No progress detected. Please shutdown gracefully.",
                    )
                except Exception:
                    pass
                audit.record(
                    r.name,
                    "warning",
                    "watchdog_soft_shutdown_requested",
                    {"idle_seconds": round(idle_for, 2)},
                )

    def enforce_hard_timeout():
        nonlocal quit_requested
        if hard_timeout_seconds <= 0:
            return False
        elapsed = time.time() - mission.started_at
        if elapsed < hard_timeout_seconds:
            return False

        quit_requested = True
        mission.failure_reason = "hard_timeout"
        now = time.time()
        for r in runners:
            if r.is_running:
                r.is_running = False
                r.end_time = now
                r.status = AgentStatus.FAILED.value
                r.failure_reason = "hard_timeout"
                r.retryable = False
                r.stop_mode = "hard_timeout"
                mission.update_agent_status(r.name, r.status)

        audit.record(
            "orchestrator",
            "error",
            "mission_hard_timeout",
            {
                "elapsed_seconds": round(elapsed, 2),
                "failure_class": "timeout_error",
            },
        )
        return True

    try:
        with Live(console=console, refresh_per_second=config.tui_refresh_rate) as live:
            spinner_idx = 0

            messages_cache = {"ts": 0.0, "items": []}
            log_tail_cache = {}
            liveness_cache = {}
            view_refresh_cache = {"messages": 0.0, "detail": 0.0}

            def invalidate_messages_cache():
                messages_cache["ts"] = 0.0

            def get_cached_messages(force=False):
                now = time.time()
                ttl = 0.25 if current_view == ViewMode.MESSAGES else 0.5
                if force or (now - messages_cache["ts"] >= ttl):
                    messages_cache["items"] = get_all_messages()
                    messages_cache["ts"] = now
                return messages_cache["items"]

            def get_cached_log_tail(runner):
                now = time.time()
                ttl = 0.25 if current_view == ViewMode.DETAIL else 0.5
                entry = log_tail_cache.get(runner.name)
                if not os.path.exists(runner.log_file):
                    log_tail_cache[runner.name] = {
                        "mtime": None, "size": 0, "ts": now, "tail": []
                    }
                    return []

                try:
                    st = os.stat(runner.log_file)
                    mtime_ns = st.st_mtime_ns
                    size = st.st_size
                except OSError:
                    return []

                if (
                    entry
                    and entry["mtime"] == mtime_ns
                    and entry["size"] == size
                    and (now - entry["ts"]) < ttl
                ):
                    return entry["tail"]

                tail = read_log_tail(runner.log_file, max_lines=20)
                log_tail_cache[runner.name] = {
                    "mtime": mtime_ns,
                    "size": size,
                    "ts": now,
                    "tail": tail,
                }
                return tail

            def update_ui(force_data_refresh=False):
                nonlocal spinner_idx
                if current_view == ViewMode.DASHBOARD:
                    content = render_dashboard(
                        runners, spinner_idx, selected_idx, backend, show_help
                    )
                elif current_view == ViewMode.MESSAGES:
                    now = time.time()
                    if force_data_refresh or (now - view_refresh_cache["messages"] >= 0.25):
                        msg_items = get_cached_messages(force=force_data_refresh)
                        content = render_messages_view(msg_items)
                        view_refresh_cache["messages"] = now
                        live.update(content)
                    spinner_idx += 1
                    return
                elif current_view == ViewMode.DETAIL:
                    if 0 <= selected_idx < len(runners):
                        now = time.time()
                        if force_data_refresh or (now - view_refresh_cache["detail"] >= 0.25):
                            selected_runner = runners[selected_idx]
                            msg_items = get_cached_messages(force=force_data_refresh)
                            log_tail = get_cached_log_tail(selected_runner)
                            content = render_detail_view(selected_runner, msg_items, log_tail)
                            view_refresh_cache["detail"] = now
                            live.update(content)
                        spinner_idx += 1
                        return
                    else:
                        content = render_dashboard(
                            runners, spinner_idx, selected_idx, backend, show_help
                        )
                else:
                    content = render_dashboard(
                        runners, spinner_idx, selected_idx, backend, show_help
                    )
                live.update(content)
                spinner_idx += 1

            def handle_keyboard():
                nonlocal current_view, selected_idx, show_help, quit_requested
                key = keyboard.get_key()
                if not key:
                    return False  # No quit

                if key == 'q':
                    quit_requested = True
                    return True  # Quit
                elif key == 'tab':
                    current_view = (current_view + 1) % 3
                elif key == 'esc':
                    current_view = ViewMode.DASHBOARD
                    show_help = False
                elif key == 'up' or key == 'w':
                    selected_idx = max(0, selected_idx - 1)
                elif key == 'down' or key == 's' or key == 'j':
                    selected_idx = min(len(runners) - 1, selected_idx + 1)
                elif key == 'enter':
                    current_view = ViewMode.DETAIL
                elif key == 'k':
                    # Kill selected agent
                    if 0 <= selected_idx < len(runners):
                        r = runners[selected_idx]
                        if r.is_running:
                            if not demo_mode:
                                backend.kill(r.name)
                            r.status = AgentStatus.SHUTDOWN.value
                            r.is_running = False
                            r.end_time = time.time()
                            r.stop_mode = "force_kill"
                            r.failure_reason = "killed_by_user"
                            r.retryable = False
                            audit.record(r.name, "shutdown", "Killed by user")
                            mission.update_agent_status(r.name, AgentStatus.SHUTDOWN.value)
                elif key == 'x':
                    # Send shutdown request
                    if 0 <= selected_idx < len(runners):
                        r = runners[selected_idx]
                        if r.is_running:
                            leader_mailbox.send(
                                r.name, MessageType.SHUTDOWN_REQUEST,
                                "Shutdown requested by orchestrator."
                            )
                            r.stop_mode = "graceful_shutdown"
                            r.stop_requested_at = time.time()
                            r.retryable = False
                            audit.record(r.name, "shutdown", "Shutdown request sent")
                elif key == '?':
                    show_help = not show_help

                return False

            def poll_leader_inbox():
                """Check leader mailbox for agent status updates."""
                changed = False
                for msg in leader_mailbox.poll():
                    changed = True
                    for r in runners:
                        if r.name == msg.sender or r.name.lower() == msg.sender:
                            r.msg_count["recv"] += 1
                            r.last_progress_at = time.time()
                            if msg.msg_type == MessageType.STATUS_UPDATE.value:
                                if msg.content:
                                    r.last_log = msg.content[:120]
                                if "__AGENT_COMPLETED__" in (msg.content or ""):
                                    r.saw_completion_signal = True
                            if msg.msg_type == MessageType.SHUTDOWN_RESPONSE.value:
                                r.status = AgentStatus.SHUTDOWN.value
                                r.is_running = False
                                r.retryable = False
                                r.end_time = time.time()
                                mission.update_agent_status(r.name, r.status)
                                audit.record(r.name, "status_change", r.status)
                                continue
                            if msg.content:
                                r.last_log = msg.content[:80]
                if changed:
                    invalidate_messages_cache()

            def check_backend_alive_many(active_runners):
                if demo_mode:
                    return

                now = time.time()
                interval = 0.5 if backend.get_type() == "tmux" else 0.2
                to_probe = []

                for r in active_runners:
                    if not r.is_running:
                        continue
                    entry = liveness_cache.get(r.name)
                    if not entry or (now - entry["ts"] >= interval):
                        to_probe.append(r.name)

                if to_probe:
                    alive_map = backend.is_alive_many(to_probe)
                    for name in to_probe:
                        liveness_cache[name] = {
                            "ts": now,
                            "alive": bool(alive_map.get(name, False)),
                        }

                for r in active_runners:
                    if not r.is_running:
                        continue
                    entry = liveness_cache.get(r.name)
                    if entry and not entry["alive"]:
                        r.is_running = False
                        r.end_time = time.time()
                        rc = backend.get_return_code(r.name)
                        if rc == 0:
                            r.status = AgentStatus.COMPLETED.value
                            r.failure_reason = ""
                            r.retryable = False
                        elif rc is None:
                            if r.saw_completion_signal:
                                r.status = AgentStatus.COMPLETED.value
                                r.failure_reason = ""
                                r.retryable = False
                            else:
                                r.status = AgentStatus.FAILED.value
                                r.failure_reason = "backend_dead_unknown_rc"
                                r.retryable = r.stop_mode not in ("force_kill", "graceful_shutdown", "watchdog_soft_shutdown")
                        else:
                            r.status = AgentStatus.FAILED.value
                            r.failure_reason = f"process_exit_{rc}"
                            r.retryable = r.stop_mode not in ("force_kill", "graceful_shutdown", "watchdog_soft_shutdown")
                        audit.record(r.name, "status_change", r.status)
                        mission.update_agent_status(r.name, r.status)

            # =============================================================
            # Phase 1: Parallel Agents
            # =============================================================
            demo_threads = []
            for r in parallel_runners:
                handle = spawn_runner(r)
                if demo_mode:
                    t = handle
                    demo_threads.append(t)

            while not quit_requested:
                # Check if all parallel runners are done
                if demo_mode:
                    all_done = not any(
                        r.is_running for r in parallel_runners
                    )
                else:
                    check_backend_alive_many(parallel_runners)
                    for r in parallel_runners:
                        r._read_new_logs()
                    apply_watchdog(parallel_runners)
                    for r in parallel_runners:
                        if not r.is_running:
                            maybe_retry_runner(r)
                    all_done = not any(
                        r.is_running for r in parallel_runners
                    )

                poll_leader_inbox()
                if enforce_hard_timeout():
                    break
                if handle_keyboard():
                    break
                update_ui(force_data_refresh=False)

                if all_done:
                    break
                time.sleep(0.1)

            if quit_requested:
                raise KeyboardInterrupt

            # =============================================================
            # Phase 2: Serial Agents
            # =============================================================
            for r in serial_runners:
                if quit_requested:
                    break

                if demo_mode:
                    spawn_runner(r)
                else:
                    spawn_runner(r)

                while not quit_requested:
                    if demo_mode:
                        if not r.is_running:
                            break
                    else:
                        check_backend_alive_many([r])
                        r._read_new_logs()
                        apply_watchdog([r])
                        if not r.is_running and maybe_retry_runner(r):
                            continue
                        if not r.is_running:
                            break

                    poll_leader_inbox()
                    if enforce_hard_timeout():
                        break
                    if handle_keyboard():
                        break
                    update_ui(force_data_refresh=False)
                    time.sleep(0.1)

            if quit_requested:
                raise KeyboardInterrupt

            # =============================================================
            # Phase 3: Validator Agents
            # =============================================================
            for r in validator_runners:
                if quit_requested:
                    break

                if demo_mode:
                    spawn_runner(r)
                else:
                    spawn_runner(r)

                while not quit_requested:
                    if demo_mode:
                        if not r.is_running:
                            break
                    else:
                        check_backend_alive_many([r])
                        r._read_new_logs()
                        apply_watchdog([r])
                        if not r.is_running and maybe_retry_runner(r):
                            continue
                        if not r.is_running:
                            break

                    poll_leader_inbox()
                    if enforce_hard_timeout():
                        break
                    if handle_keyboard():
                        break
                    update_ui(force_data_refresh=False)
                    time.sleep(0.1)

            if quit_requested:
                raise KeyboardInterrupt

            # Final UI update
            update_ui()
            time.sleep(1)

    except KeyboardInterrupt:
        pass  # Graceful exit

    finally:
        keyboard.stop()
        for r in runners:
            if r.is_running:
                if r.stop_mode == "none":
                    r.stop_mode = "graceful_shutdown"
                    r.stop_requested_at = time.time()
                try:
                    leader_mailbox.send(
                        r.name,
                        MessageType.SHUTDOWN_REQUEST,
                        "Shutdown requested by orchestrator cleanup.",
                    )
                except Exception:
                    pass

        if not demo_mode:
            for r in runners:
                if r.is_running:
                    try:
                        backend.kill(r.name)
                    except Exception:
                        pass
            backend.cleanup()

        # Update mission state
        failed_runners = [
            r for r in runners if r.status != AgentStatus.COMPLETED.value
        ]
        mission.status = "completed" if not failed_runners else "failed"
        mission.ended_at = time.time()
        if failed_runners and not mission.failure_reason:
            mission.failure_reason = "runtime_failed"
        mission.save()

        # Generate post-mission report
        try:
            generate_report(mission.mission_id)
        except Exception:
            pass  # Don't crash on report generation failure

    # Exit code
    failed_runners = [
        r for r in runners if r.status != AgentStatus.COMPLETED.value
    ]
    if failed_runners:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
