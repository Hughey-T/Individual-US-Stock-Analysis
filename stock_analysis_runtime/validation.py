"""Semantic validation for evidence, dilution, graphs, scenarios and valuation."""

from __future__ import annotations

import math
from collections import Counter
from datetime import UTC, datetime
from typing import Any

from .models import CLASSIFICATIONS, DILUTION_STATES, ContractError, instant


def finite(value: Any, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ContractError(f"{name} must be finite")
    return float(value)


def validate_evidence(
    records: list[dict[str, Any]], cutoff: str, now: datetime | None = None
) -> None:
    now = now or datetime.now(UTC)
    ids = [r.get("evidence_id") for r in records]
    if None in ids or len(ids) != len(set(ids)):
        raise ContractError("missing or duplicate evidence ID")
    limit = instant(cutoff)
    for record in records:
        classification = record.get("classification")
        if classification not in CLASSIFICATIONS:
            raise ContractError("unknown information classification")
        published = instant(record["published_at"])
        retrieved = instant(record["retrieved_at"])
        evidence_as_of = instant(record["evidence_as_of"])
        if max(published, retrieved, evidence_as_of) > limit or evidence_as_of > now:
            raise ContractError("future or cutoff-ineligible evidence")
        source_type = record.get("source_type")
        if source_type in {"management", "company_ir"} and classification == "FACTS":
            raise ContractError("company claim cannot be FACTS")
        if source_type in {"consensus", "industry_estimate"} and classification == "FACTS":
            raise ContractError("external estimate cannot be FACTS")
        if source_type == "ai" and classification == "EXTERNAL_ESTIMATES":
            raise ContractError("AI assumption cannot be external estimate")
        if not record.get("source_identity") or not record.get("publisher"):
            raise ContractError("source identity is required")
        if not record.get("point_in_time_eligible"):
            raise ContractError("evidence is not point-in-time eligible")
        if record.get("stale") and not record.get("stale_warning"):
            raise ContractError("stale evidence requires warning")


def validate_dilution(bridge: dict[str, Any]) -> None:
    included = 0.0
    for name, item in bridge["components"].items():
        if item["state"] not in DILUTION_STATES:
            raise ContractError(f"invalid dilution state: {name}")
        amount = finite(item["shares"], name)
        if name in {
            "authorized_but_unissued_shares",
            "future_financing_shares",
            "anti_dilutive_exclusions",
        }:
            if item["included"]:
                raise ContractError(f"{name} cannot enter current denominator")
        if item["included"]:
            included += amount
    expected = finite(bridge["economic_fully_diluted_shares"], "economic diluted shares")
    if not math.isclose(included, expected, rel_tol=1e-9, abs_tol=1e-6):
        raise ContractError("diluted-share arithmetic mismatch")


def validate_graph(graph: dict[str, Any], known_evidence: set[str]) -> None:
    nodes = [n["node_id"] for n in graph["nodes"]]
    if len(nodes) != len(set(nodes)):
        raise ContractError("duplicate causal node")
    node_set = set(nodes)
    roots = {r["dependency_root_id"] for r in graph["dependency_roots"]}
    signatures: Counter[tuple[str, str]] = Counter()
    for edge in graph["edges"]:
        if edge["source_node"] not in node_set or edge["target_node"] not in node_set:
            raise ContractError("unknown causal node")
        if edge["dependency_root"] not in roots:
            raise ContractError("unknown dependency root")
        if not set(edge["evidence_refs"]) <= known_evidence:
            raise ContractError("unknown graph evidence")
        signatures[(edge["dependency_root"], edge["claim_id"])] += 1
    if any(count > 1 for count in signatures.values()):
        raise ContractError("dependency-root evidence double counting")


def validate_scenarios(items: list[dict[str, Any]], current_price: float) -> None:
    ids = [item["scenario_id"] for item in items]
    names = [item["scenario_name"] for item in items]
    if len(ids) != len(set(ids)) or len(names) != len(set(names)):
        raise ContractError("duplicate scenario")
    groups = {item["mutually_exclusive_group"] for item in items}
    horizons = {item["horizon"] for item in items}
    if len(groups) != 1 or len(horizons) != 1:
        raise ContractError("scenarios must be one exclusive horizon group")
    if not math.isclose(
        sum(finite(i["probability"], "probability") for i in items), 100.0, abs_tol=1e-8
    ):
        raise ContractError("scenario probabilities must total 100")
    for item in items:
        ev = finite(item["enterprise_value"], "enterprise value")
        equity = (
            ev
            - finite(item["future_debt"], "debt")
            - finite(item["future_leases"], "leases")
            + finite(item["cash_and_non_core_assets"], "assets")
        )
        shares = finite(item["future_diluted_shares"], "shares")
        if shares <= 0:
            raise ContractError("future diluted shares must be positive")
        per_share = equity / shares
        if not math.isclose(equity, item["equity_value"], rel_tol=1e-8) or not math.isclose(
            per_share, item["per_share_value"], rel_tol=1e-8
        ):
            raise ContractError("scenario valuation arithmetic mismatch")
        years = finite(item["years"], "years")
        total_return = per_share / current_price - 1
        annualized = (1 + total_return) ** (1 / years) - 1 if total_return > -1 else -1
        if not math.isclose(total_return, item["total_return"], rel_tol=1e-8) or not math.isclose(
            annualized, item["annualized_return"], rel_tol=1e-8
        ):
            raise ContractError("scenario return arithmetic mismatch")


def validate_reverse(value: dict[str, Any]) -> None:
    solved = value.get("solved_variables", [])
    if len(solved) != 1 or solved[0] in value.get("fixed_variables", {}):
        raise ContractError("reverse valuation requires exactly one solved variable")
    if not value.get("fixed_variables"):
        raise ContractError("reverse valuation requires fixed variables")


def validate_update_cutoff(previous: str, new: str) -> None:
    if instant(new) <= instant(previous):
        raise ContractError("update cutoff must be a strictly later UTC instant")
