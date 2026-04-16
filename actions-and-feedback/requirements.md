# Requirements — Actions and Feedback

## Requirement IDs
All requirements in this file use the prefix `AF`.

### AF-001 — Supported actions
The system shall support exactly three user actions: `feed`, `play`, and `rest`.

### AF-002 — Feed effect on Hunger
The `feed` action shall increase Hunger by 18 points before clamping.

### AF-003 — Feed effect on Happiness
The `feed` action shall increase Happiness by 4 points before clamping.

### AF-004 — Feed effect on Energy
The `feed` action shall not modify Energy.

### AF-005 — Play effect on Happiness
The `play` action shall increase Happiness by 16 points before clamping.

### AF-006 — Play effect on Energy
The `play` action shall decrease Energy by 8 points before clamping.

### AF-007 — Play effect on Hunger
The `play` action shall decrease Hunger by 4 points before clamping.

### AF-008 — Rest effect on Energy
The `rest` action shall increase Energy by 20 points before clamping.

### AF-009 — Rest effect on Happiness
The `rest` action shall decrease Happiness by 3 points before clamping.

### AF-010 — Rest effect on Hunger
The `rest` action shall decrease Hunger by 2 points before clamping.

### AF-011 — Post-action stat clamping
After action effects are applied, all stats shall be clamped to the inclusive range `0` to `100`.

### AF-012 — Invalid action rejection
If an unsupported action key is provided, the system shall reject the action without mutating the pet.

### AF-013 — Immediate user feedback
After each successful action, the system shall display a feedback message in the same session.

### AF-014 — Action event logging
Each successful action shall create an event log entry.

### AF-015 — Action availability in all states
The system shall allow Feed, Play, and Rest in `normal`, `sick`, and `evolved` states.

### AF-016 — Snack attack easter egg
If Feed is used 3 times within the most recent 10 minutes of event history, the system shall display the defined snack attack message.

### AF-017 — Tired play easter egg
If Play is triggered while pre-action Energy is below 20, the system shall display the defined tired play message.

### AF-018 — Cozy rest easter egg
If Rest raises Energy from below 15 to at least 30, the system shall display the defined cozy rest message.

### AF-019 — No hidden easter egg stat bonuses
Easter egg logic shall alter messaging only and shall not modify stats beyond the base action effects.

### AF-020 — Action processing order
The system shall process actions in the order defined in the feature plan.

### AF-021 — Deterministic action outcomes
Given the same pre-action state and the same action input, the resulting pet state shall always be identical.

### AF-022 — Updated stat visibility
After a successful action, the UI shall render the updated stat values.

### AF-023 — Standard feedback fallback
If no easter egg condition is met, the system shall show a standard action feedback message.

### AF-024 — No silent actions
The system shall not perform a successful action without either a standard or special feedback message.
