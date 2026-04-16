# Tiny Tamagotchi MVP Tech Stack

## Stack Decision Summary
The Tiny Tamagotchi MVP will be built using:

- **Frontend/UI shell:** Streamlit
- **Language:** Python 3.11+
- **Database:** Supabase Postgres
- **Data access:** Supabase Python client and repository layer
- **Testing:** pytest
- **Deployment:** Streamlit Community Cloud
- **Configuration:** `.streamlit/config.toml` and Streamlit secrets

This stack is selected to balance speed, clarity, deployability, and implementation accessibility for a Python-first workflow.

## Why This Stack Fits the Project

### 1. Strong alignment with developer familiarity
The project owner is more comfortable with Python than with a modern JavaScript framework stack. Streamlit keeps the full product inside one language family, reducing implementation friction.

### 2. Fast MVP delivery
Streamlit enables a polished interactive app without requiring a custom frontend framework. That keeps effort focused on specification quality and product behavior.

### 3. Clean separation still possible
Although Streamlit is often used for prototypes, this project will avoid monolithic app code by separating:

- domain logic
- service layer
- data access
- UI rendering

### 4. Real persistence without backend overbuild
Supabase provides a production-grade managed Postgres database, which is more durable and realistic than local files while remaining simple for an MVP.

### 5. Demo-friendly hosting
Streamlit Community Cloud is sufficient for a public or reviewer-facing demo and fits the chosen frontend directly.

## Architecture Overview

### Presentation Layer
Streamlit pages and UI components render the pet state and provide care actions.

### Domain Layer
Pure Python modules define pet state, stat updates, transitions, and evolution logic.

### Service Layer
Application services coordinate ticks, actions, persistence, and event generation.

### Data Layer
Supabase repositories read and write pet records and pet event history.

### Infrastructure Layer
Secrets, theme config, environment configuration, and deployment files support runtime behavior.

## Proposed Repository Structure

```text
/specs
  mission.md
  roadmap.md
  tech-stack.md

/pet-core
  feature-plan.md
  requirements.md
  validation.md

/time-simulation
  feature-plan.md
  requirements.md
  validation.md

/actions-and-feedback
  feature-plan.md
  requirements.md
  validation.md

/state-transitions
  feature-plan.md
  requirements.md
  validation.md

/persistence
  feature-plan.md
  requirements.md
  validation.md

/src
  /domain
    pet_types.py
    pet_rules.py
    pet_engine.py
    state_machine.py
  /services
    pet_service.py
    tick_service.py
    persistence_service.py
  /data
    supabase_client.py
    repositories.py
  /ui
    components.py
    styles.py
    theme.py

/tests
  /unit
  /integration
  /smoke

app.py
requirements.txt
.streamlit/config.toml
```

## Technology Choices in Detail

### Streamlit
**Role:** presentation layer and interaction shell

**Why chosen:**
- fast to build and iterate
- Python-native
- supports session state, forms, sidebar, layout columns, and custom CSS
- deploys directly to Streamlit Community Cloud

**How it will be used:**
- naming flow
- main care interface
- stat display
- action buttons
- state/mood text
- history page or expandable event log

**Important implementation rule:**
Streamlit must not contain core simulation rules directly in button callbacks. It should call domain/service functions.

### Python 3.11+
**Role:** core implementation language

**Why chosen:**
- excellent readability
- strong compatibility with Streamlit and Supabase tooling
- suitable for pure domain logic and testing

**Standards:**
- use type hints
- prefer dataclasses or typed models for pet state
- keep modules small and single-purpose

### Supabase Postgres
**Role:** persistent storage

**Why chosen:**
- managed Postgres with modern developer ergonomics
- stable persistence across sessions and deployments
- simple enough for a tiny MVP

**How it will be used:**
- store one active pet record
- store pet event history
- optionally support analytics or future enhancements without changing core model

**Out-of-scope use:**
- no auth required for the MVP
- no row-level multi-user complexity required

