\# CryptoTrace AI — Engineering Operating Specification



\## Project



Name: CryptoTrace AI



SIH Problem Statement: 183



Mission:



Build an evidence-first cryptocurrency fraud investigation and

transaction tracing platform for law-enforcement investigators.



The platform must allow an investigator to:



1\. Enter a cryptocurrency wallet/address.

2\. Retrieve and normalize transaction data.

3\. Construct a transaction graph.

4\. Trace funds across multiple hops.

5\. Detect suspicious transaction patterns.

6\. Calculate an explainable risk score.

7\. Attribute addresses/clusters to exchanges or known entities when

&#x20;  sufficient evidence exists.

8\. Enrich investigations with threat intelligence.

9\. Visualize the investigation interactively.

10\. Ask an NVIDIA Nemotron-powered investigation copilot questions

&#x20;   about the evidence.

11\. Generate an evidence-backed investigation report.



\---



\# 1. CORE ENGINEERING PRINCIPLE



CryptoTrace is:



&#x20;   EVIDENCE-FIRST

&#x20;   AI-ASSISTED

&#x20;   HUMAN-VERIFIED



The AI must NEVER be treated as the source of truth.



Blockchain facts, graph relationships, detection results,

attribution sources, model outputs and investigator conclusions

must remain distinguishable.



The LLM explains evidence.



The LLM does NOT invent evidence.



\---



\# 2. DEVELOPMENT PHILOSOPHY



Use vertical-slice development.



DO NOT build every backend module independently and connect them

at the end.



Instead, every major phase should produce a working end-to-end

capability.



Preferred development flow:



&#x20;   Requirement

&#x20;       ↓

&#x20;   Architecture

&#x20;       ↓

&#x20;   Data contract

&#x20;       ↓

&#x20;   Implementation

&#x20;       ↓

&#x20;   Unit tests

&#x20;       ↓

&#x20;   Integration tests

&#x20;       ↓

&#x20;   UI integration

&#x20;       ↓

&#x20;   Demonstration



\---



\# 3. ARCHITECTURE



Initially use a MODULAR MONOLITH.



Do NOT introduce microservices unless there is a demonstrated

technical requirement.



Architecture:



&#x20;   React + TypeScript

&#x20;           |

&#x20;           | REST/WebSocket

&#x20;           ↓

&#x20;       FastAPI

&#x20;           |

&#x20;   ┌───────┼────────┐

&#x20;   ↓       ↓        ↓

&#x20; Graph   Risk     AI/Copilot

&#x20;   ↓       ↓        ↓

&#x20;Neo4j  ML Engine  Nemotron

&#x20;   |

&#x20;PostgreSQL

&#x20;   |

&#x20;Threat Intelligence / Qdrant



Blockchain ingestion feeds the graph and structured databases.



\---



\# 4. REPOSITORY STRUCTURE



Use this target structure:



CryptoTrace/

│

├── backend/

│   ├── app/

│   │   ├── api/

│   │   ├── core/

│   │   ├── models/

│   │   ├── schemas/

│   │   ├── services/

│   │   ├── ingestion/

│   │   ├── graph/

│   │   ├── tracing/

│   │   ├── detection/

│   │   ├── attribution/

│   │   ├── risk/

│   │   ├── intelligence/

│   │   ├── ai/

│   │   └── evidence/

│   │

│   └── tests/

│

├── frontend/

│   └── src/

│       ├── components/

│       ├── pages/

│       ├── features/

│       ├── graph/

│       ├── investigation/

│       ├── api/

│       ├── hooks/

│       └── types/

│

├── ml/

│   ├── datasets/

│   ├── preprocessing/

│   ├── features/

│   ├── models/

│   ├── training/

│   ├── inference/

│   └── evaluation/

│

├── data/

│   ├── raw/

│   ├── normalized/

│   └── synthetic/

│

├── tests/

│   ├── integration/

│   └── e2e/

│

├── docs/

│   ├── architecture/

│   ├── api/

│   ├── decisions/

│   └── investigation/

│

├── scripts/

│

├── docker/

│

├── docker-compose.yml

├── .env.example

├── .gitignore

├── AGENTS.md

└── README.md



Adapt this structure to the existing repository rather than

destroying or unnecessarily replacing existing working code.



\---



\# 5. TECHNOLOGY STACK



\## Backend



Python 3.11+



FastAPI



Pydantic v2



SQLAlchemy



Alembic



Pytest



httpx



Reason:



Python provides the strongest ecosystem for blockchain processing,

graph analytics and machine learning.



FastAPI provides typed, documented and high-performance APIs.



