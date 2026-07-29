#!/usr/bin/env python3
"""Validate canonical stock-analysis Markdown using only the standard library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STANDARD = Path("templates/standard_analysis.md")
UPDATE = Path("templates/update_analysis.md")
SCHEMA = Path("schema/handoff.schema.json")
CONTENT_FILES = [
    Path("README.md"),
    Path("templates/standard_analysis.md"),
    Path("templates/update_analysis.md"),
    Path("docs/specification.md"),
    Path("examples/standard_sample.md"),
    Path("examples/update_sample.md"),
]

PROMPT = "「次」と送信してください。"
COMPLETE = "Phaseはすべて完了しています。"
FACT_KEYS = [
    "analysis_id", "基準日時", "基準株価", "直近決算期", "基本株式数", "完全希薄化株式数",
    "現金", "負債", "リース負債", "企業価値", "ガイダンス", "主要KPI", "主要契約",
    "主要イベント", "未確認情報", "使用資料", "データ信頼度",
]
JUDGMENT_KEYS = [
    "強気仮説", "弱気仮説", "クラックス", "因果モデル", "共同シナリオ", "シナリオ確率",
    "基準シナリオ", "使用した評価モデル", "妥当価値帯", "投資適格性", "判断頑健性",
    "価格レビューライン", "バリュエーション帯", "テーゼ無効化条件", "更新トリガー", "未解決事項",
]


@dataclass(frozen=True)
class Issue:
    code: str
    path: Path
    message: str

    def __str__(self) -> str:
        return f"{self.path}: [{self.code}] {self.message}"


def read_utf8_lf(path: Path, issues: list[Issue]) -> str:
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        issues.append(Issue("encoding", path, f"UTF-8ではありません: {exc}"))
        return ""
    if b"\r" in raw:
        issues.append(Issue("newline", path, "LF以外の改行があります"))
    if not raw.endswith(b"\n"):
        issues.append(Issue("newline", path, "末尾改行がありません"))
    return text


def check_markdown(path: Path, text: str, issues: list[Issue]) -> None:
    if not re.search(r"^# .+", text, re.MULTILINE):
        issues.append(Issue("markdown-heading", path, "H1見出しがありません"))
    fences = re.findall(r"^```", text, re.MULTILINE)
    if len(fences) % 2:
        issues.append(Issue("markdown-fence", path, "コードフェンスが閉じていません"))


def prohibited_patterns() -> dict[str, str]:
    # Build retired wording without embedding it in maintained prose.
    retired_label = chr(27573) + chr(38542)
    return {
        retired_label: "retired-label",
        "Phase12：更新": "retired-phase-system",
        "Phase 12：更新": "retired-phase-system",
        "6〜12カ月を長期": "retired-horizon",
        "食い違うのが普通": "retired-independence",
        "仮説である確信度": "retired-confidence",
        "クラックスを相互独立": "retired-probability",
        "代替投資先との比較を必須": "forbidden-comparison",
        "Phaseはこれで終了です": "retired-completion",
    }


def phase_numbers(text: str) -> list[int]:
    return [int(n) for n in re.findall(r"^## Phase(\d+)(?:：|$)", text, re.MULTILINE)]


def validate_tree(root: Path = ROOT) -> list[Issue]:
    issues: list[Issue] = []
    texts: dict[Path, str] = {}
    for rel in CONTENT_FILES:
        path = root / rel
        if not path.is_file():
            issues.append(Issue("missing-file", rel, "必須ファイルがありません"))
            continue
        text = read_utf8_lf(path, issues)
        texts[rel] = text
        check_markdown(rel, text, issues)
        for phrase, code in prohibited_patterns().items():
            if phrase in text:
                issues.append(Issue(code, rel, f"禁止された表記を検出: {phrase!r}"))

    standard = texts.get(STANDARD, "")
    update = texts.get(UPDATE, "")
    numbers = phase_numbers(standard)
    if numbers != list(range(1, 15)):
        issues.append(Issue("standard-phases", STANDARD, f"Phase見出しは1〜14を一度ずつ順番に置く必要があります: {numbers}"))
    update_numbers = phase_numbers(update)
    if update_numbers != [15]:
        issues.append(Issue("update-phase", UPDATE, f"更新正本の実行単位はPhase15だけです: {update_numbers}"))

    standard_requirements = {
        "title-reply": "{TICKER} yyyy/mm/dd",
        "first-next": "最初の `次` で Phase1",
        "one-phase-turn": "1ターンにつき1Phaseのみ",
        "progress-prompt": PROMPT,
        "completion": COMPLETE,
        "snapshot": "固定スナップショット",
        "rebase": "リベース",
        "dilution-bridge": "完全希薄化ブリッジ",
        "facts": "FACTS",
        "judgments": "JUDGMENTS",
        "probability-total": "シナリオ確率の合計を100%",
        "phase1-target-ban": "アナリスト目標株価は表示しない",
        "phase10-target-order": "独立評価完成後にのみアナリスト目標株価",
    }
    for code, phrase in standard_requirements.items():
        if phrase not in standard:
            issues.append(Issue(code, STANDARD, f"必須要素がありません: {phrase!r}"))

    for rel, text in ((STANDARD, standard), (UPDATE, update)):
        if COMPLETE not in text:
            issues.append(Issue("completion", rel, "正しい完了文がありません"))
        if PROMPT not in text:
            issues.append(Issue("progress-prompt", rel, "正しい進行文がありません"))

    schema_path = root / SCHEMA
    if not schema_path.is_file():
        issues.append(Issue("missing-file", SCHEMA, "schemaがありません"))
        return issues
    try:
        schema = json.loads(read_utf8_lf(schema_path, issues))
    except json.JSONDecodeError as exc:
        issues.append(Issue("schema-json", SCHEMA, f"JSONが不正です: {exc}"))
        return issues
    required_top = schema.get("required", [])
    if required_top != ["handoff_version", "FACTS", "JUDGMENTS"]:
        issues.append(Issue("handoff-top", SCHEMA, "トップレベル引き継ぎキーが不正です"))
    properties = schema.get("properties", {})
    for section, expected in (("FACTS", FACT_KEYS), ("JUDGMENTS", JUDGMENT_KEYS)):
        actual = properties.get(section, {}).get("required", [])
        missing = [key for key in expected if key not in actual]
        extra = [key for key in actual if key not in expected]
        if missing or extra:
            issues.append(Issue("handoff-keys", SCHEMA, f"{section}キー不整合 missing={missing}, extra={extra}"))
        for rel, text in ((STANDARD, standard), (UPDATE, update)):
            absent = [key for key in expected if key not in text]
            if absent:
                issues.append(Issue("handoff-reference", rel, f"{section}引き継ぎ項目が不足: {absent}"))
    return issues


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="検証対象リポジトリ")
    args = parser.parse_args(argv)
    issues = validate_tree(args.root.resolve())
    if issues:
        for issue in issues:
            print(issue)
        print(f"validation failed: {len(issues)} issue(s)")
        return 1
    print(f"validation passed: {len(CONTENT_FILES)} Markdown files, 15 Phase units, handoff schema")
    return 0


if __name__ == "__main__":
    sys.exit(main())
