# Validation — Pet Core

## Validation Intent
This document proves that the Pet Core feature is complete, testable, and aligned with the written requirements.

## Validation Levels
This feature uses two primary validation levels:

1. **Automated tests** using `pytest`
2. **Manual reviewer flows** for UX and first-run behavior

## Automated Test Suite

### PC-AUTO-001 — Valid creation populates defaults
**Type:** unit
**Covers:** PC-004, PC-005, PC-006, PC-007, PC-010, PC-011, PC-012, PC-013, PC-014, PC-015, PC-016, PC-017, PC-019, PC-026

**Method:**
Call the pet creation service with a valid name such as `Mochi`.

**Expected result:**
- name stored as `Mochi`
- state is `normal`
- hunger = 80
- happiness = 80
- energy = 80
- age_ticks = 0
- is_evolved = false
- evolved_at = null
- timestamps are present

### PC-AUTO-002 — Trim whitespace before storage
**Type:** unit
**Covers:** PC-005

**Method:**
Create a pet with input `  Mochi  `.

**Expected result:**
Stored name is `Mochi`.

### PC-AUTO-003 — Reject blank name
**Type:** unit
**Covers:** PC-004, PC-006, PC-008, PC-009

**Method:**
Attempt creation with `""` and with whitespace-only input.

**Expected result:**
Creation fails with validation error and no pet is created.

### PC-AUTO-004 — Reject overly long name
**Type:** unit
**Covers:** PC-007, PC-008, PC-009

**Method:**
Attempt creation with a 21-character name.

**Expected result:**
Creation fails and returns user-safe validation feedback.

### PC-AUTO-005 — Deterministic defaults
**Type:** unit
**Covers:** PC-025, PC-026

**Method:**
Create two pets in isolated runs with the same valid name while ignoring IDs and timestamps.

**Expected result:**
All default gameplay values are identical.

### PC-AUTO-006 — Existing valid pet skips creation flow
**Type:** integration
**Covers:** PC-020

**Method:**
Seed a valid pet record, then load app bootstrap logic.

**Expected result:**
Bootstrap returns main-view-ready pet state instead of creation-needed state.

### PC-AUTO-007 — Invalid stored pet is flagged
**Type:** integration
**Covers:** PC-021

**Method:**
Seed a malformed pet record missing a required field such as `energy`.

**Expected result:**
System recognizes invalid record and routes to safe fallback path.

## Manual Validation Flows

### PC-MAN-001 — First-run naming flow
**Type:** manual UX
**Covers:** PC-003, PC-004, PC-022, PC-023, PC-024

**Steps:**
1. Start from an empty database state.
2. Open the app.
3. Enter a valid pet name.
4. Submit.

**Expected result:**
- app first shows creation view
- valid submission succeeds
- app transitions to main care view
- name is visible
- pet appears in Normal presentation

### PC-MAN-002 — Invalid input message quality
**Type:** manual UX
**Covers:** PC-008, PC-009

**Steps:**
1. Enter blank or oversized name.
2. Submit.

**Expected result:**
- no pet is created
- feedback is clear and friendly
- user can immediately correct the input

### PC-MAN-003 — Returning user load behavior
**Type:** manual smoke
**Covers:** PC-020

**Steps:**
1. Create a valid pet.
2. Refresh or reopen the app.

**Expected result:**
Creation screen is skipped and the existing pet loads.

## Requirement Coverage Matrix
| Requirement | Validation IDs |
|---|---|
| PC-001 | PC-MAN-001, PC-MAN-003 |
| PC-002 | PC-MAN-001 |
| PC-003 | PC-MAN-001 |
| PC-004 | PC-AUTO-001, PC-AUTO-003, PC-MAN-001 |
| PC-005 | PC-AUTO-001, PC-AUTO-002 |
| PC-006 | PC-AUTO-001, PC-AUTO-003 |
| PC-007 | PC-AUTO-001, PC-AUTO-004 |
| PC-008 | PC-AUTO-003, PC-AUTO-004, PC-MAN-002 |
| PC-009 | PC-AUTO-003, PC-AUTO-004, PC-MAN-002 |
| PC-010 | PC-AUTO-001 |
| PC-011 | PC-AUTO-001 |
| PC-012 | PC-AUTO-001 |
| PC-013 | PC-AUTO-001 |
| PC-014 | PC-AUTO-001 |
| PC-015 | PC-AUTO-001 |
| PC-016 | PC-AUTO-001 |
| PC-017 | PC-AUTO-001 |
| PC-018 | PC-AUTO-001 |
| PC-019 | PC-AUTO-001 |
| PC-020 | PC-AUTO-006, PC-MAN-003 |
| PC-021 | PC-AUTO-007 |
| PC-022 | PC-MAN-001 |
| PC-023 | PC-MAN-001 |
| PC-024 | PC-MAN-001 |
| PC-025 | PC-AUTO-005 |
| PC-026 | PC-AUTO-001, PC-AUTO-005 |

## Exit Condition
The Pet Core feature is considered validated when:
- all automated tests listed above pass
- all three manual flows pass
- no contradictory creation behavior exists elsewhere in the specification set
