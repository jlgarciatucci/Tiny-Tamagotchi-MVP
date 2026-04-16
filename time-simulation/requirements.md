# Requirements — Time Simulation

## Requirement IDs
All requirements in this file use the prefix `TS`.

### TS-001 — Tick duration
The system shall define one simulation tick as exactly 5 real minutes.

### TS-002 — Hunger decay per tick
For each elapsed full tick, the system shall reduce Hunger by 4 points before clamping.

### TS-003 — Happiness decay per tick
For each elapsed full tick, the system shall reduce Happiness by 3 points before clamping.

### TS-004 — Energy decay per tick
For each elapsed full tick, the system shall reduce Energy by 2 points before clamping.

### TS-005 — Age progression
For each elapsed full tick, the system shall increment `age_ticks` by 1.

### TS-006 — Full-tick-only decay
The system shall apply decay only for complete elapsed ticks and shall ignore incomplete partial ticks for stat updates.

### TS-007 — Floor conversion
The system shall calculate elapsed tick count using floor division of elapsed time by tick duration.

### TS-008 — Resume calculation trigger
The system shall evaluate elapsed ticks whenever an existing pet is loaded from persistence.

### TS-009 — Clamp lower bound
After decay is applied, each stat shall be clamped to a minimum of 0.

### TS-010 — Clamp upper bound
After decay is applied, each stat shall be clamped to a maximum of 100.

### TS-011 — No-op for zero ticks
If zero full ticks have elapsed, the system shall not modify stat values or age_ticks.

### TS-012 — Last tick advancement
After applying elapsed full ticks, the system shall advance `last_tick_at` by the consumed number of full ticks.

### TS-013 — Cap offline catch-up
The system shall apply no more than 72 elapsed ticks in a single resume calculation.

### TS-014 — Future timestamp safety
If `last_tick_at` is later than the current time, the system shall treat elapsed ticks as 0 and shall not decay stats.

### TS-015 — Malformed timestamp safety
If `last_tick_at` is missing or malformed, the system shall avoid applying time decay until safe fallback behavior is performed.

### TS-016 — Deterministic elapsed calculation
Given identical input pet state, identical `last_tick_at`, and identical current time, the elapsed-time result shall always be identical.

### TS-017 — Decay order consistency
For each processed tick batch, the system shall apply stat decay, then clamp stats, then update age_ticks, then update `last_tick_at`.

### TS-018 — Batch equivalence
Applying `n` elapsed ticks in one batch shall produce the same final stat result as applying one tick `n` times in sequence, subject to the same clamp rules.

### TS-019 — No hidden randomness in decay
The system shall not randomize decay amounts or tick duration.

### TS-020 — Safe zero result after exhaustion
If decay would reduce a stat below 0, the stat shall remain exactly 0 after clamping.
