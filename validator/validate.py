#!/usr/bin/env python3
"""Validate canonical stock-analysis Markdown using only the standard library."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STANDARD = Path("templates/standard_analysis.md")
UPDATE = Path("templates/update_analysis.md")
SCHEMA = Path("schema/handoff.schema.json")
STANDARD_SAMPLE = Path("examples/standard_sample.md")
UPDATE_SAMPLE = Path("examples/update_sample.md")
CONTENT_FILES = [
    Path("README.md"),
    Path("templates/standard_analysis.md"),
    Path("templates/update_analysis.md"),
    Path("docs/specification.md"),
    Path("docs/compliance.md"),
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


def extract_fenced_json(path: Path, text: str, issues: list[Issue]) -> object | None:
    blocks = re.findall(r"^```json\s*\n(.*?)^```\s*$", text, re.MULTILINE | re.DOTALL)
    if len(blocks) != 1:
        issues.append(Issue("handoff-json-count", path, f"引き継ぎJSONは1個必要です: {len(blocks)}"))
        return None
    try:
        return json.loads(blocks[0])
    except json.JSONDecodeError as exc:
        issues.append(Issue("handoff-json-syntax", path, f"JSON構文エラー: {exc}"))
        return None


def resolve_ref(schema_root: dict[str, object], reference: str) -> object:
    if not reference.startswith("#/"):
        raise ValueError(f"ローカル参照だけを使用できます: {reference}")
    node: object = schema_root
    for part in reference[2:].split("/"):
        if not isinstance(node, dict) or part not in node:
            raise ValueError(f"参照先がありません: {reference}")
        node = node[part]
    return node


def json_type_matches(value: object, expected: str) -> bool:
    checks = {
        "object": lambda item: isinstance(item, dict),
        "array": lambda item: isinstance(item, list),
        "string": lambda item: isinstance(item, str),
        "number": lambda item: isinstance(item, (int, float)) and not isinstance(item, bool),
        "integer": lambda item: isinstance(item, int) and not isinstance(item, bool),
        "boolean": lambda item: isinstance(item, bool),
        "null": lambda item: item is None,
    }
    return expected in checks and checks[expected](value)


def validate_instance(
    value: object,
    rule: object,
    schema_root: dict[str, object],
    path: str = "$",
) -> list[str]:
    """Validate the JSON Schema subset deliberately used by this repository."""
    if not isinstance(rule, dict):
        return [f"{path}: schema rule must be an object"]
    if "$ref" in rule:
        try:
            resolved = resolve_ref(schema_root, str(rule["$ref"]))
        except ValueError as exc:
            return [f"{path}: {exc}"]
        return validate_instance(value, resolved, schema_root, path)
    errors: list[str] = []
    if "const" in rule and value != rule["const"]:
        errors.append(f"{path}: const {rule['const']!r} required, got {value!r}")
    if "enum" in rule and value not in rule["enum"]:
        errors.append(f"{path}: value {value!r} is not in enum")
    expected = rule.get("type")
    if expected is not None:
        choices = expected if isinstance(expected, list) else [expected]
        if not all(isinstance(choice, str) for choice in choices) or not any(json_type_matches(value, choice) for choice in choices):
            errors.append(f"{path}: type {choices!r} required, got {type(value).__name__}")
            return errors
    if isinstance(value, dict):
        properties = rule.get("properties", {})
        required = rule.get("required", [])
        if not isinstance(properties, dict) or not isinstance(required, list):
            return errors + [f"{path}: properties/required schema definition is invalid"]
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required key {key!r}")
        if rule.get("additionalProperties") is False:
            for key in value:
                if key not in properties:
                    errors.append(f"{path}: additional key {key!r} is not allowed")
        for key, child in value.items():
            if key in properties:
                errors.extend(validate_instance(child, properties[key], schema_root, f"{path}.{key}"))
    if isinstance(value, list):
        minimum = rule.get("minItems")
        if isinstance(minimum, int) and len(value) < minimum:
            errors.append(f"{path}: at least {minimum} items required")
        if "items" in rule:
            for index, child in enumerate(value):
                errors.extend(validate_instance(child, rule["items"], schema_root, f"{path}[{index}]"))
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in rule and value < rule["minimum"]:
            errors.append(f"{path}: value is below minimum {rule['minimum']}")
        if "maximum" in rule and value > rule["maximum"]:
            errors.append(f"{path}: value is above maximum {rule['maximum']}")
    if isinstance(value, str) and rule.get("format") == "date-time":
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                raise ValueError("timezone offset is required")
        except ValueError:
            errors.append(f"{path}: RFC 3339 date-time required")
    return errors


def validate_schema_contract(schema: dict[str, object], issues: list[Issue]) -> None:
    """Ensure every closed object declares exactly the keys it requires/allows."""
    def walk(rule: object, location: str) -> None:
        if not isinstance(rule, dict):
            return
        if rule.get("type") == "object":
            properties = rule.get("properties")
            required = rule.get("required")
            if not isinstance(properties, dict) or not isinstance(required, list):
                issues.append(Issue("schema-object-contract", SCHEMA, f"{location}: properties/requiredが必要です"))
            else:
                missing_properties = [key for key in required if key not in properties]
                optional_properties = [key for key in properties if key not in required]
                if missing_properties or optional_properties:
                    issues.append(Issue("schema-properties-required", SCHEMA, f"{location}: required/properties不一致 missing={missing_properties}, optional={optional_properties}"))
            if rule.get("additionalProperties") is not False:
                issues.append(Issue("schema-additional-properties", SCHEMA, f"{location}: additionalPropertiesはfalseが必要です"))
        for key, child in rule.items():
            if key not in {"properties"} and isinstance(child, (dict, list)):
                walk(child, f"{location}/{key}")
        properties = rule.get("properties", {})
        if isinstance(properties, dict):
            for key, child in properties.items():
                walk(child, f"{location}/properties/{key}")
    walk(schema, "#")


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
    if not isinstance(schema, dict):
        issues.append(Issue("schema-json", SCHEMA, "schemaのトップレベルはobjectが必要です"))
        return issues
    validate_schema_contract(schema, issues)
    required_top = schema.get("required", [])
    if required_top != ["handoff_version", "FACTS", "JUDGMENTS"]:
        issues.append(Issue("handoff-top", SCHEMA, "トップレベル引き継ぎキーが不正です"))
    definitions = schema.get("$defs", {})
    if not isinstance(definitions, dict):
        issues.append(Issue("schema-definitions", SCHEMA, "$defsがありません"))
        return issues
    for section, expected in (("FACTS", FACT_KEYS), ("JUDGMENTS", JUDGMENT_KEYS)):
        definition_name = "facts" if section == "FACTS" else "judgments"
        definition = definitions.get(definition_name, {})
        actual = definition.get("required", []) if isinstance(definition, dict) else []
        missing = [key for key in expected if key not in actual]
        extra = [key for key in actual if key not in expected]
        if missing or extra:
            issues.append(Issue("handoff-keys", SCHEMA, f"{section}キー不整合 missing={missing}, extra={extra}"))
        for rel, text in ((STANDARD, standard), (UPDATE, update)):
            absent = [key for key in expected if key not in text]
            if absent:
                issues.append(Issue("handoff-reference", rel, f"{section}引き継ぎ項目が不足: {absent}"))

    samples: dict[Path, object] = {}
    for rel in (STANDARD_SAMPLE, UPDATE_SAMPLE):
        instance = extract_fenced_json(rel, texts.get(rel, ""), issues)
        if instance is None:
            continue
        samples[rel] = instance
        for message in validate_instance(instance, schema, schema):
            issues.append(Issue("handoff-instance", rel, message))
        if isinstance(instance, dict):
            probabilities = instance.get("JUDGMENTS", {}).get("シナリオ確率", {}).get("items", []) if isinstance(instance.get("JUDGMENTS"), dict) else []
            if isinstance(probabilities, list) and probabilities and all(isinstance(item, dict) and isinstance(item.get("probability"), (int, float)) for item in probabilities):
                total = sum(item["probability"] for item in probabilities)
                if abs(total - 100) > 1e-9:
                    issues.append(Issue("scenario-probability-total", rel, f"シナリオ確率の合計は100が必要です: {total}"))
                scenarios = instance.get("JUDGMENTS", {}).get("共同シナリオ", [])
                scenario_name_list = [item.get("name") for item in scenarios if isinstance(item, dict)] if isinstance(scenarios, list) else []
                probability_name_list = [item.get("scenario") for item in probabilities]
                scenario_names = set(scenario_name_list)
                probability_names = set(probability_name_list)
                if len(scenario_names) != len(scenario_name_list) or len(probability_names) != len(probability_name_list):
                    issues.append(Issue("scenario-name-duplicate", rel, "共同シナリオと確率項目の名称は重複できません"))
                if scenario_names != probability_names:
                    issues.append(Issue("scenario-name-mismatch", rel, "共同シナリオと確率項目の名称が一致しません"))
                baseline = instance.get("JUDGMENTS", {}).get("基準シナリオ")
                if baseline not in scenario_names:
                    issues.append(Issue("baseline-scenario-mismatch", rel, "基準シナリオは共同シナリオの名称と一致する必要があります"))
    if STANDARD_SAMPLE in samples and UPDATE_SAMPLE in samples:
        for section in ("FACTS", "JUDGMENTS"):
            left = samples[STANDARD_SAMPLE].get(section, {}) if isinstance(samples[STANDARD_SAMPLE], dict) else {}
            right = samples[UPDATE_SAMPLE].get(section, {}) if isinstance(samples[UPDATE_SAMPLE], dict) else {}
            if not isinstance(left, dict) or not isinstance(right, dict) or set(left) != set(right):
                issues.append(Issue("handoff-sample-mismatch", UPDATE_SAMPLE, f"通常例と更新例の{section}キーが一致しません"))
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
