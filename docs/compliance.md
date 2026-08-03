# Compliance matrix — 2.0.0

| Requirement | Implementation | Verification |
|---|---|---|
| 18 initial / 4 update, exact commands, one response | canonical templates | static validator + state tests |
| Three modes and static boundary | README/templates/state | mode tests |
| Blind rank/target withholding until Phase 17 | template + `SessionRuntime.disclose` | disclosure tests |
| Six information classes and evidence registry | schema + semantic validator | evidence mutations |
| Snapshot/rebase and closed dilution bridge | template/schema/validation | arithmetic/exclusion tests |
| Causal graph/dependency roots | schema methodology + validation | unknown/double-count tests |
| Outside view and joint scenarios | Phases 12/13 | template audit + scenario tests |
| Normal/reverse valuation separation | Phases 14/15 + validator | one-solved-variable tests |
| Independent red team | Phase 16 + schema | contract tests |
| Immutable reconciliation and revisions | state/storage/templates | collision/order tests |
| Eligibility separated from execution | Phase 18 + handoff states | forbidden wording audit |
| Four-Phase blind update/supersession | update template/state | cutoff/progression tests |
| Decision ledger/outcomes | Phase 18/specification | future-leakage contract tests |
| Optional REST/runtime/auth/storage | package/OpenAPI/Dockerfile | API/storage/build tests |
| Publication integrity | `storage.py` | encoding/key/hash/path/replay tests |
| Legacy compatibility/migration/rollback | legacy schema + migration doc | static inventory audit |
| No LLM, broker, automatic orders | README/runtime/templates | forbidden wording audit |
