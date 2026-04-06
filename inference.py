"""
inference.py — Baseline inference script for CI/CD Debugger Environment

Runs an LLM agent against all 3 tasks and prints reproducible scores.

Required environment variables:
  API_BASE_URL   — the LLM API endpoint
  MODEL_NAME     — the model identifier
  HF_TOKEN       — your Hugging Face / API key

Usage:
  export API_BASE_URL="https://api-inference.huggingface.co/v1"
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
HF_TOKEN = os.getenv("HF_TOKEN", "")

if not HF_TOKEN:
    raise ValueError("HF_TOKEN environment variable is not set.")

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
    print(f"\n{'='*50}")
    print(f"Running task: {task_id}")
    print(f"{'='*50}")

    # Set up environment
    env = CICDDebuggerEnv(task_id=task_id)
    observation = env.reset()

    print(f"Difficulty: {env.current_task['difficulty']}")
    print(f"Error log: {observation.error_log.strip()}")

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
        print(f"Agent response: {raw_response}")

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
        print(f"Failed to parse agent response: {e}")
        # Return a blank action so grader gives 0.0
        action = Action(issue_type="", fix_action="")

    # Step the environment with the agent's action
    _, reward, done, info = env.step(action)

    print(f"Score: {reward.score}")
    print(f"Message: {reward.message}")

    result = {
        "task_id": task_id,
        "difficulty": info["difficulty"],
        "score": reward.score,
        "issue_correct": reward.issue_correct,
        "fix_correct": reward.fix_correct,
        "message": reward.message
    }

    print("[STEP]")
    print(json.dumps(result))

    return result


def main():
    print("CI/CD Debugger Environment — Baseline Inference")
    print(f"Model: {MODEL_NAME}")
    print(f"API: {API_BASE_URL}")

    task_ids = CICDDebuggerEnv.available_tasks()

    print("[START]")
    print(json.dumps({
        "status": "baseline_inference_started",
        "model": MODEL_NAME,
        "api": API_BASE_URL,
        "tasks": task_ids
    }))

    results = []

    for task_id in task_ids:
        result = run_agent_on_task(task_id)
        results.append(result)

    # Print final summary
    print(f"\n{'='*50}")
    print("FINAL SCORES SUMMARY")
    print(f"{'='*50}")
    total_score = 0.0
    for r in results:
        print(f"  {r['task_id']} ({r['difficulty']:6s}): {r['score']:.1f} — {r['message']}")
        total_score += r["score"]

    avg_score = total_score / len(results)
    print(f"\nAverage score: {avg_score:.2f} / 1.0")
    print(f"Total score:   {total_score:.1f} / {float(len(results)):.1f}")

    print("[END]")
    print(json.dumps({
        "average_score": avg_score,
        "total_score": total_score,
        "tasks_completed": len(results)
    }))

    return results


if __name__ == "__main__":
    main()