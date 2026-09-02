import typing

# Simple data structures for risk calculation
class RiskFactor:
    def __init__(self, id: str, name: str, contribution: float, explanation: str, evidence_ids: list[str]):
        self.id = id
        self.name = name
        self.contribution = contribution
        self.explanation = explanation
        self.evidence_ids = evidence_ids

class RiskResult:
    def __init__(self, score: int, level: str, factors: list[RiskFactor]):
        self.score = score
        self.level = level
        self.factors = factors

def calculate_risk(investigation: dict) -> RiskResult:
    """Deterministic risk calculation based on investigation risk factors."""
    # Extract risk factors from the investigation payload
    factors_data = investigation.get('risk', {}).get('factors', [])
    
    # Compute total contribution and cap at 100
    total_contribution = sum(f['contribution'] for f in factors_data)
    score = min(100, int(total_contribution))
    
    # Determine risk level based on score thresholds
    if score >= 80:
        level = "high"
    elif score >= 50:
        level = "medium"
    elif score >= 30:
        level = "low"
    else:
        level = "critical"
    
    # Convert raw factor dicts to RiskFactor objects
    risk_factors = [
        RiskFactor(
            id=f['id'],
            name=f['name'],
            contribution=f['contribution'],
            explanation=f['explanation'],
            evidence_ids=f['evidenceIds']
        )
        for f in factors_data
    ]
    
    return RiskResult(score=score, level=level, factors=risk_factors)
