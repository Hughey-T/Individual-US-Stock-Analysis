from __future__ import annotations

import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from validator.validate import COMPLETE, ROOT, validate_tree


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__"))

    def tearDown(self) -> None:
        self.temp.cleanup()

    def codes(self) -> set[str]:
        return {issue.code for issue in validate_tree(self.root)}

    def mutate(self, relative: str, old: str, new: str) -> None:
        path = self.root / relative
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="\n")

    def sample_data(self, relative: str = "examples/standard_sample.md") -> dict:
        text = (self.root / relative).read_text(encoding="utf-8")
        block = re.search(r"^```json\s*\n(.*?)^```\s*$", text, re.MULTILINE | re.DOTALL)
        self.assertIsNotNone(block)
        return json.loads(block.group(1))

    def write_sample(self, data: object, relative: str = "examples/standard_sample.md") -> None:
        path = self.root / relative
        text = path.read_text(encoding="utf-8")
        replacement = "```json\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n```"
        text, count = re.subn(
            r"^```json\s*\n.*?^```\s*$", replacement, text, count=1, flags=re.MULTILINE | re.DOTALL
        )
        self.assertEqual(1, count)
        path.write_text(text, encoding="utf-8", newline="\n")

    def test_valid_repository(self) -> None:
        self.assertEqual([], validate_tree(self.root))

    def test_detects_retired_phase_system(self) -> None:
        marker = "Phase" + "12" + "：" + "更新"
        self.mutate(
            "README.md",
            "# Individual US Stock Analysis",
            "# Individual US Stock Analysis\n\n" + marker,
        )
        self.assertIn("retired-phase-system", self.codes())

    def test_detects_prohibited_wording(self) -> None:
        marker = chr(27573) + chr(38542)
        self.mutate("README.md", "米国個別株", marker + " 米国個別株")
        self.assertIn("retired-label", self.codes())

    def test_detects_missing_phase(self) -> None:
        path = self.root / "templates/standard_analysis.md"
        text = path.read_text(encoding="utf-8")
        start = text.index("## Phase7：")
        end = text.index("## Phase8：")
        path.write_text(text[:start] + text[end:], encoding="utf-8", newline="\n")
        self.assertIn("standard-phases", self.codes())

    def test_detects_duplicate_phase(self) -> None:
        self.mutate("templates/standard_analysis.md", "## Phase8：", "## Phase7：")
        self.assertIn("standard-phases", self.codes())

    def test_detects_invalid_completion(self) -> None:
        self.mutate("templates/standard_analysis.md", COMPLETE, "全て完了しました。")
        self.assertIn("completion", self.codes())

    def test_detects_missing_handoff_key(self) -> None:
        path = self.root / "schema/handoff.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        schema["$defs"]["facts"]["required"].remove("analysis_id")
        path.write_text(
            json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        self.assertIn("handoff-keys", self.codes())

    def test_detects_broken_fence(self) -> None:
        path = self.root / "examples/update_sample.md"
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write("```text\n")
        self.assertIn("markdown-fence", self.codes())

    def test_detects_invalid_handoff_version(self) -> None:
        data = self.sample_data()
        data["handoff_version"] = "2.0"
        self.write_sample(data)
        self.assertIn("handoff-instance", self.codes())

    def test_detects_missing_facts_required_key(self) -> None:
        data = self.sample_data()
        del data["FACTS"]["analysis_id"]
        self.write_sample(data)
        self.assertIn("handoff-instance", self.codes())

    def test_detects_missing_judgments_required_key(self) -> None:
        data = self.sample_data()
        del data["JUDGMENTS"]["強気仮説"]
        self.write_sample(data)
        self.assertIn("handoff-instance", self.codes())

    def test_detects_additional_key(self) -> None:
        data = self.sample_data()
        data["FACTS"]["extra"] = "not allowed"
        self.write_sample(data)
        self.assertIn("handoff-instance", self.codes())

    def test_detects_number_string_and_array_type_mismatches(self) -> None:
        data = self.sample_data()
        data["FACTS"]["基本株式数"] = "100 million"
        data["JUDGMENTS"]["強気仮説"] = ["wrong"]
        data["JUDGMENTS"]["共同シナリオ"] = "wrong"
        self.write_sample(data)
        issues = [issue for issue in validate_tree(self.root) if issue.code == "handoff-instance"]
        self.assertGreaterEqual(len(issues), 3)

    def test_detects_null_where_not_allowed(self) -> None:
        data = self.sample_data()
        data["FACTS"]["analysis_id"] = None
        self.write_sample(data)
        self.assertIn("handoff-instance", self.codes())

    def test_detects_swapped_facts_and_judgments(self) -> None:
        data = self.sample_data()
        data["FACTS"], data["JUDGMENTS"] = data["JUDGMENTS"], data["FACTS"]
        self.write_sample(data)
        self.assertIn("handoff-instance", self.codes())

    def test_detects_invalid_json(self) -> None:
        self.mutate(
            "examples/standard_sample.md", '"handoff_version": "1.0"', '"handoff_version": "1.0",,'
        )
        self.assertIn("handoff-json-syntax", self.codes())

    def test_detects_standard_update_sample_mismatch(self) -> None:
        data = self.sample_data("examples/update_sample.md")
        del data["FACTS"]["主要契約"]
        self.write_sample(data, "examples/update_sample.md")
        codes = self.codes()
        self.assertIn("handoff-instance", codes)
        self.assertIn("handoff-sample-mismatch", codes)

    def test_detects_template_schema_key_mismatch(self) -> None:
        self.mutate("templates/update_analysis.md", "主要契約、主要イベント", "主要イベント")
        self.assertIn("handoff-reference", self.codes())

    def test_detects_schema_properties_required_mismatch(self) -> None:
        path = self.root / "schema/handoff.schema.json"
        schema = json.loads(path.read_text(encoding="utf-8"))
        del schema["$defs"]["facts"]["properties"]["analysis_id"]
        path.write_text(
            json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
        self.assertIn("schema-properties-required", self.codes())

    def test_detects_date_time_without_timezone(self) -> None:
        data = self.sample_data()
        data["FACTS"]["基準日時"] = "2026-07-29T09:00:00"
        self.write_sample(data)
        self.assertIn("handoff-instance", self.codes())

    def test_detects_duplicate_and_unknown_scenario_names(self) -> None:
        data = self.sample_data()
        data["JUDGMENTS"]["シナリオ確率"]["items"][1]["scenario"] = "成功"
        data["JUDGMENTS"]["基準シナリオ"] = "存在しないシナリオ"
        self.write_sample(data)
        codes = self.codes()
        self.assertIn("scenario-name-duplicate", codes)
        self.assertIn("scenario-name-mismatch", codes)
        self.assertIn("baseline-scenario-mismatch", codes)


if __name__ == "__main__":
    unittest.main()
