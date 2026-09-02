import sys
from pathlib import Path

from agent_lab.approval import is_approved
from agent_lab.workflow import get_task


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: python -m agent_lab.implement <task_id>"
        )
        raise SystemExit(1)

    task_id = sys.argv[1]

    repo_root = Path(__file__).resolve().parent.parent

    task = get_task(task_id)

    print("=" * 70)
    print("CRYPTOTRACE IMPLEMENTATION AUTHORIZATION")
    print("=" * 70)
    print()

    print(f"TASK: {task.task_id}")
    print(f"AGENT: {task.agent}")
    print()

    if not is_approved(
        task_id=task_id,
        repo_root=repo_root,
    ):
        task.status = "blocked"

        print("APPROVAL: NOT FOUND")
        print()
        print(
            "Implementation is blocked because explicit "
            "human approval has not been recorded."
        )
        print()
        print("=" * 70)
        print("STATUS: BLOCKED")
        print("=" * 70)

        raise SystemExit(1)

    task.status = "running"

    print("APPROVAL: VERIFIED")
    print()
    print(
        "Human approval exists."
    )
    print()
    print(
        f"IMPLEMENTATION AUTHORIZED FOR: {task.agent}"
    )
    print()
    print(
        "The specialist may now implement the approved task."
    )
    print()
    print("=" * 70)
    print("STATUS: IMPLEMENTATION_AUTHORIZED")
    print("=" * 70)


if __name__ == "__main__":
    main()