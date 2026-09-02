\# ADR-001 — CryptoTrace V1 Architecture \& Engineering Decisions



\*\*Status:\*\* Proposed for Director Approval  

\*\*Date:\*\* 2026-08-29  

\*\*Decision scope:\*\* V1 demonstrable end-to-end investigation slice  

\*\*Decision authority:\*\* Project Director / Human decision-makers



\---



\## 1. Context



CryptoTrace AI is an evidence-first cryptocurrency fraud investigation and transaction-tracing platform.



The team has completed the decision/proposal stage for the nine open architectural questions. The project operating specification requires:



\- agents to analyze and propose approaches before implementation;

\- humans to review and approve decisions;

\- observed evidence, computed results, investigator annotations, attribution claims, and AI inference to remain distinguishable;

\- one complete vertical slice to be built before expanding horizontally;

\- a modular monolith rather than premature microservices.



This ADR consolidates the nine decisions into the V1 implementation baseline.



The target V1 loop is:



```text

Wallet

&#x20; ↓

Transaction Retrieval

&#x20; ↓

Normalization + Evidence

&#x20; ↓

Graph Construction

&#x20; ↓

Bounded K-Hop Traversal

&#x20; ↓

Suspicious-Path / Peel-Chain Detection

&#x20; ↓

Deterministic Risk

&#x20; ↓

Attribution Evidence

&#x20; ↓

Investigator UI

&#x20; ↓

Evidence-Grounded Nemotron

&#x20; ↓

Validation

&#x20; ↓

Human Verification

```



\---



\# 2. Decisions



\## Decision 1 — Blockchain Prioritisation



\### Decision



\*\*Ethereum/EVM is the V1 implementation target.\*\*



The internal provider and data contracts must remain chain-agnostic so Bitcoin and other chains can be added later without rewriting graph, evidence, risk, or UI layers.



\### Why



\- Ethereum provides a practical first environment for wallet/transaction graph demonstration.

\- The existing project contracts already use Ethereum as the canonical V1 example.

\- A single chain keeps the first vertical slice narrow.

\- Chain-agnostic interfaces prevent the V1 implementation from becoming permanently Ethereum-specific.



\### V1 scope



```text

Supported now:

&#x20;   Ethereum / EVM



Designed for later:

&#x20;   Bitcoin

&#x20;   Additional EVM-compatible chains

```



\### Constraint



Do not implement multiple chain adapters merely to demonstrate architectural flexibility.



\---



\## Decision 2 — Data Source Strategy



\### Decision



\*\*Use a hybrid provider architecture:\*\*



1\. deterministic synthetic fixtures for development, testing and repeatable demos;

2\. a provider abstraction for live blockchain data;

3\. a live RPC/indexed provider can be added behind that interface without changing downstream services.



\### Why



The investigation pipeline must be reproducible without depending on external provider availability.



The provider abstraction also isolates:



\- rate limits;

\- provider failures;

\- credentials;

\- normalization differences;

\- future provider replacement.



\### Required boundary



```text

EvidenceProvider

&#x20;     │

&#x20;     ├── Fixture Provider

&#x20;     │

&#x20;     └── Live Provider

&#x20;             ↓

&#x20;       Normalization

&#x20;             ↓

&#x20;      Evidence Objects

```



Downstream graph/risk/UI code must not depend directly on a concrete provider.



\### Security



Secrets belong in environment configuration and must never be committed.



\---



\## Decision 3 — Graph Depth



\### Decision



\*\*3 hops is the V1 default. 5 hops is the V1 maximum.\*\*



The traversal interface should accept a bounded depth parameter, but the backend must enforce the V1 ceiling.



\### Why



A bounded traversal provides:



\- predictable performance;

\- understandable investigator results;

\- manageable graph visualization;

\- protection against accidental graph explosion;

\- deterministic test cases.



\### V1 behaviour



```text

Default: 3 hops

Maximum: 5 hops

```



The UI may allow the investigator to choose depth within the permitted range.



