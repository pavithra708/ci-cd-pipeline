from models import Observation

# Each task has:
# - observation: what the agent sees
# - ground_truth: the correct answer (used by grader, never shown to agent)

TASKS = {
    "task_1": {
        "observation": Observation(
            task_id="task_1",
            pipeline_yaml="""
name: Run Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest tests/
""",
            error_log="Error: API_KEY not found. Please set the API_KEY environment variable.",
            hint="Look at what environment variable is missing."
        ),
        "ground_truth": {
            "issue_type": "missing_env",
            "fix_action": "add_secret"
        },
        "difficulty": "easy",
        "description": "A required environment variable is not set in the pipeline secrets."
    },

    "task_2": {
        "observation": Observation(
            task_id="task_2",
            pipeline_yaml="""
name: Run Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install and test
        run: |
          pip install -r requirements.txt
          pytest tests/
""",
            error_log="ModuleNotFoundError: No module named 'numpy'. Check your requirements.txt.",
            hint=None
        ),
        "ground_truth": {
            "issue_type": "missing_dep",
            "fix_action": "add_numpy"
        },
        "difficulty": "medium",
        "description": "A required Python dependency is missing from requirements.txt."
    },

    "task_3": {
        "observation": Observation(
            task_id="task_3",
            pipeline_yaml="""
name: Deploy and Test
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install deps
        run: pip install -r requirements.txt
      - name: Run integration tests
        run: pytest tests/integration/
      - name: Deploy
        run: ./deploy.sh
""",
            error_log="""
FAILED tests/integration/test_api.py::test_health_check
AssertionError: assert 404 == 200
 +  where 404 = <Response [404]>.status_code
The endpoint /api/v1/health returned 404. Expected 200.
""",
            hint=None
        ),
        "ground_truth": {
            "issue_type": "failing_test",
            "fix_action": "fix_endpoint"
        },
        "difficulty": "hard",
        "description": "An integration test is failing because an API endpoint URL is wrong."
    }
}


def get_task(task_id: str):
    """Return the task dict for a given task_id."""
    if task_id not in TASKS:
        raise ValueError(f"Unknown task_id: {task_id}. Choose from {list(TASKS.keys())}")
    return TASKS[task_id]


def get_all_task_ids():
    """Return list of all task IDs in order."""
    return list(TASKS.keys())