Pydantic provides strict validation.



\---



\# 6. GRAPH DATABASE



Use Neo4j.



Represent:



&#x20;   Wallet

&#x20;   Transaction

&#x20;   Address/Entity

&#x20;   Exchange

&#x20;   Investigation



Relationships may include:



&#x20;   SENT

&#x20;   RECEIVED

&#x20;   INPUT\_TO

&#x20;   OUTPUT\_TO

&#x20;   ATTRIBUTED\_TO

&#x20;   RELATED\_TO

&#x20;   PART\_OF\_CLUSTER



Every important graph relationship should retain provenance where

appropriate.



Neo4j is preferred because cryptocurrency investigations are

fundamentally relationship/path-analysis problems.



Do not replace Neo4j with PostgreSQL for graph traversal.



PostgreSQL is used for structured application metadata.



\---



\# 7. FRONTEND



Use:



React



TypeScript



Vite



Cytoscape.js



Reason:



React provides component architecture.



TypeScript reduces frontend integration errors.



Cytoscape.js is specifically suited for interactive network graphs.



The UI must prioritize investigator workflow over visual effects.



\---



\# 8. ML ARCHITECTURE



Do NOT start with a GNN.



First establish deterministic baselines.



Detection pipeline:



&#x20;   Transaction data

&#x20;         ↓

&#x20;   Feature extraction

&#x20;         ↓

&#x20;   Rule-based detection

&#x20;         ↓

&#x20;   Classical ML baseline

&#x20;         ↓

&#x20;   GNN

&#x20;         ↓

&#x20;   Ensemble / risk engine



Possible features:



\- transaction frequency

\- transaction amount

\- amount variance

\- wallet age

\- inbound/outbound ratio

\- fan-in

\- fan-out

\- transaction timing

\- hop distance

\- path length

\- address reuse

\- temporal bursts

\- peel-chain characteristics

\- interaction with known entities



The GNN must demonstrate measurable improvement over the baseline.



Never claim "AI detected fraud" without defining what the model

actually predicts.



\---



\# 9. RISK ENGINE



Risk scoring must be explainable.



Example conceptual structure:



&#x20;   Risk Score

&#x20;       =

&#x20;   Behavioral Score

&#x20;   +

&#x20;   Graph Score

&#x20;   +

&#x20;   Pattern Score

&#x20;   +

&#x20;   Attribution Score

&#x20;   +

&#x20;   Intelligence Score



The exact mathematical formulation must be documented and

versioned.



Every score should expose contributing factors.



Example:



&#x20;   Risk Score: 87/100



&#x20;   Contributing evidence:



&#x20;   + Peel-chain pattern

&#x20;   + Rapid fund movement

&#x20;   + High fan-out

&#x20;   + Known-risk counterparty

&#x20;   + Suspicious temporal behavior



The investigator must be able to inspect why the score exists.



\---



\# 10. EVIDENCE SYSTEM



Every important conclusion must be traceable to evidence.



Evidence object should contain concepts such as:



&#x20;   evidence\_id

&#x20;   investigation\_id

&#x20;   evidence\_type

&#x20;   source

&#x20;   source\_reference

&#x20;   observed\_at

&#x20;   collected\_at

&#x20;   confidence

&#x20;   description

&#x20;   related\_transaction

&#x20;   related\_address

&#x20;   algorithm\_version

&#x20;   model\_version



Never silently modify evidence.



Maintain provenance.



\---



\# 11. ATTRIBUTION



Attribution is NOT the same as suspicion.



Do not state:



&#x20;   "This wallet belongs to Exchange X"



unless there is sufficient evidence.



Instead use:



&#x20;   "Potential attribution"



with:



&#x20;   confidence

&#x20;   source

&#x20;   supporting evidence

&#x20;   timestamp



Possible sources:



\- public exchange addresses

\- verified datasets

\- OSINT

\- investigator-provided labels

\- threat intelligence



\---



\# 12. THREAT INTELLIGENCE



Threat intelligence should enrich the investigation.



Use Qdrant only where semantic retrieval provides actual value.



Potential pipeline:



&#x20;   OSINT / reports

&#x20;         ↓

&#x20;   normalization

&#x20;         ↓

&#x20;   embeddings

&#x20;         ↓

&#x20;      Qdrant

&#x20;         ↓

&#x20;   relevant intelligence

&#x20;         ↓

&#x20;   investigation



Do not introduce vector search merely because it is an AI feature.



\---



\# 13. NVIDIA NEMOTRON



Use NVIDIA Nemotron as the Investigation Copilot.



Current development model:



&#x20;   nvidia/nemotron-3-nano-30b-a3b



