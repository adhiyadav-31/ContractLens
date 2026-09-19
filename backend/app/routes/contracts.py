"""Contract-related endpoints. Owned by Safa."""

import os
import uuid

from fastapi import APIRouter, HTTPException, UploadFile

from app.agents.contract_agent import analyze_contract
from app.agents.obligation_agent import extract_obligations
from app.agents.risk_agent import identify_review_flags
from app.database.mongodb import (
    get_contract_by_id,
    list_contracts,
    save_contract,
    save_obligations,
)
from app.services.pdf_service import extract_pages, extract_text_from_pdf
from app.services.rag_service import index_contract

router = APIRouter(prefix="/contracts", tags=["contracts"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_CONTENT_TYPES = {"application/pdf"}
MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024  # 20 MB


@router.post("/upload")
async def upload_contract(file: UploadFile):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    contract_id = f"CL{uuid.uuid4().hex[:8].upper()}"
    file_path = os.path.join(UPLOAD_DIR, f"{contract_id}.pdf")

    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(status_code=400, detail="File exceeds the maximum allowed size.")

    with open(file_path, "wb") as f:
        f.write(contents)

    try:
        pages = extract_pages(file_path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Could not read PDF: {exc}")

    full_text = "\n\n".join(p.text for p in pages)

    try:
        extraction = analyze_contract(full_text)
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=f"AI extraction failed: {exc}")

    try:
        review_flags = identify_review_flags(full_text)
    except RuntimeError:
        review_flags = []

    contract_doc = {
        "contract_id": contract_id,
        "filename": file.filename,
        "parties": extraction.parties,
        "effective_date": extraction.effective_date.isoformat() if extraction.effective_date else None,
        "expiration_date": extraction.expiration_date.isoformat() if extraction.expiration_date else None,
        "renewal": extraction.renewal.model_dump() if extraction.renewal else None,
        "payment_terms": extraction.payment_terms.model_dump() if extraction.payment_terms else None,
        "termination_conditions": extraction.termination_conditions,
        "service_terms": extraction.service_terms,
        "liability_clauses": extraction.liability_clauses,
        "confidentiality_clauses": extraction.confidentiality_clauses,
        "extracted_sections": extraction.important_sections,
        "review_flags": [f.model_dump() for f in review_flags],
        "raw_text": full_text,
    }
    save_contract(contract_doc)

    try:
        obligations = extract_obligations(contract_id, full_text)
        save_obligations(contract_id, [o.model_dump(mode="json") for o in obligations])
    except RuntimeError:
        pass  # obligation extraction failure shouldn't block the upload response

    try:
        index_contract(contract_id, pages)
    except Exception:
        pass  # RAG indexing failure shouldn't block the upload response

    return {"contract_id": contract_id, "status": "processed"}


@router.get("")
def get_contracts():
    contracts = list_contracts()
    return [
        {
            "contract_id": c["contract_id"],
            "filename": c["filename"],
            "parties": c.get("parties", []),
            "effective_date": c.get("effective_date"),
            "expiration_date": c.get("expiration_date"),
            "review_flag_count": len(c.get("review_flags", [])),
        }
        for c in contracts
    ]


@router.get("/{contract_id}")
def get_contract(contract_id: str):
    contract = get_contract_by_id(contract_id)
    if contract is None:
        raise HTTPException(status_code=404, detail="Contract not found.")
    contract.pop("raw_text", None)  # don't ship full raw text to the frontend by default
    return contract
