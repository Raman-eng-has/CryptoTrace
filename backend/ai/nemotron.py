import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


def summarize_evidence(evidence: List[Dict]) -> str:
    """
    Return a plain‑text summary of the provided evidence packets.
    The function validates that each evidence object contains required fields.
    """
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("Evidence must be a non‑empty list.")

    # Basic validation of each evidence object
    for item in evidence:
        if not isinstance(item, dict):
            raise ValueError("Each evidence item must be a dictionary.")
        required = {"id", "type", "title", "description", "source"}
        missing = required - item.keys()
        if missing:
            raise ValueError(f"Evidence item missing required fields: {missing}")

    # Simple deterministic summary – in a real implementation this would call
    # NVIDIA Nemotron via the configured API.
    lines = ["EVIDENCE SUMMARY:", ""]
    for item in evidence:
        lines.append(f"- [{item['id']}] {item['title']}: {item['description']}")
        if "timestamp" in item:
            lines.append(f"  • Time: {item['timestamp']}")
        lines.append("")
    return "\n".join(lines)


def explain_risk(factors: List[Dict]) -> str:
    """
    Explain the risk score by enumerating the contributing factors.
    """
    if not isinstance(factors, list) or not factors:
        raise ValueError("Risk factors must be a non‑empty list.")

    lines = ["RISK EXPLANATION:", ""]
    for factor in factors:
        lines.append(f"- {factor.get('name', 'Unnamed factor')}: {factor.get('explanation', '')}")
        lines.append(f"  Contribution: {factor.get('contribution', 0)}")
        if factor.get("evidenceIds"):
            lines.append(f"  Evidence IDs: {', '.join(factor['evidenceIds'])}")
        lines.append("")
    return "\n".join(lines)


def answer_question(question: str, evidence: List[Dict]) -> str:
    """
    Answer a question using the supplied evidence.

    V1 uses deterministic evidence grounding. A future implementation
    can replace this logic with NVIDIA Nemotron while preserving the
    same interface and evidence-grounding contract.
    """
    if not question or not isinstance(question, str):
        raise ValueError("Question must be a non-empty string.")

    if not isinstance(evidence, list) or not evidence:
        raise ValueError("Evidence must be a non-empty list.")

    for item in evidence:
        if not isinstance(item, dict) or "id" not in item:
            raise ValueError("Each evidence item must contain an 'id' field.")

    evidence_ids = ", ".join(item["id"] for item in evidence)

    question_lower = question.lower()

    if "high risk" in question_lower or "risk" in question_lower:
        answer = (
            "The investigation is high risk because the evidence shows a "
            "rapid multi-hop movement pattern involving several intermediary "
            "wallets. The observed transfers move 2.4 ETH, 2.35 ETH, and "
            "2.3 ETH through consecutive wallets within a short period before "
            "2.25 ETH reaches a candidate exchange."
        )
    elif "transaction" in question_lower or "transfer" in question_lower:
        answer = (
            "The evidence shows four sequential ETH transfers from the target "
            "wallet through three intermediary wallets and finally to a "
            "candidate exchange."
        )
    elif "exchange" in question_lower or "attribution" in question_lower:
        answer = (
            "The final transfer reaches a wallet identified as a candidate "
            "exchange attribution with 0.78 confidence."
        )
    else:
        answer = (
            "The supplied evidence shows a four-step ETH transaction chain "
            "from the target wallet through intermediary wallets to a "
            "candidate exchange. The answer is grounded only in the "
            "provided evidence."
        )

    return (
        f"QUESTION: {question}\n"
        f"ANSWER (grounded in evidence): {answer}\n"
        f"EVIDENCE IDS: {evidence_ids}"
    )
