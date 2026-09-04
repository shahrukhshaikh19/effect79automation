# Claude Adapter — Progressive Skill Loading

**Registry source:** `registry/SKILLS.yaml`  
**Inventory:** 36 external + 14 proprietary (from registry, not duplicated here)

## Levels

| Level | Content | When |
|---|---|---|
| L1 | Skill id, name, description, domain tags from registry | Task classification / routing hint |
| L2 | Full `skills/**/SKILL.md` for activated skill only | Skill activated for current task |
| L3 | `references/`, scripts, assets under skill folder | Required by activated skill procedure |

## Rules

- Skill **availability** ≠ skill **activation**
- Never inject all 50 skills into context
- Read skill locations from registry paths — do not copy bodies into `adapters/claude/`
- img2threejs: respect existing `restricted` status in lockfile
- EXT-FE-01/02: do not copy content — licensing unresolved

## Activation input (Phase F hook)

Future routing may supply:

```yaml
activated_skill_ids: [ACOS-01, EXT-3DWEB-03]
```

Claude adapter loads L2+ only for those IDs.
