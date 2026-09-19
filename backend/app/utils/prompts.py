"""Central prompt templates. Owned by Safa.

Do not hard-code prompt strings anywhere else. Every agent/service imports from here.
"""

CONTRACT_EXTRACTION_PROMPT = """You are a contract analysis assistant. Read the contract text below and
extract structured information as JSON matching this schema exactly:

{{
  "parties": ["string", ...],
  "effective_date": "YYYY-MM-DD or null",
  "expiration_date": "YYYY-MM-DD or null",
  "renewal": {{"type": "automatic|manual|none", "notice_period_days": int or null}},
  "payment_terms": {{"description": "string or null"}},
  "termination_conditions": "string or null",
  "service_terms": "string or null",
  "liability_clauses": "string or null",
  "confidentiality_clauses": "string or null",
  "important_sections": ["string", ...]
}}

Rules:
- Only extract what is explicitly stated in the text. Never invent values.
- If a field is not present, use null (or an empty list/array as appropriate).
- Respond with ONLY the JSON object, no other text, no markdown fences.

CONTRACT TEXT:
{contract_text}
"""

OBLIGATION_EXTRACTION_PROMPT = """You are extracting explicit obligations from a contract. For every commitment
a party must fulfil, produce a JSON array of objects matching this schema:

[
  {{
    "party": "string",
    "action": "string (what must be done)",
    "deadline_text": "string (natural language deadline, e.g. '5th of every month')",
    "frequency": "monthly|quarterly|annual|once|null",
    "condition": "string or null",
    "source_section": "string or null",
    "source_page": int or null
  }}
]

Rules:
- Only extract obligations explicitly stated in the text.
- Do not calculate or guess actual calendar dates — that is handled separately in Python.
- Respond with ONLY the JSON array, no other text.

CONTRACT TEXT:
{contract_text}
"""

RISK_REVIEW_PROMPT = """You are a contract review assistant. You NEVER give definitive legal verdicts.
You only flag items that MAY require human review, using language like "may require review",
"potential inconsistency detected", or "review recommended".

Examine the contract text below and identify possible issues. Return a JSON array:

[
  {{
    "type": "AUTO_RENEWAL|SHORT_NOTICE_PERIOD|UNUSUAL_PAYMENT_TERM|MISSING_INFORMATION|CONFLICTING_CLAUSE|INCONSISTENT_DATE|INCONSISTENT_PARTY|AMBIGUOUS_OBLIGATION|LIABILITY_REVIEW|MISSING_REFERENCE|ONE_SIDED_OBLIGATION",
    "description": "string",
    "severity": "low|medium|high",
    "source_section": "string or null",
    "source_page": int or null,
    "explanation": "string"
  }}
]

Never state a definitive legal conclusion, and never claim the contract is fake, dangerous, or
untrustworthy. Respond with ONLY the JSON array.

CONTRACT TEXT:
{contract_text}
"""

QA_PROMPT = """You are answering a question about a contract using ONLY the evidence chunks provided
below. If the evidence does not contain the answer, say so explicitly rather than guessing.

QUESTION:
{question}

EVIDENCE CHUNKS:
{evidence_chunks}

Respond with a concise, direct answer grounded only in the evidence above. Do not invent
contract terms that are not present in the evidence.
"""

COMPARISON_PROMPT = """You are comparing two versions of a contract. Identify business-relevant
semantic changes (not just text diffs) across these categories: payment, deadlines, obligations,
renewal, termination, parties, dates, liability, confidentiality, service levels.

Return a JSON array:

[
  {{
    "category": "payment|deadlines|obligations|renewal|termination|parties|dates|liability|confidentiality|service_levels",
    "description": "string, business-meaning explanation of the change",
    "old_value": "string or null",
    "new_value": "string or null"
  }}
]

VERSION 1 TEXT:
{text_v1}

VERSION 2 TEXT:
{text_v2}

Respond with ONLY the JSON array.
"""

SUMMARY_PROMPT = """Summarize the key business terms of this contract in 3-5 concise sentences,
suitable for a dashboard card. Focus on parties, dates, payment, and renewal/termination terms.
Do not offer legal conclusions.

CONTRACT TEXT:
{contract_text}
"""
