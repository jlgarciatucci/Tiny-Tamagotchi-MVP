# Validation — Persistence

## Validation Levels
1. Automated integration and unit tests
2. Manual deployment and refresh checks

## Automated Test Suite

### PR-AUTO-001 — First run with no pet routes safely
**Type:** integration
**Covers:** PR-003, PR-008, PR-019

**Method:**
Run startup logic against empty database state.

**Expected result:**
Creation flow is selected and no crash occurs.

### PR-AUTO-002 — Existing valid pet resumes
**Type:** integration
**Covers:** PR-004, PR-017

**Method:**
Seed a valid pet record and run startup load with known current time.

**Expected result:**
Pet loads, elapsed-time processing runs deterministically, and main view state is returned.

### PR-AUTO-003 — Save after user action
**Type:** integration
**Covers:** PR-005, PR-006

**Method:**
Perform a valid action through application service.

**Expected result:**
Updated pet is persisted and a matching event is appended.

### PR-AUTO-004 — Resume changes are persisted
**Type:** integration
**Covers:** PR-007

**Method:**
Seed a pet with elapsed time greater than one tick and run startup flow.

**Expected result:**
Decayed state is written back before render completion.

### PR-AUTO-005 — Incomplete record invalidated
**Type:** integration
**Covers:** PR-009, PR-019

**Method:**
Seed a pet record missing required structural data.

**Expected result:**
Record is rejected and safe fallback path is used.

### PR-AUTO-006 — Out-of-range stats normalized
**Type:** unit/integration
**Covers:** PR-010, PR-017

**Method:**
Load a record with Hunger = 130 and Energy = -5 while other fields are valid.

**Expected result:**
Stats are normalized to valid bounds and load succeeds if policy allows.

### PR-AUTO-007 — Unknown state handled safely
**Type:** integration
**Covers:** PR-011

**Method:**
Load a record with an unsupported state string.

**Expected result:**
Record is rejected or repaired only through documented safe handling.

### PR-AUTO-008 — Malformed timestamp blocks unsafe resume
**Type:** integration
**Covers:** PR-012

**Method:**
Load a record with malformed `last_tick_at`.

**Expected result:**
Unsafe elapsed-time processing is skipped and app remains stable.

### PR-AUTO-009 — Save failure surfaced
**Type:** integration
**Covers:** PR-014

**Method:**
Mock repository save failure during action processing.

**Expected result:**
Application returns recoverable error signal and does not falsely claim success.

### PR-AUTO-010 — Secrets not hard-coded
**Type:** static/review
**Covers:** PR-020

**Method:**
Review configuration loading path and repository code.

**Expected result:**
Supabase URL and key come from secrets configuration only.

## Manual Validation Flows

### PR-MAN-001 — Refresh persistence check
**Type:** manual smoke
**Covers:** PR-001, PR-015

**Steps:**
1. Create pet and perform action.
2. Refresh the page.

**Expected result:**
Pet state persists across refresh and reload.

### PR-MAN-002 — Return later and observe elapsed resume
**Type:** manual smoke
**Covers:** PR-004, PR-007

**Steps:**
1. Note pet stats.
2. Close app and return later.

**Expected result:**
Elapsed time is reflected in the loaded pet state.

### PR-MAN-003 — Hosted demo startup behavior
**Type:** manual deployment
**Covers:** PR-013, PR-020

**Steps:**
1. Deploy to Streamlit Community Cloud.
2. Configure secrets.
3. Start hosted app.

**Expected result:**
App launches without secret leakage and fails gracefully if secrets are missing or invalid.

## Requirement Coverage Matrix
| Requirement | Validation IDs |
|---|---|
| PR-001 | PR-MAN-001 |
| PR-002 | PR-AUTO-003 |
| PR-003 | PR-AUTO-001 |
| PR-004 | PR-AUTO-002, PR-MAN-002 |
| PR-005 | PR-AUTO-003 |
| PR-006 | PR-AUTO-003 |
| PR-007 | PR-AUTO-004, PR-MAN-002 |
| PR-008 | PR-AUTO-001 |
| PR-009 | PR-AUTO-005 |
| PR-010 | PR-AUTO-006 |
| PR-011 | PR-AUTO-007 |
| PR-012 | PR-AUTO-008 |
| PR-013 | PR-MAN-003 |
| PR-014 | PR-AUTO-009 |
| PR-015 | PR-MAN-001 |
| PR-016 | PR-MAN-001 |
| PR-017 | PR-AUTO-002, PR-AUTO-006 |
| PR-018 | AF-AUTO-006, PR-AUTO-003 |
| PR-019 | PR-AUTO-001, PR-AUTO-005 |
| PR-020 | PR-AUTO-010, PR-MAN-003 |

## Exit Condition
This feature is validated when startup, refresh, return-later, and hosted demo behavior all remain stable and persistence failures are handled transparently.
