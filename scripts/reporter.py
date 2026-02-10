import sys
import os
import time

# Add parent dir to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.core.audit import AuditLog
from scripts.core.mission import MissionState

def format_duration(seconds):
    if seconds < 60:
        return f"{seconds:.1f}s"
    minutes = int(seconds // 60)
    secs = seconds % 60
    return f"{minutes}m {secs:.0f}s"

def generate_report(mission_id=None):
    """Generate a post-mission summary report."""
    # Load mission
    if mission_id:
        mission = MissionState.load(mission_id)
    else:
        mission = MissionState.latest()

    if not mission:
        print("[Reporter] No mission found.")
        return

    # Load audit
    audit = AuditLog(mission.mission_id)
    summary = audit.get_summary()

    # Calculate duration
    duration = time.time() - mission.started_at

    # Count agent results
    completed = sum(1 for a in mission.agents if a.get("status") == "completed")
    failed = sum(1 for a in mission.agents if a.get("status") == "failed")
    total = len(mission.agents)

    # Print report
    print()
    print("=" * 60)
    print("          Swarm Mission Report")
    print("=" * 60)
    print(f"  Mission:  {mission.description}")
    print(f"  Status:   {mission.status}")
    print(f"  Duration: {format_duration(duration)}")
    print(f"  Agents:   {total} ({completed} succeeded, {failed} failed)")
    print(f"  Attempts: {mission.attempt}")
    print()

    # Agent breakdown
    if summary["agents"]:
        print("  Agent Breakdown:")
        for agent_name, stats in summary["agents"].items():
            agent_info = next((a for a in mission.agents if a.get("name") == agent_name), {})
            mode = agent_info.get("mode", "?")
            status_icon = "✔" if agent_info.get("status") == "completed" else "✘"
            print(f"    {status_icon} {agent_name:<16} ({mode:<9}) "
                  f"{stats['file_writes']} writes, {stats['commands']} cmds, {stats['messages']} msgs")

    print()

    # Files and commands
    if summary["files_modified"]:
        print(f"  Files Modified: {', '.join(summary['files_modified'])}")
    print(f"  Commands Run: {summary['commands_run']}")
    print(f"  Messages Exchanged: {summary['messages_sent']}")

    if summary["errors"]:
        print(f"  Errors: {summary['errors']}")

    print(f"  Audit Trail: {audit.log_file}")
    print("=" * 60)
    print()

def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')

    mission_id = sys.argv[1] if len(sys.argv) > 1 else None
    generate_report(mission_id)

if __name__ == "__main__":
    main()