Higher limits are a future performance-tested decision, not a V1 assumption.



\---



\## Decision 4 — Risk-Score Formula



\### Decision



\*\*V1 uses a deterministic, explainable weighted-rule risk engine.\*\*



The risk engine is authoritative for the CryptoTrace risk score.



Machine-learning/GNN scoring is explicitly deferred to a later phase.



\### Why



The first slice must provide:



\- reproducible results;

\- explainable reasons;

\- evidence-linked scoring;

\- deterministic regression tests;

\- clear investigator review.



The project may later add GNN/ML models, but those must not silently replace the authoritative V1 scoring behaviour.



\### Required result



A risk result must include at minimum:



```text

address

score

risk level

triggered rules/reasons

model/rule version

supporting evidence IDs

```



\### Principle



```text

Risk Engine → calculates

Evidence → supports

Nemotron → explains

Human → verifies

```



Nemotron must never independently generate or override the authoritative risk score.



\---



\## Decision 5 — Attribution



\### Decision



\*\*Use evidence-tiered candidate attribution.\*\*



Attribution must be presented as a claim supported by source and provenance, not as absolute identity.



\### V1 output



An attribution result should include:



```text

candidate entity

category

confidence

source

timestamp

supporting evidence IDs

attribution tier

```



\### UI semantics



The UI must distinguish:



```text

Candidate attribution

&#x20;       ≠

Confirmed identity

```



High confidence does not remove the investigator's verification responsibility.



External intelligence and similarity signals must not by themselves become definitive attribution.



\---



\## Decision 6 — UI Workflow



\### Decision



\*\*Build an interactive investigator workspace with a read/write investigator layer while keeping source evidence immutable.\*\*



The investigator should be able to:



\- enter/search a wallet;

\- inspect transactions;

\- explore the graph;

\- select nodes and edges;

\- highlight suspicious paths;

\- inspect evidence;

\- inspect risk factors;

\- inspect attribution provenance;

\- add investigator notes/annotations;

\- prepare the investigation for case/report workflows.



\### Critical UI distinction



The interface must visually distinguish:



```text

Observed blockchain evidence

Computed/system analysis

Attribution evidence

Investigator annotation

AI-generated explanation

```



Annotations must never look like blockchain facts.



\### V1 UI priority



For the first vertical slice, prioritize:



```text

Wallet → Graph → Suspicious Path → Risk → Evidence

```



Case management/reporting can expand after this path works end-to-end.



\---



\## Decision 7 — AI Copilot Scope



\### Decision



\*\*V1 Nemotron supports three capabilities:\*\*



1\. Evidence Summarization

2\. Risk-Factor Explanation

3\. Evidence-Grounded Q\&A



\### Evidence Summarization



Examples:



```text

Summarize the evidence for this wallet.

What are the key findings?

```



\### Risk-Factor Explanation



Examples:



```text

Why was this wallet flagged high risk?

Which transactions contributed to the score?

```



Nemotron explains deterministic risk results; it does not calculate them.



\### Evidence-Grounded Q\&A



Examples:



```text

What happened between these wallets?

Which transactions connect them?

When did this activity occur?

```



Answers must be grounded in the supplied investigation context.



\### Context boundary



Nemotron receives a \*\*Structured Evidence Packet\*\*, not unrestricted database access.



The packet must preserve:



\- evidence IDs;

\- provenance;

\- observed facts;

\- computed results;

\- attribution information;

\- relevant investigation context.



\### Out of scope for V1



\- autonomous ownership determination;

\- guilt conclusions;

\- autonomous sanctions/AML decisions;

\- AI-generated risk scores;

\- unrestricted database querying;

\- future-crime prediction;

\- autonomous investigative actions.



\### Failure rule



If evidence is missing or contradictory, Nemotron must qualify the answer rather than inventing a conclusion.



\---



\## Decision 8 — Deployment Model



\### Decision



\*\*Use Docker Compose for the V1 local development/demo environment.\*\*



The architecture remains a modular monolith.



The expected infrastructure boundary is:



