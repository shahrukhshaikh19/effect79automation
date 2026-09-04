# Cursor Adapter — Progressive Skill Loading

Same contract as shared `registry/ADAPTERS.yaml` → `shared_contract.skill_loading`.

**Registry:** `registry/SKILLS.yaml`

| Level | Load |
|---|---|
| L1 | Metadata from registry / skill frontmatter |
| L2 | `SKILL.md` for activated skills only |
| L3 | References/scripts on demand |

Cursor may discover skills via workspace paths — still use registry as inventory authority.

Do not copy skill bodies into `.cursor/rules/` or `adapters/cursor/`.

Future Phase F may pass `activated_skill_ids`; load L2+ only for those.
