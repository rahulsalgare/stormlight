from dataclasses import dataclass, field
from typing import Optional, Dict, Any

@dataclass
class Task:
    method: str
    path: str
    data: Optional[Any] = None
    headers: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.method = self.method.upper()  # Ensure method is always uppercase


@dataclass
class Environment:
    host: str
    tasks: list[Task]
    user_count: int
    spawn_rate: float
    duration: float