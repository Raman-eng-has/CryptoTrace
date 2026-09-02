import os
from pathlib import Path

from openai import OpenAI

from agent_lab.orchestrator import AdvisoryOrchestrator
from agent_lab.workflow import WorkflowTask


MODEL = "nvidia/nemotron-3-nano-30b-a3b"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"


def run_specialist(
    task: WorkflowTask,
    repo_root: Path,
    feedback: list[str] | None = None,
) -> str:
    api_key = os.environ.get("NVIDIA_API_KEY")

    if not api_key:
        raise RuntimeError(
            "NVIDIA_API_KEY is not set in the current PowerShell session."
        )

    client = OpenAI(
        base_url=NVIDIA_BASE_URL,
        api_key=api_key,
    )

    orchestrator = AdvisoryOrchestrator(repo_root)

    lead_task = orchestrator.create_task(
        agent=task.agent,
        objective=task.objective,
        task_id=task.task_id,
    )

    revision_section = ""

    if feedback:
        revision_section = f"""
LEAD REVISION FEEDBACK
======================
Your previous proposal did not pass Lead validation.

The Lead identified these issues:

{chr(10).join(f"- {item}" for item in feedback)}

You MUST correct these issues in this proposal.

Do not defend the previous proposal.
Re-inspect the repository and produce a corrected proposal.
"""

    prompt = f"""
You are the CryptoTrace {task.agent} specialist.

You are working under the CryptoTrace Lead Orchestrator.

TASK
====
{lead_task.objective}

DEPENDENCIES
============
{task.depends_on}

CURRENT MODE
============
ADVISORY IMPLEMENTATION PLANNING

The architecture has already been approved.

Your job is to produce a concrete implementation proposal for the Lead.

You MUST:

1. Inspect the existing repository before making technical claims.
2. Reference only files, directories, technologies, and tools that
   actually exist or are explicitly required by the approved architecture.
3. Identify the files relevant to your task.
4. Explain the implementation required.
5. Identify interfaces with other agents.
6. Identify inputs and outputs.
7. Identify tests that must pass.
8. Identify security concerns.
9. Identify risks and failure modes.
10. State what artifacts you will hand to downstream agents.
11. Stay strictly within your assigned specialist scope.
12. Follow the existing CryptoTrace technology stack.
13. Never invent repository structure.

You MUST NOT:

- modify files
- create files
- install packages
- make architectural decisions outside your scope
- assume a different programming language or framework
- invent directories or existing components
- override the approved architecture
- make autonomous risk decisions

The Lead will validate your proposal against the actual repository
before implementation is allowed.

{revision_section}

End with:

STATUS: WAITING_FOR_HUMAN_APPROVAL
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a CryptoTrace specialist operating under "
                    "a Lead Orchestrator. Follow the approved architecture, "
                    "inspect the real repository, remain within your assigned "
                    "scope, and never invent project structure."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
        max_tokens=4000,
    )

    return response.choices[0].message.content or ""