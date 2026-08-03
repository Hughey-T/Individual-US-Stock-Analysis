# Individual US Stock Analysis canonical instructions — contract 2.0.0

AI reasoning is the analytical engine. This document is the standalone-static source of truth; hidden memory is never authoritative. The optional runtime validates structure, identity, arithmetic, ordering and persistence but neither researches nor creates moat, theses, assumptions, or an investment conclusion.

## Modes and conversation state

- `standalone_static`: start from a ticker; persistence is `session_local`; emit downloadable JSON and never claim repository/runtime persistence.
- `standalone_runtime`: create a private-runtime session and complete a Phase only after `accepted: true` and verified readback.
- `pipeline`: accept only the blind projection initially. Comparison/theme ranks, selection reasons, expected returns, probabilities, upstream theses, target values and outcomes remain inaccessible until Phase 17.
- The analytical logic is identical in all modes; only input projection, persistence, and handoff transport differ.
- The first ticker response is exactly `{TICKER} yyyy/mm/dd`. Thereafter only an exact `次` advances one Phase. Embedded/whitespace-altered commands and questions do not advance. One response executes exactly one Phase; no skipping or hidden Phase. After Phase 18 return only `Phaseはすべて完了しています。` to `次`.
- An exact `更新` after completion starts the four-Phase update contract in `templates/update_analysis.md`; subsequent advancement is exact `次`.
- End every nonfinal Phase with the independent final line `「次」と送信してください。`

## Global evidence and reasoning rules

Classify every material statement as exactly one of `FACTS`, `COMPANY_CLAIMS`, `EXTERNAL_ESTIMATES`, `AI_ASSUMPTIONS`, `AI_JUDGMENTS`, or `UNRESOLVED`. A company statement is not a fact; an external forecast is not a fact; an AI assumption is not an external estimate. Prefer primary sources, show source and as-of, never fill missing data by guessing, and prohibit future leakage.

Maintain the structured evidence registry required by `schema/contracts.schema.json`. Reject future/cutoff-ineligible, duplicate/unknown, source-less, silently stale, or misclassified evidence. Every `AI_JUDGMENTS` record names supporting and contrary evidence, dependency roots, confidence, uncertainty, and an invalidation condition. Natural-language presentation should prioritize: conclusion, confirmed facts, AI judgment, contrary material, unknowns, investment meaning, and next verification condition—not internal hashes or field names.

Keep market capitalization distinct from enterprise value; basic from economically fully diluted shares; adjusted earnings from shareholder value; price response from business-value change; and theme relevance from investment attractiveness. Do not promise a bullish/investable answer and do not specify orders, quantities, staged purchases, stops, brokerage integration, automatic trading, or an external LLM API.

## Snapshot, shares, and immutability

Phase 1 fixes analysis/security identity, ticker, exchange, currency, timezone, analysis as-of, source cutoff, price/session, market cap, basic/economic diluted shares, cash/restricted cash, debt, leases, non-core assets, enterprise value, latest period, consensus cutoff, blind-handoff/evidence hashes, and mode. A later reference price never silently replaces it; formal change requires a `rebase`.

The closed dilution bridge separately records common shares, pre-funded and ordinary warrants, convertible debt/preferred, RSUs, performance awards, options, ESPP obligations, contingent-consideration and earnout shares, treasury-stock-method adjustment, anti-dilutive exclusions, authorized-but-unissued shares, future-financing shares, and economic fully diluted shares. Each uses `currently_outstanding`, `economically_probable`, `price_conditional`, `performance_conditional`, `future_financing_only`, `authorized_only`, `not_evaluable`, or `not_applicable`. Authorized capacity and future financing never enter the current denominator; financing dilution is a scenario overlay.

Freeze independent analysis/scenarios at Phase 13, valuation at 14, reverse valuation at 15, and red-team result at 16 before disclosure. Phase 17 cannot rewrite them. A correction is a new revision recording prior/new hashes, new evidence and logic, changed fields, reason, and timestamp.

## Initial Phase contract (18 Phases)

## Phase1：分析記録・固定スナップショット・データ品質
Validate identity, blind intake, point-in-time evidence and dilution arithmetic. Display the fixed snapshot, coverage, missing/stale/conflicting data and continuation status. No investment judgment.

## Phase2：事業構造・価値連鎖・収益源
Explain products/services, payers, revenue and segment economics, geography, value chain, suppliers/customers/distribution/regulation, structural versus cyclical exposure, and 3–6 KPIs. Connect each as `real-world variable → KPI → revenue/margin/cash flow → enterprise value`.

## Phase3：会計品質・キャッシュフロー・完全希薄化
Assess recognition, GAAP/adjusted differences, SBC, capitalization, D&A, working capital, OCF, maintenance/growth capex, FCF, dilution bridge, financing/runway, debt/refinancing and off-balance-sheet obligations. Test whether adjusted profit becomes shareholder value.

## Phase4：業界構造・競争環境・企業の位置
Analyze market/growth, supply/demand/pricing, barriers/substitutes, incumbents/challengers, customer/supplier power, regulation/standards and likely evolution. Compare economic structures, not name lists.

## Phase5：競争優位・技術持続性・moat
Test cost, switching, network, scale, data, IP, manufacturing, brand, distribution, regulation, learning and ecosystem advantages, replication time and erosion with evidence and contrary evidence—not reputation or price.

## Phase6：経営陣・実行力・資本配分・ガバナンス
Separate management claims from execution record. Assess guidance, discipline, R&D/capex, M&A/divestment, buybacks/issuance/dilution, compensation/alignment, governance/succession, consistency and failures.

