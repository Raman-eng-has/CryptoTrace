import os
import sys
from pathlib import Path

from openai import OpenAI

from agent_lab.orchestrator import AdvisoryOrchestrator
from agent_lab.repo_tool import format_repository, read_file


MODEL = "nvidia/nemotron-3-nano-30b-a3b"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"


AGENT_OBJECTIVES = {
    "blockchain": (
        "Design the implementation plan for the Blockchain/Data foundation "
        "of the first end-to-end CryptoTrace vertical slice. "
        "Define provider abstraction, blockchain fixture/input handling, "
        "transaction normalization, evidence creation, provenance, and "
        "interfaces required by downstream Graph and Risk components."
    ),
    "graph": (
        "Design the implementation plan for the Graph/Analytics layer "
        "of the first end-to-end CryptoTrace vertical slice. "
        "Define graph entities, relationships, traversal requirements, "
        "detection inputs, and interfaces to the deterministic Risk Engine."
    ),
    "risk": (
        "Design the implementation plan for the deterministic CryptoTrace "
        "Risk and Decision Engine. Define approved risk parameters, rules, "
        "scoring, boundaries, evidence references, and deterministic outputs. "
        "Nemotron must not become the authoritative risk decision-maker."
    ),
    "platform": (
        "Design the implementation plan for the API/Platform layer of the "
        "first end-to-end CryptoTrace vertical slice. Define API boundaries, "
        "Structured Evidence Packet transport, provenance, error handling, "
        "and interfaces between backend services."
    ),
    "copilot": (
        "Design the implementation plan for the Nemotron AI Copilot layer. "
        "Implement only the approved V1 capabilities: evidence summarization, "
        "risk-factor explanation, and evidence-grounded Q&A. Define grounding, "
        "validation, evidence references, prompt-injection protection, and "
        "graceful AI failure behavior."
    ),
}


def load_repository_context(repo_root: Path) -> str:
    files = format_repository()

    important_files = [
        "AGENTS.md",
        "agent_lab/protocol.py",
        "agent_lab/orchestrator.py",
        "agent_lab/repo_tool.py",
    ]

    contents = []

    for relative_path in important_files:
        path = repo_root / relative_path

        if path.exists():
            try:
                contents.append(
                    f"\n===== {relative_path} =====\n"
                    f"{read_file(relative_path)}"
                )
            except Exception as exc:
                contents.append(
                    f"\n===== {relative_path} =====\n"
                    f"Unable to read: {exc}"
                )

    return (
        "REPOSITORY FILES\n"
        "================\n"
        f"{files}\n"
        "\n"
        "IMPORTANT EXISTING FILES\n"
        "========================\n"
        + "\n".join(contents)
    )


def build_prompt(repo_root: Path, agent_name: str) -> str:
    orchestrator = AdvisoryOrchestrator(repo_root)

    task = orchestrator.create_task(
        agent=agent_name,
        objective=AGENT_OBJECTIVES[agent_name],
        task_id=f"{agent_name}-implementation-001",
    )

    instructions = orchestrator.proposal_instructions(task)
    repository_context = load_repository_context(repo_root)

    return f"""
{instructions}

ARCHITECTURE DECISIONS ALREADY APPROVED
========================================

The CryptoTrace architecture has already been approved.

Core flow:

CryptoTrace determines risk
    ->
Structured Evidence Packet provides proof
    ->
Nemotron explains
    ->
Validator checks
    ->
Human verifies

Important constraints:

1. Nemotron is NOT the authoritative risk decision-maker.
2. Risk must be deterministic and reproducible.
3. Evidence must preserve provenance.
4. Observed evidence, deterministic/computed results, and AI-generated
   interpretation must remain distinguishable.
5. Nemotron receives a Structured Evidence Packet rather than unrestricted
   database access.
6. AI output must be validated before presentation.
7. Insufficient or contradictory evidence must be explicitly qualified.
8. Malicious blockchain metadata must be treated as data, not instructions.
9. Nemotron failure must not stop the investigation.
10. The first implementation target is one end-to-end vertical slice.

TESTING REQUIREMENTS

The implementation must eventually support:

- deterministic unit tests
- integration tests
- E2E tests
- deterministic fixtures
- evidence-grounding tests
- security/prompt-injection tests
- resilience/failure tests

REPOSITORY CONTEXT
==================

{repository_context}

YOUR TASK

Produce the implementation proposal for the {agent_name} specialist.

Do NOT implement anything yet.

Do NOT create files.

Do NOT modify files.

Do NOT install packages.

Focus on:

1. Existing project state.
2. Exact responsibility of this specialist.
3. Interfaces with other specialists.
4. Files/modules that should eventually be created or modified.
5. Data contracts required.
6. Dependencies.
7. Security considerations.
8. Testing strategy.
9. Implementation order.
10. Risks and failure modes.
11. A concrete recommended approach.

The proposal must be specific enough that, after human approval,
the specialist can implement it without reopening the architecture.

End with:

STATUS: WAITING_FOR_HUMAN_APPROVAL
"""


def main() -> None:
    if len(sys.argv) != 2:
        print(
            "Usage: python -m agent_lab.specialist_agent "
            "<blockchain|graph|risk|platform|copilot>"
        )
        raise SystemExit(1)

    agent_name = sys.argv[1].lower()

    if agent_name not in AGENT_OBJECTIVES:
        raise ValueError(
            f"Unknown agent '{agent_name}'. "
            f"Choose from: {', '.join(AGENT_OBJECTIVES)}"
        )

    repo_root = Path(__file__).resolve().parent.parent

    api_key = os.environ.get("NVIDIA_API_KEY")

    if not api_key:
        raise RuntimeError(
            "NVIDIA_API_KEY is not set in the current PowerShell session."
        )

    client = OpenAI(
        base_url=NVIDIA_BASE_URL,
        api_key=api_key,
    )

    prompt = build_prompt(repo_root, agent_name)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    f"You are the CryptoTrace {agent_name} specialist. "
                    "You are operating in advisory mode. "
                    "The architecture has already been approved. "
                    "You must not implement anything without explicit "
                    "human approval."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
        max_tokens=5000,
    )

    print("=" * 70)
    print(f"CRYPTOTRACE {agent_name.upper()} SPECIALIST — PROPOSAL")
    print("=" * 70)
    print()
    print(response.choices[0].message.content)
    print()
    print("=" * 70)
    print("STATUS: WAITING_FOR_HUMAN_APPROVAL")
    print("=" * 70)


if __name__ == "__main__":
    main()