# Sparrow Net Game — AI Terminal Puzzle Game

## Game Overview

Sparrow Net Game is a terminal-style puzzle adventure.  
The player takes the role of a new IT employee navigating a corporate network, performing IT tasks while uncovering hidden nefarious activity.  

### Chapters & Levels
- The game is divided into **chapters**, each containing **levels**.
- Each level is a multi-step puzzle with clear **win conditions**.
- Some narrative choices can alter story flow (choose-your-own-adventure elements).

---

## Core Architecture

### Entities in the Main Loop

1. **User Input**  
   - Commands typed into the terminal  
   - Parsed into structured **Intent objects**

2. **Intent -> Patch (LLM mutator)**  
   - `generate_patch(intent, state, level_context)` produces:
     - `strict` patch: authoritative state changes
     - `vibe` patch: flavor text / narrative
   - Only fields allowed by `intent.modifies_strict` can appear in `strict`
   - Vibe fields are free-form

3. **Patch Application**  
   - Engine applies patches to **GameState** (`engine.patch.apply_patch`)
   - Enforces:
     - strict validation rules
     - authoritative state update
   - Any invalid patch is rejected; the engine remains the source of truth

4. **Output Generation**  
   - Strict fields update game state  
   - Vibe fields generate terminal text for player feedback

5. **State Inspection**  
   - Check for win conditions, level advancement

---

## Patch Philosophy

- **Strict:** minimal, precise, validated; LLM cannot hallucinate  
- **Vibe:** flexible, narrative-driven, safe to hallucinate  
- **No-ops:** Intents that do not modify strict state produce empty strict patches, only vibe outputs  

---

## Developer Guidelines

- **Mutator switching:** Use config flag `USE_LLM` to toggle between stub and LLM mutator  
- **Intent self-description:** Each Intent object declares if it modifies strict fields  
- **Benchmarks:** Run `tests/benchmark_mutator.py` to measure LLM patch reliability and convergence  
- **Post-processing:** LLM output placeholders like `${intent.time}` are resolved before patch application  

---

## Design Principles

- Engine is **authoritative**; LLM only proposes  
- Keep LLM creativity **contained** (strict vs vibe)  
- No direct state mutation outside engine  
- Benchmarks and intent-aware filtering prevent cascading failures  

---

## Next Steps (for future development)

- LLM-generated vibe text for immersive terminal output  
- Per-level context and prompt tuning  
- Support multiple intents per turn  
- Logging and replay for debugging
