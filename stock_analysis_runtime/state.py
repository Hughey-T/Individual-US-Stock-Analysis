"""Session state machine enforcing blind disclosure and append-only progression."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from .models import CONTRACT_VERSION, FROZEN_INITIAL_PHASES, MODES, ContractError
from .storage import ArtifactStore
from .validation import validate_update_cutoff


class SessionRuntime:
    def __init__(self, root: str | Path):
        self.store = ArtifactStore(root)

    def create(self, request: dict[str, Any]) -> dict[str, Any]:
        mode = request.get("mode")
        if mode not in MODES - {"standalone_static"}:
            raise ContractError("runtime mode required")
        if mode == "pipeline" and not request.get("blind_handoff"):
            raise ContractError("pipeline requires blind handoff")
        forbidden = {"comparison_rank", "selection_reason", "target_value", "future_outcome"}
        blind = request.get("blind_handoff", {})
        if forbidden & blind.keys():
            raise ContractError("blind handoff contains prohibited upstream fields")
        state = {
            "contract_version": CONTRACT_VERSION,
            "session_id": request["session_id"],
            "analysis_id": request["analysis_id"],
            "security_id": request["security_id"],
            "mode": mode,
            "source_cutoff": request["source_cutoff"],
            "initial_phase": 1,
            "update_phase": None,
            "update_id": None,
            "independent_frozen": False,
            "reconciliation_disclosed": False,
            "completed": False,
            "active_handoff": None,
        }
        self.store.put(request["session_id"], "session", state)
        if blind:
            self.store.put(request["session_id"], "blind-handoff", blind)
        return state

    def load(self, session_id: str) -> dict[str, Any]:
        return cast(
            dict[str, Any],
            json.loads((self.store.root / session_id / "session.json").read_text()),
        )

    def _replace_state(self, state: dict[str, Any]) -> None:
        path = self.store.root / state["session_id"] / "session.json"
        raw = json.dumps(
            state, ensure_ascii=False, allow_nan=False, sort_keys=True, separators=(",", ":")
        ).encode()
        temp = path.with_suffix(".pending")
        temp.write_bytes(raw)
        temp.replace(path)

    def next_contract(self, session_id: str) -> dict[str, Any]:
        state = self.load(session_id)
        phase = (
            state["update_phase"] if state["update_phase"] is not None else state["initial_phase"]
        )
        kind = "update" if state["update_phase"] is not None else "initial"
        if state["completed"]:
            raise ContractError("all phases complete")
        return {
            "contract_version": CONTRACT_VERSION,
            "kind": kind,
            "phase": phase,
            "one_response_one_phase": True,
            "persistence_state": "not_generated",
        }

    def submit(
        self, session_id: str, kind: str, phase: int, artifact: dict[str, Any]
    ) -> dict[str, Any]:
        state = self.load(session_id)
        expected = state["update_phase"] if kind == "update" else state["initial_phase"]
        if expected != phase or (kind == "update") != (state["update_phase"] is not None):
            raise ContractError("phase skip or wrong workflow")
        if (
            artifact.get("analysis_id") != state["analysis_id"]
            or artifact.get("security_id") != state["security_id"]
        ):
            raise ContractError("artifact identity mismatch")
        artifact_id = f"{kind}-phase-{phase:02d}"
        receipt = self.store.put(session_id, artifact_id, artifact)
        if kind == "initial":
            if phase in FROZEN_INITIAL_PHASES:
                state["independent_frozen"] = True
            if phase == 18:
                if "handoff" not in artifact or "ledger" not in artifact:
                    raise ContractError("Phase 18 requires handoff and ledger")
                state["active_handoff"] = artifact["handoff"].get("handoff_id", "initial-phase-18")
                state["completed"] = True
            else:
                state["initial_phase"] += 1
        else:
            if phase == 4:
                supersession = artifact.get("handoff_supersession")
                if not isinstance(supersession, dict):
                    raise ContractError("Update Phase 4 requires handoff supersession")
                if supersession.get("superseded") != state["active_handoff"]:
                    raise ContractError("superseded handoff is not the active handoff")
                state["active_handoff"] = supersession.get("active")
                state["completed"] = True
                state["update_phase"] = None
            else:
                state["update_phase"] += 1
        self._replace_state(state)
        return {**receipt, "persistence_state": "integrity_verified"}

    def disclose(self, session_id: str, reconciliation: dict[str, Any]) -> dict[str, Any]:
        state = self.load(session_id)
        if state["initial_phase"] < 17 or not state["independent_frozen"]:
            raise ContractError("reconciliation cannot be disclosed before Phase 17 freeze")
        receipt = self.store.put(session_id, "reconciliation", reconciliation)
        state["reconciliation_disclosed"] = True
        self._replace_state(state)
        return receipt

    def start_update(self, session_id: str, update_id: str, new_cutoff: str) -> dict[str, Any]:
        state = self.load(session_id)
        if not state["completed"]:
            raise ContractError("initial analysis is incomplete")
        validate_update_cutoff(state["source_cutoff"], new_cutoff)
        state.update(update_id=update_id, source_cutoff=new_cutoff, update_phase=1, completed=False)
        self._replace_state(state)
        return state

    def publication(self, session_id: str) -> dict[str, Any]:
        return self.store.verify(session_id)

    def final_component(self, session_id: str, component: str) -> Any:
        """Read a Phase-18 handoff or ledger without mutating history."""
        if component not in {"handoff", "ledger"}:
            raise ContractError("unknown final component")
        state = self.load(session_id)
        if not state["completed"]:
            raise ContractError("analysis is incomplete")
        path = self.store.root / session_id / "initial-phase-18.json"
        artifact = cast(dict[str, Any], json.loads(path.read_text()))
        if component not in artifact:
            raise ContractError(f"Phase 18 has no {component}")
        return artifact[component]
