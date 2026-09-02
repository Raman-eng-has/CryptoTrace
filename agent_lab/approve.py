import sys
from pathlib import Path

from agent_lab.approval import approve_task


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: python -m agent_lab.approve <task_id>"
        )
        raise SystemExit(1)

    task_id = sys.argv[1]

    repo_root = Path(__file__).resolve().parent.parent

    approve_task(
        task_id=task_id,
        repo_root=repo_root,
    )


if __name__ == "__main__":
    main()