Provider:



&#x20;   NVIDIA API



The architecture must allow the model to be changed through

configuration.



Do NOT hard-code the model throughout the application.



Use configuration such as:



&#x20;   NVIDIA\_API\_KEY

&#x20;   NVIDIA\_BASE\_URL

&#x20;   NVIDIA\_MODEL



The LLM may:



\- summarize evidence

\- explain transaction paths

\- answer investigator questions

\- explain risk factors

\- summarize suspicious behavior

\- generate report drafts

\- help formulate investigation queries



The LLM must NOT:



\- fabricate transactions

\- invent wallet ownership

\- invent exchange attribution

\- alter evidence

\- silently change risk scores

\- claim certainty where evidence is uncertain



\---



\# 14. AI OUTPUT CONTRACT



LLM-generated investigation responses should distinguish:



&#x20;   OBSERVED FACT

&#x20;   COMPUTED RESULT

&#x20;   MODEL INFERENCE

&#x20;   EXTERNAL INTELLIGENCE

&#x20;   INVESTIGATOR CONCLUSION



Example:



&#x20;   Observed:

&#x20;   Wallet A transferred 4.2 BTC to Wallet B.



&#x20;   Computed:

&#x20;   Wallet B participated in a 7-hop transaction path.



&#x20;   Model inference:

&#x20;   The behavior is consistent with a peel-chain pattern.



&#x20;   Intelligence:

&#x20;   Wallet C has an external attribution source.



&#x20;   Conclusion:

&#x20;   Investigator review recommended.



\---



\# 15. BLOCKCHAIN INGESTION



The ingestion layer must be modular.



Do not tightly couple the entire system to one RPC provider.



Architecture:



&#x20;   BlockchainProvider

&#x20;         ↓

&#x20;   RawTransaction

&#x20;         ↓

&#x20;   NormalizedTransaction

&#x20;         ↓

&#x20;   GraphPersistence



Provider interface should allow:



&#x20;   Bitcoin

&#x20;   Ethereum

&#x20;   Future chains



Handle:



\- RPC errors

\- rate limits

\- malformed responses

\- missing fields

\- duplicate transactions

\- reorgs

\- unconfirmed transactions

\- provider timeouts

\- pagination

\- retry logic



Never crash the entire application because one external request

failed.



\---



\# 16. SECURITY



Never commit:



&#x20;   API keys

&#x20;   passwords

&#x20;   tokens

&#x20;   private keys

&#x20;   credentials



Use environment variables.



Validate all API inputs.



Apply authentication/authorization architecture where appropriate.



Log security-relevant events.



Never expose raw secrets in logs.



\---



\# 17. TESTING REQUIREMENTS



Every significant module must have tests.



Minimum:



\- transaction parser tests

\- schema validation tests

\- graph persistence tests

\- Cypher traversal tests

\- tracing tests

\- detection tests

\- risk scoring tests

\- attribution tests

\- AI response validation tests

\- API tests

\- frontend critical-path tests



Test failure cases, not only successful cases.



\---



\# 18. NO FAKE FUNCTIONALITY



Do not create fake implementations that pretend to work.



If a feature cannot yet be implemented:



1\. clearly identify it

2\. define its interface

3\. explain the limitation

4\. create a controlled development stub only if necessary

5\. NEVER present the stub as production functionality



Synthetic data may be used for demonstration and testing, but it

must be explicitly labelled synthetic.



\---



\# 19. VERTICAL SLICE PRIORITY



Build in this order.



\## VERTICAL SLICE 1 — CORE INVESTIGATION



Goal:



An investigator enters an address and sees a transaction graph.



Flow:



&#x20;   Address

&#x20;     ↓

&#x20;   API

&#x20;     ↓

&#x20;   Transaction provider

&#x20;     ↓

&#x20;   Normalization

&#x20;     ↓

&#x20;   Neo4j

&#x20;     ↓

&#x20;   Graph query

&#x20;     ↓

&#x20;   FastAPI

&#x20;     ↓

&#x20;   React

&#x20;     ↓

&#x20;   Interactive graph



Definition of done:



\- address input works

\- transactions retrieved

\- data normalized

\- graph stored

\- graph queried

\- UI displays graph

\- errors handled

\- tests pass



\---



\# 20. VERTICAL SLICE 2 — FUND TRACING



Add:



\- multi-hop traversal

\- path highlighting

\- transaction timeline

\- inbound/outbound analysis

\- hop controls



Definition of done:



Investigator can select a wallet and trace funds across

configurable hops.



\---



\# 21. VERTICAL SLICE 3 — DETECTION



