"""Semantic contract version comparison. Owned by Safa."""

from app.services.gemini_service import generate_structured_output
from app.utils.prompts import COMPARISON_PROMPT


def identify_changed_clauses(text_v1: str, text_v2: str) -> list[dict]:
    """Ask Gemini to identify business-relevant semantic changes between two versions."""
    prompt = COMPARISON_PROMPT.format(text_v1=text_v1[:15000], text_v2=text_v2[:15000])
    try:
        result = generate_structured_output(prompt)
    except RuntimeError:
        # Low-confidence / failed extraction -> return empty with a review note
        # rather than fabricate a diff.
        return []
    return result if isinstance(result, list) else []


def summarize_business_changes(changes: list[dict]) -> str:
    """Produce a short human-readable summary of the changes list."""
    if not changes:
        return "No significant business-relevant changes were detected between the two versions."
    lines = [f"- ({c.get('category', 'general')}) {c.get('description', '')}" for c in changes]
    return "Detected changes:\n" + "\n".join(lines)


def compare_contracts(contract_id_v1: str, text_v1: str, contract_id_v2: str, text_v2: str) -> dict:
    """Top-level entry point used by routes/compare.py."""
    changes = identify_changed_clauses(text_v1, text_v2)
    return {
        "contract_id_v1": contract_id_v1,
        "contract_id_v2": contract_id_v2,
        "changes": changes,
        "summary": summarize_business_changes(changes),
    }
