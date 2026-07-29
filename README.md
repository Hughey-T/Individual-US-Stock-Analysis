# Individual US Stock Analysis

米国個別株を、新規投資家の視点から一貫した基準で分析するための Custom GPT 向け Markdown 正本です。外部 API や売買機能は含まず、標準ライブラリだけで正本と例を検証できます。

## 正本と責務

| ファイル | 責務 |
|---|---|
| `templates/standard_analysis.md` | 通常分析の唯一の命令正本（Phase1〜14、会話状態、出力契約） |
| `templates/update_analysis.md` | 別チャットで行う更新の唯一の命令正本（Phase15） |
| `schema/handoff.schema.json` | Phase14/15 が共有するキー、型、null可否、配列要素の機械可読なデータ契約 |
| `docs/specification.md` | 正本の読み方、各 Phase の責務、設計判断 |
| `examples/` | 架空企業を使った通常分析と更新分析の短縮例 |

運用規則は正本を優先し、説明文書は規則を再定義せず参照関係を説明します。通常分析と更新分析は独立しており、共有するものは引き継ぎデータだけです。

## 使い方

1. 通常分析では `templates/standard_analysis.md` 全文を Custom GPT の指示へ登録します。
2. 新規チャットでティッカーだけを送り、タイトル返信の後は `次` で Phase を一つずつ進めます。
3. Phase14 の fenced JSON 引き継ぎデータを保存します。
4. 後日、`templates/update_analysis.md` を登録した別チャットへ JSON を貼り、`更新` または `次` を送って Phase15 を実行します。

通常分析は Phase1〜14、更新は Phase15 です。1ターンでは一つだけ実行し、先取りしません。事実は `FACTS`、分析判断は `JUDGMENTS` に分離されます。売買執行や投資先選択ではなく、対象企業の分析と投資適格性までを扱います。

## 設計の要点

- Phase1 の固定スナップショットを後続計算の基準とし、更新は明示的なリベースとして再計算します。
- 基本株式数と経済的完全希薄化株式数を区別し、Phase1・3・10・11で同じ定義を使います。
- 確率は相互排他的な共同シナリオへ付与し、合計100%にします。相互依存する原因を二重計上しません。
- 独立評価を終えた Phase10 で初めて外部の目標株価との差を調べます。
- Phase12 は投資適格性までとし、注文数量・購入タイミングなどの執行判断は作りません。

## 検証

```bash
python3 validator/validate.py
python3 -m unittest discover -s tests -v
```

validator は Phase 配列、会話文、必須要素、引き継ぎ schema、両サンプル内の実データ、確率合計、禁止された指示、UTF-8、LF、Markdown の見出しとコードフェンスを検査します。専用のschema subset validatorを内蔵するため、ネットワークも追加パッケージも不要です。Pull requestとmainへのpushでは `.github/workflows/validate.yml` が同じ検証を実行します。

## ディレクトリ

```text
.
├── README.md
├── .github/workflows/validate.yml
├── docs/{specification.md,compliance.md}
├── examples/{standard_sample.md,update_sample.md}
├── schema/handoff.schema.json
├── templates/{standard_analysis.md,update_analysis.md}
├── tests/test_validator.py
└── validator/validate.py
```

本成果物は教育・調査用の分析手順であり、投資助言や注文執行システムではありません。確認できない数値は推測で補完せず、利用時には一次資料と取得日時を示します。
