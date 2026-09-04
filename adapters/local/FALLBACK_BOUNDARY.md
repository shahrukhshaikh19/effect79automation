# Local Adapter — Fallback Boundary (NOT Phase F Runtime)

This document defines the **compatibility boundary** for external orchestrators.  
Phase E does **not** implement the orchestrator or routing engine.

## Ownership model

```text
External caller / future Phase F routing layer
    ↓ supplies: scope, classification, activated_skill_ids, tools, evidence requirements
Local adapter (Phase E)
    ↓ validates packet, loads supplied skills, bounded context, structured output
Local/open-source model
```

**Adapter consumes routing. Adapter does not own routing.**

## Allowed concept

```text
authorized external caller (manual pre-Phase F) OR future Phase F router
→ compile bounded TASK_PACKET with activated_skill_ids
→ local adapter validates IDs against registry/SKILLS.yaml
→ load only supplied skills
→ send bounded context to local model API
→ validate output against schema/handoff
→ next stage
```

## Acceptable Phase E fallback (no Phase F yet)

Caller manually supplies:

- normalized scope
- `activated_skill_ids`
- allowed tools + runtime status
- output contract

## Not acceptable

```text
adapter or model classifies the ACOS task itself
adapter or model selects relevant skills autonomously
adapter substitutes "figure out routing" when IDs missing
```

If routing input is missing → emit `routing_required` / `insufficient_routing_input`.

## Forbidden in Phase E

- Autonomous task classifier / router
- Autonomous multi-agent coordinator
- Memory retrieval runtime
- Quality gate aggregation runtime
- Benchmark runner
- Persistent vector store

## Phase F hook

Phase F routing layer will supply `routing.activated_skill_ids`.  
Local adapter already consumes this field — it does not implement Phase F.

## Proof of model independence

Deleting `adapters/local/` does not delete ACOS intelligence — canonical files remain authoritative.
