"""
inference.py — Baseline inference script for CI/CD Debugger Environment

Runs an LLM agent against all 3 tasks and prints reproducible scores.

Required environment variables:
  API_BASE_URL   — the LLM API endpoint (optional: defaults to https://router.huggingface.co/v1)
  MODEL_NAME     — the model identifier
  HF_TOKEN       — your Hugging Face / API key

Usage:
  export API_BASE_URL="https://router.huggingface.co/v1"
  export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
  export HF_TOKEN="hf_your_token_here"
  python inference.py
"""

import os
import json
from openai import OpenAI
from environment import CICDDebuggerEnv
from models import Action
from graders import VALID_ISSUE_TYPES, VALID_FIX_ACTIONS

# --- Load credentials from environment variables ---
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("OPENAI_API_KEY", "")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN or OPENAI_API_KEY environment variable is not set.")

# --- Initialize OpenAI-compatible client ---
client = OpenAI(
    base_url=API_BASE_URL,
    api_key=HF_TOKEN
)

def build_prompt(observation) -> str:
    """Build the prompt shown to the LLM agent."""
    return f"""You are an expert DevOps engineer debugging a broken CI/CD pipeline.

You will be shown a pipeline YAML configuration and an error log.
Your job is to identify the issue and suggest the correct fix.

PIPELINE YAML:
{observation.pipeline_yaml}

ERROR LOG:
{observation.error_log}

{"HINT: " + observation.hint if observation.hint else ""}

You MUST respond with ONLY a valid JSON object. No explanation outside the JSON.
Choose issue_type from: {VALID_ISSUE_TYPES}
Choose fix_action from: {VALID_FIX_ACTIONS}

Response format:
{{
  "issue_type": "<one of the valid issue types>",
  "fix_action": "<one of the valid fix actions>",
  "explanation": "<brief explanation of your reasoning>"
}}"""


def run_agent_on_task(task_id: str) -> dict:
    """Run the agent on a single task and return the result."""
    # Set up environment
    env = CICDDebuggerEnv(task_id=task_id)
    observation = env.reset()

    # Build prompt and call LLM
    prompt = build_prompt(observation)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.0   # deterministic output
        )

        raw_response = response.choices[0].message.content.strip()

        # Parse JSON response
        # Strip markdown code fences if present
        clean = raw_response.replace("```json", "").replace("```", "").strip()
        parsed = json.loads(clean)

        action = Action(
            issue_type=parsed.get("issue_type", ""),
            fix_action=parsed.get("fix_action", ""),
            explanation=parsed.get("explanation", "")
        )

    except (json.JSONDecodeError, KeyError) as e:
        # Return a blank action so grader gives 0.0
        action = Action(issue_type="", fix_action="")

    # Step the environment with the agent's action
    _, reward, done, info = env.step(action)

    return {
        "task_id": task_id,
        "difficulty": info["difficulty"],
        "score": reward.score,
        "issue_correct": reward.issue_correct,
        "fix_correct": reward.fix_correct,
        "message": reward.message
    }


def main():
    # Print START marker with initialization info
    print("[START]")
    print(json.dumps({
        "model": MODEL_NAME,
        "api_base": API_BASE_URL,
        "environment": "cicd-debugger-env",
        "num_tasks": 5
    }))

    task_ids = CICDDebuggerEnv.available_tasks()
    results = []
    total_score = 0.0

    for task_id in task_ids:
        result = run_agent_on_task(task_id)
        results.append(result)
        
        # Print STEP marker for each task completion
        print("[STEP]")
        print(json.dumps({
            "task_id": result["task_id"],
            "difficulty": result["difficulty"],
            "score": result["score"],
            "issue_correct": result["issue_correct"],
            "fix_correct": result["fix_correct"],
            "message": result["message"]
        }))
        
        total_score += result["score"]

    avg_score = total_score / len(results)

    # Print END marker with final results
    print("[END]")
    print(json.dumps({
        "total_tasks": len(results),
        "total_score": total_score,
        "average_score": avg_score,
        "scores_by_task": [
            {
                "task_id": r["task_id"],
                "difficulty": r["difficulty"],
                "score": r["score"]
            }
            for r in results
        ]
    }))

    return results


if __name__ == "__main__":
    main()