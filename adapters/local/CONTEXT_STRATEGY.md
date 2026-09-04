# Local Adapter — Context Strategy

Local/open-source models often have limited context and weaker tool use.

## Sequence

```text
TASK_PACKET (bounded)
→ canonical file refs (not full paste of master doc)
→ single-stage scope
→ one/few activated skills
→ allowed tools with status
→ output contract
→ external validation
→ next stage packet
```

## Constraints

- Do not embed entire `ACOS_FINAL_CANONICAL_v1.2.md` in one prompt
- Prefer file paths + short summaries
- Use deterministic scripts from `validation/` where possible
- Model profile fields (`templates/MODEL_PROFILE_TEMPLATE.md`) populated only after benchmarks

## Weaker model fallbacks

- Shorter tasks
- Explicit checklists per stage
- Human or script validation between stages