```text

Frontend

&#x20;  ↓

FastAPI application

&#x20;  ↓

PostgreSQL

Neo4j

Qdrant

Nemotron/provider integration

```



\### Why



Docker Compose provides:



\- reproducible local setup;

\- consistent service versions;

\- simple dependency management;

\- easy demonstration;

\- a path toward later deployment without prematurely introducing Kubernetes/microservices.



\### Required configuration



Use:



```text

.env.example   ← committed

.env           ← local only, ignored

```



No credentials or API keys are committed.



\---



\## Decision 9 — Testing Strategy



\### Decision



\*\*Use layered deterministic testing with pytest plus AI-specific grounding/security/failure evaluation.\*\*



\### Layer 1 — Unit tests



Test:



\- transaction parsing;

\- normalization;

\- malformed input;

\- timestamps;

\- graph query construction;

\- traversal boundaries;

\- suspicious-path detection;

\- risk calculation;

\- attribution validation;

\- evidence packet construction.



\### Layer 2 — Integration tests



Test:



\- API ↔ graph;

\- API ↔ evidence;

\- API ↔ risk;

\- API ↔ attribution;

\- API ↔ AI;

\- Qdrant retrieval when introduced;

\- database persistence.



\### Layer 3 — End-to-end



The critical E2E path is:



```text

Synthetic transactions

&#x20;→ ingestion

&#x20;→ normalization

&#x20;→ Neo4j

&#x20;→ 3-hop traversal

&#x20;→ suspicious-path detection

&#x20;→ risk

&#x20;→ attribution

&#x20;→ React graph

&#x20;→ evidence inspection

&#x20;→ Copilot

&#x20;→ evidence export

```



\### AI-specific tests



Must include:



\- unsupported claims;

\- fabricated Evidence IDs;

\- insufficient evidence;

\- contradictory evidence;

\- incorrect interpretation;

\- prompt injection through malicious blockchain metadata;

\- secret leakage attempts;

\- attempts to override deterministic risk;

\- malformed model responses;

\- oversized context;

\- Nemotron timeout/outage.



\### Quality focus



Track:



```text

unsupported-claim rate

Evidence-ID validity

grounding accuracy

risk consistency

false positives / false negatives

traversal latency

AI inference latency

```



\### Resilience requirement



\*\*Nemotron failure must not stop the investigation.\*\*



Graph, evidence, alerts and deterministic risk must remain available if the AI service is unavailable.



\---



\# 3. Consolidated V1 Architecture



```text

&#x20;                   ┌──────────────────────┐

&#x20;                   │    React + TS UI     │

&#x20;                   │  Investigator View   │

&#x20;                   └──────────┬───────────┘

&#x20;                              │

&#x20;                             REST

&#x20;                              │

&#x20;                   ┌──────────▼───────────┐

&#x20;                   │       FastAPI        │

&#x20;                   │   Modular Monolith   │

&#x20;                   └──────────┬───────────┘

&#x20;                              │

&#x20;         ┌────────────────────┼────────────────────┐

&#x20;         │                    │                    │

&#x20;         ▼                    ▼                    ▼

&#x20;  Ingestion Layer       Graph / Forensics     Risk Engine

&#x20;         │                    │                    │

&#x20;         ▼                    ▼                    │

&#x20;  Evidence Objects         Neo4j                  │

&#x20;         │                    │                    │

&#x20;         └────────────────────┼────────────────────┘

&#x20;                              ▼

&#x20;                    Structured Evidence

&#x20;                          Packet

&#x20;                              │

&#x20;                ┌─────────────┴─────────────┐

&#x20;                ▼                           ▼

&#x20;          Attribution                  Nemotron

&#x20;          + provenance                Copilot

&#x20;                │                           │

&#x20;                └─────────────┬─────────────┘

&#x20;                              ▼

&#x20;                         AI Validator

&#x20;                              │

&#x20;                              ▼

&#x20;                        Investigator

```



\---



\# 4. V1 Vertical Slice



