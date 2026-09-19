"""Agent 4: Counterparty Due Diligence Agent. Owned by Safa.

MVP note: lightweight/mock verification flow, clearly labeled as such.
Never claim "trustworthy" - only report evidence found or not found.
"""


def extract_counterparty(parties: list[str], primary_party_hint: str | None = None) -> str | None:
    """Best-effort pick of the 'counterparty' (i.e. not our own company) from the parties list.

    For the MVP this simply returns the party that is not the hinted primary party,
    or the first party if no hint is given.
    """
    if not parties:
        return None
    if primary_party_hint:
        others = [p for p in parties if p.strip().lower() != primary_party_hint.strip().lower()]
        if others:
            return others[0]
    return parties[0]


def verify_counterparty(company_name: str) -> dict:
    """MVP mock verification flow.

    Real external lookups (registries, licensing bodies, etc.) are out of scope
    for the 5-hour MVP (Section 30). This returns a clearly-labeled mock result
    so the UI can demonstrate the intended flow without fabricating real data.
    """
    if not company_name:
        return {
            "company_name": None,
            "status": "no_data",
            "notes": "No counterparty name could be extracted from the contract.",
            "mock": True,
        }

    return {
        "company_name": company_name,
        "status": "unverified",
        "notes": (
            "No reliable public record was checked in this demo build. "
            "Additional verification recommended."
        ),
        "mock": True,
    }
