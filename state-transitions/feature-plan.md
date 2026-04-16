# Feature Plan — State Transitions

## Feature Intent
This feature defines when the pet is Normal, Sick, or Evolved, and how it moves between those states.

These transitions give consequences to care quality and provide emotional stakes. They also create visible milestones in the pet relationship.

## Scope
This feature includes:
- sickness trigger
- sickness recovery path
- evolution trigger
- state priority rules
- one-time evolution rule
- state-driven feedback events

This feature excludes:
- core stat decay formulas
- action effect formulas
- persistence storage mechanics

## State Definitions

### Normal
Default condition when the pet is functioning without critical neglect and has not yet evolved.

### Sick
A warning state caused by sustained neglect. The pet is still recoverable.

### Evolved
A positive milestone reached through sustained good care. This occurs only once.

## Transition Philosophy
- Sickness should not trigger instantly from one bad moment.
- Recovery should require deliberate care, not a single lucky action.
- Evolution should feel earned through consistency.
- State transitions must be deterministic and understandable.

## Sickness Rule
The pet becomes Sick when **at least two of the three stats are below 25 for 2 consecutive full ticks**.

### Why this rule
- protects against accidental sickness from one bad stat
- creates meaningful neglect signal
- remains achievable in testing and demo

## Recovery Rule
A Sick pet returns to Normal when **all three stats are at least 40 for 2 consecutive evaluations**.

An evaluation occurs after either:
- an elapsed-time update operation, or
- a user action

### Why this rule
- requires balanced care
- avoids instant state flipping
- stays understandable to users

## Evolution Rule
The pet evolves once when all of the following are true:

1. `is_evolved` is false
2. current state is not Sick
3. `age_ticks` is at least 12
4. Hunger is at least 70
5. Happiness is at least 70
6. Energy is at least 70
7. the pet has at least 6 logged care actions total

### Why this rule
- prevents immediate evolution after creation
- rewards ongoing engagement
- avoids evolution from passive waiting

## State Priority Rules
When multiple state conditions could apply in the same evaluation, priority shall be:

1. Sick
2. Evolved
3. Normal

This means sickness blocks evolution until the pet is healthy.

## One-Time Evolution Rule
Once a pet evolves:
- `is_evolved` becomes true
- `evolved_at` is set
- the pet remains in Evolved presentation unless later sickness overrides presentation as specified below

## Sick vs Evolved presentation policy
If an evolved pet later satisfies the Sick condition, the functional state shall become `sick` for gameplay purposes, but the permanent `is_evolved` flag shall remain true.

When that pet recovers, its displayed state returns to `evolved` rather than `normal`.

This preserves the one-time milestone.

## Transition Event Messages
The system should create notable event messages for:
- becoming sick
- recovering from sickness
- evolving

These events should be distinct from ordinary action messages.

## Internal Tracking Needs
To support consecutive evaluations, the system should track:
- sick condition streak counter
- recovery condition streak counter

These counters may be derived or stored, but behavior must remain consistent.

## Edge Cases
- pet oscillates around thresholds
- pet qualifies for sickness and recovery on different evaluations
- pet qualifies for evolution on same evaluation that sickness also triggers
- evolved pet becomes sick later
- repeated re-checks after already evolved

## Success Criteria
1. Neglect meaningfully changes the pet’s condition.
2. Recovery feels earned but not frustrating.
3. Evolution is a clear reward for good care.
4. The state system is internally consistent and testable.