Add:



\- suspicious patterns

\- peel-chain detection

\- fan-in/fan-out analysis

\- rapid movement

\- temporal anomalies



Definition of done:



System produces explainable detection findings.



\---



\# 22. VERTICAL SLICE 4 — RISK



Add:



\- risk score

\- contributing factors

\- confidence

\- evidence references



Definition of done:



Selecting an entity displays an explainable risk assessment.



\---



\# 23. VERTICAL SLICE 5 — ATTRIBUTION



Add:



\- known exchange labels

\- cluster matching

\- confidence

\- source references



Definition of done:



Potential entity attribution can be inspected with evidence.



\---



\# 24. VERTICAL SLICE 6 — NEMOTRON COPILOT



Add:



Investigator chat.



Example:



&#x20;   "Why is this wallet suspicious?"



&#x20;   "Trace the flow from this wallet."



&#x20;   "What are the strongest indicators?"



&#x20;   "Summarize this investigation."



Nemotron must receive structured evidence rather than unrestricted

raw database access.



Preferred architecture:



&#x20;   Investigator

&#x20;        ↓

&#x20;   FastAPI

&#x20;        ↓

&#x20;   Evidence retrieval

&#x20;        ↓

&#x20;   Structured context

&#x20;        ↓

&#x20;   Nemotron

&#x20;        ↓

&#x20;   Validated response

&#x20;        ↓

&#x20;   Investigator



\---



\# 25. VERTICAL SLICE 7 — REPORTING



Generate an investigation report containing:



\- investigation ID

\- target address

\- transaction summary

\- traced paths

\- suspicious patterns

\- risk score

\- attribution

\- evidence

\- model information

\- timestamps

\- investigator notes



Clearly distinguish AI-generated text from factual evidence.



\---



\# 26. DEVELOPMENT RULES FOR THE AI CODING AGENT



Before modifying code:



1\. Inspect relevant files.

2\. Understand existing architecture.

3\. Identify dependencies.

4\. Explain planned changes.

5\. Implement the smallest coherent change.

6\. Run tests.

7\. Fix failures.

8\. Report changed files.

9\. Report remaining risks.



Do not rewrite unrelated files.



Do not introduce unnecessary dependencies.



Do not create duplicate implementations.



Prefer existing project conventions.



\---



\# 27. GIT DISCIPLINE



Use small commits.



Suggested commits:



&#x20;   feat: initialize backend

&#x20;   feat: add transaction normalization

&#x20;   feat: add neo4j persistence

&#x20;   feat: add multi-hop tracing

&#x20;   feat: add risk engine

&#x20;   feat: add investigation graph UI

&#x20;   feat: add nemotron copilot

&#x20;   test: add tracing tests



Never commit:



&#x20;   .env

&#x20;   secrets

&#x20;   API keys

&#x20;   private credentials



\---



\# 28. AI AGENT BEHAVIOR



You are an implementation agent.



You are NOT allowed to make major architectural changes without

explaining them.



When uncertain:



&#x20;   inspect → reason → propose → implement



not:



&#x20;   guess → rewrite



Prioritize correctness over code volume.



Prioritize demonstrable functionality over theoretical

complexity.



\---



\# 29. SIH DEMONSTRATION PRIORITY



The final demo must tell this story:



&#x20;   Criminal wallet

&#x20;         ↓

&#x20;   Transaction network

&#x20;         ↓

&#x20;   Multi-hop tracing

&#x20;         ↓

&#x20;   Suspicious pattern

&#x20;         ↓

&#x20;   Risk score

&#x20;         ↓

&#x20;   Attribution evidence

&#x20;         ↓

&#x20;   AI explanation

&#x20;         ↓

&#x20;   Investigation report



The system should feel like one integrated investigator platform,

not a collection of disconnected technologies.



\---



\# 30. DEFINITION OF DONE



A feature is DONE only when:



\[ ] implementation exists

\[ ] types/schemas exist

\[ ] error handling exists

\[ ] tests exist

\[ ] tests pass

\[ ] API contract documented

\[ ] UI integrated where applicable

\[ ] logging is appropriate

\[ ] security checked

\[ ] no secrets committed

\[ ] README/docs updated

\[ ] demo path works



\---



\# 31. GOLDEN RULE



Do not optimize for:



&#x20;   number of files

&#x20;   number of technologies

&#x20;   amount of generated code

&#x20;   complexity



Optimize for:



&#x20;   correctness

&#x20;   explainability

&#x20;   evidence

&#x20;   reliability

&#x20;   investigator usability

&#x20;   measurable innovation

&#x20;   working demonstration

