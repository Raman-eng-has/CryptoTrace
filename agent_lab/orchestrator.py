from dataclasses import dataclass
from pathlib import Path

from agent_lab.protocol import AgentProposal, AgentTask


@dataclass
class AdvisoryOrchestrator:
    repo_root: Path

    def create_task(
        self,
        agent: str,
        objective: str,
        task_id: str,
    ) -> AgentTask:
        return AgentTask(
            task_id=task_id,
            agent=agent,
            objective=objective,
            approval_required=True,
        )

    def proposal_instructions(self, task: AgentTask) -> str:
        return f"""
You are the {task.agent} specialist for CryptoTrace AI.

TASK:
{task.objective}

You are currently in ADVISORY MODE.

You MUST:
1. Inspect the relevant existing project state.
2. Explain the problem.
3. Identify constraints and dependencies.
4. Present multiple viable approaches.
5. Compare advantages and disadvantages.
6. Identify technical and security risks.
7. Recommend one approach.
8. Explain why you recommend it.
9. Ask questions that require human decisions.

You MUST NOT:
- create files
- modify files
- delete files
- install packages
- implement the solution
- silently make architectural decisions

Your output is a proposal for human review.

End with:

STATUS: WAITING_FOR_HUMAN_APPROVAL
"""

    def implementation_allowed(
        self,
        proposal: AgentProposal,
    ) -> bool:
        return proposal.status == "approved"