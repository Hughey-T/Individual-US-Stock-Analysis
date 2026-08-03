# Legacy test preservation and sample matrix

## Existing validator tests

Every test method present on baseline `93b414d` remains an independent method in `tests/test_validator.py`:

| Baseline method | 2.0 location |
|---|---|
| `test_valid_repository` | unchanged name, 2.0 validator baseline |
| `test_detects_retired_phase_system` | unchanged |
| `test_detects_prohibited_wording` | unchanged |
| `test_detects_missing_phase` | unchanged, now checks the 18-Phase sequence |
| `test_detects_duplicate_phase` | unchanged |
| `test_detects_invalid_completion` | unchanged |
| `test_detects_missing_handoff_key` | unchanged, legacy read-only schema |
| `test_detects_broken_fence` | unchanged |
| `test_detects_invalid_handoff_version` | unchanged |
| `test_detects_missing_facts_required_key` | unchanged |
| `test_detects_missing_judgments_required_key` | unchanged |
| `test_detects_additional_key` | unchanged |
| `test_detects_number_string_and_array_type_mismatches` | unchanged |
| `test_detects_null_where_not_allowed` | unchanged |
| `test_detects_swapped_facts_and_judgments` | unchanged |
| `test_detects_invalid_json` | unchanged |
| `test_detects_standard_update_sample_mismatch` | unchanged |
| `test_detects_template_schema_key_mismatch` | unchanged |
| `test_detects_schema_properties_required_mismatch` | unchanged |
| `test_detects_date_time_without_timezone` | unchanged |
| `test_detects_duplicate_and_unknown_scenario_names` | unchanged |

The baseline actually contains 21 discoverable methods (rather than 17). All 21 are retained. Runtime semantic and publication tests remain in `tests/test_runtime.py`; independent fixture/E2E failure tests are added in `tests/test_e2e.py`. Current discovery count is 59 methods.

## Sample-to-Phase mapping

| Workflow | Fixture entries | Specialized artifacts |
|---|---:|---|
| Initial | `examples/fixtures/initial-18.json` entries 1–18 | snapshot (1), graph (11), outside view (12), scenarios (13), normal value (14), reverse value (15), red team (16), reconciliation (17), handoff/ledger/outcome (18) |
| Update | `examples/fixtures/update-4.json` entries 1–4 | diff (1), blind graph reassessment (2), revaluation/reverse/robustness (3), handoff supersession/ledger/outcome (4) |
| Modes | `examples/fixtures/modes.json` | static session-local, runtime identity, pipeline blind projection and delayed reconciliation |

Legacy fenced JSON remains in both Markdown samples so the original 1.x schema mutation suite stays executable. The adjacent 2.0 mapping points to complete machine-readable fixtures rather than replacing those tests with prose.
