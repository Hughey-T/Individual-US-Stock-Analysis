# Private runtime operations

The optional Python 3.11+ runtime is a validator and append-only artifact store, not an AI service. It is not hosted or deployed by this repository. Set `STOCK_ANALYSIS_TOKEN`, mount persistent `/data`, then run `docker build -t stock-analysis-runtime .` and `docker run --read-only --tmpfs /tmp -v analysis-data:/data -e STOCK_ANALYSIS_TOKEN=... -p 8080:8080 stock-analysis-runtime`.

Bearer authentication protects every route except `/health`. The state machine exposes create, next contract, submit, freeze-by-progression, reconciliation disclosure, update start, and integrity verification. Final handoff and ledger are ordinary Phase-18 artifacts retrieved from the immutable inventory. Back up by stopping writes and copying the volume; restore into an empty volume and call integrity verification. Atomic rename and readback protect writes; deployments needing multi-process concurrency should place one runtime instance per volume or add an external lock manager.

Publications use canonical UTF-8 JSON, SHA-256, byte length and exact inventory. Duplicate keys, malformed UTF-8, NaN/Infinity, unexpected files, symlinks, path traversal, collisions and modified immutable artifacts are rejected. Identical replay is idempotent. Superseded artifacts remain immutable; active-pointer semantics live in the latest session/ledger artifact.
