import json
import os
import time
import uuid
import glob
from dataclasses import dataclass, field, asdict
from typing import List, Optional

MISSIONS_DIR = ".swarm/missions"

@dataclass
class MissionState:
    mission_id: str
    description: str
    started_at: float
    status: str = "planning"  # planning | running | paused | completed | failed
    agents: List[dict] = field(default_factory=list)
    attempt: int = 1
    team_name: str = ""

    def __post_init__(self):
        if not self.team_name:
            # Generate team name from description
            words = self.description.lower().split()[:3]
            self.team_name = "-".join(w for w in words if w.isalnum())[:30] or "mission"

    def save(self):
        os.makedirs(MISSIONS_DIR, exist_ok=True)
        path = os.path.join(MISSIONS_DIR, f"{self.mission_id}.json")
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, indent=2)

    @classmethod
    def load(cls, mission_id: str) -> Optional["MissionState"]:
        path = os.path.join(MISSIONS_DIR, f"{mission_id}.json")
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
        return None

    @classmethod
    def latest(cls) -> Optional["MissionState"]:
        """Load the most recent mission state."""
        os.makedirs(MISSIONS_DIR, exist_ok=True)
        files = glob.glob(os.path.join(MISSIONS_DIR, "*.json"))
        if not files:
            return None
        latest_file = max(files, key=os.path.getmtime)
        mission_id = os.path.basename(latest_file).replace(".json", "")
        return cls.load(mission_id)

    @classmethod
    def create(cls, description: str) -> "MissionState":
        return cls(
            mission_id=str(uuid.uuid4())[:8],
            description=description,
            started_at=time.time()
        )

    def update_agent_status(self, agent_name: str, status: str):
        for agent in self.agents:
            if agent.get("name") == agent_name:
                agent["status"] = status
                break
        self.save()

    def is_resumable(self) -> bool:
        return self.status in ("running", "paused") and any(
            a.get("status") not in ("completed", "failed") for a in self.agents
        )
