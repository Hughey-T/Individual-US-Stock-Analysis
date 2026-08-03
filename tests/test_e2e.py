from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from wsgiref.util import setup_testing_defaults

from stock_analysis_runtime.api import App
from stock_analysis_runtime.models import ContractError
from stock_analysis_runtime.state import SessionRuntime
from stock_analysis_runtime.storage import ArtifactStore, decode_json

ROOT = Path(__file__).resolve().parents[1]


def request(mode: str = "standalone_runtime") -> dict:
    value = {
        "session_id": "fixture-session",
        "analysis_id": "analysis-demo-001",
        "security_id": "sec-demo",
        "mode": mode,
        "source_cutoff": "2026-01-01T00:00:00Z",
    }
    if mode == "pipeline":
        value["blind_handoff"] = {"ticker": "DEMO", "verified_facts": []}
    return value


class FixtureAndE2ETests(unittest.TestCase):
    def initial(self):
        return json.loads((ROOT / "examples/fixtures/initial-18.json").read_text())

    def updates(self):
        return json.loads((ROOT / "examples/fixtures/update-4.json").read_text())

    def test_initial_fixture_has_each_phase(self):
        self.assertEqual([x["phase"] for x in self.initial()], list(range(1, 19)))

    def test_update_fixture_has_each_phase(self):
        self.assertEqual([x["phase"] for x in self.updates()], list(range(1, 5)))

    def test_all_three_mode_fixtures(self):
        self.assertEqual(
            set(json.loads((ROOT / "examples/fixtures/modes.json").read_text())),
            {"standalone_static", "standalone_runtime", "pipeline"},
        )

    def test_initial_18_phase_e2e_and_session_resume(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = SessionRuntime(directory)
            runtime.create(request())
            for item in self.initial():
                runtime = SessionRuntime(directory)
                runtime.submit("fixture-session", "initial", item["phase"], item)
            self.assertTrue(runtime.load("fixture-session")["completed"])
            self.assertEqual(
                runtime.final_component("fixture-session", "ledger")["decision_id"], "decision-001"
            )

    def test_pipeline_blind_disclosure_e2e(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = SessionRuntime(directory)
            runtime.create(request("pipeline"))
            with self.assertRaises(ContractError):
                runtime.disclose("fixture-session", {"rank": 2})
            for item in self.initial()[:16]:
                runtime.submit("fixture-session", "initial", item["phase"], item)
            self.assertTrue(runtime.disclose("fixture-session", {"rank": 2})["accepted"])

    def test_update_4_phase_and_handoff_supersession_e2e(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = SessionRuntime(directory)
            runtime.create(request())
            initial = self.initial()
            initial[-1]["handoff"]["handoff_id"] = "handoff-initial-001"
            for item in initial:
                runtime.submit("fixture-session", "initial", item["phase"], item)
            runtime.start_update("fixture-session", "update-demo-001", "2026-02-01T00:00:00Z")
            for item in self.updates():
                runtime.submit("fixture-session", "update", item["phase"], item)
            self.assertEqual(
                runtime.load("fixture-session")["active_handoff"], "handoff-update-001"
            )
            self.assertTrue(
                (Path(directory) / "fixture-session" / "initial-phase-18.json").exists()
            )

    def test_backup_restore_and_integrity(self):
        with tempfile.TemporaryDirectory() as source, tempfile.TemporaryDirectory() as backup:
            runtime = SessionRuntime(source)
            runtime.create(request())
            runtime.submit("fixture-session", "initial", 1, self.initial()[0])
            shutil.copytree(Path(source) / "fixture-session", Path(backup) / "fixture-session")
            restored = SessionRuntime(backup)
            self.assertTrue(restored.publication("fixture-session")["integrity_verified"])
            self.assertEqual(restored.next_contract("fixture-session")["phase"], 2)

    def test_missing_artifact_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = SessionRuntime(directory)
            runtime.create(request())
            with self.assertRaises(ContractError):
                runtime.final_component("fixture-session", "handoff")

    def test_unexpected_artifact_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ArtifactStore(directory)
            store.put("s", "a", {"x": 1})
            (Path(directory) / "s" / "extra.txt").write_text("x")
            with self.assertRaises(ContractError):
                store.verify("s")

    def test_duplicate_replay_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ArtifactStore(directory)
            store.put("s", "a", {"x": 1})
            self.assertTrue(store.put("s", "a", {"x": 1})["identical_replay"])

    def test_generation_collision_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ArtifactStore(directory)
            store.put("s", "a", {"x": 1})
            with self.assertRaises(ContractError):
                store.put("s", "a", {"x": 2})

    def test_malformed_utf8_rejected(self):
        with self.assertRaises(ContractError):
            decode_json(b"\xff")

    def test_duplicate_json_key_rejected(self):
        with self.assertRaises(ContractError):
            decode_json(b'{"x":1,"x":2}')

    def test_nan_rejected(self):
        with self.assertRaises(ContractError):
            decode_json(b'{"x":NaN}')

    def test_infinity_rejected(self):
        with self.assertRaises(ContractError):
            decode_json(b'{"x":Infinity}')

    def test_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ContractError):
                ArtifactStore(directory).put("../s", "a", {})

    def test_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ArtifactStore(directory)
            store.put("s", "a", {"x": 1})
            (Path(directory) / "s" / "b.json").symlink_to(Path(directory) / "s" / "a.json")
            with self.assertRaises(ContractError):
                store.verify("s")

    def test_health_endpoint_without_auth(self):
        with tempfile.TemporaryDirectory() as directory:
            app = App(directory, "secret")
            env = {}
            setup_testing_defaults(env)
            env.update(PATH_INFO="/health", REQUEST_METHOD="GET", wsgi_input=io.BytesIO())
            status = []
            body = b"".join(app(env, lambda value, headers: status.append(value)))
            self.assertEqual(status[0], "200 OK")
            self.assertFalse(json.loads(body)["llm"])

    def test_openapi_routes_match_runtime_routes(self):
        spec = (ROOT / "openapi.yaml").read_text()
        api = (ROOT / "stock_analysis_runtime/api.py").read_text()
        for suffix in [
            "next",
            "artifacts",
            "reconciliation",
            "updates",
            "integrity",
            "handoff",
            "ledger",
        ]:
            self.assertIn(suffix, spec)
            self.assertIn(suffix, api)


if __name__ == "__main__":
    unittest.main()
