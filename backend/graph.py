from typing import List, Dict, Any


def construct_graph(evidence: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
    """
    Convert evidence objects into a transaction graph representation.
    Returns a dict with 'nodes' and 'edges' lists.
    """
    nodes: Dict[str, Dict] = {}
    edges: List[Dict] = []

    for ev in evidence:
        if ev.get("type") == "transaction":
            source = ev["source"]
            target = ev["target"]
            amount = ev.get("amount", 0)
            asset = ev.get("asset", "ETH")
            tx_id = ev["id"]

            # Ensure source and target nodes exist
            nodes.setdefault(source, {"id": source, "label": source[:6] + "..."})
            nodes.setdefault(target, {"id": target, "label": target[:6] + "..."})

            edges.append({
                "id": f"tx-{tx_id}",
                "source": source,
                "target": target,
                "amount": amount,
                "asset": asset,
                "timestamp": ev.get("timestamp", ""),
                "suspicious": ev.get("suspicious", False),
                "evidence_ids": ev.get("evidenceIds", []),
            })

    return {"nodes": list(nodes.values()), "edges": edges}
