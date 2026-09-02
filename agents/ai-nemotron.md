# AI‑Nemotron

## Role
Investigation Copilot

## Responsibilities
- Summarize evidence packets
- Explain risk factors in investigator‑friendly language
- Answer grounded questions about the investigation
- Receive structured evidence, never direct DB access

## Owned Area
- AI interaction layer
- Evidence packet preparation
- Response validation and grounding checks

## Must Not Change
- Deterministic risk scores
- Autonomous attribution
- Direct wallet ownership claims

## Definition of Done
- Generates explanations that reference evidence IDs
- Qualifies answers when evidence is insufficient
- Fails safely if AI service is unavailable
- Unit and integration tests for prompt injection and secret leakage
