# Feature Plan — Actions and Feedback

## Feature Intent
This feature defines how the user cares for the pet and how the pet responds. It is the interactive heart of the product.

The system must make the three actions feel meaningfully different while also keeping the rules simple enough to understand immediately.

## Scope
This feature includes:
- Feed, Play, Rest action effects
- stat adjustments caused by actions
- immediate UI feedback after actions
- mood messages and easter eggs
- action event logging

This feature excludes:
- passive stat decay over time
- sickness and recovery thresholds
- persistence storage strategy in detail

## Design Goals
- each action should have benefits and tradeoffs
- action outcomes should be visible immediately
- the pet should feel expressive without needing animation-heavy implementation
- copy should add charm without obscuring rules

## Action Definitions

### Feed
Purpose: restore Hunger and slightly comfort the pet.

Effects:
- Hunger `+18`
- Happiness `+4`
- Energy `+0`

### Play
Purpose: boost Happiness through interaction, but spending effort should lower Energy and slightly increase appetite pressure.

Effects:
- Happiness `+16`
- Energy `-8`
- Hunger `-4`

### Rest
Purpose: restore Energy while slightly reducing Happiness due to inactivity and slightly increasing hunger pressure.

Effects:
- Energy `+20`
- Happiness `-3`
- Hunger `-2`

All effects are applied before clamping to the `0–100` range.

## Why these values were chosen
- Feed should feel safe and useful, but not solve all stats.
- Play should be strong for Happiness but carry visible cost.
- Rest should be the best Energy recovery path but not a universal free gain.

## Feedback Strategy
After each action, the app should display:
- a short success message
- the pet’s updated stat bars
- if applicable, a special personality line

## Standard Feedback Copy Categories
- content reaction
- playful reaction
- sleepy reaction
- overwhelmed reaction
- proud reaction after good care

## Easter Egg Rules
The app should include lightweight personality reactions.

### Easter Egg 1 — Snack attack
If the user performs Feed 3 times within the most recent 10 minutes of event history, show a special message:
`"Tiny tummy alert... that was a lot of snacks!"`

### Easter Egg 2 — Tired play reaction
If Play is used while Energy is below 20 before action application, show a special message:
`"I’m playing, but I could really use a nap..."`

### Easter Egg 3 — Cozy rest bonus message
If Rest raises Energy from below 15 to above or equal to 30, show a special message:
`"That nap fixed everything. Almost."`

These are message-only easter eggs and must not add hidden stat bonuses.

## Action Availability
All three actions remain available in Normal, Sick, and Evolved states.

Reasoning:
- the user must always have a recovery path
- the app should not become frustrating through state-based action locking

## Action Processing Order
For a user action:
1. validate action name
2. capture current pet state for message logic if needed
3. apply action stat effects
4. clamp stats to valid range
5. generate standard or special feedback message
6. log action event
7. evaluate state transitions using the state transition feature rules
8. persist updated pet

## Edge Cases
- action would exceed 100 on one stat
- action would reduce stat below 0
- action called with unknown action key
- repeated action spam
- special-message conditions overlapping with standard response

## Success Criteria
1. Each action feels distinct.
2. The user can understand action outcomes by observation.
3. Feedback adds charm without adding confusion.
4. Action processing remains deterministic and testable.
