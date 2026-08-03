from __future__ import annotations

import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from stock_analysis_runtime.models import ContractError
from stock_analysis_runtime.state import SessionRuntime
from stock_analysis_runtime.storage import ArtifactStore, decode_json
from stock_analysis_runtime.validation import (
    validate_dilution,
    validate_evidence,
    validate_graph,
    validate_reverse,
    validate_scenarios,
    validate_update_cutoff,
)


class RuntimeTests(unittest.TestCase):
    def request(self, mode="standalone_runtime"):
        value = {
            "session_id": "s1",
            "analysis_id": "a1",
            "security_id": "sec1",
            "mode": mode,
            "source_cutoff": "2026-01-01T00:00:00Z",
        }
        if mode == "pipeline":
            value["blind_handoff"] = {"ticker": "DEMO", "verified_facts": []}
        return value

    def artifact(self, phase=None, kind="initial"):
        value = {"analysis_id": "a1", "security_id": "sec1", "payload": {}}
        if kind == "initial" and phase == 18:
            value.update(handoff={"handoff_id": "initial-phase-18"}, ledger={})
        if kind == "update" and phase == 4:
            value["handoff_supersession"] = {
                "active": "update-u1",
                "superseded": "initial-phase-18",
            }
        return value

    def test_modes_and_18_phase_progression(self):
        with tempfile.TemporaryDirectory() as d:
            rt = SessionRuntime(d)
            rt.create(self.request())
            for phase in range(1, 19):
                self.assertEqual(rt.next_contract("s1")["phase"], phase)
                self.assertTrue(rt.submit("s1", "initial", phase, self.artifact(phase))["accepted"])
            with self.assertRaises(ContractError):
                rt.next_contract("s1")

    def test_phase_skip_and_identity_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            rt = SessionRuntime(d)
            rt.create(self.request())
            with self.assertRaises(ContractError):
                rt.submit("s1", "initial", 2, self.artifact())
            bad = self.artifact()
            bad["analysis_id"] = "wrong"
            with self.assertRaises(ContractError):
                rt.submit("s1", "initial", 1, bad)

    def test_pipeline_blind_and_disclosure_order(self):
        with tempfile.TemporaryDirectory() as d:
            rt = SessionRuntime(d)
            req = self.request("pipeline")
            rt.create(req)
            with self.assertRaises(ContractError):
                rt.disclose("s1", {"comparison_rank": 1})
            for p in range(1, 17):
                rt.submit("s1", "initial", p, self.artifact(p))
            self.assertTrue(rt.disclose("s1", {"comparison_rank": 1})["accepted"])

    def test_prohibited_blind_fields(self):
        with tempfile.TemporaryDirectory() as d:
            req = self.request("pipeline")
            req["blind_handoff"]["target_value"] = 10
            with self.assertRaises(ContractError):
                SessionRuntime(d).create(req)

    def test_update_four_phases_and_strict_cutoff(self):
        with tempfile.TemporaryDirectory() as d:
            rt = SessionRuntime(d)
            rt.create(self.request())
            for p in range(1, 19):
                rt.submit("s1", "initial", p, self.artifact(p))
            with self.assertRaises(ContractError):
                rt.start_update("s1", "u1", "2025-12-31T19:00:00-05:00")
            rt.start_update("s1", "u1", "2026-01-02T00:00:00Z")
            for p in range(1, 5):
                self.assertTrue(
                    rt.submit("s1", "update", p, self.artifact(p, "update"))["integrity_verified"]
                )

    def test_storage_replay_collision_path_and_json(self):
        with tempfile.TemporaryDirectory() as d:
            store = ArtifactStore(d)
            self.assertFalse(store.put("s", "a", {"x": 1})["identical_replay"])
            self.assertTrue(store.put("s", "a", {"x": 1})["identical_replay"])
            with self.assertRaises(ContractError):
                store.put("s", "a", {"x": 2})
            with self.assertRaises(ContractError):
                store.put("../s", "a", {})
            for raw in [b'{"x":1,"x":2}', b'{"x":NaN}', b"\xff"]:
                with self.assertRaises(ContractError):
                    decode_json(raw)

    def test_publication_rejects_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            store = ArtifactStore(d)
            store.put("s", "a", {"x": 1})
            (Path(d) / "s" / "bad.json").symlink_to(Path(d) / "s" / "a.json")
            with self.assertRaises(ContractError):
                store.verify("s")

    def test_evidence_classes_cutoff_stale_and_duplicates(self):
        base = {
            "evidence_id": "e1",
            "source_type": "filing",
            "publisher": "SEC",
            "source_identity": "url",
            "published_at": "2025-01-01T00:00:00Z",
            "retrieved_at": "2025-01-02T00:00:00Z",
            "evidence_as_of": "2025-01-01T00:00:00Z",
            "classification": "FACTS",
            "point_in_time_eligible": True,
            "stale": False,
            "stale_warning": None,
        }
        validate_evidence([base], "2025-01-03T00:00:00Z", datetime(2025, 1, 4, tzinfo=UTC))
        with self.assertRaises(ContractError):
            validate_evidence([base, base], "2025-01-03T00:00:00Z")
        for source, cls in [
            ("company_ir", "FACTS"),
            ("consensus", "FACTS"),
            ("ai", "EXTERNAL_ESTIMATES"),
        ]:
            bad = {**base, "source_type": source, "classification": cls}
            with self.assertRaises(ContractError):
                validate_evidence([bad], "2025-01-03T00:00:00Z")
        bad = {**base, "stale": True}
        with self.assertRaises(ContractError):
            validate_evidence([bad], "2025-01-03T00:00:00Z")

    def test_dilution_arithmetic_and_exclusions(self):
        bridge = {
            "components": {
                "common_shares": {
                    "shares": 100,
                    "state": "currently_outstanding",
                    "included": True,
                },
                "rsus": {"shares": 5, "state": "economically_probable", "included": True},
                "authorized_but_unissued_shares": {
                    "shares": 50,
                    "state": "authorized_only",
                    "included": False,
                },
                "future_financing_shares": {
                    "shares": 20,
                    "state": "future_financing_only",
                    "included": False,
                },
                "anti_dilutive_exclusions": {
                    "shares": 3,
                    "state": "price_conditional",
                    "included": False,
                },
            },
            "economic_fully_diluted_shares": 105,
        }
        validate_dilution(bridge)
        bridge["components"]["authorized_but_unissued_shares"]["included"] = True
        with self.assertRaises(ContractError):
            validate_dilution(bridge)

    def test_graph_roots_unknown_and_double_count(self):
        graph = {
            "nodes": [{"node_id": "a"}, {"node_id": "b"}],
            "dependency_roots": [{"dependency_root_id": "r"}],
            "edges": [
                {
                    "source_node": "a",
                    "target_node": "b",
                    "dependency_root": "r",
                    "claim_id": "c",
                    "evidence_refs": ["e"],
                }
            ],
        }
        validate_graph(graph, {"e"})
        graph["edges"].append(dict(graph["edges"][0]))
        with self.assertRaises(ContractError):
            validate_graph(graph, {"e"})

    def test_scenario_and_reverse_math(self):
        def s(i, p, ev):
            equity = ev - 10 - 5 + 15
            ps = equity / 10
            tr = ps / 10 - 1
            return {
                "scenario_id": str(i),
                "scenario_name": str(i),
                "mutually_exclusive_group": "g",
                "horizon": "3y",
                "probability": p,
                "enterprise_value": ev,
                "future_debt": 10,
                "future_leases": 5,
                "cash_and_non_core_assets": 15,
                "equity_value": equity,
                "future_diluted_shares": 10,
                "per_share_value": ps,
                "years": 3,
                "total_return": tr,
                "annualized_return": (1 + tr) ** (1 / 3) - 1,
            }

        validate_scenarios([s(1, 25, 80), s(2, 50, 100), s(3, 25, 120)], 10)
        bad = [s(1, 20, 80), s(2, 50, 100), s(3, 25, 120)]
        with self.assertRaises(ContractError):
            validate_scenarios(bad, 10)
        validate_reverse({"solved_variables": ["growth"], "fixed_variables": {"margin": 0.2}})
        with self.assertRaises(ContractError):
            validate_reverse({"solved_variables": ["growth", "margin"], "fixed_variables": {}})

    def test_timezone_equivalence(self):
        with self.assertRaises(ContractError):
            validate_update_cutoff("2026-01-01T00:00:00Z", "2025-12-31T19:00:00-05:00")


if __name__ == "__main__":
    unittest.main()
