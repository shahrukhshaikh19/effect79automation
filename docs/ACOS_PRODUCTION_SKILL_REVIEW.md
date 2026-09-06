# ACOS production review — why the loop is cheaper than a prompt

**Date:** 2026-09-06  
**Trigger:** VELAR (and prior TWS runs) spent days in host stages and still did not look like a charging case + earbuds. Normal prompting would have been faster.  
**End goal (canonical):** `ACOS_END_GOAL_WORKFLOW.md` + `ACOS_FINAL_CANONICAL_v1.2.md`

> One clear prompt → route + **load** real skills → direction → real product (if physical) → real hero 3D → cinematic site → browser evidence → independent critique → correct → **portfolio-quality** result.  
> User does not orchestrate. YAML is not quality.

This document is the skill + workflow review. It is **not** permission to start another VELAR dump.

---

## 1. End goal vs what we actually built

| End goal | What the host does today |
|---|---|
| Smallest sufficient craft | Routes a **catalog dump**: 5 creative skills + 5 Blender skills + industrial trio before anyone looks at a product |
| Skill = domain expertise the model **executes** | Skill = SKILL.md + `procedure_evidence` string ≥ 24 chars + matching sha256 |
| Rendered pixels decide | Files, luma, bbox, and YAML `pass` decide until a human/critic chat |
| Correction loop on weak pictures | Correction loop on missing filenames |
| Flagship portfolio | Cheap MCP kitbash + honest-looking receipts |

**Skill ≠ Tool ≠ Model ≠ Memory** is still correct. The failure is that **Skill was implemented as a conductor contract**, and **Tool (Blender MCP `execute_blender_code`)** became the entire “modeler.”

Normal prompting wins because it does the thing ACOS pretends to do:

```text
look at the picture → say it is wrong → change the mesh → look again
```

ACOS did:

```text
write YAML → satisfy locks → advance stage → write pass so the next lock opens
```

Producer `product_read_verdict: pass` is now **banned** (`validate_form_model`). That stops the lie. It does **not** create a product.

---

## 2. Why this wasted months of calendar and still looks cheap

### 2.1 The host is a file conductor

`tools/host_driver/HOST_LOOP.md` and `runtime/host/product_form.py` can fail-close on:

- missing PNGs
- crushed luma
- through-floor bboxes
- first-dump `pass`
- same-chat critic

They **cannot** fail-close on “this does not look like earbuds.”  
So the producer is trained to feed the lock, not the eye.

### 2.2 Too many stages before one good picture

Creative → Design Gate → ACOS-15 YAML → ACOS-16 MCP dump → clay renders → critic chat → form gate → lookdev → production → capture → more critics → quality gate.

A physical-product brief does not need five creative YAML files before someone models a pebble that reads. Direction can be **one short thesis**. The rest is delay.

### 2.3 The Blender skills we forked teach the cheap path

