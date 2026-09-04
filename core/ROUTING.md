# ACOS Routing v1.2

Routing selects among already-approved capabilities. It never re-shortlists the foundation.

## Routing algorithm

1. classify task/domain;
2. identify required outputs;
3. identify risk/quality dimensions;
4. inspect approved skill metadata;
5. activate smallest sufficient subset;
6. load full `SKILL.md` only for activated skills;
7. load references/resources on demand;
8. execute;
9. route defects to responsible skill;
10. deactivate irrelevant skills as phase changes.

Typical simultaneous specialist target: approximately 3–8 where practical, adjusted for model context limits.

## Example capability routes

These are routing patterns, not project examples.

### Standard application/interface
creative skills only when creative redesign is actually requested; frontend + accessibility + testing skills as required. Do not activate 3D.

### Interactive 3D experience
creative/experience direction → Design Gate → cinematic 3D direction → relevant Three.js/R3F and/or Blender route → motion if required → responsive/performance → critics/gate.

### Reference image → procedural browser-native object
reference-analysis → cinematic-3d-director → `img2threejs` → relevant Three.js skills → 3d-critic → webgl-performance → quality-gate.

### High-fidelity authored 3D asset
cinematic-3d-director → curated Blender production subset → Blender MCP as execution tool → 3d-critic → optimization/export → gate.

## img2threejs vs Blender boundary

Use `img2threejs` when procedural/browser-native reconstruction is appropriate.

Escalate/prefer Blender when the task needs deliberate reusable topology, complex hidden geometry, organic sculpting, baking, simulations, advanced asset authoring, or fidelity beyond the procedural route.

A project may use both, but neither is the default.

## Routing prohibitions

- skill availability does not imply activation;
- do not load whole upstream mega-packs;
- do not let GSAP replace motion direction;
- do not let Three.js replace cinematic direction;
- do not let Blender MCP replace Blender knowledge;
- do not let Playwright replace visual/creative critics.
