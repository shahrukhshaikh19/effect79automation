# Local Adapter — Progressive Skill Loading

Local models often lack native Agent Skills. Skills are loaded from **caller-supplied** `routing.activated_skill_ids` — not adapter-selected.

| Level | Mechanism |
|---|---|
| L1 | Metadata for IDs in `routing.activated_skill_ids` (from registry) |
| L2 | `SKILL.md` for each validated activated ID only |
| L3 | References/scripts on demand per loaded skill |

**Registry:** `registry/SKILLS.yaml` — used to **validate** supplied IDs, not to autonomously pick skills.

If `activated_skill_ids` is empty when routing is required → `routing_required` / `insufficient_routing_input`.

For very weak models: single-skill stages (one supplied ID per stage) with external validation between stages.
