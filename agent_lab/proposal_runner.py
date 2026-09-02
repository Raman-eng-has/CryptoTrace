from pathlib import Path

from agent_lab.orchestrator import AdvisoryOrchestrator


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent

    orchestrator = AdvisoryOrchestrator(repo_root)

    task = orchestrator.create_task(
        agent="architect",
        objective=(
            "Determine the best architecture for the first "
            "end-to-end CryptoTrace vertical slice."
        ),
        task_id="architecture-001",
    )

    print("=" * 70)
    print("CRYPTOTRACE ARCHITECT — ADVISORY MODE")
    print("=" * 70)
    print()
    print("TASK:")
    print(task.objective)
    print()
    print(orchestrator.proposal_instructions(task))


if __name__ == "__main__":
    main()