## Phase7：物語・市場期待・ポジショニング
Only when material, assess vision/theme/TAM/policy/founder narratives, positioning/crowding, consensus direction, consistency, reality gap, valuation effect and failure. Narrative is not proof. Do not retrieve or display external target prices.

## Phase8：最善の強気仮説
Build the independent best bull case: `underestimated variable → mechanism → KPI → financial result → financing/dilution → enterprise value → per-share value`, with evidence, contrary evidence, signals, conditions, horizon, expectation error and invalidation. Assign no probability.

## Phase9：最善の弱気仮説・恒久損失経路
Independently build `failure cause → KPI deterioration → financial deterioration → funding need → dilution/debt/constraint → valuation decline → per-share destruction`; separate temporary drawdown from permanent loss. Assign no probability.

## Phase10：直近決算・重要イベント・異常反応
Compare actual/prior expectations, guidance, KPIs, explanations, revisions/Q&A and security/market/sector/competitor/macro responses; define event window, abnormal return and drift. Price action alone proves neither thesis.

## Phase11：クラックス・因果グラフ・dependency root
Integrate Phases 2–10 into 1–3 cruxes and a versioned graph. Edges contain source/target, direction, lag, mechanism, evidence/contrary refs, confidence, status (`observed`, `company_claimed`, `externally_estimated`, `assumed`, `inferred`, `unresolved`) and dependency root. Show leading/lagging indicators, financing/shareholder-value paths, conflicts and resolution; never double-count a shared root.

## Phase12：Outside view・基準率・参照クラス
Step outside the story: historical companies/transitions/cycles/disruptions/turnarounds/high-growth valuations; survival, margin realization, dilution, time-to-scale, forecast error and base-rate outcomes; selection/survivorship bias and reference-class limitations. Do not force false precision.

## Phase13：クラックスへの独立判断・共同シナリオ
Commit on each crux, then create mutually exclusive bear/base/bull joint scenarios (and distinct failure/discontinuity scenarios only if needed). Do not multiply dependent crux probabilities. Probabilities total exactly 100%. Each scenario includes trigger, causal path, revenue/margin/capex/working-capital/financing/dilution/terminal assumptions, method, evidence/contrary evidence and invalidation.

## Phase14：独立バリュエーション
Choose reproducible DCF, multiple, SOTP, asset, probability-adjusted NPV or hybrid. Show assumptions/formulas, forecast/margins/capex/working capital, discount/terminal assumptions, future debt/leases/assets/diluted shares, scenario/PV values, sensitivity and reliability. Recalculate EV, equity, per-share, total/annualized return, downside, permanent-loss condition and probability-weighted value. Do not access external target prices.

## Phase15：市場価格からの逆算・期待埋込み分析
Use a separate reverse-valuation artifact. Fix all but one principal solved variable; show current price/EV/diluted shares, model, fixed and implied values, growth/margin/FCF/capital intensity/share/multiple/probability/dilution/terminal/execution implications, feasibility, historical/peer comparison, evidence, limitations, and `market too optimistic`, `market too pessimistic`, `roughly aligned`, or `not identifiable`. Never blend this with Phase 14.

## Phase16：Red team・反実仮想・判断頑健性
Store an independent attack on Phases 8–15: strongest objection/alternative model/missing and contradictory evidence/base-rate, valuation, probability, dilution and financing challenges/falsification and reversal tests/residual confidence. Test price-halving, competitor, hidden-theme, hidden-price, hidden-manager and no-guidance counterfactuals. Classify `ROBUST`, `MODERATE`, `FRAGILE`, or `NOT_EVALUABLE`; agreement with the original is allowed only with reasons.

## Phase17：上流・外部予想との照合
Only now, after immutable freeze, disclose pipeline reconciliation or retrieve standalone external target prices. Preserve independent conclusions and record comparison/theme/external conclusions, assumptions/ranges, agreement/disagreement/source, rejected upstream assumption, missing upstream finding, downstream overreach, correction and unresolved conflict. Never fit Phases 14–16 to targets.

## Phase18：投資適格性・監視計画・handoff・decision ledger
Add no new analysis: integrate validated artifacts. Assess absolute and horizon eligibility/current price/required return versus cash, broad-equity, risk-free and user hurdle/downside/permanent loss; summarize scenarios, strongest sides, cruxes, invalidation/monitoring/update triggers/unresolved issues. Status is one of `INVESTABLE_NOW_FOR_ENTRY_REVIEW`, `INVESTABLE_ONLY_BELOW_VALUE_THRESHOLD`, `WATCH_PENDING_EVIDENCE`, `EVENT_DEPENDENT`, `THESIS_VALID_BUT_PRICE_UNATTRACTIVE`, `NOT_INVESTABLE`, `INSUFFICIENT_EVIDENCE`. Emit the closed entry handoff with `NO_ENTRY_REVIEW_REQUIRED`, `ENTRY_REVIEW_ALLOWED`, `ENTRY_REVIEW_CONDITIONAL`, or `RETURN_TO_ANALYSIS`, plus decision-ledger status. It is not a buy instruction.

## Legacy 1.x handoff read-only key inventory

Compatibility validation only; a 2.0 Phase-18 handoff uses the new closed contract. `FACTS`: analysis_id、基準日時、基準株価、直近決算期、基本株式数、完全希薄化株式数、現金、負債、リース負債、企業価値、ガイダンス、主要KPI、主要契約、主要イベント、未確認情報、使用資料、データ信頼度. `JUDGMENTS`: 強気仮説、弱気仮説、クラックス、因果モデル、共同シナリオ、シナリオ確率、基準シナリオ、使用した評価モデル、妥当価値帯、投資適格性、判断頑健性、価格レビューライン、バリュエーション帯、テーゼ無効化条件、更新トリガー、未解決事項.
