"""Agent 2: Obligation Agent. Owned by Safa.

AI identifies obligations; Python (alert_service) handles all date math and status.
"""

import re
import uuid

from app.models.contract import SourceReference
from app.models.obligation import Deadline, Obligation, ObligationStatus
from app.services.alert_service import calculate_status, next_monthly_occurrence
from app.services.gemini_service import generate_structured_output
from app.utils.prompts import OBLIGATION_EXTRACTION_PROMPT

_DAY_OF_MONTH_PATTERN = re.compile(r"\b(\d{1,2})(?:st|nd|rd|th)?\s+(?:day\s+)?of\s+(?:every|each)\s+month\b", re.IGNORECASE)


def extract_obligations(contract_id: str, contract_text: str) -> list[Obligation]:
    """AI-driven obligation identification, converted into validated Obligation objects."""
    prompt = OBLIGATION_EXTRACTION_PROMPT.format(contract_text=contract_text[:20000])
    try:
        raw = generate_structured_output(prompt)
    except RuntimeError:
        return []

    if not isinstance(raw, list):
        return []

    obligations: list[Obligation] = []
    for item in raw:
        if not isinstance(item, dict):
            continue

        deadline_text = item.get("deadline_text") or ""
        calculated_date = _try_calculate_date(deadline_text)

        deadline = Deadline(raw_text=deadline_text, calculated_date=calculated_date)
        status = calculate_status(calculated_date)

        obligations.append(
            Obligation(
                obligation_id=str(uuid.uuid4()),
                contract_id=contract_id,
                party=item.get("party", "Unknown"),
                action=item.get("action", ""),
                deadline=deadline,
                frequency=item.get("frequency"),
                condition=item.get("condition"),
                status=status,
                source=SourceReference(
                    section=item.get("source_section"),
                    page=item.get("source_page"),
                ),
            )
        )
    return obligations


def _try_calculate_date(deadline_text: str):
    """Deterministic Python parsing for common recurring-deadline phrasing.

    Only handles the reliable "Nth of every month" case for the MVP; anything
    else keeps calculated_date = None and preserves the natural-language text,
    per Section 16 of the spec (never guess a date Gemini can't reliably give).
    """
    match = _DAY_OF_MONTH_PATTERN.search(deadline_text)
    if match:
        day = int(match.group(1))
        try:
            return next_monthly_occurrence(day)
        except ValueError:
            return None
    return None
