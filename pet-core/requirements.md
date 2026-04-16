# Requirements — Pet Core

## Requirement IDs
All requirements in this file use the prefix `PC`.

### PC-001 — Single active pet model
The system shall support exactly one active pet for the MVP.

### PC-002 — No pet selection flow
The system shall not provide pet switching, pet slots, or multiple concurrent pets.

### PC-003 — Creation gate
If no valid pet record exists, the system shall require pet creation before access to the main care loop.

### PC-004 — Mandatory name input
The system shall require the user to enter a pet name before creating the pet.

### PC-005 — Name trimming
The system shall trim leading and trailing whitespace from the entered pet name before validation and storage.

### PC-006 — Minimum name length
After trimming, the pet name shall contain at least 1 character.

### PC-007 — Maximum name length
After trimming, the pet name shall contain no more than 20 characters.

### PC-008 — Invalid name rejection
The system shall reject any pet name that is empty or exceeds the maximum allowed length.

### PC-009 — Friendly validation feedback
When name validation fails, the system shall display a user-friendly validation message and shall not create a pet record.

### PC-010 — Default state on creation
Upon creation, the system shall initialize the pet in the `normal` state.

### PC-011 — Default hunger
Upon creation, the system shall initialize Hunger to `80`.

### PC-012 — Default happiness
Upon creation, the system shall initialize Happiness to `80`.

### PC-013 — Default energy
Upon creation, the system shall initialize Energy to `80`.

### PC-014 — Default age
Upon creation, the system shall initialize `age_ticks` to `0`.

### PC-015 — Default evolution flag
Upon creation, the system shall initialize `is_evolved` to `false`.

### PC-016 — Default evolved timestamp
Upon creation, the system shall initialize `evolved_at` to `null`.

### PC-017 — Creation timestamps
Upon creation, the system shall populate `created_at`, `updated_at`, and `last_tick_at` with valid timestamps.

### PC-018 — Persistent identity
Each pet record shall have a unique identifier.

### PC-019 — Valid stat bounds at creation
Upon creation, all stat values shall be within the inclusive range `0` to `100`.

### PC-020 — Bypass creation if valid pet exists
If a valid pet record already exists, the system shall bypass the creation screen and load the existing pet.

### PC-021 — Incomplete record fallback
If a pet record exists but is missing required fields or contains invalid core values, the system shall treat it as invalid and trigger safe recovery behavior as defined in the persistence feature.

### PC-022 — Main view after creation
After successful creation, the system shall transition the user to the main care view in the same session.

### PC-023 — Name display
The system shall display the pet’s stored name on the main care screen.

### PC-024 — Baseline avatar presentation
The system shall render the pet using the Normal presentation style immediately after creation.

### PC-025 — No hidden randomization in core creation
The system shall not randomize default stat values or initial state during pet creation.

### PC-026 — Deterministic creation outcome
Given the same valid name input and empty system state, pet creation shall always produce the same initial pet values except for generated IDs and timestamps.
