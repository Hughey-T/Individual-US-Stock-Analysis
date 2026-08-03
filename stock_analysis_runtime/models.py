"""Closed constants and small value helpers for contract 2.0.0."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

CONTRACT_VERSION = "2.0.0"
INITIAL_PHASES = tuple(range(1, 19))
UPDATE_PHASES = tuple(range(1, 5))
MODES = {"standalone_static", "standalone_runtime", "pipeline"}
CLASSIFICATIONS = {
    "FACTS",
    "COMPANY_CLAIMS",
    "EXTERNAL_ESTIMATES",
    "AI_ASSUMPTIONS",
    "AI_JUDGMENTS",
    "UNRESOLVED",
}
PERSISTENCE_STATES = {
    "not_generated",
    "generated_not_persisted",
    "persisted_pending_verification",
    "integrity_verified",
    "failed_terminal",
    "superseded",
}
DILUTION_STATES = {
    "currently_outstanding",
    "economically_probable",
    "price_conditional",
    "performance_conditional",
    "future_financing_only",
    "authorized_only",
    "not_evaluable",
    "not_applicable",
}
FROZEN_INITIAL_PHASES = {13, 14, 15, 16}


class ContractError(ValueError):
    """A machine-verifiable contract violation."""


def instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ContractError("timestamp must include timezone")
    return parsed.astimezone(UTC)


def require_keys(value: dict[str, Any], keys: set[str], context: str) -> None:
    missing = keys - value.keys()
    extra = value.keys() - keys
    if missing or extra:
        raise ContractError(f"{context}: missing={sorted(missing)}, extra={sorted(extra)}")
