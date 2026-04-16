# Feature Plan — Time Simulation

## Feature Intent
Time Simulation makes the pet feel alive by reducing core stats over real elapsed time and by ensuring the pet changes even when the user is away.

This feature is the backbone of the Tamagotchi experience. Without it, the pet becomes a static form with buttons rather than a living companion.

## Scope
This feature includes:
- tick model
- real elapsed-time reconstruction
- decay rates
- stat clamping during decay
- tick-based age progression
- rules for applying offline time

This feature excludes:
- action effects
- sickness and recovery thresholds
- persistence storage mechanics beyond needing timestamps

## Design Goals
- deterministic behavior
- no dependence on long-running server timers
- correct behavior after refresh or later revisit
- easy testability using injected timestamps

## Chosen Model
The pet simulation uses a **discrete tick system** based on elapsed time.

### Tick duration
One tick equals **5 real minutes**.

### Rationale
A 5-minute tick gives the pet a sense of activity without decaying so quickly that a reviewer loses the pet during a short demo.

## Stat Decay Per Tick
On every elapsed tick, the system applies:
- Hunger: `-4`
- Happiness: `-3`
- Energy: `-2`

These values create visible change while leaving enough time for recovery and exploration.

## Age Progression
The pet’s `age_ticks` increases by `1` per applied elapsed tick.

## Offline Resume Strategy
On app load or pet fetch:
1. compute elapsed seconds since `last_tick_at`
2. convert to full elapsed ticks using floor division
3. apply decay once per full tick
4. ignore incomplete remaining partial tick for stat mutation
5. update `last_tick_at` by the consumed tick duration, not necessarily by the current wall clock time if a partial tick remains

This preserves deterministic timing.

## Maximum Offline Catch-Up Cap
To avoid extreme decay during very long absences and to keep demo recovery feasible, elapsed ticks applied in a single resume operation shall be capped at **72 ticks**.

At 5 minutes per tick, this cap represents 6 hours of full simulation.

## Why a cap exists
- protects demo usability
- prevents absurd catch-up jumps
- avoids permanent near-zero states after long inactivity
- keeps the pet recoverable

## Stat Boundaries
After every decay application, each stat must remain within `0` and `100` inclusive.

## Partial Tick Handling
If less than one full tick has elapsed, no decay is applied.

Example:
- last tick at 12:00
- current time 12:04
- elapsed ticks = 0
- no stat decay

## Edge Cases
- zero elapsed time
- partial elapsed tick
- exactly one full tick
- many ticks elapsed
- future timestamp due to clock issues
- malformed timestamp
- negative elapsed duration

## Future Timestamp Rule
If `last_tick_at` is in the future relative to current time, the system shall treat elapsed ticks as zero and flag a recoverable anomaly event.

## Success Criteria
This feature is successful when:
1. The pet visibly changes over time.
2. Refreshing after time passes updates the pet correctly.
3. Stat decay is deterministic and bounded.
4. Long absences do not produce unbounded or broken states.
5. Time logic can be tested entirely without the UI.
