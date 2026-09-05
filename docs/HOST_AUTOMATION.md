# ACOS host automation

**End goal:** one project request into Cursor / Claude Code / Codex. ACOS routes, the host executes the current stage, the conductor advances. The user does not slash-pick skills.

## In place

- Canonical skills live in `skills/`. Hosts discover them from `.cursor/skills/`, `.claude/skills/`, `.agents/skills/`.
- Phase F routes IDs. Briefs expose native `/skill` names for the **current stage only**.
- `tools/host_driver/run_stage.py` is the conductor: `init` → brief → host work → `advance` → next brief.
- `check` is the mechanical audit. `serve` / `capture` collect real browser pixels. `critic-pass` opens an independent critic window.
- Design Gate is substantive. File presence cannot APPROVE.
- Quality Gate cannot SHIP unless pixel evidence exists **and** a different chat attested independence.
- The conductor never invents APPROVED. It can only block an illegal one.

## Commands

See `tools/host_driver/HOST_LOOP.md`.

Flagship authored-3D / Blender-required prompts: `docs/FLAGSHIP_PREMIUM_WORKFLOW.md`. The word “premium” is not required.

## Honest limit

The host model still does the skill work (read `SKILL.md`, write artifacts, implement, inspect pixels). This runner does not call a hidden Cursor API and does not generate creative direction by itself.
