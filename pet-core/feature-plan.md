# Feature Plan — Pet Core

## Feature Intent
The Pet Core feature defines the foundational identity and baseline data model of the virtual pet. It answers the questions:

- What is a pet in this system?
- How is a pet created?
- What information must always exist for the app to function?
- What default state does the pet begin in?

This feature is deliberately narrow. It does not define time decay, action effects, or state transitions in detail; those are handled by other feature specifications.

## Why This Feature Exists
Every other feature depends on a stable, explicit pet model. Without a well-defined core, downstream behavior becomes inconsistent or under-specified.

## Scope
This feature includes:
- pet creation flow
- pet naming
- default stats
- baseline state
- single active pet rule
- pet identity and metadata
- first-run behavior

This feature excludes:
- stat decay formulas
- action behavior
- sickness and recovery logic
- evolution logic beyond default flags
- database persistence mechanics

## User Story
As a first-time user, I want to create and name my pet quickly so I can start caring for it immediately.

## Product Decisions

### Single active pet only
The app supports exactly one active pet. There is no pet selection screen and no pet switching.

### Naming is mandatory
The user must provide a non-empty valid name before entering the main care loop.

### Friendly first-run flow
On first launch, the app should feel welcoming and lightweight rather than setup-heavy.

## Functional Outline

### First launch
If no pet exists, the app shows:
- title
- short welcome copy
- pet naming input
- create button

### After creation
Once the pet is created, the app transitions to the main care view and shows:
- pet name
- avatar in Normal state
- current stat values
- available actions

### Returning launch
If a pet already exists, the app loads that pet and bypasses the creation form.

## Pet Data Fields
At minimum, the pet model should contain:
- unique identifier
- name
- state
- hunger
- happiness
- energy
- age in ticks
- evolution flag
- created timestamp
- updated timestamp
- last tick timestamp

## Default Initialization Rules
Upon creation, the pet starts with:
- state: `normal`
- hunger: `80`
- happiness: `80`
- energy: `80`
- age_ticks: `0`
- is_evolved: `false`
- evolved_at: `null`

These values are chosen to create a safe and optimistic starting experience without instantly pressuring the user.

## Name Validation Strategy
The pet name must:
- be required
- be trimmed before validation
- contain between 1 and 20 characters after trimming
- be stored exactly as validated

The name must not:
- be empty after trimming
- exceed 20 characters
- consist only of whitespace

No profanity filtering is required for the MVP.

## UX Notes
- The name field should be visually central and friendly.
- Error feedback for invalid names should be immediate and polite.
- The user should not need multiple steps or confirmation dialogs.

## Edge Cases
- Empty input
- Input with only spaces
- Very long input
- Reopening app after pet already exists
- Partial pet record exists but is invalid

## Dependencies
- Persistence feature for actual storage
- UI layer for rendering

## Success Criteria
This feature is successful when:
1. A new user can create a pet in under 10 seconds.
2. The created pet always starts with valid default values.
3. The app never creates multiple active pets.
4. Invalid naming input is blocked consistently.
5. Returning users see their existing pet rather than the creation screen.
