from models import Observation, Action, Reward
from tasks import get_task, get_all_task_ids
from graders import grade


class CICDDebuggerEnv:
    """
    CI/CD Pipeline Debugger — OpenEnv Environment

    The agent is shown a broken CI/CD pipeline (YAML config + error log)
    and must identify the issue type and correct fix.

    Follows the OpenEnv interface:
    - reset()        → returns initial Observation
    - step(action)   → returns (Observation, Reward, done, info)
    - state()        → returns current environment state as dict
    """

    def __init__(self, task_id: str = "task_1"):
        self.task_id = task_id
        self.current_task = None
        self.done = False
        self.steps_taken = 0
        self.last_reward = None

    def reset(self) -> Observation:
        """
        Reset the environment to a fresh state.
        Returns the initial observation (the broken pipeline problem).
        """
        task = get_task(self.task_id)
        self.current_task = task
        self.done = False
        self.steps_taken = 0
        self.last_reward = None
        return task["observation"]

    def step(self, action: Action):
        """
        Take one step: agent submits its diagnosis.

        Args:
            action: Action object with issue_type and fix_action

        Returns:
            observation: Observation (same task — agent sees result)
            reward: Reward object with score 0.0-1.0
            done: bool (always True after one step — one diagnosis per task)
            info: dict with extra metadata
        """
        if self.done:
            raise RuntimeError("Episode is done. Call reset() to start a new task.")

        if self.current_task is None:
            raise RuntimeError("Environment not initialized. Call reset() first.")

        # Grade the action
        reward = grade(action, self.current_task["ground_truth"])

        self.done = True
        self.steps_taken += 1
        self.last_reward = reward

        # Return the same observation so agent can see what it was working on
        observation = self.current_task["observation"]

        info = {
            "task_id": self.task_id,
            "difficulty": self.current_task["difficulty"],
            "steps_taken": self.steps_taken
        }

        return observation, reward, self.done, info

    def state(self) -> dict:
        """
        Return the current state of the environment.
        """
        return {
            "task_id": self.task_id,
            "done": self.done,
            "steps_taken": self.steps_taken,
            "current_task_difficulty": (
                self.current_task["difficulty"] if self.current_task else None
            ),
            "last_score": (
                self.last_reward.score if self.last_reward else None
            )
        }

    @staticmethod
    def available_tasks() -> list:
        """Return all available task IDs."""
        return get_all_task_ids()