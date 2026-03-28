from pydantic import BaseModel
from typing import Optional


class Observation(BaseModel):
    """What the AI agent sees when it looks at the environment."""
    task_id: str                  # which task is this: "task_1", "task_2", "task_3"
    pipeline_yaml: str            # the broken CI/CD pipeline config
    error_log: str                # the error message from the failed pipeline
    hint: Optional[str] = None    # optional hint for easier tasks


class Action(BaseModel):
    """What the AI agent responds with — its diagnosis."""
    issue_type: str               # e.g. "missing_env", "missing_dep", "failing_test"
    fix_action: str               # e.g. "add_secret", "add_numpy", "fix_endpoint"
    explanation: Optional[str] = None  # agent can optionally explain its reasoning


class Reward(BaseModel):
    """The score given to the agent after each action."""
    score: float                  # 0.0 to 1.0
    issue_correct: bool           # did agent identify the right issue type?
    fix_correct: bool             # did agent suggest the right fix?
    message: str                  # human-readable feedback