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
from scripts.core.types import AgentStatus, AgentIdentity, assign_color
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
                            if ch2 == '[':
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
            time.sleep(random.uniform(0.5, 1.5))

        # 90% chance of success, 10% failure for demo realism
        if random.random() > 0.1:
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
        (" [↑↓] ", "bold white on dark_blue"), ("Select  ", "dim"),
        (" [Enter] ", "bold white on dark_blue"), ("Detail  ", "dim"),
        (" [k] ", "bold white on dark_blue"), ("Kill  ", "dim"),
        (" [s] ", "bold white on dark_blue"), ("Shutdown  ", "dim"),
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
        help_text.append("  ↑ / ↓     ", style="bold white")
        help_text.append("Navigate agent list\n", style="dim")
        help_text.append("  Enter     ", style="bold white")
        help_text.append("Show selected agent detail\n", style="dim")
        help_text.append("  k         ", style="bold white")
        help_text.append("Kill selected agent\n", style="dim")
        help_text.append("  s         ", style="bold white")
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


def render_messages_view():
    """Render the messages view showing all inter-agent communication.

    Returns a Panel renderable.
    """
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


def render_detail_view(runner):
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
        try:
            with open(runner.log_file, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()
            tail = lines[-20:] if len(lines) > 20 else lines
            for line in tail:
                content.append(f"  {line.rstrip()}\n", style="white")
        except Exception:
            content.append("  [Could not read log file]\n", style="dim italic")
    else:
        content.append("  [No log file yet]\n", style="dim italic")

    content.append("\n")

    # -- Message history for this agent --
    content.append("Message History\n", style="bold underline cyan")
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
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    demo_mode = "--demo" in sys.argv
    resume_mode = "--resume" in sys.argv

    if demo_mode:
        print("[Orchestrator] Running in DEMO MODE (Simulated Execution)")

    # Load swarm config
    config = SwarmConfig.load()
    ensure_dirs()

    # Backend selection
    backend = get_backend(config)

    # Resume logic
    mission = None
    if resume_mode:
        mission = MissionState.latest()
        if not mission or not mission.is_resumable():
            print("[Orchestrator] No resumable mission found.")
            sys.exit(1)
        print(f"[Orchestrator] Resuming mission: {mission.description}")
        mission.attempt += 1
        mission.save()

    # Read config file
    if not os.path.exists(CONFIG_FILE) and not demo_mode:
        print(f"Error: {CONFIG_FILE} not found.")
        sys.exit(1)

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

    console = Console()

    try:
        with Live(console=console, refresh_per_second=config.tui_refresh_rate) as live:
            spinner_idx = 0

            def update_ui():
                nonlocal spinner_idx
                if current_view == ViewMode.DASHBOARD:
                    content = render_dashboard(
                        runners, spinner_idx, selected_idx, backend, show_help
                    )
                elif current_view == ViewMode.MESSAGES:
                    content = render_messages_view()
                elif current_view == ViewMode.DETAIL:
                    if 0 <= selected_idx < len(runners):
                        content = render_detail_view(runners[selected_idx])
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
                elif key == 'up':
                    selected_idx = max(0, selected_idx - 1)
                elif key == 'down':
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
                            r.status = AgentStatus.FAILED.value
                            r.is_running = False
                            r.end_time = time.time()
                            audit.record(r.name, "shutdown", "Killed by user")
                            mission.update_agent_status(r.name, AgentStatus.FAILED.value)
                elif key == 's':
                    # Send shutdown request
                    if 0 <= selected_idx < len(runners):
                        r = runners[selected_idx]
                        if r.is_running:
                            leader_mailbox.send(
                                r.name, "shutdown_request",
                                "Shutdown requested by orchestrator."
                            )
                            audit.record(r.name, "shutdown", "Shutdown request sent")
                elif key == '?':
                    show_help = not show_help

                return False

            def poll_leader_inbox():
                """Check leader mailbox for agent status updates."""
                for msg in leader_mailbox.poll():
                    for r in runners:
                        if r.name == msg.sender or r.name.lower() == msg.sender:
                            r.msg_count["recv"] += 1
                            if msg.content:
                                r.last_log = msg.content[:80]

            def check_backend_alive(r):
                """Check if a non-demo runner's backend process is still alive."""
                if r.is_running and not demo_mode:
                    if not backend.is_alive(r.name):
                        r.is_running = False
                        r.end_time = time.time()
                        if hasattr(backend, 'get_return_code'):
                            rc = backend.get_return_code(r.name)
                            r.status = (
                                AgentStatus.COMPLETED.value
                                if rc == 0
                                else AgentStatus.FAILED.value
                            )
                        else:
                            r.status = AgentStatus.COMPLETED.value
                        audit.record(r.name, "status_change", r.status)
                        mission.update_agent_status(r.name, r.status)

            # =============================================================
            # Phase 1: Parallel Agents
            # =============================================================
            demo_threads = []
            for r in parallel_runners:
                if demo_mode:
                    t = threading.Thread(target=r.run, daemon=True)
                    t.start()
                    demo_threads.append(t)
                    r.backend_info = "demo"
                else:
                    cmd = r.build_command()
                    handle = backend.spawn(r.name, cmd, r.color)
                    r.backend_info = (
                        f"{backend.get_type()} {handle}" if handle else backend.get_type()
                    )
                    r.is_running = True
                    r.status = AgentStatus.RUNNING.value
                    r.start_time = time.time()
                    audit.record(
                        r.name, "spawned",
                        f"mode={r.mode}",
                        {"backend": backend.get_type()},
                    )

            while not quit_requested:
                # Check if all parallel runners are done
                if demo_mode:
                    all_done = not any(
                        r.is_running for r in parallel_runners
                    )
                else:
                    for r in parallel_runners:
                        check_backend_alive(r)
                        r._read_new_logs()
                    all_done = not any(
                        r.is_running for r in parallel_runners
                    )

                poll_leader_inbox()
                if handle_keyboard():
                    break
                update_ui()

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
                    t = threading.Thread(target=r.run, daemon=True)
                    t.start()
                    r.backend_info = "demo"
                else:
                    cmd = r.build_command()
                    handle = backend.spawn(r.name, cmd, r.color)
                    r.backend_info = (
                        f"{backend.get_type()} {handle}" if handle else backend.get_type()
                    )
                    r.is_running = True
                    r.status = AgentStatus.RUNNING.value
                    r.start_time = time.time()
                    audit.record(
                        r.name, "spawned",
                        f"mode=serial",
                        {"backend": backend.get_type()},
                    )

                while not quit_requested:
                    if demo_mode:
                        if not r.is_running:
                            break
                    else:
                        check_backend_alive(r)
                        r._read_new_logs()
                        if not r.is_running:
                            break

                    poll_leader_inbox()
                    if handle_keyboard():
                        break
                    update_ui()
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
                    t = threading.Thread(target=r.run, daemon=True)
                    t.start()
                    r.backend_info = "demo"
                else:
                    cmd = r.build_command()
                    handle = backend.spawn(r.name, cmd, r.color)
                    r.backend_info = (
                        f"{backend.get_type()} {handle}" if handle else backend.get_type()
                    )
                    r.is_running = True
                    r.status = AgentStatus.RUNNING.value
                    r.start_time = time.time()
                    audit.record(
                        r.name, "spawned",
                        f"mode=validator",
                        {"backend": backend.get_type()},
                    )

                while not quit_requested:
                    if demo_mode:
                        if not r.is_running:
                            break
                    else:
                        check_backend_alive(r)
                        r._read_new_logs()
                        if not r.is_running:
                            break

                    poll_leader_inbox()
                    if handle_keyboard():
                        break
                    update_ui()
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
        if not demo_mode:
            backend.cleanup()

        # Update mission state
        failed_runners = [
            r for r in runners if r.status != AgentStatus.COMPLETED.value
        ]
        mission.status = "completed" if not failed_runners else "failed"
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
