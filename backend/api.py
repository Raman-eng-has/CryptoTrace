import logging
from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from backend.graph import construct_graph
from backend.risk_engine import calculate_risk
from backend.ai.nemotron import summarize_evidence, explain_risk, answer_question

# Import investigation fixture
from backend.data.investigation import get_investigation

app = FastAPI()
router = APIRouter()


class EvidencePacket(BaseModel):
    evidence: List[Dict[str, Any]]

class ExplainRequest(BaseModel):
    factors: List[Dict[str, Any]]

class QuestionRequest(BaseModel):
    question: str
    evidence: List[Dict[str, Any]]

@router.post("/graph")
async def get_graph(req: EvidencePacket):
    try:
        graph = construct_graph(req.evidence)
        return graph
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/risk")
async def calculate_risk_endpoint(investigation: Dict[str, Any]):
    """Calculate deterministic risk for an investigation."""
    try:
        result = calculate_risk(investigation)
        # Convert RiskResult to serializable dict
        return {
            "score": result.score,
            "level": result.level,
            "factors": [
                {
                    "id": f.id,
                    "name": f.name,
                    "contribution": f.contribution,
                    "explanation": f.explanation,
                    "evidence_ids": f.evidence_ids,
                }
                for f in result.factors
            ],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/investigation")
async def get_investigation_endpoint():
    """Return a synthetic investigation package including risk, attribution, and evidence."""
    try:
        investigation = get_investigation()
        return investigation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evidence-packet")
async def get_evidence_packet(request: EvidencePacket):
    """Return the structured evidence packet (evidence list, risk, attribution)."""
    try:
        # For demo, reuse the same investigation data
        investigation = get_investigation()
        # Extract evidence, risk, attribution into a packet
        packet = {
            "evidence": investigation["evidence"],
            "risk": investigation["risk"],
            "attribution": investigation["attribution"],
        }
        return packet
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/summarize")
async def summarize_endpoint(packet: EvidencePacket):
    try:
        summary = summarize_evidence(packet.evidence)
        return {"summary": summary}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.exception("Unexpected error in summarize")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/explain")
async def explain_endpoint(req: ExplainRequest):
    try:
        explanation = explain_risk(req.factors)
        return {"explanation": explanation}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.exception("Unexpected error in explain")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/qa")
async def qa_endpoint(req: QuestionRequest):
    try:
        answer = answer_question(req.question, req.evidence)
        return {"answer": answer}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logging.exception("Unexpected error in qa")
        raise HTTPException(status_code=500, detail="Internal server error")

app.include_router(router)
