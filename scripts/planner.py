import sys
import subprocess
import re
import os

import shutil

CONFIG_FILE = "subagents.yaml"

def get_gemini_path():
    # 1. Check env var
    path = os.environ.get("GEMINI_PATH")
    if path and os.path.isfile(path) and os.access(path, os.X_OK):
        return path
    
    # 2. Check system PATH
    path = shutil.which("gemini")
    if path:
        return path
        
    return None

def generate_prompt(mission):
    return f"""
You are a Principal Software Architect and Team Lead.
Your goal is to hire a squad of specialized sub-agents to complete the following mission:
"{mission}"

Rules for hiring:
1. Identify 2-5 distinct roles needed (e.g., specific coders, reviewers, designers).
2. For each role, define a clear, specialized system prompt.
3. Assign a unique color (green, yellow, blue, magenta, cyan, red) to each agent.
4. Assign a suitable model:
   - Use 'gemini-3-flash-preview' for standard tasks, speed, and coding.
   - Use 'gemini-3-pro-preview' for complex reasoning or creative writing.
5. [CRITICAL] The FINAL agent in the list MUST be a 'Quality_Validator'.
   - Role: Verify all work done by previous agents.
   - Responsibilities: Check file existence, validate code syntax (if applicable), and ensure the mission goal is met.
6. Output the team configuration in YAML format.

Output Format:
Please output ONE single YAML block enclosed in tripple backticks (```yaml).
The YAML must follow this exact structure:

subagents:
  - name: "Agent-Name"
    description: "Short description of role"
    color: "color_name"
    model: "gemini-model-name"
    prompt: |
      You are [Role].
      [Detailed instructions...]

Do not include any other text outside the YAML block.
"""

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/planner.py <mission_description>")
        sys.exit(1)

    mission = " ".join(sys.argv[1:])
    print(f"[Planner] Analyzing mission: '{mission}'...")
    print("[Planner] Consulting with Supervisor Agent...")

    gemini_path = get_gemini_path()
    if not gemini_path:
        print("Error: 'gemini' executable not found.")
        print("Please resolve this by:\n1. Installing gemini CLI.\n2. Ensuring it is in your PATH.\n3. Or setting GEMINI_PATH environment variable.")
        sys.exit(1)

    full_prompt = generate_prompt(mission)

    try:
        # Call gemini to generate layout
        process = subprocess.run(
            [gemini_path, "chat", full_prompt],
            capture_output=True,
            text=True
        )
        
        output = process.stdout
        
        # Extract YAML block
        yaml_match = re.search(r"```yaml\n(.*?)\n```", output, re.DOTALL)
        
        # Extract Plan block
        plan_match = re.search(r"\[PLAN\]\n(.*?)\n\[/PLAN\]", output, re.DOTALL)
        
        if yaml_match:
            yaml_content = yaml_match.group(1)
            plan_content = plan_match.group(1).strip() if plan_match else "# Task Plan (Auto-Generated)\n- [ ] Review Mission"
            
            # Plan Mode (Confirmation)
            print("\n[Planner] Proposed Plan:")
            print("------------------------------------------")
            print("[1] TASK PLAN (task_plan.md):")
            print(plan_content)
            print("\n[2] AGENT ROSTER (subagents.yaml):")
            # Print only agent names and descriptions for brevity
            for line in yaml_content.splitlines():
                if "name:" in line or "description:" in line:
                    print(line)
            print("------------------------------------------")

            if "--yes" not in sys.argv:
                confirm = input("\n[Plan Mode] Save this configuration? [y/N]: ").strip().lower()
                if confirm != 'y':
                    print("[Planner] Operation cancelled by user.")
                    sys.exit(0)

            # Save artifacts
            with open(CONFIG_FILE, 'w') as f:
                f.write(yaml_content)
            
            with open("task_plan.md", 'w') as f:
                f.write(plan_content)
                
            # Initialize other Manus Protocol files if they don't exist
            if not os.path.exists("findings.md"):
                with open("findings.md", 'w') as f:
                    f.write("# Findings & Scratchpad\n\nUse this file to store shared knowledge, research notes, and intermediate outputs.")
            
            if not os.path.exists("progress.md"):
                with open("progress.md", 'w') as f:
                    f.write(f"# Mission Progress\n\nMission: {mission}\n\n## Status Log\n")

            print(f"[Planner] Configuration saved to {CONFIG_FILE}.")
            print(f"[Planner] Created 'task_plan.md', 'findings.md', 'progress.md'.")
            print("[Planner] Ready to execute. Run 'python3 scripts/orchestrator.py' to start.")
        else:
            print("[Planner] Error: Could not parse YAML from agent output.")
            print("--- Raw Output ---")
            print(output)
            sys.exit(1)

    except Exception as e:
        print(f"[Planner] Critical Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
