"""Obligation-related endpoints. Owned by Safa."""

from fastapi import APIRouter, HTTPException

from app.database.mongodb import get_contract_by_id, get_obligations_for_contract
from app.services.alert_service import get_overdue_obligations, get_upcoming_obligations

router = APIRouter(prefix="/contracts", tags=["obligations"])


@router.get("/{contract_id}/obligations")
def get_obligations(contract_id: str):
    if get_contract_by_id(contract_id) is None:
        raise HTTPException(status_code=404, detail="Contract not found.")
    return get_obligations_for_contract(contract_id)


@router.get("/{contract_id}/timeline")
def get_timeline(contract_id: str):
    if get_contract_by_id(contract_id) is None:
        raise HTTPException(status_code=404, detail="Contract not found.")

    obligations = get_obligations_for_contract(contract_id)
    timeline = [
        {
            "obligation_id": o["obligation_id"],
            "date": o.get("deadline", {}).get("calculated_date"),
            "label": o.get("action"),
            "status": o.get("status"),
        }
        for o in obligations
        if o.get("deadline", {}).get("calculated_date")
    ]
    return sorted(timeline, key=lambda t: t["date"])


@router.get("/{contract_id}/obligations/status")
def get_obligation_status(contract_id: str):
    """Convenience endpoint: upcoming + overdue for a single contract."""
    if get_contract_by_id(contract_id) is None:
        raise HTTPException(status_code=404, detail="Contract not found.")

    obligations = get_obligations_for_contract(contract_id)
    return {
        "upcoming": get_upcoming_obligations(obligations),
        "overdue": get_overdue_obligations(obligations),
    }
