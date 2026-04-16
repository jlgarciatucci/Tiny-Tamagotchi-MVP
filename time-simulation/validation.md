# Validation — Time Simulation

## Validation Levels
1. Automated unit and integration tests
2. Manual smoke validation in the deployed app

## Automated Test Suite

### TS-AUTO-001 — No decay before one full tick
**Type:** unit
**Covers:** TS-001, TS-006, TS-007, TS-011

**Method:**
Set elapsed time to 4 minutes 59 seconds.

**Expected result:**
No stats change and `age_ticks` does not change.

### TS-AUTO-002 — Exact one-tick decay
**Type:** unit
**Covers:** TS-001, TS-002, TS-003, TS-004, TS-005, TS-017

**Method:**
Apply exactly one full elapsed tick to a pet with known values.

**Expected result:**
Hunger -4, Happiness -3, Energy -2, age +1.

### TS-AUTO-003 — Multiple elapsed ticks
**Type:** unit
**Covers:** TS-002, TS-003, TS-004, TS-005, TS-018

**Method:**
Apply 3 elapsed ticks to a pet initialized at 80/80/80.

**Expected result:**
Final stats are 68/71/74 and age_ticks increases by 3.

### TS-AUTO-004 — Lower-bound clamp
**Type:** unit
**Covers:** TS-009, TS-020

**Method:**
Apply enough ticks to drive a low stat negative.

**Expected result:**
Stat equals 0 and not below 0.

### TS-AUTO-005 — Upper-bound safety retained
**Type:** unit
**Covers:** TS-010

**Method:**
Run elapsed-time processing on a pet with all stats already at 100 and zero elapsed ticks.

**Expected result:**
Stats remain at or below 100.

### TS-AUTO-006 — Last tick timestamp advancement
**Type:** unit
**Covers:** TS-012

**Method:**
Apply 2 full ticks where current time includes an additional partial tick remainder.

**Expected result:**
`last_tick_at` advances by exactly 10 minutes, not to the full current time.

### TS-AUTO-007 — Offline cap enforced
**Type:** unit
**Covers:** TS-013

**Method:**
Provide elapsed time equivalent to more than 72 ticks.

**Expected result:**
Only 72 ticks are applied.

### TS-AUTO-008 — Future timestamp safe handling
**Type:** unit
**Covers:** TS-014

**Method:**
Use a `last_tick_at` later than current time.

**Expected result:**
Elapsed ticks = 0 and no decay occurs.

### TS-AUTO-009 — Malformed timestamp safe handling
**Type:** integration
**Covers:** TS-015

**Method:**
Load a pet record with missing or malformed `last_tick_at`.

**Expected result:**
System follows safe fallback path without crashing.

### TS-AUTO-010 — Deterministic repeatability
**Type:** unit
**Covers:** TS-016, TS-019

**Method:**
Run the same elapsed-time computation twice with identical inputs.

**Expected result:**
Outputs are identical.

## Manual Validation Flows

### TS-MAN-001 — Refresh after elapsed time
**Type:** manual smoke
**Covers:** TS-008

**Steps:**
1. Load pet and note stat values.
2. Wait at least one full tick duration in a test setup or simulate via admin/debug helper only during development.
3. Refresh.

**Expected result:**
Stats decrease according to the defined decay rates.

### TS-MAN-002 — Long absence remains recoverable
**Type:** manual UX/smoke
**Covers:** TS-013

**Steps:**
1. Return to the app after a sufficiently long simulated elapsed period.
2. Observe resumed state.

**Expected result:**
Pet is degraded but app remains usable and pet is still recoverable.

## Requirement Coverage Matrix
| Requirement | Validation IDs |
|---|---|
| TS-001 | TS-AUTO-001, TS-AUTO-002 |
| TS-002 | TS-AUTO-002, TS-AUTO-003 |
| TS-003 | TS-AUTO-002, TS-AUTO-003 |
| TS-004 | TS-AUTO-002, TS-AUTO-003 |
| TS-005 | TS-AUTO-002, TS-AUTO-003 |
| TS-006 | TS-AUTO-001 |
| TS-007 | TS-AUTO-001 |
| TS-008 | TS-MAN-001 |
| TS-009 | TS-AUTO-004 |
| TS-010 | TS-AUTO-005 |
| TS-011 | TS-AUTO-001 |
| TS-012 | TS-AUTO-006 |
| TS-013 | TS-AUTO-007, TS-MAN-002 |
| TS-014 | TS-AUTO-008 |
| TS-015 | TS-AUTO-009 |
| TS-016 | TS-AUTO-010 |
| TS-017 | TS-AUTO-002 |
| TS-018 | TS-AUTO-003 |
| TS-019 | TS-AUTO-010 |
| TS-020 | TS-AUTO-004 |

## Exit Condition
This feature is validated when all ten automated tests and both manual flows pass and the implementation shows identical elapsed-time behavior across repeated runs.
