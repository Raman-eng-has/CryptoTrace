from pathlib import Path

from agent_lab.approval import is_approved
from agent_lab.implementation_runner import run_implementation
from agent_lab.proposal_validator import ProposalValidator
from agent_lab.specialist_runner import run_specialist
from agent_lab.workflow import get_ready_tasks


def print_header() -> None:
    print("=" * 70)
    print("CRYPTOTRACE LEAD ORCHESTRATOR")
    print("=" * 70)
    print()


def run_task(task, repo_root: Path) -> None:

    print(f"TASK: {task.task_id}")
    print(f"AGENT: {task.agent}")
    print()
    print(task.objective)
    print()

    # =========================================================
    # APPROVAL CHECK
    # =========================================================

    if is_approved(
        task_id=task.task_id,
        repo_root=repo_root,
    ):
        print("-" * 70)
        print("HUMAN APPROVAL")
        print("-" * 70)
        print()
        print("APPROVED")
        print()
        print(
            "Human approval already exists."
        )
        print(
            "Lead is moving directly to implementation."
        )
        print()

        # -----------------------------------------------------
        # IMPLEMENTATION
        # -----------------------------------------------------

        task.status = "running"

        print("-" * 70)
        print(
            f"LEAD → {task.agent.upper()} | IMPLEMENTATION"
        )
        print("-" * 70)
        print()

        result = run_implementation(
            task=task,
            repo_root=repo_root,
        )

        print()
        print("IMPLEMENTATION RESULT")
        print("-" * 70)
        print(result)
        print()

        if "STATUS: IMPLEMENTATION_COMPLETED" in result:
            task.status = "completed"

            print("=" * 70)
            print("TASK STATUS: COMPLETED")
            print("=" * 70)

        else:
            task.status = "blocked"

            print("=" * 70)
            print("TASK STATUS: BLOCKED")
            print("=" * 70)

        return

    # =========================================================
    # ADVISORY PHASE
    # =========================================================

    print("-" * 70)
    print(
        f"LEAD → {task.agent.upper()} | ADVISORY"
    )
    print("-" * 70)
    print()

    proposal = run_specialist(
        task,
        repo_root,
    )

    print("SPECIALIST PROPOSAL")
    print("-" * 70)
    print(proposal)
    print()

    # =========================================================
    # VALIDATION
    # =========================================================

    print("-" * 70)
    print("LEAD VALIDATION")
    print("-" * 70)

    validator = ProposalValidator(
        repo_root
    )

    validation = validator.validate(
        task=task,
        proposal=proposal,
    )

    if not validation.valid:

        print("RESULT: INVALID")
        print()

        for issue in validation.issues:
            print(f"- {issue}")

        print()
        print("=" * 70)
        print("LEAD STATUS: REVISION_REQUIRED")
        print("=" * 70)

        return

    print("RESULT: VALID")
    print()
    print(
        "The specialist proposal passed the Lead's "
        "repository, scope, technology, handoff, "
        "and safety checks."
    )

    print()
    print("=" * 70)
    print("LEAD STATUS: WAITING_FOR_HUMAN_APPROVAL")
    print("=" * 70)

    print()
    print(
        f"Human action required before implementation:"
    )
    print()
    print(
        f"Approve task: {task.task_id}"
    )


def main() -> None:

    repo_root = (
        Path(__file__).resolve().parent.parent
    )

    print_header()

    ready_tasks = get_ready_tasks()

    if not ready_tasks:

        print(
            "No tasks are currently ready."
        )

        return

    # ---------------------------------------------------------
    # CURRENTLY: PROCESS THE FIRST READY TASK
    # ---------------------------------------------------------

    task = ready_tasks[0]

    print(
        f"DELEGATING TASK: {task.task_id}"
    )

    print(
        f"AGENT: {task.agent}"
    )

    print()

    run_task(
        task=task,
        repo_root=repo_root,
    )


if __name__ == "__main__":
    main()