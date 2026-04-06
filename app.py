from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
import uvicorn

from environment import CICDDebuggerEnv
from models import Action

app = FastAPI(
    title="CI/CD Debugger Environment",
    description="An OpenEnv environment where AI agents debug broken CI/CD pipelines.",
    version="1.0.0"
)

# One environment instance per task — stored in memory
envs = {}


class ResetRequest(BaseModel):
    task_id: str = "task_1"


class StepRequest(BaseModel):
    task_id: str
    issue_type: str
    fix_action: str
    explanation: Optional[str] = None


@app.get("/")
def root():
    """Health check — judges ping this to verify the Space is live."""
    return {
        "status": "ok",
        "environment": "cicd-debugger-env",
        "version": "1.0.0",
        "available_tasks": CICDDebuggerEnv.available_tasks()
    }


@app.post("/reset")
def reset(request: Optional[ResetRequest] = None):
    """
    Reset the environment for a given task.
    Returns the initial observation (broken pipeline + error log).
    """
    if request is None:
        request = ResetRequest()

    valid_tasks = CICDDebuggerEnv.available_tasks()
    if request.task_id not in valid_tasks:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid task_id. Choose from: {valid_tasks}"
        )

    env = CICDDebuggerEnv(task_id=request.task_id)
    observation = env.reset()
    envs[request.task_id] = env

    return {
        "task_id": request.task_id,
        "observation": observation.dict()
    }


@app.post("/step")
def step(request: StepRequest):
    """
    Submit the agent's diagnosis for the current task.
    Returns observation, reward (score), done status, and info.
    """
    if request.task_id not in envs:
        raise HTTPException(
            status_code=400,
            detail=f"No active session for task_id '{request.task_id}'. Call /reset first."
        )

    env = envs[request.task_id]

    action = Action(
        issue_type=request.issue_type,
        fix_action=request.fix_action,
        explanation=request.explanation
    )

    try:
        observation, reward, done, info = env.step(action)
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "observation": observation.dict(),
        "reward": reward.dict(),
        "done": done,
        "info": info
    }


@app.get("/state")
def state(task_id: str = "task_1"):
    """Return the current state of the environment for a given task."""
    if task_id not in envs:
        raise HTTPException(
            status_code=400,
            detail=f"No active session for task_id '{task_id}'. Call /reset first."
        )
    return envs[task_id].state()


@app.get("/tasks")
def list_tasks():
    """List all available tasks with their difficulty and description."""
    from tasks import TASKS
    return {
        task_id: {
            "difficulty": task["difficulty"],
            "description": task["description"]
        }
        for task_id, task in TASKS.items()
    }


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=7860, reload=False)