# BM-002 — CINEMATIC 3D FLAGSHIP BENCHMARK — OPERATOR INPUT

## Purpose

Test ACOS as a **premium cinematic interactive 3D web-production system**, not as a normal landing-page generator.

This benchmark must specifically stress the capabilities for which ACOS was built:

* creative direction
* art direction
* experience architecture
* cinematic 3D direction
* motion direction
* Three.js / WebGL production
* Blender / procedural asset pipeline where justified
* responsive 3D art direction
* WebGL performance
* visual critique
* creative critique
* 3D critique
* evidence-driven correction
* Quality Gate

## Operator intent

BM-002 must require an **original fictional premium physical technology/product experience**.

The exact fictional product name, identity, visual language, scene concept and storytelling may be originated by ACOS during execution.

Do NOT imitate an existing brand or website.

## Mandatory deliverable character

The final BM-002 deliverable must be an actual functional web experience where **meaningful real-time 3D is a core part of the experience**.

3D is NOT optional for BM-002.

The experience must include:

* a real three-dimensional product/object/scene
* intentional cinematic camera work
* authored lighting and materials
* meaningful spatial composition
* scroll and/or interaction-driven scene progression
* integration between WebGL/3D and DOM/UI typography
* multiple meaningful experience sections/states
* premium motion choreography
* responsive adaptation of camera/composition
* production-quality browser implementation

A static render placed inside a webpage does NOT satisfy the benchmark.

A rotating GLB/model viewer alone does NOT satisfy the benchmark.

A simple object spinning on scroll does NOT satisfy the benchmark.

## 3D requirement

Benchmark semantics must cause ACOS routing to determine:

`requires_3d = true`

through the task requirements themselves.

Do NOT manually hard-code ACOS skill IDs in the benchmark.

The Phase F router remains responsible for actual skill selection.

## Blender

Blender itself is NOT automatically mandatory.

The chosen production pipeline may use Blender-generated assets, procedural Three.js geometry, imported/generated 3D assets, or another approved production method depending on ACOS creative/technical reasoning.

However, the resulting 3D quality must be production-grade.

If Blender materially improves the required asset quality, routing/tool selection should be able to use it.

Do not avoid Blender merely because a cheaper primitive implementation is easier.

## Cinematic quality

The benchmark must evaluate actual cinematic craft, including where applicable:

* camera framing
* camera movement
* focal hierarchy
* depth
* lighting direction
* highlights/shadows
* material response
* scene transitions
* visual rhythm
* spatial storytelling
* product reveal
* composition between 3D and typography
* emotional/brand atmosphere

## Motion

Motion must have narrative or interaction purpose.

Reject meaningless floating, arbitrary parallax, random object rotation, animation added only for decoration, and excessive movement that hurts usability.

Evaluate timing, easing, sequencing, continuity, scroll choreography, interaction feedback, camera/object coordination, and reduced-motion strategy.

## Responsive 3D art direction

Desktop composition must NOT simply shrink onto mobile.

Required evaluation viewports:

* Desktop: 1440 × 900
* Laptop: 1280 × 800
* Tablet: 768 × 1024
* Mobile: 390 × 844

Evaluate camera recomposition, object scale/position, typography/3D relationship, interaction adaptation, readable framing, scene cropping, and performance/degradation strategy.

## Performance

High-end visuals must not excuse unusable performance.

The benchmark must define measurable evidence for browser/runtime health, failed requests, WebGL/runtime errors, relevant load/runtime timing, responsive stability, asset/network weight where measurable, interaction smoothness where measurable, and graceful fallback/degradation where necessary.

Do not invent arbitrary performance thresholds unless justified by existing ACOS policy or operator-approved benchmark criteria.

## Anti-cheap-3D hard failures

The acceptance contract must explicitly prevent false cinematic PASS for cases such as decorative-checkbox 3D, primitive/demo-quality scenes, model-viewer-only experiences, poor geometry/materials/lighting, broken WebGL, disconnected 3D storytelling, desktop-only composition, major mobile framing failure, generic imitation, fabricated evidence, and missing required 3D evidence.

Do not map these to HR IDs arbitrarily; canonical Quality Gate owns HR semantics.

## Critic expectation

BM-002 must require independent evaluation capabilities for visual quality, creative quality, 3D quality, responsive behavior, motion quality, performance, and accessibility where applicable.

Do NOT hard-code exact ACOS skill IDs. Use role/capability semantics and normal Phase F routing.

## Evidence

BM-002 evidence contract must require sufficient real execution evidence to judge the result, including viewport renders, 3D-specific visual evidence, interaction/scroll states, camera/scene progression, responsive 3D behavior, runtime/console evidence, network failures, performance evidence, reduced-motion behavior, implementation completion, critic findings, Design Gate provenance, and Quality Gate provenance.

If evidence cannot support a quality claim, `BLOCKED_INSUFFICIENT_EVIDENCE` must remain possible.

## Scoring

Create a proposed BM-002 scoring model for operator review.

3D/cinematic quality must carry meaningful weight.

Quality Gate remains authoritative over numeric score.

Do NOT freeze arbitrary weights without operator approval.

## Lifecycle

BM-002 = REGISTERED / OPERATOR_APPROVAL_PENDING

Do NOT freeze until operator explicitly approves the derived acceptance contract.

Do NOT execute BM-002 yet.

Do NOT start PF-3.

## Repository location

All BM-002 registration artifacts must live under:

`C:\Shahrukh\Effect79\effect79automation\benchmarks\BM-002\`
