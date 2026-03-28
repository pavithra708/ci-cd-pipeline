---
title: CI/CD Debugger Environment
emoji: 🔧
colorFrom: purple
colorTo: teal
sdk: docker
pinned: false
tags:
  - openenv
---

# CI/CD Pipeline Debugger — OpenEnv Environment

An OpenEnv-compliant environment where AI agents learn to debug broken CI/CD pipelines.

## Why This Matters

Every software team uses CI/CD pipelines. When they break, engineers spend valuable time diagnosing errors from cryptic logs. This environment trains and evaluates AI agents to do that job automatically — a genuine, high-value real-world task.

## Environment Description

The agent is shown a broken GitHub Actions pipeline:
- A **YAML config** showing the pipeline definition
- An **error log** showing what went wrong

The agent must output a structured JSON diagnosis:
```json
{
  "issue_type": "missing_env",
  "fix_action": "add_secret",
  "explanation": "The API_KEY environment variable is not set in GitHub secrets."
}
```

## Observation Space

| Field | Type | Description |
|---|---|---|
| `task_id` | string | Which task is active |
| `pipeline_yaml` | string | The broken pipeline YAML config |
| `error_log` | string | The error message from the failed run |
| `hint` | string (optional) | Hint provided for easier tasks |

## Action Space

| Field | Type | Valid Values |
|---|---|---|
| `issue_type` | string | `missing_env`, `missing_dep`, `failing_test` |
| `fix_action` | string | `add_secret`, `add_numpy`, `fix_endpoint` |
| `explanation` | string (optional) | Agent's reasoning |

## Tasks

| Task | Difficulty | Description |
|---|---|---|
| `task_1` | Easy | Missing environment variable (`API_KEY`) |
| `task_2` | Medium | Missing Python dependency (`numpy`) |
| `task_3` | Hard | Failing integration test (wrong API endpoint) |

## Reward Function

Partial credit scoring — not binary:
- Correct `issue_type` → **+0.5**
- Correct `fix_action` → **+0.5**
- Both correct → **1.0** (full score)

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health check |
| POST | `/reset` | Start a task, get observation |
| POST | `/step` | Submit diagnosis, get score |
| GET | `/state` | Current environment state |
| GET | `/tasks` | List all tasks |

## Setup & Usage

### Local

```bash
git clone <your-repo-url>
cd cicd-debugger-env
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 7860
```

### Docker

```bash
docker build -t cicd-debugger-env .
docker run -p 7860:7860 cicd-debugger-env
```

### Run Inference

```bash
export API_BASE_URL="https://api-inference.huggingface.co/v1"
export MODEL_NAME="Qwen/Qwen2.5-72B-Instruct"
export HF_TOKEN="hf_your_token_here"
python inference.py
```

## Baseline Scores

Tested with `Qwen/Qwen2.5-72B-Instruct`:

| Task | Difficulty | Score |
|---|---|---|
| task_1 | Easy | 1.0 |
| task_2 | Medium | 1.0 |
| task_3 | Hard | 1.0 |
| **Average** | | **1.0** |

## Project Structure

```
cicd-debugger-env/
├── app.py            # FastAPI server
├── environment.py    # OpenEnv interface (reset/step/state)
├── models.py         # Pydantic models
├── tasks.py          # 3 pipeline failure scenarios
├── graders.py        # Deterministic scoring
├── inference.py      # Baseline agent script
├── openenv.yaml      # OpenEnv metadata
├── Dockerfile        # Container config
├── requirements.txt  # Dependencies
└── README.md         # This file
```