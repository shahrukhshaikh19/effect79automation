# Claude Adapter — Progressive Skill Loading

**Registry source:** `registry/SKILLS.yaml`  
**Inventory:** 36 external + 17 proprietary (from registry, not duplicated here)

## Levels

| Level | Content | When |
|---|---|---|
| L1 | Skill id, name, description, domain tags from registry | Task classification / routing hint |
| L2 | Full `skills/**/SKILL.md` for activated skill only | Skill activated for current task |
| L3 | `references/`, scripts, assets under skill folder | Required by activated skill procedure |

## Rules

- Skill **availability** ≠ skill **activation**
- Never inject all 50 skills into context
- Native Claude Code discovery is generated into `.claude/skills/` by `tools/skill_exposure/sync_native_skills.py`
- Read skill locations from registry paths — do not copy bodies into `adapters/claude/`
- img2threejs: respect existing `restricted` status in lockfile
- EXT-FE-01/02: do not copy content — licensing unresolved

## Activation input

Phase F routing is consumed from `runtime/host/CURRENT_HOST_BRIEF.md`.
Load L2+ only for `invoke_now` native skill names. IDs remain in the YAML packet.
