from __future__ import annotations

import json
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

    def test_valid_repository(self) -> None:
        self.assertEqual([], validate_tree(self.root))

    def test_detects_retired_phase_system(self) -> None:
        marker = "Phase" + "12" + "：" + "更新"
        self.mutate("README.md", "# Individual US Stock Analysis", "# Individual US Stock Analysis\n\n" + marker)
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
        schema["properties"]["FACTS"]["required"].remove("analysis_id")
        path.write_text(json.dumps(schema, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
        self.assertIn("handoff-keys", self.codes())

    def test_detects_broken_fence(self) -> None:
        path = self.root / "examples/update_sample.md"
        with path.open("a", encoding="utf-8", newline="\n") as stream:
            stream.write("```text\n")
        self.assertIn("markdown-fence", self.codes())


if __name__ == "__main__":
    unittest.main()
