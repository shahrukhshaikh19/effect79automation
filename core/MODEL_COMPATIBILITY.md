# ACOS Model Compatibility & Migration v1.2

ACOS intelligence must survive model/provider/client changes.

## Migration flow

```text
REGISTER MODEL/VERSION
→ CREATE COMPATIBILITY PROFILE
→ RUN REPRESENTATIVE BENCHMARKS
→ COMPARE WITH APPROVED BASELINE
→ IDENTIFY REGRESSIONS/STRENGTHS
→ ADJUST THIN ADAPTER / ROUTING / SKILL BATCHING
→ RE-TEST FAILED AREAS
→ APPROVE | RESTRICT | REJECT
```

## Canonical rule

Never rebuild ACOS knowledge from zero because a model changed.

Keep outside model weights:
- skills;
- workflow;
- routing;
- quality gates;
- memory;
- benchmarks;
- accepted/rejected evidence;
- project history.

## Adapter examples

A context-limited model:
- load metadata first;
- smaller skill batches;
- shorter tasks/checkpoints.

A strong coder with weak visual reasoning:
- route implementation to it;
- retain stronger independent visual/creative evaluation.

A smaller local model:
- more deterministic scripts/checklists;
- explicit handoffs;
- narrower task chunks.

## Fine-tuning

Fine-tuning may later specialize behavior but cannot become the only copy of ACOS knowledge.

## Compatibility profile fields

provider/model/version/deployment, ACOS version, adapter version, context limits, tool support, skill support, strengths, weaknesses, quirks, overrides, benchmark results, resource requirements, status, last tested.
