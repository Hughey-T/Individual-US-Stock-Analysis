# 更新分析の短縮サンプル（架空銘柄 XYZ）

別チャットへ通常分析例の JSON を貼り、`更新` を送った後の Phase15 抜粋です。

## 事実差分（判断より先に表示）

| 項目 | 前回 | 現在 | 分類 |
|---|---|---|---|
| 稼働率 | 70% | 78% | [確認済み事実] 変更 |
| 通期売上見通し | +20% | +22% | [会社主張] 変更 |
| 基本株式数 | 100百万株 | 100百万株 | [確認済み事実] 不変 |

稼働率とガイダンスは同じ実行改善が原因となり得るため、独立した二つの証拠として重複加算しません。差分は「実行・供給」クラスターと、能力売上化のクラックスへ作用します。

## 判断更新

正常化シナリオを45%から50%、遅延を25%から20%へ更新し、他は据え置きます。共同シナリオは25% + 50% + 20% + 5% = 100%です。価値計算の基準を変えるほどの株式数・純負債変化はないためリベースしません。

更新後のサマリーカードと、`FACTS` / `JUDGMENTS` の全キーを持つ単一 JSON を再出力します。以下は更新後の完全な引き継ぎ例です。

```json
{
  "handoff_version": "1.0",
  "FACTS": {
    "analysis_id": "XYZ-20260729-0900JST", "基準日時": "2026-07-29T09:00:00+09:00",
    "基準株価": {"value": 20.0, "currency": "USD", "session": "通常取引"},
    "直近決算期": "FY2026 Q3", "基本株式数": 100000000, "完全希薄化株式数": 110000000,
    "現金": 300000000, "負債": 100000000, "リース負債": 20000000, "企業価値": 1920000000,
    "ガイダンス": [{"name": "売上成長率", "value": 22, "unit": "%", "as_of": "2026-10-29T09:00:00+09:00", "classification": "会社主張"}],
    "主要KPI": [{"name": "稼働率", "value": 78, "unit": "%", "as_of": "2026-10-29T09:00:00+09:00", "classification": "確認済み事実"}],
    "主要契約": [], "主要イベント": [{"summary": "次回決算", "date": null, "classification": "未確認"}],
    "未確認情報": ["新工場の歩留まり"],
    "使用資料": [{"title": "架空Q3報告書", "url": null, "published_at": "2026-10-28T16:00:00-04:00", "accessed_at": "2026-10-29T09:00:00+09:00"}],
    "データ信頼度": {"level": "中", "rationale": "例示用の架空データ"}
  },
  "JUDGMENTS": {
    "強気仮説": "稼働率上昇で固定費を吸収する", "弱気仮説": "遅延が資金需要と希薄化へ連鎖する",
    "クラックス": [{"question": "能力が期限内に売上化するか", "current_judgment": "正常化が優勢", "break_condition": "稼働率が二四半期連続で低下"}],
    "因果モデル": [{"cause": "納入と稼働率上昇", "effect": "粗利とFCFの改善"}],
    "共同シナリオ": [{"name": "成功", "description": "高採算で追加発行なし"}, {"name": "正常化", "description": "採算正常化と小幅発行"}, {"name": "遅延", "description": "資金需要増加"}, {"name": "失敗", "description": "構造的失敗"}],
    "シナリオ確率": {"horizon": "3〜12カ月", "items": [{"scenario": "成功", "probability": 25}, {"scenario": "正常化", "probability": 50}, {"scenario": "遅延", "probability": 20}, {"scenario": "失敗", "probability": 5}]},
    "基準シナリオ": "正常化", "使用した評価モデル": ["EV/売上", "DCF"], "妥当価値帯": "18〜26 USD",
    "投資適格性": "条件付き投資対象", "判断頑健性": {"level": "中", "rationale": "実行改善を確認したが倍率にも感応する"},
    "価格レビューライン": [{"price": 16, "currency": "USD", "review_reason": "下落原因を再確認"}],
    "バリュエーション帯": {"currency": "USD", "割安": "16未満", "妥当": "18〜26", "割高": "28超"},
    "テーゼ無効化条件": ["主要契約解約と資金枯渇"], "更新トリガー": ["次回決算"], "未解決事項": ["新工場の歩留まり"]
  }
}
```

「次」と送信してください。

## Contract 2.0 complete update mapping

The executable fixture `examples/fixtures/update-4.json` maps array index 0–3 to Update Phase 1–4. It contains the strictly newer snapshot/diff, blind causal reassessment, separate revaluation/reverse/red-team result, then active/superseded handoff identities and an append-only `not_matured` ledger outcome. `tests/test_e2e.py` submits these artifacts one per transition and verifies resume, supersession and publication replay.
