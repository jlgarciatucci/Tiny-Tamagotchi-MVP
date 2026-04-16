# Validation — Actions and Feedback

## Validation Levels
1. Automated unit and integration tests
2. Manual reviewer interaction flows

## Automated Test Suite

### AF-AUTO-001 — Feed applies correct effects
**Type:** unit
**Covers:** AF-001, AF-002, AF-003, AF-004, AF-011, AF-021

**Method:**
Apply `feed` to a known state.

**Expected result:**
Hunger +18, Happiness +4, Energy unchanged, then all stats clamped.

### AF-AUTO-002 — Play applies correct effects
**Type:** unit
**Covers:** AF-005, AF-006, AF-007, AF-011, AF-021

**Method:**
Apply `play` to a known state.

**Expected result:**
Happiness +16, Energy -8, Hunger -4, then clamped.

### AF-AUTO-003 — Rest applies correct effects
**Type:** unit
**Covers:** AF-008, AF-009, AF-010, AF-011, AF-021

**Method:**
Apply `rest` to a known state.

**Expected result:**
Energy +20, Happiness -3, Hunger -2, then clamped.

### AF-AUTO-004 — Invalid action rejected
**Type:** unit
**Covers:** AF-012

**Method:**
Call action processor with unsupported action key.

**Expected result:**
Action fails safely and pet state remains unchanged.

### AF-AUTO-005 — Action log entry created
**Type:** integration
**Covers:** AF-014

**Method:**
Perform one valid action through service layer.

**Expected result:**
One corresponding event record is created.

### AF-AUTO-006 — Snack attack message triggers
**Type:** integration
**Covers:** AF-016, AF-019

**Method:**
Seed two recent feed events within 10 minutes, then perform Feed again.

**Expected result:**
Snack attack message appears and stats only reflect normal Feed effects.

### AF-AUTO-007 — Tired play message triggers
**Type:** unit
**Covers:** AF-017, AF-019

**Method:**
Set Energy to 19 and perform Play.

**Expected result:**
Tired play message appears and no extra stat bonus is added.

### AF-AUTO-008 — Cozy rest message triggers
**Type:** unit
**Covers:** AF-018, AF-019

**Method:**
Set Energy to 14 and perform Rest.

**Expected result:**
Energy reaches at least 30 and cozy rest message appears.

### AF-AUTO-009 — Standard feedback fallback
**Type:** unit
**Covers:** AF-013, AF-023, AF-024

**Method:**
Perform a normal Feed with no easter egg condition met.

**Expected result:**
A standard feedback message is returned.

### AF-AUTO-010 — Action processing order stable
**Type:** integration
**Covers:** AF-020, AF-022

**Method:**
Inspect action service result sequence or equivalent outputs.

**Expected result:**
Stats are updated before UI render, event is logged, and transition evaluation is invoked after action application.

## Manual Validation Flows

### AF-MAN-001 — Button actions feel distinct
**Type:** manual UX
**Covers:** AF-001, AF-022

**Steps:**
1. Use Feed, Play, and Rest separately from similar baseline states.
2. Observe stat bars and feedback.

**Expected result:**
Each action has a visibly different effect profile.

### AF-MAN-002 — Immediate feedback quality
**Type:** manual UX
**Covers:** AF-013, AF-024

**Steps:**
1. Perform any valid action.
2. Observe message area.

**Expected result:**
Message appears immediately and is readable and friendly.

### AF-MAN-003 — Actions remain usable in Sick and Evolved states
**Type:** manual smoke
**Covers:** AF-015

**Steps:**
1. Enter Sick state.
2. Use all three actions.
3. Repeat later in Evolved state.

**Expected result:**
All actions remain available in both states.

## Requirement Coverage Matrix
| Requirement | Validation IDs |
|---|---|
| AF-001 | AF-AUTO-001, AF-MAN-001 |
| AF-002 | AF-AUTO-001 |
| AF-003 | AF-AUTO-001 |
| AF-004 | AF-AUTO-001 |
| AF-005 | AF-AUTO-002 |
| AF-006 | AF-AUTO-002 |
| AF-007 | AF-AUTO-002 |
| AF-008 | AF-AUTO-003 |
| AF-009 | AF-AUTO-003 |
| AF-010 | AF-AUTO-003 |
| AF-011 | AF-AUTO-001, AF-AUTO-002, AF-AUTO-003 |
| AF-012 | AF-AUTO-004 |
| AF-013 | AF-AUTO-009, AF-MAN-002 |
| AF-014 | AF-AUTO-005 |
| AF-015 | AF-MAN-003 |
| AF-016 | AF-AUTO-006 |
| AF-017 | AF-AUTO-007 |
| AF-018 | AF-AUTO-008 |
| AF-019 | AF-AUTO-006, AF-AUTO-007, AF-AUTO-008 |
| AF-020 | AF-AUTO-010 |
| AF-021 | AF-AUTO-001, AF-AUTO-002, AF-AUTO-003 |
| AF-022 | AF-AUTO-010, AF-MAN-001 |
| AF-023 | AF-AUTO-009 |
| AF-024 | AF-AUTO-009, AF-MAN-002 |

## Exit Condition
This feature is validated when all ten automated tests and three manual flows pass, and user actions always provide readable immediate feedback.
