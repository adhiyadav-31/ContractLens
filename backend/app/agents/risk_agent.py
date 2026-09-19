"""Agent 3: Contract Risk & Review Agent. Owned by Safa.

Flags items that MAY require human review. Never issues a definitive legal verdict.
"""

from app.models.contract import ReviewFlag, SourceReference
from app.services.gemini_service import generate_structured_output
from app.utils.prompts import RISK_REVIEW_PROMPT

VALID_FLAG_TYPES = {
    "AUTO_RENEWAL",
    "SHORT_NOTICE_PERIOD",
    "UNUSUAL_PAYMENT_TERM",
    "MISSING_INFORMATION",
    "CONFLICTING_CLAUSE",
    "INCONSISTENT_DATE",
    "INCONSISTENT_PARTY",
    "AMBIGUOUS_OBLIGATION",
    "LIABILITY_REVIEW",
    "MISSING_REFERENCE",
    "ONE_SIDED_OBLIGATION",
}


def identify_review_flags(contract_text: str) -> list[ReviewFlag]:
    prompt = RISK_REVIEW_PROMPT.format(contract_text=contract_text[:20000])
    try:
        raw = generate_structured_output(prompt)
    except RuntimeError:
        return []

    if not isinstance(raw, list):
        return []

    flags: list[ReviewFlag] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        flag_type = item.get("type", "MISSING_INFORMATION")
        if flag_type not in VALID_FLAG_TYPES:
            flag_type = "MISSING_INFORMATION"

        flags.append(
            ReviewFlag(
                type=flag_type,
                description=item.get("description", "Review recommended."),
                severity=item.get("severity"),
                source=SourceReference(
                    section=item.get("source_section"),
                    page=item.get("source_page"),
                ),
                explanation=item.get("explanation"),
            )
        )
    return flags
