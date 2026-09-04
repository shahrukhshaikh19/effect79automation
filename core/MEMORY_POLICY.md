# ACOS Memory Policy v1.2

Memory is structured evidence, not a giant prompt.

## Stores

```text
memory/
├── knowledge/
├── taste/
├── projects/
├── failures/
├── successes/
└── model-compatibility/
```

## Knowledge memory
Stable technical/process knowledge validated for reuse.

## Taste memory
Validated aesthetic preferences/patterns with scope. Never convert one project's aesthetic into a universal house style.

## Project memory
Brief, decisions, active skills, implementation history, evidence, final outcomes.

## Failure memory
Record:
```yaml
id:
project:
date:
domain:
problem:
evidence:
root_cause:
correction:
affected_skills: []
scope:
confidence:
status:
```

## Success memory
Record what worked, why, evidence, constraints and reuse scope. Success does not automatically become a global rule.

## Model compatibility memory
Store model/version-specific strengths, weaknesses, quirks, tool constraints and benchmark results separately.

## Promotion lifecycle

```text
observation
→ project-rule
→ candidate-global
→ validated-global
→ deprecated
```

Promotion to global requires repeated evidence across sufficiently different projects/conditions.

## Retrieval

Retrieve only memory relevant to the current task/phase. Do not dump all historical memory into context.

## Prohibitions

- one model failure != global law;
- one successful visual style != ACOS house style;
- project-specific benchmark content != canonical foundation;
- rejected experiments should retain reason/evidence when useful.
