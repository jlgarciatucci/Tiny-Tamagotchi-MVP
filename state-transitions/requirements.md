# Requirements — State Transitions

## Requirement IDs
All requirements in this file use the prefix `ST`.

### ST-001 — Supported states
The system shall support the functional states `normal`, `sick`, and `evolved`.

### ST-002 — Normal as default state
A newly created pet shall begin in the `normal` state.

### ST-003 — Sickness threshold definition
The system shall consider the sickness condition satisfied when at least two of the three stats are below 25 in a given evaluation.

### ST-004 — Sickness streak threshold
The system shall transition the pet into `sick` only after the sickness condition is satisfied for 2 consecutive full-tick evaluations.

### ST-005 — Recovery threshold definition
The system shall consider the recovery condition satisfied when Hunger, Happiness, and Energy are all at least 40 in a given evaluation.

### ST-006 — Recovery streak threshold
The system shall transition a Sick pet out of `sick` only after the recovery condition is satisfied for 2 consecutive evaluations.

### ST-007 — Recovery target for non-evolved pet
If a non-evolved Sick pet recovers, its state shall become `normal`.

### ST-008 — Recovery target for evolved pet
If an evolved Sick pet recovers, its state shall become `evolved`.

### ST-009 — Evolution minimum age
The pet shall not evolve unless `age_ticks` is at least 12.

### ST-010 — Evolution minimum hunger
The pet shall not evolve unless Hunger is at least 70.

### ST-011 — Evolution minimum happiness
The pet shall not evolve unless Happiness is at least 70.

### ST-012 — Evolution minimum energy
The pet shall not evolve unless Energy is at least 70.

### ST-013 — Evolution interaction requirement
The pet shall not evolve unless at least 6 care actions have been logged.

### ST-014 — Evolution blocked while sick
The pet shall not evolve while its functional state is `sick`.

### ST-015 — Single evolution only
The pet shall evolve at most once during its lifetime.

### ST-016 — Evolution flag persistence
When evolution occurs, the system shall set `is_evolved` to `true` and shall retain that value permanently.

### ST-017 — Evolved timestamp
When evolution occurs, the system shall set `evolved_at` to a valid timestamp.

### ST-018 — State priority
If sickness and evolution eligibility are both satisfied during the same evaluation, the system shall prioritize `sick` over `evolved`.

### ST-019 — Transition event logging
The system shall create distinct event entries for becoming Sick, recovering, and evolving.

### ST-020 — Consecutive streak tracking
The system shall track consecutive sickness-condition and recovery-condition evaluations in a way that produces deterministic state transitions.

### ST-021 — No repeated evolution events
If `is_evolved` is already true, future evaluations shall not generate another evolution event.

### ST-022 — Deterministic transition outcomes
Given the same pet state, counters, and evaluation input, the resulting functional state shall always be identical.

### ST-023 — Evaluation after actions and elapsed updates
The system shall evaluate state transitions after user actions and after elapsed-time updates.

### ST-024 — No immediate sickness from single bad evaluation
The pet shall not become Sick after only one evaluation that satisfies the sickness threshold.

### ST-025 — No immediate recovery from single good evaluation
The pet shall not recover from Sick after only one evaluation that satisfies the recovery threshold.
