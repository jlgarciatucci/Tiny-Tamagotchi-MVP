# Feature Plan — Persistence

## Feature Intent
Persistence ensures that the pet survives refreshes, repeat visits, and hosted deployment conditions. It makes the pet feel continuous rather than session-bound.

## Scope
This feature includes:
- storage of the active pet in Supabase
- storage of pet events
- load and save flows
- first-run detection
- safe handling of missing or invalid data
- resume flow integrating elapsed-time processing

This feature excludes:
- detailed stat decay formulas
- detailed action formulas
- visual UI design

## Design Goals
- one authoritative pet record
- safe startup behavior
- deterministic resume logic
- graceful fallback when data is missing or malformed

## Storage Model

### Authoritative source
Supabase is the source of truth for cross-session pet state.

### Session state role
Streamlit session state may cache the current pet for interaction smoothness within a session, but must not replace database persistence.

## Required Tables

### `pets`
Stores the single active pet state.

### `pet_events`
Stores user actions and important transitions.

## Load Strategy
On app startup:
1. try to fetch the active pet record
2. if no valid pet exists, show creation flow
3. if a valid pet exists, apply elapsed-time simulation based on `last_tick_at`
4. evaluate state transitions
5. persist any updated values from resume processing
6. render the resulting pet

## Save Strategy
After every successful user action or state-changing elapsed update:
- update the `pets` record
- append relevant `pet_events` entries

## Invalid Data Strategy
If fetched pet data is incomplete or malformed:
- do not crash the app
- record a recoverable warning if supported
- fall back to safe recovery behavior

### Safe recovery behavior
Preferred fallback:
- if no reliable pet identity exists, behave as first run
- if pet identity exists but only non-critical values are invalid, normalize or repair data where possible

## Normalization Rules
When loading persisted pet values:
- unknown state values are invalid
- out-of-range stats should be clamped if the rest of the record is trustworthy
- missing required structural fields should invalidate the record
- malformed timestamps should block elapsed-time processing and trigger safe handling

## Event Logging Strategy
The event log should include:
- successful care actions
- sickness transition
- recovery transition
- evolution transition
- critical recoverable persistence anomalies if useful for debugging

## Deployment Considerations
- database credentials stored in Streamlit secrets
- app should remain functional even if event history rendering is temporarily unavailable
- user-facing crashes due to Supabase connection issues should be avoided

## Edge Cases
- first-ever launch
- empty database
- existing but malformed pet
- Supabase unavailable on startup
- save succeeds but event logging fails
- duplicate reloads close together

## Success Criteria
1. The pet persists across refreshes.
2. Offline time is correctly reflected after returning.
3. Missing or broken data does not crash the app.
4. One valid pet record remains authoritative.
