from pathlib import Path

from agent_lab.workflow import get_task


APPROVAL_FILE = ".agent_approvals"


def approve_task(
    task_id: str,
    repo_root: Path,
) -> None:
    """
    Record explicit human approval for a workflow task.

    Approval is persisted outside the task object so that
    restarting the Python process does not silently lose
    the human decision.
    """

    task = get_task(task_id)

    approval_dir = repo_root / APPROVAL_FILE
    approval_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    approval_file = approval_dir / f"{task_id}.approved"

    approval_file.write_text(
        "approved\n",
        encoding="utf-8",
    )

    task.status = "ready"

    print("=" * 70)
    print("CRYPTOTRACE HUMAN APPROVAL")
    print("=" * 70)
    print()
    print(f"TASK: {task.task_id}")
    print(f"AGENT: {task.agent}")
    print()
    print("DECISION: APPROVED")
    print()
    print(
        "The Lead may now authorize implementation "
        "for this task."
    )
    print()
    print("=" * 70)


def is_approved(
    task_id: str,
    repo_root: Path,
) -> bool:
    """
    Return True only when an explicit approval marker
    exists for the task.
    """

    approval_file = (
        repo_root
        / APPROVAL_FILE
        / f"{task_id}.approved"
    )

    return approval_file.exists()


def revoke_approval(
    task_id: str,
    repo_root: Path,
) -> None:
    """
    Remove human approval for a task.
    """

    approval_file = (
        repo_root
        / APPROVAL_FILE
        / f"{task_id}.approved"
    )

    if approval_file.exists():
        approval_file.unlink()

    task = get_task(task_id)

    if task.status != "completed":
        task.status = "blocked"

    print(
        f"Approval revoked for {task_id}."
    )