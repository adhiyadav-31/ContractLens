"""Agent 1: Contract Intelligence Agent. Owned by Safa.

Converts unstructured contract text into structured, validated data.
Does NOT touch frontend logic, deadline status, or the UI.
"""

from pydantic import ValidationError

from app.models.contract import ContractExtraction
from app.services.gemini_service import generate_structured_output
from app.utils.prompts import CONTRACT_EXTRACTION_PROMPT


def analyze_contract(contract_text: str) -> ContractExtraction:
    """Extract structured contract fields using Gemini, validated via Pydantic.

    If Gemini's output fails validation, returns an empty/partial ContractExtraction
    rather than inventing values - callers should treat this as low-confidence and
    surface a review flag.
    """
    prompt = CONTRACT_EXTRACTION_PROMPT.format(contract_text=contract_text[:20000])
    raw = generate_structured_output(prompt)

    if not isinstance(raw, dict):
        return ContractExtraction()

    try:
        return ContractExtraction(**raw)
    except ValidationError:
        # Salvage whatever fields do validate rather than discarding everything
        safe_fields = {k: v for k, v in raw.items() if k in ContractExtraction.model_fields}
        try:
            return ContractExtraction(**safe_fields)
        except ValidationError:
            return ContractExtraction()
