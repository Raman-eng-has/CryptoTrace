[architecture.md](https://github.com/user-attachments/files/31729946/architecture.md)
# Architecture Overview (V1)

## Vision
CryptoTrace AI is an evidence‑first platform that combines blockchain transaction graph analysis with NVIDIA Nemotron‑powered investigation assistance.

## Core Layers
1. **Frontend** – React/TypeScript investigator workspace
2. **Backend** – FastAPI modular monolith
3. **Graph Database** – Neo4j for wallet/transaction relationships
4. **AI Copilot** – Nemotron for evidence‑grounded explanations
5. **Risk Engine** – Deterministic, explainable scoring

## Vertical Slice Flow
Wallet → Transaction Retrieval → Normalization → Graph Construction → Traversal → Suspicious‑Path Detection → Deterministic Risk → Attribution Evidence → Investigator UI → Evidence‑Grounded Nemotron → Validation → Human Verification

## Principles
- Working end‑to‑end functionality over unnecessary complexity
- Vertical slices before horizontal expansion
- Never treat AI as authoritative risk engine
- Keep evidence and derived analysis distinguishable
- Human verification required for all conclusions
