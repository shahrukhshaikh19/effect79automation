# Claude Adapter — Context Budget Strategy

Models differ in context window and instruction quality. Adapters adjust **loading**, not canonical knowledge.

## Sequence

```text
minimum bootstrap (this file + canonical refs)
→ authority summary / file references
→ task classification
→ relevant skill metadata (L1)
→ activated SKILL.md (L2)
→ on-demand references/scripts (L3)
```

## Claude-specific guidance

- Prefer registry metadata before full skill bodies
- Batch activated skills conservatively under context pressure
- Preserve decision records in repo/files — do not rely on chat memory as ACOS memory
- Model-specific limits belong in `registry/MODELS.yaml` profiles when benchmark evidence exists — do not invent limits here

## Smaller-context fallback

- Reduce active skill batch size
- Shorter bounded stages with explicit handoff schemas
- External validation between stages when model weak at tool use
