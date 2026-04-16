# Tiny Tamagotchi MVP Roadmap

## Roadmap Intent
This roadmap defines the recommended implementation sequence for building the Tiny Tamagotchi MVP using spec-driven development. It is intentionally staged to minimize ambiguity, reduce implementation risk, and keep Codex aligned with the documented rules.

The roadmap is not a backlog of optional ideas. It is the delivery order for the MVP.

## Delivery Strategy
The product should be built in the following order:

1. Establish the rules and constraints in documentation
2. Implement the pure simulation engine
3. Add persistence and time reconstruction
4. Build the polished Streamlit interface on top of the stable engine
5. Validate behavior through automated and manual flows
6. Deploy demo build to Streamlit Community Cloud

This order ensures that visual polish does not hide logic gaps.

---

## Phase 0 — Specification Foundation

### Objective
Lock the behavior of the app before implementation begins.

### Deliverables
- `/specs/mission.md`
- `/specs/roadmap.md`
- `/specs/tech-stack.md`
- feature folders with `feature-plan.md`, `requirements.md`, and `validation.md`

### Exit Criteria
- All required project constraints are documented
- All core behaviors have explicit thresholds or formulas
- No feature document contradicts another
- Each requirement can be mapped to one or more validation cases

### Risks addressed
- Hidden logic in implementation
- Vague action behavior
- Undefined state transitions
- Incomplete test planning

---

## Phase 1 — Project Skeleton and Domain Modeling

### Objective
Create the repository structure and typed domain model before UI work.

### Deliverables
- Python package structure under `src/`
- Domain types for pet, stats, events, and state
- Central rules/config module
- Initial test harness with `pytest`

### Required outputs
- `src/domain/pet_types.py`
- `src/domain/pet_rules.py`
- `src/domain/pet_engine.py`
- `src/domain/state_machine.py`
- `tests/unit/`

### Exit Criteria
- Pet model can be created from defaults
- Rules are centralized and imported from one place
- Engine functions can run without Streamlit

### Notes
No UI work should introduce business logic at this phase.

---

## Phase 2 — Core Simulation Engine

### Objective
Implement the core pet lifecycle in pure Python.

### Includes
- stat clamping
- action effects
- elapsed-time stat decay
- age progression in ticks
- state transition evaluation
- evolution eligibility evaluation
- event creation for important changes

### Exit Criteria
- A pet can be initialized, mutated by actions, and progressed through elapsed time
- Sickness and recovery rules are deterministic
- Evolution can occur only once and only when criteria are met
- Automated unit tests cover major branches

### Risks addressed
- Streamlit reruns causing logic drift
- inconsistent transitions
- magic numbers scattered across code

---

## Phase 3 — Persistence and Data Access

### Objective
Persist pet data and reconstruct the pet correctly after reload.

### Includes
- Supabase client configuration
- repository layer for pets and pet events
- save/load flow
- timestamp-based `apply_elapsed_time()` on app start
- graceful handling of missing or corrupted records

### Data model scope
- one active pet record
- one event log table
- optional compact snapshot support only if needed

### Exit Criteria
- Refreshing the page does not reset the pet
- Closing and reopening later reflects elapsed time correctly
- Invalid stored data falls back safely rather than crashing the app

### Risks addressed
- session-only behavior
- broken restores
- demo instability

---

## Phase 4 — Streamlit UX Layer

### Objective
Build a polished, simple user interface around the stable engine.

### Includes
- naming flow
- main care screen
- stat bars
- avatar/state illustration
- action buttons
- event/mood message area
- sidebar profile and controls
- optional history page

### UX priorities
- fast comprehension
- low clutter
- visible state changes
- friendly microcopy
- clean hierarchy

### Exit Criteria
- A first-time user can understand the app in under 30 seconds
- Actions feel immediate and readable
- Sick and Evolved states are visually distinct
- The app no longer looks like a default data tool

---

## Phase 5 — Validation and Hardening

### Objective
Prove that the implementation matches the written specification.

### Includes
- automated unit tests
- integration tests for persistence and resume behavior
- manual demo checklist
- smoke tests for main user flows

### Minimum validation themes
- naming flow
- stat bounds
- decay over time
- each action effect
- sickness trigger
- recovery trigger
- single evolution only
- persistence across refresh
- handling of edge cases

### Exit Criteria
- All critical tests pass
- Manual demo flows pass consistently
- Validation documents reflect actual implementation

---

## Phase 6 — Demo Deployment

### Objective
Deploy a stable demo to Streamlit Community Cloud.

### Includes
- repo cleanup
- `requirements.txt`
- `.streamlit/config.toml`
- secrets configuration for Supabase
- deployment smoke check

### Exit Criteria
- Public or shareable demo URL works
- app starts without local-only assumptions
- secrets are stored correctly
- first-load and repeat-load flows both work in hosted environment

---

## Milestones Summary

### Milestone A — Spec Complete
All documentation exists and is internally consistent.

### Milestone B — Simulation Complete
The pet engine works in isolation and is tested.

### Milestone C — Persistence Complete
The pet survives reloads and time gaps.

### Milestone D — UX Complete
The app is polished enough for reviewer demo.

### Milestone E — Deployment Complete
The app is live and stable on Streamlit Community Cloud.

---

## Recommended Implementation Sequence for Codex

1. Create folder structure
2. Write domain types and rule constants
3. Implement engine functions with tests
4. Implement state machine with tests
5. Implement repositories and Supabase client
6. Implement load/resume flow
7. Build Streamlit pages and UI components
8. Add theming and CSS polish
9. Add smoke tests and manual validation checklist
10. Deploy and run hosted smoke verification

## Deferred Ideas After MVP
These items are intentionally deferred and must not be implemented unless the product scope changes:

- multiple evolution forms
- achievement system
- custom accessories
- sound effects
- daily streaks
- account sync across users
- notifications
- minigames

## Roadmap Governance Rule
If any implementation task introduces behavior not described in the current spec set, the spec must be updated first or the implementation task must be rejected.
