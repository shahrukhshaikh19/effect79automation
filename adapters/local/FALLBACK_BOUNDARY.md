# Local Adapter — Fallback Boundary (NOT Phase F Runtime)

This document defines the **compatibility boundary** for external orchestrators.  
Phase E does **not** implement the orchestrator.

## Allowed concept

```text
external bootstrap/orchestrator
→ read canonical files from disk
→ compile bounded TASK_PACKET
→ send to local model API
→ validate output against schema/handoff
→ next stage
```

## Forbidden in Phase E

- Autonomous multi-agent coordinator
- Memory retrieval runtime
- Quality gate aggregation runtime
- Benchmark runner
- Persistent vector store
- Routing engine selecting skills without human/policy hook

## Phase F hook

Orchestrator may later receive `activated_skill_ids` from canonical routing layer.  
Local adapter task packet already reserves fields for that input.

## Proof of model independence

Deleting `adapters/local/` does not delete ACOS intelligence — canonical files remain authoritative.
