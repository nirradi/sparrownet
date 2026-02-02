# Sparrow Net Game

Sparrow Net is a terminal-style, AI-assisted puzzle game.
The player is an IT employee interacting with a remote system via a constrained, fake terminal.
The game is chapter-based, with each level being a deterministic puzzle wrapped in narrative flavor.

The core design goal:
- Feels like a terminal
- Plays like a puzzle game
- Uses LLMs for interpretation and flavor, not authority

---

## Core Design Principles

### 1. Determinism First
- Every level has a clear, testable win condition.
- The game engine, not the LLM, decides correctness.
- LLMs may propose changes, but the engine validates and applies them.

### 2. Fake Terminal, Not Chatbot
- Input is command-like, not conversational.
- Commands are constrained and finite.
- Errors are mechanical and explicit.

### 3. LLMs as Parsers and Proposers
- LLMs interpret input and propose state changes.
- LLMs never decide outcomes.
- LLMs never mutate state directly.

---

## Game Loop Overview

High-level flow for every user input:

User Input
→ Intent Resolution
→ Patch Proposal (LLM)
→ Patch Validation (Engine)
→ State Mutation
→ Win Condition Check
→ Output Rendering (LLM)


Each step is explicit and logged.

---

## State Model

Game state is split into two zones:

### Strict State
- Small, closed schema.
- Used for win conditions.
- Fully validated.
- Deterministic.

Examples:
- system clock
- event timestamps
- facts required for puzzle completion

### Vibe State
- Free-form, realism-only.
- No win conditions depend on it.
- Exists to sell the world.

Examples:
- emails
- system configuration noise
- files, notes, logs

**Strict and Vibe must never mix.**

---

## Intents

User input is classified into a small, fixed set of intents.

Examples:
- CLOCK_STATUS
- CLOCK_SET
- SYS_SHOW
- MAIL_READ
- MAIL_SEND

Intents:
- Define what kind of action the user is attempting
- Control which parts of state may be affected
- Gate what patches are allowed

---

## Patch-Based State Mutation

LLMs do not mutate state.
They produce **patch proposals**.

A patch:
- Is a list of path → value updates
- May only touch paths allowed by the intent
- Uses placeholders like `"NOW"` for engine-resolved values

The engine:
- Validates patches
- Resolves placeholders
- Applies accepted patches
- Rejects invalid ones deterministically

---

## Time and Events

- The engine is the sole authority on time.
- LLMs may request `"NOW"` but never invent timestamps.
- Temporal logic (ordering of actions) lives in strict state as event facts.

---

## What This Repository Is (for now)

- A prototype engine
- A testbed for the intent → patch → validation model
- Focused on correctness and debuggability

## What This Repository Is Not (yet)

- A full OS simulation
- A natural-language chatbot
- A branching narrative engine

Those may come later if the foundation proves solid.

---

## Development Phases (Current)

- Phase 1: State model (strict / vibe split)
- Phase 2: Patch schema and validation
- Phase 3: Intent system
- Phase 4: Game loop
- Phase 5: LLM integration

Each phase should leave the game runnable.
