# Cursor Adapter — Progressive Skill Loading

Same contract as shared `registry/ADAPTERS.yaml` → `shared_contract.skill_loading`.

**Registry:** `registry/SKILLS.yaml`

| Level | Load |
|---|---|
| L1 | Metadata from registry / skill frontmatter |
| L2 | `SKILL.md` for activated skills only |
| L3 | References/scripts on demand |

Native Cursor discovery is generated from canonical `skills/` into `.cursor/skills/`
by `tools/skill_exposure/sync_native_skills.py`. See `tools/skill_exposure/NATIVE_EXPOSURE.md`.

Cursor may then discover name/description automatically. Registry remains inventory
authority. Availability != activation.

Do not copy skill bodies into `.cursor/rules/` or `adapters/cursor/`.

Phase F already owns routing. Consume `runtime/host/CURRENT_HOST_BRIEF.md` when present:
load L2 only for `invoke_now` native names. Do not Agent-Decide the full catalog.
