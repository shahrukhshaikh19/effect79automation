# Local Adapter — Progressive Skill Loading

Local models often lack native Agent Skills. Use registry + bounded loading.

| Level | Mechanism |
|---|---|
| L1 | Include skill id/name/description in `TASK_PACKET.schema.yaml` metadata |
| L2 | Explicitly attach one or few `SKILL.md` paths in task packet |
| L3 | Add reference file paths only when procedure requires |

**Registry:** `registry/SKILLS.yaml` — never hard-code 50 skills in bootstrap prompt.

For very weak models: single-skill stages with external validation between stages.
