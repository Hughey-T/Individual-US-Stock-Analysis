# Specification 2.0.0

## Responsibilities and modes

AI performs research, interpretation, causal reasoning, bull/bear theses, crux/outside-view/scenario assumptions, valuation assumptions, red-team reasoning, eligibility and natural-language explanation. Machine code checks only identity, cutoff, ordering, schema/references, immutable bytes, share/probability/valuation arithmetic, supersession and outcome maturity. It does not certify truth.

`standalone_static`, `standalone_runtime`, and `pipeline` share one analytical contract. Static mode is session-local and exports JSON. Runtime mode adds identity and durable immutable history. Pipeline mode adds blind intake and delayed reconciliation.

## Evidence and snapshot

Six-class taxonomy prevents claims, estimates and assumptions from masquerading as facts. Evidence records carry identity/type/title/publisher/source identity, published/retrieved/as-of timestamps, company/industry/macro scope, classification, fields, reliability, point-in-time eligibility and notes. Cutoff/future/unknown/duplicate/source-less/misclassified and silently stale evidence fails validation. AI judgments additionally carry support, opposition, roots, confidence, uncertainty and invalidation.

Phase 1 freezes the full identity/time/market/capital snapshot and evidence/blind hashes. Rebase replaces it only through a new revision. The dilution bridge enumerates common stock, warrants, converts, awards/options/ESPP, consideration/earnouts, treasury adjustment, exclusions, authorized capacity and financing overlay. Only economically included components sum to current fully diluted shares.

## Causality, scenarios and value

Graph nodes cover external/industry/company/customer/supplier/operating/financial/value concepts. Edges specify direction, lag, mechanism, evidence and contrary evidence, confidence/status and a dependency root. Duplicate `(root, claim)` evidence is rejected. Reference classes and their selection/survivorship limits form a separate outside view.

Scenarios are mutually exclusive within a horizon and sum to 100%; dependent crux odds are never multiplied blindly. Each scenario closes operating, financing, dilution, terminal and valuation assumptions. The machine recalculates EV, equity, per share, returns, downside and weighted value. Normal valuation estimates intrinsic value from independent assumptions. Reverse valuation solves exactly one primary market-implied variable while holding the rest explicit. Red team is a separate artifact and may confirm or overturn the original.

Absolute eligibility compares required return, cash, broad equity, risk-free/user hurdle, downside and permanent loss. Cross-company ranking belongs upstream. Phase 18 only integrates validated work into a monitoring plan, entry handoff and decision ledger.

## State, update, outcomes and failures

Exact `次` advances one initial/update Phase; exact `更新` starts an update. Embedded commands, questions, skips and post-final advancement do not progress. Runtime states are `not_generated`, `generated_not_persisted`, `persisted_pending_verification`, `integrity_verified`, `failed_terminal`, and `superseded`; only accepted plus successful readback completes a Phase. Independent artifacts freeze before Phase 17. Corrections append revisions with prior/new hashes, evidence, logic, changed fields, reason and time.

The four-Phase update requires a strictly newer UTC cutoff, compares actual changed/unchanged fields, re-evaluates blind, reruns both valuation directions and red team, and atomically supersedes the handoff. Ledger horizons include 1/3/6/12/24/36 months. Outcome records start `not_matured` and later support return/benchmark/excess, MDD/MAE/MFE/volatility/downside capture, catalyst/invalidation realization, KPI/revenue/margin/FCF/dilution errors, calibration, range coverage and decision/override/robustness accuracy.

Failure is conservative: missing data stays unresolved; identity or cutoff mismatch rejects; stale data requires warning; impossible arithmetic fails; unavailable runtime is never described as live; storage corruption requires restore rather than mutation. See migration and runtime documents for rollback and operational recovery.
