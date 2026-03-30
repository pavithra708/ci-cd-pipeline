from models import Action, Reward


def grade(action: Action, ground_truth: dict) -> Reward:
    """
    Grade the agent's action against the ground truth.

    Scoring breakdown:
    - Correct issue_type → +0.5
    - Correct fix_action → +0.5
    - Both correct       → 1.0 (full score)
    - Neither correct    → 0.0
    - One correct        → 0.5 (partial credit)

    This is fully deterministic — same input always gives same output.
    """
    issue_correct = action.issue_type == ground_truth["issue_type"]
    fix_correct = action.fix_action == ground_truth["fix_action"]

    score = 0.0
    if issue_correct:
        score += 0.5
    if fix_correct:
        score += 0.5

    if score == 1.0:
        message = "Perfect! Both issue type and fix action are correct."
    elif issue_correct and not fix_correct:
        message = f"Issue type correct, but fix action wrong. Expected: {ground_truth['fix_action']}"
    elif fix_correct and not issue_correct:
        message = f"Fix action correct, but issue type wrong. Expected: {ground_truth['issue_type']}"
    else:
        message = (
            f"Both incorrect. "
            f"Expected issue_type='{ground_truth['issue_type']}', "
            f"fix_action='{ground_truth['fix_action']}'"
        )

    return Reward(
        score=round(score, 2),
        issue_correct=issue_correct,
        fix_correct=fix_correct,
        message=message
    )


# Valid values the agent must choose from — this makes grading deterministic
VALID_ISSUE_TYPES = ["missing_env", "missing_dep", "failing_test", "yaml_syntax", "version_conflict"]
VALID_FIX_ACTIONS = ["add_secret", "add_numpy", "fix_endpoint", "fix_indentation", "update_requirements"]