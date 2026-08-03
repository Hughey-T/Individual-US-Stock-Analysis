# Migration and rollback

Previous contract `1.x` is Phase 1–14 plus update Phase 15; preferred contract `2.0.0` is initial Phase 1–18 plus four update Phases. Completed legacy analyses/handoffs remain versioned read-only. Active legacy sessions are not inferred into new Phases, and no outside view or red team is backfilled from later prices. Start a new 2.0.0 analysis instead. A malformed, partial, or identity-ambiguous legacy state is non-migratable. Static 1.x handoffs remain readable by the legacy schema.

Rollback means stop creating 2.0.0 sessions, retain all 2.0.0 artifacts read-only, and resume the prior static templates from a tagged release; never rewrite a 2.0.0 artifact as 1.x. Runtime storage restoration targets a fresh volume and verifies all hashes before switching the active deployment.
