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
    },

    "task_4": {
        "observation": Observation(
            task_id="task_4",
            pipeline_yaml="""
name: Build and Push
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build Docker image
        run: docker build -t myapp .
      - name: Push image
        run: docker push myapp:latest
""",
            error_log="""
Error: YAML parse error: mapping values are not allowed here
  in "<string>", line 8, column 9:
    - name: Build Docker image
        ^
""",
            hint="Check the YAML indentation carefully."
        ),
        "ground_truth": {
            "issue_type": "yaml_syntax",
            "fix_action": "fix_indentation"
        },
        "difficulty": "easy",
        "description": "A YAML syntax error due to incorrect indentation in the pipeline."
    },

    "task_5": {
        "observation": Observation(
            task_id="task_5",
            pipeline_yaml="""
name: Build Python App
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, 3.10, 3.11]
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{ matrix.python-version }}
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/
""",
            error_log="""
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. 
This behavior is the source of the following dependency conflicts.
package-a 2.0.0 requires package-b>=1.5, but you have package-b 1.2.0 which is incompatible.
""",
            hint=None
        ),
        "ground_truth": {
            "issue_type": "version_conflict",
            "fix_action": "update_requirements"
        },
        "difficulty": "medium",
        "description": "A dependency version conflict exists where required packages have incompatible versions."
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