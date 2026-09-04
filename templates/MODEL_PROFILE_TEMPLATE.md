# ACOS Model Profile Template v1.2

Create one profile per materially different model/version/deployment.

```yaml
id:
provider:
model:
version:
deployment:
acos_version: "1.2"
adapter_version:
context_window:
tool_support: []
native_agent_skills_support:
strengths: []
weaknesses: []
known_quirks: []
context_constraints: []
required_overrides: []
recommended_skill_batch_size:
benchmark_results: {}
resource_requirements: {}
security_notes: []
status: candidate   # candidate|approved|restricted|retired|rejected
last_tested:
```

## Approval notes

A model is not production-approved because it can read the docs. It must demonstrate acceptable benchmark behavior for the tasks it will be routed.

Compatibility observations stay model-specific unless independent evidence supports a broader ACOS change.
