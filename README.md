# ACOS v1.2 — AI Creative Operating System

**Status:** Phase D complete; A–D certification hardening complete. Foundation phases E–G not started.  
**Phase map:** `registry/PHASES.yaml`  
**Authority:** `ACOS_FINAL_CANONICAL_v1.2.md`

ACOS is a model-agnostic Creative Engineering Operating System. This repository is the canonical ACOS v1.2 foundation for Claude, Cursor, Codex, or compatible local/open-source coding agents.

## Authority hierarchy

1. `ACOS_FINAL_CANONICAL_v1.2.md` — supreme source of truth.
2. `AGENTS.md` — implementation-agent behavior.
3. `core/*` — operational laws, workflow, routing, gates, memory and model migration.
4. `registry/SKILLS.yaml` — machine-readable approved skill inventory.
5. `adapters/*` and `templates/*` — compatibility/bootstrap material.
6. `IMPLEMENTATION_CHECKLIST.md` — execution verification.
7. `PACK_INVENTORY.md` — pack integrity manifest.

If supporting wording conflicts with the canonical master, the master wins.

## What the implementation agent must do

- create the real canonical ACOS repository;
- import and pin only approved external skills;
- implement all 14 proprietary ACOS skills as real procedural Agent Skills;
- preserve Skill != Tool != Model != Memory != Adapter;
- implement routing, quality gates, memory structure and model compatibility;
- configure tools separately;
- create thin client/model adapters;
- validate contents, not merely directory existence;
- produce evidence for every completion claim.

## What it must not do

- research a new foundation;
- shortlist skills again;
- replace approved skills with alternatives;
- infer a default visual style;
- infer that ACOS is 3D-first because 3D skills exist;
- embed a sample project or benchmark into the foundation;
- treat compilation as visual QA;
- install complete upstream mega-packs when only a subset is approved.

## Domain neutrality

The ACOS foundation has no predefined brand, product, industry, benchmark, aesthetic or project. Real projects are supplied later as separate project packages.

Skill availability never implies activation.

## Required reading order

1. `ACOS_FINAL_CANONICAL_v1.2.md`
2. `AGENTS.md`
3. `core/CONSTITUTION.md`
4. `core/WORKFLOW.md`
5. `core/ROUTING.md`
6. `core/QUALITY_GATES.md`
7. `core/MEMORY_POLICY.md`
8. `core/MODEL_COMPATIBILITY.md`
9. `registry/SKILLS.yaml`
10. `adapters/local/LOCAL_LLM_BOOTSTRAP.md` when relevant
11. `templates/MODEL_PROFILE_TEMPLATE.md`
12. `IMPLEMENTATION_CHECKLIST.md`
13. `registry/PHASES.yaml` — canonical foundation phase map (A–G + PF-*)
14. `PACK_INVENTORY.md`

## Completion rule

**Claim != evidence. Compile != quality. Placeholder != implementation.**

A foundation phase is complete only when the actual files and behavior have been inspected and validated.
