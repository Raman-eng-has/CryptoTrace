from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

from ..graph import construct_graph
from .risk_engine import calculate_risk

# Import investigation fixture
from ..data.investigation import get_investigation

router = APIRouter()


class EvidenceRequest(BaseModel):
    evidence: List[Dict[str, Any]]


@router.post("/graph")
async def get_graph(req: EvidenceRequest):
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
async def get_evidence_packet(request: EvidenceRequest):
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