We will NOT build every planned feature simultaneously.



The first demonstrable slice is:



```text

1\. Synthetic Ethereum transactions

&#x20;            ↓

2\. Provider interface + fixture provider

&#x20;            ↓

3\. Normalize transactions

&#x20;            ↓

4\. Store wallet graph in Neo4j

&#x20;            ↓

5\. Traverse up to 3 hops

&#x20;            ↓

6\. Detect a suspicious peel-chain pattern

&#x20;            ↓

7\. Calculate deterministic risk

&#x20;            ↓

8\. Return evidence-linked reasons

&#x20;            ↓

9\. Display graph in React/Cytoscape

&#x20;            ↓

10\. Display risk + evidence

&#x20;            ↓

11\. Send Structured Evidence Packet to Nemotron

&#x20;            ↓

12\. Explain the result

&#x20;            ↓

13\. Validate Evidence IDs / grounding

&#x20;            ↓

14\. Investigator verifies

```



This follows the project's central principle:



> Build one complete investigation path first; then expand horizontally.



\---



\# 5. What Is Explicitly Deferred



The following are \*\*not V1 blockers\*\*:



\- Bitcoin implementation;

\- GNN-based risk scoring;

\- unrestricted multi-chain ingestion;

\- large graph traversal beyond 5 hops;

\- autonomous attribution;

\- unrestricted AI database access;

\- autonomous investigative actions;

\- Kubernetes/microservices;

\- advanced OSINT automation;

\- production-scale observability;

\- full legal/statutory workflow automation.



\---



\# 6. Implementation Rules After Approval



Once this ADR is approved:



\### Rule 1



No implementation agent may silently change an ADR decision.



\### Rule 2



If an implementation discovers a decision is technically impossible or materially flawed, the agent must stop at the affected boundary and submit a change proposal.



\### Rule 3



Every implementation agent must first provide:



```text

APPROACH

WHY

ALTERNATIVES CONSIDERED

TRADE-OFFS

RISKS

FILES / INTERFACES TO CHANGE

TEST PLAN

```



Only after human approval does implementation begin.



\### Rule 4



Every vertical slice must remain runnable with deterministic fixtures.



\### Rule 5



Every evidence-backed conclusion must remain traceable to provenance.



\---



\# 7. Approval Checklist



The Director should explicitly approve or modify:



\- \[ ] Decision 1 — Ethereum/EVM first

\- \[ ] Decision 2 — Hybrid provider + deterministic fixtures

\- \[ ] Decision 3 — 3-hop default / 5-hop V1 ceiling

\- \[ ] Decision 4 — Deterministic weighted risk

\- \[ ] Decision 5 — Evidence-tiered attribution

\- \[ ] Decision 6 — Interactive investigator UI + immutable source evidence

\- \[ ] Decision 7 — Grounded Nemotron with three V1 capabilities

\- \[ ] Decision 8 — Docker Compose modular monolith

\- \[ ] Decision 9 — Layered pytest + AI/security/resilience testing



\---



\# 8. Final Decision



\*\*ADR-001 is the V1 implementation baseline once approved by the Project Director.\*\*



The next engineering action after approval is \*\*not "build everything."\*\*



The next action is:



> \*\*Create the V1 vertical-slice implementation plan and have each implementation agent submit its approach before coding.\*\*



Then implementation proceeds in dependency order:



```text

Foundation / Contracts

&#x20;       ↓

Provider + Synthetic Data

&#x20;       ↓

Normalization + Evidence

&#x20;       ↓

Neo4j Graph

&#x20;       ↓

Traversal + Detection

&#x20;       ↓

Risk Engine

&#x20;       ↓

FastAPI Integration

&#x20;       ↓

React Graph / Investigator UI

&#x20;       ↓

Structured Evidence Packet

&#x20;       ↓

Nemotron

&#x20;       ↓

Validation

&#x20;       ↓

E2E Demonstration

```



\*\*Current ADR status: PROPOSED — AWAITING DIRECTOR APPROVAL\*\*



