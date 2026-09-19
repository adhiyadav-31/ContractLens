"""Pydantic models for contract data. Owned by Safa."""

from datetime import date, datetime
from pydantic import BaseModel, Field


class SourceReference(BaseModel):
    section: str | None = None
    page: int | None = None
    chunk_id: str | None = None


class RenewalTerms(BaseModel):
    type: str = "none"  # "automatic" | "manual" | "none"
    notice_period_days: int | None = None


class PaymentTerms(BaseModel):
    description: str | None = None


class ReviewFlag(BaseModel):
    type: str  # e.g. AUTO_RENEWAL, SHORT_NOTICE_PERIOD, etc.
    description: str
    severity: str | None = None  # "low" | "medium" | "high"
    source: SourceReference | None = None
    explanation: str | None = None


class ContractExtraction(BaseModel):
    """What the Contract Intelligence Agent produces from raw text."""
    parties: list[str] = Field(default_factory=list)
    effective_date: date | None = None
    expiration_date: date | None = None
    renewal: RenewalTerms | None = None
    payment_terms: PaymentTerms | None = None
    termination_conditions: str | None = None
    service_terms: str | None = None
    liability_clauses: str | None = None
    confidentiality_clauses: str | None = None
    important_sections: list[str] = Field(default_factory=list)


class Contract(BaseModel):
    """Full persisted contract document."""
    contract_id: str
    filename: str
    parties: list[str] = Field(default_factory=list)
    effective_date: date | None = None
    expiration_date: date | None = None
    renewal: RenewalTerms | None = None
    payment_terms: PaymentTerms | None = None
    termination_conditions: str | None = None
    service_terms: str | None = None
    liability_clauses: str | None = None
    confidentiality_clauses: str | None = None
    extracted_sections: list[str] = Field(default_factory=list)
    review_flags: list[ReviewFlag] = Field(default_factory=list)
    raw_text: str | None = None  # kept for RAG indexing / debugging, not returned to frontend by default
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ContractSummary(BaseModel):
    """Lightweight shape for list views."""
    contract_id: str
    filename: str
    parties: list[str]
    effective_date: date | None = None
    expiration_date: date | None = None
    review_flag_count: int = 0