### Supabase Python client
**Role:** access the database via a lightweight integration layer

**Implementation rule:**
The app should not scatter direct Supabase calls across Streamlit code. All database access should pass through repository functions.

### pytest
**Role:** automated validation framework

**Why chosen:**
- standard Python test tool
- simple to integrate with pure domain modules
- works well for deterministic simulation tests

**Testing layers expected:**
- unit tests for engine logic
- integration tests for persistence/resume behavior
- smoke/manual tests for reviewer flows

### Streamlit Community Cloud
**Role:** demo deployment target

**Why chosen:**
- directly supports Streamlit apps
- simple GitHub integration
- good enough for MVP demonstration

**Deployment considerations:**
- configure Supabase credentials as secrets
- ensure dependencies install cleanly from `requirements.txt`
- test cold start behavior

## Data Model Recommendation

### Table: `pets`
Purpose: store the single active pet’s current state

Recommended columns:
- `id`
- `name`
- `state`
- `hunger`
- `happiness`
- `energy`
- `age_ticks`
- `is_evolved`
- `evolved_at`
- `last_tick_at`
- `created_at`
- `updated_at`

### Table: `pet_events`
Purpose: store notable interactions and transitions

Recommended columns:
- `id`
- `pet_id`
- `event_type`
- `event_message`
- `payload_json`
- `created_at`

## Domain Modeling Standards

### State enum
The pet state must use explicit values:
- `normal`
- `sick`
- `evolved`

### Actions enum
The supported actions must be explicit:
- `feed`
- `play`
- `rest`

### Stat model
Tracked stats:
- Hunger
- Happiness
- Energy

All stats must remain within `0` and `100` inclusive.

## Central Rules Strategy
All thresholds and formulas must live in a single rules module, for example `pet_rules.py`.

Examples of values to centralize:
- decay rates
- action effects
- sickness thresholds
- recovery thresholds
- evolution thresholds
- consecutive tick counts
- event log limits

No hard-coded rule values should appear in UI files.

## UX and Styling Strategy
The app should avoid the visual feel of a raw dashboard. Styling strategy:

- custom theme in `.streamlit/config.toml`
- CSS injection only for targeted polish
- friendly typography hierarchy
- pet-centered main layout
- visually distinct state colors for Normal, Sick, Evolved
- compact sidebar for profile and controls only

## Persistence Strategy
The authoritative pet state must be stored in Supabase. Session state may cache loaded data for responsiveness, but the database is the source of truth across sessions.

On each app load:
1. retrieve pet
2. compute elapsed time since `last_tick_at`
3. apply deterministic decay
4. evaluate transitions
5. persist the updated result if anything changed
6. render the updated state

## Error Handling Strategy
The app must fail gracefully in these cases:

- no pet exists yet
- pet record exists but is incomplete
- Supabase temporarily unavailable
- stored values are out of bounds
- timestamps are malformed

Fallback behavior should favor preserving demo usability rather than crashing.

## Security and Secrets
Use Streamlit secrets for:
- Supabase URL
- Supabase key

Secrets must never be committed to source control.

## Rejected Alternatives

### Next.js + Vercel
Rejected because it adds frontend learning overhead and slows delivery for a Python-first implementation path.

### Local JSON or file storage
Rejected because it is fragile for deployment and less representative of a production-ready demo.

### Full backend framework (FastAPI/Django)
Rejected because the MVP does not need a separately hosted API layer.

### Complex state machine libraries
Rejected because the state model is small and can be implemented clearly in plain Python.

## Implementation Quality Rules
- Keep simulation logic pure where possible
- Keep database access centralized
- Keep UI declarative and thin
- Prefer explicit names over clever abstractions
- Prefer deterministic rules over vague behavior
- Ensure all important logic is covered by tests

## Final Stack Statement
This stack intentionally favors clarity, maintainability, demo readiness, and spec compliance over technical novelty. It is the most appropriate stack for delivering a polished Tiny Tamagotchi MVP through spec-driven development in a Python-first workflow.
