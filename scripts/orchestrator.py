import yaml
import sys
import subprocess
import threading
import time
import os
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn

# Configuration
CONFIG_FILE = "subagents.yaml"
# Resolve dispatch_agent.py relative to this script's location
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DISPATCH_SCRIPT = os.path.join(SCRIPT_DIR, "dispatch_agent.py")

class SubAgentRunner:
    def __init__(self, name, prompt, color, model="auto-gemini-3"):
        self.name = name
        self.prompt = prompt
        self.color = color
        self.model = model
        self.status = "Pending"
        self.log_file = f"logs/{name.lower().replace(' ', '_')}.log"
        self.last_log = ""
        self.is_running = False
        self.log_handle = None
        
        # Ensure log dir exists
        os.makedirs("logs", exist_ok=True)

    def run(self):
        self.is_running = True
        self.status = "Starting..."
        
        # Launch dispatch_agent.py with --log-file and --model
        cmd = [
            sys.executable, 
            DISPATCH_SCRIPT, 
            self.prompt,
            "--log-file", 
            self.log_file,
            "--model",
            self.model
        ]
        
        try:
            # We don't capture stdout here because dispatch_agent.py handles logging to file
            # But we wait for it to finish
            self.process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.status = "Running"
            
            while self.process.poll() is None:
                # Update last log line
                self._read_new_logs()
                time.sleep(0.1)
                
            self.status = "Completed" if self.process.returncode == 0 else "Failed"
            self._read_new_logs() # Final read
            
        except Exception as e:
            self.status = f"Error: {str(e)}"
        finally:
            self.is_running = False
            if self.log_handle:
                self.log_handle.close()

    def _read_new_logs(self):
        # Open handle if not already open
        if not self.log_handle:
            if os.path.exists(self.log_file):
                try:
                    self.log_handle = open(self.log_file, 'r', encoding='utf-8', errors='replace')
                except:
                    pass
        
        # Read available lines
        if self.log_handle:
            try:
                lines = self.log_handle.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    if last_line:
                        self.last_log = last_line
            except:
                pass

def generate_table(runners):
    table = Table(title="Antigravity Sub-Agents Orchestrator", expand=True)
    table.add_column("Agent", style="bold white")
    table.add_column("Status", style="dim")
    table.add_column("Latest Activity", style="italic")

    for runner in runners:
        status_style = "green" if runner.status == "Completed" else "yellow" if runner.status == "Running" else "red" if "Error" in runner.status else "white"
        
        # Add spinner if running
        status_text = runner.status
        if runner.status == "Running":
            status_text = f"🔄 {runner.status}"
        elif runner.status == "Completed":
            status_text = f"✅ {runner.status}"
            
        table.add_row(
            f"[{runner.color}]{runner.name}[/{runner.color}]", 
            f"[{status_style}]{status_text}[/{status_style}]", 
            runner.last_log[-50:] if len(runner.last_log) > 50 else runner.last_log
        )
    return table

def main():
    # Fix for Windows CP949 encoding issue
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    if not os.path.exists(CONFIG_FILE):
        print(f"Error: {CONFIG_FILE} not found.")
        return

    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Manus Protocol: Context Injection
    manus_context = "\n\n[SHARED STATE]"
    if os.path.exists("task_plan.md"):
        with open("task_plan.md", 'r', encoding='utf-8') as f:
            manus_context += f"\n--- task_plan.md ---\n{f.read()}"
    if os.path.exists("findings.md"):
        with open("findings.md", 'r', encoding='utf-8') as f:
            manus_context += f"\n--- findings.md ---\n{f.read()}"
    if os.path.exists("progress.md"):
        with open("progress.md", 'r', encoding='utf-8') as f:
            manus_context += f"\n--- progress.md ---\n{f.read()}"
    
    manus_context += "\n[END SHARED STATE]\n"
    manus_context += "Instructions: You must read the shared state above. Update 'findings.md' with new discoveries and 'progress.md' with your status using <<WRITE_FILE>>."

    runners = []
    for agent_cfg in config.get('subagents', []):
        # Inject Manus Context into prompt
        full_prompt = agent_cfg['prompt'] + manus_context
        
        runners.append(SubAgentRunner(
            agent_cfg['name'], 
            full_prompt, 
            agent_cfg.get('color', 'white'),
            agent_cfg.get('model', 'auto-gemini-3')
        ))

    # Plan Mode: Show summary before running
    print("\n[Orchestrator] Team Plan:")
    print(f"{'Name':<20} {'Model':<20} {'Color':<10}")
    print("-" * 50)
    for runner in runners:
        print(f"{runner.name:<20} {runner.model:<20} {runner.color:<10}")
    print("-" * 50)
    print(f"[Orchestrator] Context Injection: Included {len(manus_context)} bytes of shared state (task_plan, findings, progress).")

    if "--yes" not in sys.argv:
        try:
            confirm = input("\n[Plan Mode] Execute this team? [y/N]: ").strip().lower()
            if confirm != 'y':
                print("[Orchestrator] Execution cancelled.")
                return
        except EOFError:
            # Handle background execution without input stream
            print("[Orchestrator] No input stream detected. Assuming --yes for background execution.")

    print("\n[Orchestrator] Starting agents...")

    console = Console()
    
    # Start threads
    threads = []
    for runner in runners:
        t = threading.Thread(target=runner.run)
        t.start()
        threads.append(t)

    # Live UI
    with Live(generate_table(runners), refresh_per_second=4, console=console) as live:
        while any(t.is_alive() for t in threads):
            live.update(generate_table(runners))
            time.sleep(0.25)
        
        # Final update
        live.update(generate_table(runners))
 
    print("\nAll agents have finished.")

if __name__ == "__main__":
    main()
