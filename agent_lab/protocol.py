from dataclasses import dataclass, field
from typing import Any, Literal


AgentName = Literal[
    "architect",
    "blockchain",
    "graph",
    "risk",
    "platform",
    "copilot",
    "ui",
]
ProposalStatus = Literal[
    "analyzing",
    "proposal_ready",
    "waiting_for_human",
    "changes_requested",
    "approved",
    "implementing",
    "testing",
    "review_required",
    "completed",
    "blocked",
]


@dataclass
class Approach:
    name: str
    description: str
    advantages: list[str] = field(default_factory=list)
    disadvantages: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    complexity: str = "unknown"


@dataclass
class AgentProposal:
    proposal_id: str
    task_id: str
    agent: AgentName

    problem: str
    current_state: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)

    approaches: list[Approach] = field(default_factory=list)

    recommended_approach: str | None = None
    recommendation_reason: str | None = None

    consequences: list[str] = field(default_factory=list)
    questions_for_human: list[str] = field(default_factory=list)

    status: ProposalStatus = "analyzing"


@dataclass
class AgentTask:
    task_id: str
    agent: AgentName
    objective: str

    evidence: list[dict[str, Any]] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)

    approval_required: bool = True
    approved_proposal_id: str | None = None


@dataclass
class AgentResult:
    task_id: str
    agent: AgentName
    status: Literal["completed", "blocked", "needs_human"]

    findings: list[str] = field(default_factory=list)
    evidence_refs: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    human_decision_required: bool = False
@dataclass
class HumanDecision:
    proposal_id: str
    decision: Literal[
        "approved",
        "changes_requested",
        "rejected",
    ]
    comment: str = ""
    approved_by: str = "human"