External pack: [arjun988/blender-skills](https://github.com/arjun988/blender-skills)  
`blender-modeler` Core Workflow step 2 is literally:

```text
Blockout → Primitives, mirror, array
```

`hard-surface` is boolean/bevel/greeble language (sci-fi panels), not consumer TWS SubD.

We then **deferred sculpting** in `ACOS_FINAL_CANONICAL_v1.2.md` §3.4 — the one production skill in that pack that is about form, not modifiers.

The same upstream pack’s **actual quality loop** (we mostly did not run):

```text
reference analysis → camera match → geometry tiers → screenshot compare (max 3) → visual-match checklist
```

Source: [blender-director SKILL.md](https://github.com/arjun988/blender-skills/blob/main/.claude/skills/blender-director/SKILL.md) and `reference-image-match.md`.

We have `skills/external/blender/references/reference-image-match.md` on disk. VELAR mood refs were routed to ACOS-02 as “do not copy,” so the **compare loop was skipped**. Non-copy is correct. Skipping “look at the screenshot after every hop” is not.

### 2.4 ACOS-16 is a recipe, not a modeler

The executable form recipe (enclosure → split → cavity → three volumes → origin before parent) is a **stop-doing-dumb-things list**.  
It does not contain:

- TWS / in-ear anatomy
- SubD primary-form development
- clay lighting that does not blow to white
- “if the PNG does not read, the hop failed — do not write ready”
- a generator that is parametric and re-runnable

So every hop is a new improvised `bpy` novel. [PoBruno/mcp-blender-agent](https://github.com/PoBruno/mcp-blender-agent) states the failure mode we hit: *each run generates different Python; when it fails you don’t know if it was the model, the script, or the scene.*

### 2.5 img2threejs already has a vision loop — unused

`skills/external/img2threejs` is a staged sculpt-in-code + **agent-vision self-correction** pipeline.  
Flagship lock said “Blender first, no website before form.” That is right for a physical hero.  
The **method** (look → gap list → fix, never one-shot) should have been the Blender clay method. We used the opposite: one-shot scripts.

---

## 3. Internet skill map (real sources only)

Do **not** install 94 skills. The lesson is **which loops they have that we dropped**.

| Source | URL | What to steal | What not to steal |
|---|---|---|---|
| arjun988/blender-skills | https://github.com/arjun988/blender-skills | Screenshot compare loop, geometry tiers, director brief **before** mesh, sculpting skill | 94-skill dump, genre packs, “primitives = blockout” as the stop |
| blender-director reference match | https://github.com/arjun988/blender-skills/blob/main/.claude/skills/blender-director/SKILL.md | Camera match before detail; max 3 compare hops | Pixel-copy of a brand product |
| kai-chop/blender-industrial-kit | https://github.com/kai-chop/blender-industrial-kit | Split **dossier / diverge / engineering sheet / verify**; parametric script + gates | 0-star, furniture-scale examples; not a TWS bible |
| PoBruno/mcp-blender-agent | https://github.com/PoBruno/mcp-blender-agent | Typed Blender ops, undo groups, stable IDs — stop improvising 400-line dumps | Replacing ACOS overnight; unproven for consumer ID |
| img2threejs (already in repo) | local `skills/external/img2threejs` | Vision self-correction; never one-shot | Using it to skip Blender when the brief requires an authored GLB |
| alton47/threejs-skills | already approved in canonical §3.2 | Keep as implementation refs | Invoking all 10 as “craft” before a hero exists |
| greensock/gsap-skills | already approved | Keep for production motion | Scroll theater before the product reads |
| autcir/r3f-rules | https://github.com/autcir/r3f-rules/blob/main/SKILL.md | GPU budgets, demand frameloop, 2D fallback | React-only religion (VELAR is vanilla OK) |
| glyahh/threejs-ultra | https://github.com/glyahh/threejs-ultra | One orchestrator; 3D only if the concept earns it | Another mega-pack |
| hoanacantincus cinematic-site-builder | https://github.com/hoanacantincus-cmd/cinematic-site-builder | `progress 0→1` as the only transport; **real GLB first**, procedural last | Template Lusion clone |
| Anthropic Agent Skills | https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview | Skill = onboarding a specialist: procedure + **scripts that return output**, not essays | More markdown without scripts |
| VULK 2026 3D+AI guide | https://vulk.dev/blog/how-to-build-a-3d-website-with-ai-complete-guide | Honest limit: AI is fast at scenes; **hand craft still owns top-tier product form** | “Generate the whole Awwwards site in one prompt” |

Thin / do not treat as authority: 0-star industrial-kit clones, “13-step immersive landing page” skills that recommend glassmorphism + particle globes (that is the cheap web we already banned).

---

## 4. Skill verdicts (only the ones that decide quality)

### KEEP (role is right, do not multiply)

| Skill | Why |
|---|---|
| ACOS-01 Creative Director | Thesis is needed. Output must become **one page**, not a novel. |
| ACOS-02 Reference Analysis | Keep. Product-read + non-copy. Must feed a **compare loop**, not only YAML. |
| ACOS-03 Anti-generic | Keep as challenger. Must be allowed to fail a **picture**, not only adjectives. |
| ACOS-13 Quality Gate | Keep. Must stay independent. |
| ACOS-17 Industrial Design Critic | Keep. **Only** owner of form pass. |
| lookdev, materials, lighting, export-pipeline | Keep for **after** form exists. |
| threejs-core / materials / lighting / camera / loaders | Keep as **implementation** after a real GLB. |
| gsap-core / scrolltrigger | Keep for scroll-scrub. |
| img2threejs | Keep for reconstruction-by-code when Blender is **not** the hero path. |

### KEEP-REWRITE (same name, different brain)

| Skill | Rewrite or it stays cheap |
|---|---|
| **ACOS-15 Industrial Product Designer** | Keep the role. Replace adjective YAML with a **dossier + 2–3 form directions + dimensioned sheet** (industrial-kit idea). Add category anatomy references (in-ear, over-ear, appliance) that are **class**, not brand. |
| **ACOS-16 Product Form Modeler** | Delete “write pass.” Require: render → **read the PNG** → gap list → one hop. No hop without a framed clay shot. Prefer a **parametric generator script** checked into the project, not a new novel each turn. |
| **blender-director** | Force `reference-image-match.md` **compare loop** on every flagship clay hop (mood refs = lighting + product-read, not pixel clone). |
| **blender-modeler** | Replace “Blockout → Primitives” as a legal stop. Primary form = SubD / fitted enclosure. Primitives are construction only. |
| **hard-surface** | Demote for consumer electronics. Boolean/greeble is the VELAR well-cutter trap. Consumer ID is SubD + split + cavity, not sci-fi panels. |
| **prop-artist** | Must define **instrument anatomy** (housing / interface / contact) with picture tests, not “join three icospheres.” |

### MERGE / DO NOT INVOKE EARLY

| Skills | Action |
|---|---|
| ACOS-04 + ACOS-05 + ACOS-08 | One **page direction** artifact until form exists. Full art/IA novels after Product Form Gate. |
| threejs-shaders, postprocessing, gsap-react, gsap-performance | Reference only until a hero GLB exists. |
| blender qa-review, compositing, geometry-nodes | On demand. Not invoke_now for clay. |

### REPLACE (wrong tool for the job)

| Current | Replace with |
|---|---|
| Improvised `execute_blender_code` novels as “modeling” | Either (A) project-local **parametric bpy module** + gates, or (B) typed Blender tools (mcp-blender-agent pattern). Skill text cannot fix this. |
| Host `product_read_verdict: pass` from producer | Already replaced: `fail` \| `ready_for_critic`. Do not revert. |

### NEW — maximum four (not twenty)

| New skill | Why it does not exist today | What it must contain |
|---|---|---|
| **ACOS-18 Form Vision Loop** | No skill **requires** reading the clay PNG before the next bpy hop | Mandatory: render named views → agent reads images → written gaps → only then code. Stop after 3 failed hops. Scripts, not essays. |
| **ACOS-19 Product Anatomy Library** | ACOS-15/16 are domain-neutral and therefore empty of ear/hand/hinge knowledge | Short, category-scoped references: TWS, over-ear, handheld appliance. Class geometry, not AirPods. |
| **ACOS-20 Devil Critic** | Producer + friendly critic both want the stage to move | Assumes every YAML claim is a lie. Must cite pixels. Can block ready_for_critic and Design Gate. Not a ship gate. |
| **ACOS-21 Parametric Form Builder** (or a script pack under ACOS-16) | One-shot MCP is nondeterministic | One generator per product family: envelope params in, named parts out, re-runnable, bbox + render hooks. |

**Do not add:** more Three.js skills, more GSAP skills, vehicle-artist, character packs, “Awwwards mega-skill.” Those increase routing, not craft.

### DELETE from default flagship invoke_now

- `hard-surface` on in-ear / soft-goods (keep for weapons/vehicles only)
- Full creative quintet before a physical form exists (keep ACOS-01 + ACOS-02 only)
- Any skill whose only output is `procedure_evidence` with no picture

---

## 5. Workflow changes (ranked)

1. **Eye before stage.** No `advance` on clay unless the producer (or a vision script) lists what the PNG shows in plain words. If they cannot name “case + two buds,” verdict is `fail`.
2. **Critic owns form pass.** Done. Do not let producer `pass` return.
3. **One direction packet, then form.** Cut CREATIVE invoke_now to ACOS-01 + ACOS-02 (+ ACOS-03 only if thesis is generic). Art/IA after form gate.
4. **Parametric build, not chat novels.** VELAR-style `_clay_iterN.py` rewritten from scratch each hop is the waste.
5. **Restore the compare loop we already licensed.** Wire blender-director `reference-image-match` + clay lighting that cannot blow out (fixed exposure card).
6. **Kill stage theater.** FORM_EVIDENCE can merge into FORM_AUTHORING (files exist or they don’t). Two chats for critic is fine; twelve YAML files are not.

---

## 6. Agent team (how ACOS should run a flagship job)

Not 17 Gemini agents. **Four roles + devil.** Same end goal.

| Role | Job | Forbidden |
|---|---|---|
| **Conductor** (host) | Route, wait for Blender, refuse skip, open critic pass | Judging beauty; writing pass |
| **Director** | Thesis + non-copy + page job (thin) | Meshes, YAML novels |
| **Form craft** | Anatomy + parametric build + vision loop | Website, lookdev, self-pass |
| **Web craft** | Load the approved GLB; scroll is the hinge | Inventing the product in Three.js |
| **Devil** | Final review of the other four. Assumes receipts are fake. Reads pixels. | Building, “fixing” by adding more YAML |

Devil checklist (always):

- Would a stranger name the object from the picture in 2 seconds?
- Would a competent human with the same brief have a better still after one afternoon?
- Did any lock **force a lie**?
- Is this skill encyclopedia or an executable hop?
- Did we skip Blender, or skip **looking**?

If devil fails, the job returns to Form craft — not to a new skill file.

---

## 7. Honest limit (do not paper over this)

Locks and skills **do not invent industrial design talent**.  
A pocket TWS that reads as a real product is still hard for LLM + `execute_blender_code`.

The internet’s serious writeups agree: AI is fast at scenes and GLSL; **top-tier product form is still craft**.  
ACOS can:

- stop rewarding cheap dumps
- force looking
- give anatomy + parametric structure
- keep critics independent

ACOS cannot promise “one prompt, Apple-level object” until the form craft loop is real. Shipping another host lock instead of that loop is how we burned the time.

---

## 8. Locked next work (Devil REJECTED the skill-ID order)

[Devil](19dfe205-087a-4b9e-93c3-870aab9a6525) rejected ACOS-18/19/20/21 and the “short benchmark.” That verdict is locked.

**In code (2026-09-06):**

1. Producer-pass ban — kept.  
2. CREATIVE `invoke_now` + Design Gate = ACOS-01 + ACOS-02 only.  
3. `direction/clay_look.yaml` must match current clay PNG sha256 + `png_shows` + gaps before advance / next builder run.  
4. Re-runnable builder: `tools/form/build_form.py` (`runtime/host/form_builder.py`).  
5. `_CATEGORY_KILL` / wide-bar regex removed. `/hard-surface` only if `requires_hard_surface` (weapons / vehicles / sci-fi).  

**Cut:** ACOS-18, 19, 20, 21 as IDs. Internet-map follow-up as work. Agent-org markdown as delivery. ACOS-15 dossier inflation. SKILL.md rewrites of modeler/hard-surface/prop as the “fix.” Form benchmark until the loop above is code. Devil skill.

**Do not:** re-init VELAR, form-critic on current clay, install 94 blender skills.

---

## 9. Expert consensus (2026-09-06)

### [Workflow architect](567487f1-2cbd-4e3b-99ad-f9dfd35b1c8d)

Host is a YAML compliance conductor. User still runs `init` / `advance` / `capture` / critic chats — that is not one prompt. `procedure_evidence` (≥24 chars) is theater. Correction router exists and is **not wired**. WAITING_BLENDER should not block creative. Highest-impact: vision-owned gates, collapse 5 form stages → 2, auto conductor, abandon MCP-as-primary-modeler, wire REJECTED → correction.

### [Skills catalog auditor](97e3604b-f9b6-4cb3-8aa3-223e3b9e746d)

ACOS-01–15 and ACOS-17 roles are fine. ACOS-16 + blender-modeler **cannot** produce stranger-readable TWS. `img2threejs` is the only skill with a real vision/stop loop — wrong tool for Blender-first heroes, right *method*. Do not replace ACOS-15/17. Prefer **annex inside ACOS-16** over a pile of new IDs. Missing craft: SubD pebble hops, TWS anatomy mm, disk ortho clay (not viewport), stop-if-unread.

### [Production 3D researcher](5e00d96c-6f75-41b8-ab35-079913c494ae)

Public packs are thin for industrial form. We already forked the useful half of [arjun988/blender-skills](https://github.com/arjun988/blender-skills). More game/horror skills will not help. Studios: sketch → CAD/SubD skin → clay → CMF → KeyShot/VRED → tessellate → GLB. MCP dumps primitives because `primitive_*` is the highest-confidence `bpy`. **Keep MCP after form exists. Do not use it as form author.** Extra internet skills worth stealing as *files*, not new routed IDs: assembly overlap audit ([ProfRino](https://github.com/ProfRino/Blender-MCP-Assemply-Skill)), GLB-for-web bake/Draco ([vladmdgolam](https://github.com/vladmdgolam/agent-skills)), ID→CAD DFM ([beiming industrial-product-design-gbt](https://github.com/beiming183-cloud/industrial-product-design-gbt)).

### Tension (resolved pessimistically)

Auditor wants new skills with MCP hop recipes. Researcher says MCP cannot author form. **Researcher wins** until a picture proves a hop recipe works. First ship: method change + picture gate + stop-condition rewrite. New skill IDs only if those three still fail.

### [Devil](19dfe205-087a-4b9e-93c3-870aab9a6525) — REJECT

The review named Skill-as-receipt, then scheduled four new IDs. Same disease.

- ACOS-18/19/20/21 = original sin. 18 makes looking a loadable skill. 19 is anatomy encyclopedia. 20 is a mean-named critic YAML. 21 wraps a `.py` in a skill ID; the script alone was honest.  
- ACOS-16 “recipe rewrite” already shipped and already failed (S1, W6/W7/W10/W11). More stop-text is amnesia.  
- `ready_for_critic` + `iteration >= 2` will be the next lie.  
- Canonical workflow diagram still dumps the creative quintet — router will catalog-dump again unless that changes.  
- “Short form benchmark” is VELAR with a nicer name.  
- Smallest delta that would not lose to normal prompting: one thesis, open Blender, force PNGs into the next hop, re-run one builder `.py`. That still does not beat a competent human afternoon on Apple-level TWS. ACOS’s only win was *not wasting the week before the first readable still*. Minting skills spends that week again.

**Verdict:** REJECT the implementation order in the first draft of this file. KEEP only the five bullets in §8.
