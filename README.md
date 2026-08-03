# Individual US Stock Analysis

米国個別株の独立AI分析契約です。

Contract **2.0.0** is an AI-reasoning-first system for independent, point-in-time US-company analysis. The Custom GPT researches and reasons; the machine validates identities, chronology, references, arithmetic, state and persistence. The runtime never generates moat, management quality, theses, assumptions or recommendations. This is neither automatic trading nor brokerage/order execution.

## Architecture and current state

The repository supports the same analytical method through three transports: `standalone_static` needs no runtime and remains conversation-local (`session_local`); `standalone_runtime` validates and persists artifacts in a user-deployed private service; `pipeline` initially projects only a blind comparison handoff. No runtime is deployed by this repository. The Python runtime is optional, local/private, and calls no LLM.

| Layer | Source of truth |
|---|---|
| Initial conversation, 18 Phases | `templates/standard_analysis.md` |
| Update conversation, 4 Phases | `templates/update_analysis.md` |
| Closed data contracts | `schema/contracts.schema.json`, legacy `schema/handoff.schema.json` |
| Semantic/runtime enforcement | `stock_analysis_runtime/` |
| REST contract | `openapi.yaml` |
| Static repository audit | `validator/validate.py` |

## Independence protocol

Pipeline intake exposes security identity, request/horizons/cutoff, verified facts/source references, data quality, dilution definition and unresolved primary-source checks. It hides ranks, classifications, selection rationale, expected return/probability/confidence, upstream theses/recommendations, theme rank, persuasive narrative, target value and future outcomes. Independent scenarios, normal valuation, reverse valuation and red-team artifacts are frozen first. Reconciliation appears only in Phase 17. In standalone mode external analyst target prices are likewise unseen until Phase 17 and can never rewrite the independent valuation.

## Analytical contracts

Material information is separated into `FACTS`, `COMPANY_CLAIMS`, `EXTERNAL_ESTIMATES`, `AI_ASSUMPTIONS`, `AI_JUDGMENTS` and `UNRESOLVED`. Evidence is point-in-time registered. Economic fully diluted shares use a closed bridge, excluding authorized capacity and future financing from the current denominator. A versioned causal graph maps mechanisms and dependency roots so shared causes are not counted as independent evidence.

The 18 initial Phases cover snapshot, business, accounting/dilution, industry, moat, management, narrative, independent bull and bear theses, event study, causal cruxes, outside view, joint scenarios, independent normal valuation, reverse valuation, independent red team, delayed reconciliation, and absolute investment eligibility/handoff/ledger. Joint scenario probabilities total 100%; valuation identities are reproducible. Normal valuation and price-implied reverse valuation remain separate. The AI must challenge itself and need not find the stock investable.

Updates are four explicit Phases: newer snapshot/diff; blind re-evaluation and graph update; separate revaluation/reverse/red-team/reconciliation; eligibility, atomic handoff supersession and append-only ledger. Outcomes remain `not_matured` until their horizon and can later measure return, drawdown, forecast errors, calibration and value-range coverage without future leakage or hindsight edits.

The Entry Strategy handoff is a closed downstream contract and contains one of `NO_ENTRY_REVIEW_REQUIRED`, `ENTRY_REVIEW_ALLOWED`, `ENTRY_REVIEW_CONDITIONAL`, or `RETURN_TO_ANALYSIS`. It is not a buy instruction, and this repository never chooses quantities, timing, staged orders or stops.

## Use

For static use, install the applicable template as the Custom GPT canonical instruction, send a ticker, and thereafter send exact `次`; exact `更新` begins an update after completion. One response produces one Phase. Save the Phase-18 JSON yourself—static mode does not claim durable storage.

For private runtime use, see `docs/runtime.md` and `openapi.yaml`. A minimal local run is:

```bash
STOCK_ANALYSIS_TOKEN=secret STOCK_ANALYSIS_STORAGE=./data python -m stock_analysis_runtime.api
```

## Validation

```bash
python -m unittest discover -s tests -v
python validator/validate.py
python -m ruff check .
python -m ruff format --check .
python -m mypy stock_analysis_runtime
python -m build
```

See `docs/specification.md` for methodology/failure modes, `docs/compliance.md` for requirement mapping, `docs/migration.md` for compatibility/rollback, and `docs/runtime.md` for authentication, deployment, backup and publication integrity.
