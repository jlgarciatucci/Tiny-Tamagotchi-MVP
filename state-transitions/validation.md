# Validation — State Transitions

## Validation Levels
1. Automated unit and integration tests
2. Manual scenario validation

## Automated Test Suite

### ST-AUTO-001 — Single bad evaluation does not cause sickness
**Type:** unit
**Covers:** ST-003, ST-004, ST-024

**Method:**
Evaluate a pet with two stats below 25 for one qualifying evaluation only.

**Expected result:**
State does not yet become `sick`.

### ST-AUTO-002 — Two consecutive bad evaluations cause sickness
**Type:** unit
**Covers:** ST-003, ST-004

**Method:**
Provide two consecutive qualifying sickness evaluations.

**Expected result:**
State becomes `sick`.

### ST-AUTO-003 — Single good evaluation does not recover sick pet
**Type:** unit
**Covers:** ST-005, ST-006, ST-025

**Method:**
Start from `sick` and provide one evaluation with all stats at least 40.

**Expected result:**
State remains `sick`.

### ST-AUTO-004 — Two consecutive good evaluations recover non-evolved pet
**Type:** unit
**Covers:** ST-005, ST-006, ST-007

**Method:**
Start from Sick non-evolved pet and provide two qualifying recovery evaluations.

**Expected result:**
State becomes `normal`.

### ST-AUTO-005 — Evolution requires all thresholds
**Type:** unit
**Covers:** ST-009, ST-010, ST-011, ST-012, ST-013, ST-014

**Method:**
Test several nearly qualifying pets, each missing exactly one evolution criterion.

**Expected result:**
No evolution occurs for any incomplete case.

### ST-AUTO-006 — Successful evolution occurs once
**Type:** integration
**Covers:** ST-015, ST-016, ST-017, ST-021

**Method:**
Provide a fully eligible pet, trigger evaluation, then evaluate again later while still eligible.

**Expected result:**
Evolution occurs on first qualifying evaluation only; subsequent evaluations do not create a second evolution event.

### ST-AUTO-007 — Sick blocks evolution
**Type:** unit
**Covers:** ST-014, ST-018

**Method:**
Create an evaluation where evolution thresholds are met but sickness condition also takes priority.

**Expected result:**
Functional state becomes or remains `sick`, not `evolved`.

### ST-AUTO-008 — Evolved pet recovers back to evolved
**Type:** unit
**Covers:** ST-008, ST-016

**Method:**
Use a pet with `is_evolved = true`, set it Sick, then satisfy recovery rule.

**Expected result:**
Recovered state returns to `evolved`.

### ST-AUTO-009 — Transition events logged
**Type:** integration
**Covers:** ST-019

**Method:**
Trigger sickness, recovery, and evolution in isolated scenarios.

**Expected result:**
Each transition creates one distinct event entry.

### ST-AUTO-010 — Deterministic transition logic
**Type:** unit
**Covers:** ST-020, ST-022, ST-023

**Method:**
Repeat the same action/update transition scenario twice with identical counters and inputs.

**Expected result:**
State outcomes and counters match exactly.

## Manual Validation Flows

### ST-MAN-001 — Neglect leads to Sick state
**Type:** manual smoke
**Covers:** ST-003, ST-004

**Steps:**
1. Allow stats to decay or simulate poor conditions.
2. Reach two consecutive qualifying sickness evaluations.

**Expected result:**
Pet visually and functionally becomes Sick.

### ST-MAN-002 — Balanced care recovers the pet
**Type:** manual smoke
**Covers:** ST-005, ST-006, ST-007

**Steps:**
1. Start from Sick state.
2. Use actions to raise all three stats to recovery thresholds across two evaluations.

**Expected result:**
Pet recovers from Sick.

### ST-MAN-003 — Good sustained care reaches evolution
**Type:** manual UX/smoke
**Covers:** ST-009 to ST-017

**Steps:**
1. Keep the pet healthy for enough ticks.
2. Log enough care actions.
3. Reach required stat thresholds.

**Expected result:**
Pet evolves once and shows celebration feedback.

## Requirement Coverage Matrix
| Requirement | Validation IDs |
|---|---|
| ST-001 | ST-MAN-001, ST-MAN-003 |
| ST-002 | PC-AUTO-001 |
| ST-003 | ST-AUTO-001, ST-AUTO-002, ST-MAN-001 |
| ST-004 | ST-AUTO-001, ST-AUTO-002, ST-MAN-001 |
| ST-005 | ST-AUTO-003, ST-AUTO-004, ST-MAN-002 |
| ST-006 | ST-AUTO-003, ST-AUTO-004, ST-MAN-002 |
| ST-007 | ST-AUTO-004, ST-MAN-002 |
| ST-008 | ST-AUTO-008 |
| ST-009 | ST-AUTO-005, ST-MAN-003 |
| ST-010 | ST-AUTO-005, ST-MAN-003 |
| ST-011 | ST-AUTO-005, ST-MAN-003 |
| ST-012 | ST-AUTO-005, ST-MAN-003 |
| ST-013 | ST-AUTO-005, ST-MAN-003 |
| ST-014 | ST-AUTO-005, ST-AUTO-007 |
| ST-015 | ST-AUTO-006 |
| ST-016 | ST-AUTO-006, ST-AUTO-008 |
| ST-017 | ST-AUTO-006 |
| ST-018 | ST-AUTO-007 |
| ST-019 | ST-AUTO-009 |
| ST-020 | ST-AUTO-010 |
| ST-021 | ST-AUTO-006 |
| ST-022 | ST-AUTO-010 |
| ST-023 | ST-AUTO-010 |
| ST-024 | ST-AUTO-001 |
| ST-025 | ST-AUTO-003 |

## Exit Condition
This feature is validated when all transition rules behave consistently in automated testing and the three manual state scenarios can be reproduced reliably.
