"""Pydantic models for obligations/timeline. Owned by Safa."""

from datetime import date
from enum import Enum
from pydantic import BaseModel, Field

from app.models.contract import SourceReference


class ObligationStatus(str, Enum):
    UPCOMING = "UPCOMING"
    DUE_SOON = "DUE_SOON"
    OVERDUE = "OVERDUE"
    COMPLETED = "COMPLETED"
    UNKNOWN = "UNKNOWN"


class Deadline(BaseModel):
    raw_text: str  # natural language, e.g. "5th of every month"
    calculated_date: date | None = None  # next concrete occurrence, if derivable


class Obligation(BaseModel):
    obligation_id: str
    contract_id: str
    party: str
    action: str
    deadline: Deadline
    frequency: str | None = None  # "monthly" | "once" | "quarterly" | "annual" | None
    condition: str | None = None
    status: ObligationStatus = ObligationStatus.UNKNOWN
    source: SourceReference | None = None


class TimelineItem(BaseModel):
    obligation_id: str
    date: date
    label: str
    status: ObligationStatus
