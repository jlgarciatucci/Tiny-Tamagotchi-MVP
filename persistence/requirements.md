# Requirements — Persistence

## Requirement IDs
All requirements in this file use the prefix `PR`.

### PR-001 — Authoritative pet persistence
The system shall persist the active pet in Supabase as the cross-session source of truth.

### PR-002 — Event persistence
The system shall persist notable pet events in a `pet_events` store.

### PR-003 — First-run detection
If no valid pet record exists, the system shall route the user to the pet creation flow.

### PR-004 — Existing pet resume
If a valid pet record exists, the system shall load it and perform elapsed-time resume processing before rendering the main view.

### PR-005 — Save after action
After each successful user action, the system shall persist the updated pet state.

### PR-006 — Event append after action
After each successful user action, the system shall append a corresponding pet event.

### PR-007 — Save after state-changing resume
If elapsed-time processing changes the pet state or stats, the system shall persist the updated pet state before rendering completes.

### PR-008 — Missing record safety
If no pet record is found, the system shall not crash.

### PR-009 — Incomplete record invalidation
If a fetched pet record is missing required structural fields, the system shall treat it as invalid.

### PR-010 — Trustworthy stat normalization
If a fetched pet record has out-of-range stat values but is otherwise structurally valid, the system shall normalize those stats into the valid range.

### PR-011 — Invalid state rejection
If a fetched pet record contains an unknown state value, the system shall treat the record as invalid or repairable only if a documented fallback is applied.

### PR-012 — Malformed timestamp safety
If required timestamps are malformed, the system shall avoid unsafe elapsed-time processing and follow safe recovery behavior.

### PR-013 — Supabase startup failure handling
If the app cannot reach Supabase on startup, the system shall show a graceful error state rather than an unhandled exception.

### PR-014 — Supabase save failure handling
If pet saving fails after an attempted action, the system shall report a recoverable error and shall not silently claim durable persistence.

### PR-015 — Session cache as non-authoritative
Session state may cache pet data during runtime, but it shall not be treated as the source of truth across sessions.

### PR-016 — Single active pet record policy
The persistence layer shall enforce or assume one active pet record for the MVP.

### PR-017 — Deterministic load normalization
Given the same persisted record and the same current time, the normalized loaded result shall be deterministic.

### PR-018 — Event history retrieval
The system shall support retrieving recent pet events for display or feedback logic.

### PR-019 — Safe first-run fallback
If the persistence layer cannot provide a trustworthy pet record, the system shall support a safe first-run experience rather than leaving the app in an undefined state.

### PR-020 — No secret leakage
Supabase credentials shall be loaded from secrets configuration and shall not be hard-coded in the repository.
