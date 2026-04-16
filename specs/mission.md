# Tiny Tamagotchi MVP Mission

## Product Mission
Build a tiny virtual pet web application that feels alive through a simple but convincing care loop, while keeping the system intentionally small, deterministic, and easy for an implementation agent to build from specification alone.

This project exists to demonstrate **MVP Spec-Driven Development**. The primary deliverable is not only a working app, but a documentation set that makes the app’s intended behavior unambiguous, testable, and implementation-ready.

## Why This Product Should Exist
Many toy apps look appealing but hide their logic in ad hoc UI code, undocumented thresholds, or vague descriptions such as “the pet gets sad over time.” This project takes the opposite approach:

- Every important behavior is defined before implementation.
- Every game rule has a reason, a threshold, and an expected outcome.
- Every feature can be validated with both automated and manual testing.
- The app remains delightful without becoming over-scoped.

The result should be a digital companion that is easy to understand, easy to implement, and satisfying to demo.

## Primary Goal
Produce a lovable single-pet experience whose behavior can be implemented consistently from markdown specifications, with no hidden logic and no dependency on verbal clarification.

## Secondary Goals
- Deliver a polished demo suitable for Streamlit Community Cloud.
- Keep the application local-feeling and responsive despite using a remote database.
- Make all core simulation logic deterministic and portable.
- Preserve the option to evolve the product later without rewriting the domain model.

## Non-Goals
The following are explicitly out of scope for this MVP and must not be introduced during implementation unless the specification is revised:

- Authentication or user accounts
- Multiple pets or pet slots
- Inventories, shops, currencies, or rewards economies
- Minigames
- Social or multiplayer features
- Push notifications
- Admin tools
- Multiple evolution branches
- Permanent death mechanics

These exclusions are part of the product strategy, not missing features.

## Target Audience
The intended audience is a reviewer, teammate, or stakeholder who wants to see:

1. A clearly scoped product idea
2. A clean implementation path for Codex or another coding agent
3. A polished but lightweight demo
4. Strong evidence of disciplined product thinking and engineering planning

The end-user persona inside the app is a casual player who wants to care for a cute pet in a few seconds at a time.

## Product Principles

### 1. Small but complete
The app should feel whole at MVP size. It does not need more features; it needs the right features, connected coherently.

### 2. Rules before visuals
Visual presentation is important, but no animation, icon, or layout choice should substitute for missing behavior definitions.

### 3. Deterministic simulation
Whenever possible, pet behavior must be governed by explicit rules rather than vague heuristics. Two identical pet histories should produce the same resulting state.

### 4. Thin UI, thick domain logic
The Streamlit UI should display and trigger behavior, but the actual pet rules should live in pure Python domain modules that can be tested independently.

### 5. Delight through personality, not complexity
The pet should feel charming through reactions, copywriting, mood messages, and state changes rather than through extra systems.

### 6. Demo-first polish
Although the project is spec-focused, the deployed app should still feel intentional, visually friendly, and easy to understand within the first 30 seconds.

## Core User Promise
“If I open this app, name my pet, and care for it through simple actions, the pet will respond in a way that feels consistent, understandable, and alive.”

## User Experience Pillars

### Living vitals
The pet must visibly depend on the player through stats that decay over time.

### Clear care loop
The user should always understand what actions are available and why they matter.

### Meaningful consequences
Neglect should make the pet sick. Good care should help it recover and eventually evolve.

### Emotional feedback
The pet should communicate mood and status through text, visuals, and small surprises.

## MVP Success Criteria
The MVP is successful if all of the following are true:

1. A first-time user can name the pet and reach the main care screen without confusion.
2. Hunger, Happiness, and Energy visibly change over time and remain bounded between 0 and 100.
3. Feed, Play, and Rest each produce distinct effects that are immediately understandable.
4. The pet can enter the Sick state through neglect.
5. The pet can recover from the Sick state through proper care.
6. The pet can evolve exactly once through sustained good care.
7. The app persists pet state across refreshes and between sessions.
8. The UI is polished enough for a public demo.
9. The documentation is precise enough that a coding agent can implement the application without inventing missing rules.
10. Validation documents clearly prove that the written requirements can be tested.

## Constraints

### Functional constraints
- Single active pet only
- Single evolution only
- Single recovery path only
- Exactly three tracked stats: Hunger, Happiness, Energy
- Exactly three care actions: Feed, Play, Rest
- Exactly three product states: Normal, Sick, Evolved

### Technical constraints
- Frontend shell must be built in Streamlit
- Persistence must use Supabase Postgres
- Demo deployment target is Streamlit Community Cloud
- Core pet logic must be implemented in Python modules independent of Streamlit widgets
- Time progression must work across app reloads using timestamps, not only in-memory timers

### Delivery constraints
- Documentation quality is a primary evaluation factor
- Implementation must follow the specification rather than drift from it
- Validation must include more than one testing level

## Design Positioning
The app should feel like a **cozy tiny creature dashboard** rather than a corporate analytics page. The visual tone should be:

- warm
- friendly
- minimal
- playful
- clean

A reviewer should immediately understand that this is a product demo, not just a default Streamlit prototype.

## Operational Philosophy
The app should be robust enough for demo use but simple enough to maintain. When there is a tradeoff between more features and more clarity, clarity wins.

## Final Mission Statement
Create a tiny but polished virtual pet that demonstrates how a narrowly scoped product can become implementation-ready through precise specifications, deterministic rules, and thoughtful validation.
