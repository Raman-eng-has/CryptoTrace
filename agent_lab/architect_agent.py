import os
from pathlib import Path

from openai import OpenAI

from agent_lab.orchestrator import AdvisoryOrchestrator


MODEL = "nvidia/nemotron-3-nano-30b-a3b"
NVIDIA_BASE_URL = "https://integrate.api.nvidia.com/v1"


def load_file(repo_root: Path, filename: str) -> str:
    path = repo_root / filename

    if not path.exists():
        return f"{filename} was not found."

    return path.read_text(encoding="utf-8")


def build_prompt(repo_root: Path) -> str:
    orchestrator = AdvisoryOrchestrator(repo_root)

    task = orchestrator.create_task(
        agent="architect",
        objective=(
            "Produce the complete implementation blueprint for the "
            "Director-approved CryptoTrace V1 architecture."
        ),
        task_id="implementation-architecture-003",
    )

    instructions = orchestrator.proposal_instructions(task)

    project_specification = load_file(repo_root, "AGENTS.md")

    adr = load_file(
        repo_root,
        "ADR-001-CryptoTrace-V1-Architecture.md",
    )

    return f"""
{instructions}

============================================================
DIRECTOR-APPROVED ARCHITECTURE
============================================================

ADR-001 is APPROVED.

The original nine architectural questions are CLOSED.

Do NOT reopen them.
Do NOT ask the Director to answer them again.
Do NOT replace an approved decision with a new preference.

If you discover a genuine contradiction in the approved
architecture, identify it clearly under:

DIRECTOR DECISION REQUIRED

Otherwise resolve implementation details yourself and explain
your reasoning.

============================================================
ADR-001
============================================================

{adr}

============================================================
PROJECT SPECIFICATION
============================================================

{project_specification}

============================================================
YOUR ROLE
============================================================

You are the CryptoTrace V1 Principal Implementation Architect.

The product-discovery and decision phase is complete.

Your job is to translate the approved architecture into a
concrete, dependency-aware implementation blueprint.

You are NOT an implementation agent.

DO NOT write production code.
DO NOT modify files.
DO NOT provide large code blocks.
DO NOT claim that anything has already been implemented.

The implementation agents will use your blueprint later.

============================================================
MANDATORY ARCHITECTURE PRINCIPLES
============================================================

1. CryptoTrace's deterministic Risk & Decision Engine is the
   authoritative source of risk score, risk level, and triggered
   rules.

2. Nemotron explains approved deterministic results and retrieved
   evidence. Nemotron does NOT calculate or override authoritative
   risk.

3. Nemotron receives a Structured Evidence Packet.

4. Nemotron does NOT receive unrestricted database access.

5. Evidence must preserve provenance and Evidence IDs.

6. The system must distinguish:

   - observed evidence
   - deterministic/computed results
   - attribution
   - investigator annotation
   - AI interpretation

7. Blockchain metadata is untrusted data and must never be treated
   as executable instructions.

8. AI failure must NOT stop the underlying investigation.

9. If AI validation fails, the AI response must not be presented
   as trusted or validated.

10. Risk and Attribution MUST NOT form a circular dependency.

11. Neo4j is authoritative for graph representation and traversal.
    Neo4j is NOT the universal source of truth for every
    application record.

12. PostgreSQL owns application persistence where appropriate,
    including investigation state, evidence records, risk results,
    attribution records, and audit information.

============================================================
APPROVED V1 IMPLEMENTATION FLOW
============================================================

Ethereum fixture
    ↓
Provider abstraction
    ↓
Normalization
    ↓
Evidence creation
    ↓
Graph persistence
    ↓
Bounded traversal
    ↓
Suspicious-path detection
    ↓
Deterministic risk
    ↓
Attribution evidence
    ↓
FastAPI
    ↓
React investigator UI
    ↓
Structured Evidence Packet
    ↓
Nemotron
    ↓
AI validation
    ↓
Human verification

============================================================
ARCHITECTURE REQUIREMENTS
============================================================

The blueprint must define the following areas.

1. Architecture Overview

Explain the complete V1 system and data flow.

Clearly identify authoritative boundaries.

2. System Dependency Graph

Show dependencies between components.

Explicitly identify:

- foundations
- downstream components
- integration boundaries
- parallelizable work

There MUST NOT be a circular dependency between Risk
and Attribution.

3. Source-of-Truth Model

Explicitly define ownership for:

- raw blockchain observations
- normalized transactions
- graph data
- evidence
- investigations
- risk results
- attribution
- annotations
- AI responses
- validation results

Do not describe Neo4j as the universal source of truth.

4. Domain and Data Contracts

Define conceptual contracts for:

- transaction
- wallet/address
- normalized transaction
- graph node
- graph relationship
- evidence
- investigation
- risk result
- attribution result
- annotation
- Structured Evidence Packet
- Nemotron response
- validation result

For each explain:

- purpose
- important fields/concepts
- producer
- consumer
- provenance requirements

5. Backend Module Architecture

Define the exact V1 backend modules.

For every module explain:

- responsibility
- input
- output
- dependencies
- ownership
- tests
- forbidden responsibilities

6. Provider and Ethereum Architecture

Define:

- provider interface
- deterministic fixture provider
- future live provider boundary
- normalization boundary
- provider failure handling
- credential handling

Downstream services must depend on the provider interface,
not directly on a concrete provider.

7. Evidence Architecture

Explain how observations become evidence.

Every evidence record should preserve:

- Evidence ID
- source
- transaction/address reference
- timestamp where applicable
- provenance
- observed/computed distinction

Explain how evidence is retrieved for investigation and AI use.

8. Neo4j Architecture

Define:

- node types
- relationship types
- important properties
- indexes/constraints
- traversal boundaries

Use:

- 3-hop default
- 5-hop maximum for V1

Avoid unnecessary graph complexity.

9. Detection Architecture

Define suspicious-path and peel-chain detection.

Explain:

- inputs
- algorithms/rules
- outputs
- Evidence IDs
- deterministic behaviour

10. Risk Architecture

Define the deterministic Risk & Decision Engine.

Explain:

- risk parameters
- rules
- scoring
- risk levels
- triggered rules
- evidence references
- versioning
- missing-input behaviour

Explicitly state:

Nemotron does not calculate or override risk.

11. Attribution Architecture

Define:

- attribution candidates
- confidence
- source
- provenance
- Evidence IDs
- investigator verification

Attribution MUST NOT automatically mean confirmed identity.

Define the dependency direction so Risk and Attribution
do not become circular.

12. FastAPI Architecture

Define the V1 API surface.

For each endpoint/conceptual operation explain:

- purpose
- request
- response
- producer
- consumer
- errors

13. React Investigator Workspace

Define the UI for the first demonstrable slice.

Cover:

- address/wallet search
- investigation overview
- graph
- graph controls
- suspicious-path highlighting
- transaction details
- evidence panel
- risk panel
- attribution
- annotations
- Copilot
- loading states
- empty states
- errors
- AI validation state

The UI must clearly distinguish evidence from AI interpretation.

14. Structured Evidence Packet

Define exactly what enters the Nemotron boundary.

Include only investigation-relevant context.

Explain:

- Evidence IDs
- provenance
- transactions
- graph findings
- risk results
- attribution information
- investigation context

Explicitly state what MUST NOT be included.

15. Nemotron Architecture

V1 supports exactly:

1. Evidence Summarization
2. Risk-Factor Explanation
3. Evidence-Grounded Q&A

Explain:

- request construction
- context construction
- prompt boundary
- response schema
- timeout
- malformed response
- insufficient evidence
- contradictory evidence

Nemotron must not make autonomous:

- compliance decisions
- identity decisions
- attribution decisions
- risk decisions

16. AI Validation Architecture

Define the validation layer between Nemotron and the investigator.

Validate:

- Evidence IDs
- evidence-reference existence
- unsupported claims
- grounding
- contradictions
- insufficient evidence
- malicious instructions

Critical rule:

If validation fails, the AI answer must be:

- withheld
- marked untrusted
- or returned for correction

Validation failure MUST NOT stop the underlying investigation.

The investigator must still have access to:

- evidence
- deterministic analytics
- graph
- alerts
- risk result
- provenance

17. Agent Responsibilities

Define implementation contracts for:

A. Foundation / Domain Contracts
B. Ethereum Provider
C. Normalization + Evidence
D. Neo4j Graph
E. Traversal + Detection
F. Deterministic Risk Engine
G. Attribution
H. FastAPI
I. React UI
J. Structured Evidence Packet
K. Nemotron Copilot
L. AI Validation
M. Testing / E2E

For EVERY agent provide:

OWNER
RESPONSIBILITY
INPUT CONTRACT
OUTPUT CONTRACT
DEPENDENCIES
EXPECTED MODULES
TEST RESPONSIBILITY
WHAT IT MUST NOT CHANGE

Keep ownership boundaries explicit.

18. Implementation Order

Provide a precise dependency-aware implementation sequence.

Separate:

SEQUENTIAL WORK

from:

PARALLEL WORK

Show dependencies.

The order must allow the team to produce a working vertical
slice as early as reasonably possible.

Identify the earliest point at which the UI can consume a real
deterministic backend result.

19. Agent Approach Review Protocol

Before ANY implementation agent writes production code,
that agent MUST submit:

1. Proposed approach
2. Alternative approach, if meaningful
3. Trade-offs
4. Recommended approach
5. Why it fits ADR-001
6. Files/modules it intends to change
7. Dependencies
8. Tests it intends to add
9. Risks
10. Explicit statement of what it will NOT change

The Director must approve the approach BEFORE coding begins.

Agents must not implement based only on their own assumptions.

20. V1 Exclusions

List explicitly deferred features.

At minimum include:

- unrestricted database querying through AI
- autonomous attribution
- autonomous identity confirmation
- autonomous compliance decisions
- AI-generated authoritative risk scores
- future-crime prediction
- autonomous investigative actions
- unnecessary multi-chain expansion
- unnecessary distributed-service complexity

Implementation agents MUST NOT expand V1 scope without
Director approval.

21. Testing Strategy

Define the V1 testing strategy.

Cover:

- unit tests
- integration tests
- E2E tests
- deterministic fixtures
- provider failures
- graph traversal
- detection regression
- risk regression
- attribution
- evidence grounding
- Evidence ID validation
- unsupported AI claims
- hallucination
- prompt injection
- malformed AI responses
- AI timeout
- AI outage
- oversized context

Primary AI quality measures must include:

- unsupported-claim rate
- Evidence ID/reference validity
- grounding accuracy

Explain what constitutes a test failure.

22. Vertical Slice Acceptance Criteria

Define objective, testable acceptance criteria for:

wallet
→ transaction
→ evidence
→ graph
→ traversal
→ detection
→ risk
→ attribution
→ API
→ UI
→ Structured Evidence Packet
→ Nemotron
→ validation
→ investigator verification

Each criterion must be observable and testable.

The deterministic portion of the vertical slice must work using
Ethereum fixture data without requiring live blockchain access.

AI availability must NOT be required for the deterministic
investigation portion.

23. Risks and Trade-offs

Identify the most important V1 architectural and implementation
risks.

For each provide:

- risk
- impact
- mitigation

Keep the list focused.

Do not introduce unnecessary infrastructure or complexity.

24. DIRECTOR DECISION REQUIRED

Only list decisions that genuinely cannot be resolved from
ADR-001 and the approved architecture.

Do NOT reopen the original nine questions.

If no additional decision is required, write exactly:

No additional Director decision is required.

============================================================
FINAL CONSISTENCY CHECK
============================================================

Before producing the proposal, verify internally:

- no circular dependencies
- no unrestricted Nemotron database access
- no AI-generated authoritative risk
- provenance exists
- Evidence IDs exist
- observed/computed/AI distinctions are preserved
- AI validation is separate from deterministic analytics
- AI failure does not stop investigation
- Neo4j is not incorrectly declared universal source of truth
- provider abstraction is preserved
- V1 scope is respected
- implementation order is dependency-aware
- all 24 sections are present
- vertical slice acceptance criteria are testable

Do not stop early.

Complete all 24 sections.

============================================================
FINAL REQUIREMENT
============================================================

This is a proposal for human review.

Do not implement anything.

Do not claim that components have already been built.

End with exactly:

STATUS: WAITING_FOR_HUMAN_APPROVAL
"""


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent

    api_key = os.environ.get("NVIDIA_API_KEY")

    if not api_key:
        raise RuntimeError(
            "NVIDIA_API_KEY is not set in the current environment."
        )

    client = OpenAI(
        base_url=NVIDIA_BASE_URL,
        api_key=api_key,
    )

    prompt = build_prompt(repo_root)

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are the CryptoTrace Principal Architect. "
                    "ADR-001 has already been approved by the "
                    "Project Director. Work in implementation-planning "
                    "advisory mode. Never implement production code "
                    "without explicit human approval."
                ),
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        temperature=0.2,
        max_tokens=6000,
    )

    print("=" * 70)
    print("CRYPTOTRACE V1 IMPLEMENTATION ARCHITECT")
    print("=" * 70)
    print()
    print(response.choices[0].message.content)
    print()
    print("=" * 70)
    print("STATUS: WAITING_FOR_HUMAN_APPROVAL")
    print("=" * 70)


if __name__ == "__main__":
    main()