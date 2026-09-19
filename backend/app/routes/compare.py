"""Version comparison endpoint. Owned by Safa."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database.mongodb import get_contract_by_id, save_comparison
from app.services.comparison_service import compare_contracts

router = APIRouter(prefix="/contracts", tags=["compare"])


class CompareRequest(BaseModel):
    contract_id_v1: str
    contract_id_v2: str


@router.post("/compare")
def compare_versions(request: CompareRequest):
    contract_v1 = get_contract_by_id(request.contract_id_v1)
    contract_v2 = get_contract_by_id(request.contract_id_v2)

    if contract_v1 is None or contract_v2 is None:
        raise HTTPException(status_code=404, detail="One or both contracts were not found.")

    result = compare_contracts(
        request.contract_id_v1,
        contract_v1.get("raw_text", ""),
        request.contract_id_v2,
        contract_v2.get("raw_text", ""),
    )

    save_comparison(
        {
            "contract_id_v1": request.contract_id_v1,
            "contract_id_v2": request.contract_id_v2,
            "changes": result["changes"],
        }
    )

    return result
