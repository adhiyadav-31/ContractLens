"""Counterparty verification endpoint. Owned by Safa."""

from fastapi import APIRouter, HTTPException

from app.agents.due_diligence_agent import extract_counterparty, verify_counterparty
from app.database.mongodb import get_contract_by_id

router = APIRouter(prefix="/contracts", tags=["due_diligence"])


@router.get("/{contract_id}/due-diligence")
def get_due_diligence(contract_id: str):
    contract = get_contract_by_id(contract_id)
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found.")

    counterparty = extract_counterparty(contract.get("parties", []))
    return verify_counterparty(counterparty)
