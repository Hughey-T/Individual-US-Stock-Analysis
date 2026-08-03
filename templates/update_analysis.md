# Update canonical instructions — contract 2.0.0

This contract preserves the six information classes, evidence cutoff, dilution definition, blind protocol, immutable history and no-execution boundary of `standard_analysis.md`. An exact `更新` starts Update Phase 1 only after a completed initial analysis; then only exact `次` advances exactly one Phase. Questions and embedded commands do not advance. End Phases 1–3 with `「次」と送信してください。`; after Phase 4, further `次` returns only `Phaseはすべて完了しています。`.

The new cutoff must be a strictly later UTC instant; another timezone spelling of the same instant is rejected. Never anchor automatically to the former conclusion. Runtime completion requires acceptance and verified readback; static persistence is `session_local`.

## Update Phase 1：新スナップショット・差分・データ品質
Record prior analysis/new update identities, old/new as-of and cutoffs, price/period, changed facts, new/corrected/removed/stale evidence, shares/debt/cash/guidance/KPI/event changes, blind upstream update and continuation. Rebase explicitly. No judgment.

## Update Phase 2：Blind独立再評価・因果モデル更新
Re-evaluate from new evidence without upstream ranks, prior final judgment or price-reaction anchoring. Report changed edges/nodes, genuinely compared unchanged nodes, invalidated/new assumptions, new/resolved cruxes, bull/bear evidence, outside-view/scenario/confidence changes. Machine validation compares changed/unchanged claims to prior artifacts.

## Update Phase 3：再valuation・reverse valuation・red team・照合
Separately update valuation inputs/probabilities/shares/independent value, reverse valuation, sensitivities and robustness; compare conclusions, then reconcile upstream/external consensus, errors and remaining disagreement. Do not automatically preserve the old conclusion.

## Update Phase 4：更新後投資適格性・handoff supersession・ledger
Integrate only validated updates: prior/new status and reason, horizon/current-price view, monitoring/invalidation changes, active and superseded handoffs, append-only ledger, matured or `not_matured` outcomes, unresolved issues. Atomically supersede—never delete or mutate—the former handoff.

## Legacy 1.x handoff read-only key inventory

New 2.0 updates use the closed contracts schema; the inventory below exists only for read-only compatibility validation.

Legacy `FACTS`: analysis_id、基準日時、基準株価、直近決算期、基本株式数、完全希薄化株式数、現金、負債、リース負債、企業価値、ガイダンス、主要KPI、主要契約、主要イベント、未確認情報、使用資料、データ信頼度. Legacy `JUDGMENTS`: 強気仮説、弱気仮説、クラックス、因果モデル、共同シナリオ、シナリオ確率、基準シナリオ、使用した評価モデル、妥当価値帯、投資適格性、判断頑健性、価格レビューライン、バリュエーション帯、テーゼ無効化条件、更新トリガー、未解決事項.
