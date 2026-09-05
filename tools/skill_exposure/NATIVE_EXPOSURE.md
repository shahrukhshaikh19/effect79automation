# Native skill exposure

Canonical skill bodies stay in `skills/`. Cursor, Claude Code, and Codex discover skills only from host-specific roots. This layer creates **directory links**, not copies.

| Host | Discovery root |
|---|---|
| Cursor | `.cursor/skills/<skill-name>/SKILL.md` |
| Claude Code | `.claude/skills/<skill-name>/SKILL.md` |
| Codex | `.agents/skills/<skill-name>/SKILL.md` |

Cursor also accepts `.agents/skills/`. ACOS still exposes `.cursor/skills/` so Cursor Settings / `/skill-name` stay obvious.

## Sync

From the ACOS repo root:

```text
python tools/skill_exposure/sync_native_skills.py
```

If the Cursor workspace is the parent folder, also expose there:

```text
python tools/skill_exposure/sync_native_skills.py --extra-root ..
```

## Validate

```text
python validation/validate_native_skill_exposure.py
```

## Rules

- Do not move or delete `skills/`.
- Do not paste `SKILL.md` bodies into `.cursor/rules/` or `adapters/*`.
- Availability is not activation. Hosts may index all descriptions; load full bodies only for the routed subset.
- After clone or skill add/rename, re-run the sync script.
