"""Deterministic date/status logic. Owned by Safa.

Gemini never calculates dates or status - this module does, in plain Python.
"""

from datetime import date, datetime, timedelta

from app.models.obligation import ObligationStatus

DUE_SOON_WINDOW_DAYS = 7


def calculate_status(due_date: date | None, today: date | None = None) -> ObligationStatus:
    """Classify a single obligation's status from its calculated due date."""
    if due_date is None:
        return ObligationStatus.UNKNOWN

    today = today or date.today()
    delta_days = (due_date - today).days

    if delta_days < 0:
        return ObligationStatus.OVERDUE
    if delta_days <= DUE_SOON_WINDOW_DAYS:
        return ObligationStatus.DUE_SOON
    return ObligationStatus.UPCOMING


def get_upcoming_obligations(obligations: list[dict], today: date | None = None) -> list[dict]:
    today = today or date.today()
    result = []
    for ob in obligations:
        due = _parse_date(ob.get("deadline", {}).get("calculated_date"))
        status = calculate_status(due, today)
        if status in (ObligationStatus.UPCOMING, ObligationStatus.DUE_SOON):
            result.append({**ob, "status": status.value})
    return sorted(result, key=lambda o: o["deadline"].get("calculated_date") or "")


def get_overdue_obligations(obligations: list[dict], today: date | None = None) -> list[dict]:
    today = today or date.today()
    result = []
    for ob in obligations:
        due = _parse_date(ob.get("deadline", {}).get("calculated_date"))
        if calculate_status(due, today) == ObligationStatus.OVERDUE:
            result.append({**ob, "status": ObligationStatus.OVERDUE.value})
    return result


def next_monthly_occurrence(day_of_month: int, today: date | None = None) -> date:
    """Given e.g. '5th of every month', return the next concrete calendar date."""
    today = today or date.today()
    year, month = today.year, today.month
    try:
        candidate = date(year, month, day_of_month)
    except ValueError:
        candidate = date(year, month, 28)  # clamp for short months
    if candidate < today:
        month += 1
        if month > 12:
            month = 1
            year += 1
        try:
            candidate = date(year, month, day_of_month)
        except ValueError:
            candidate = date(year, month, 28)
    return candidate


def _parse_date(value) -> date | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None
