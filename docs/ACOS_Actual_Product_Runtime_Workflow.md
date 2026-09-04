# ACOS — Actual Product Runtime Workflow

**Version:** 1.2 (canonical-aligned)  
**Authority:** `ACOS_FINAL_CANONICAL_v1.2.md`  
**Type:** Runtime workflow diagram — visual summary only; canonical docs win on conflict.

Execution engines (Cursor, Claude, Codex, local models) are replaceable. ACOS is the persistent operating intelligence.

---

## Runtime workflow

```mermaid
flowchart TD
    subgraph AUTHORITY[" "]
        YOU["YOU — Product Owner / Final Authority<br/>goals · requirements · assets · references · constraints · final decision"]
    end

    YOU -->|project request| HOST["EXECUTION HOST / MODEL<br/>Cursor · Claude · Codex · local LLM<br/>writes code/assets · calls tools · runs checks"]
    HOST -->|loads| BRAIN["ACOS PERSISTENT BRAIN<br/>Constitution · Workflow · Routing · Skills Registry · Memory · Quality Gates<br/><i>knowledge stays external when model changes</i>"]
    BRAIN -->|classifies + routes| INTAKE["PROJECT INTAKE<br/>brief · assets · references · existing code · constraints<br/><i>no default style/industry/3D assumption</i>"]
    INTAKE -->|smallest sufficient skill set| CREATIVE

    subgraph CREATIVE["CREATIVE PHASE — before Design Gate"]
        direction TB
        C1["Reference Analysis"]
        C2["Creative Direction"]
        C3["Anti-Generic Review"]
        C4["Art Direction"]
        C5["Experience Architecture"]
        C1 --> C2 --> C3 --> C4 --> C5
    end

    CREATIVE --> DG{"DESIGN GATE<br/>distinctive? · project-specific? · feasible?<br/>responsive? · 3D/motion justified?"}
    DG -->|FAIL| CREATIVE
    DG -->|PASS| PLAN["TECHNICAL PLAN"]

    PLAN --> PROD["SPECIALIST PRODUCTION<br/>activate only required approved skills"]
    PROD --> TECH
    PROD --> TOOLS

    subgraph TECH["TECHNICAL SKILLS — only after Design Gate PASS"]
        direction TB
        T1["Frontend"]
        T2["Three.js / R3F"]
        T3["GSAP / Motion"]
        T4["Blender"]
        T5["img2threejs — ONLY when required"]
    end

    subgraph TOOLS["TOOLS — execution infrastructure, not skills"]
        direction TB
        TL1["Git + deterministic scripts"]
        TL2["Blender MCP — during Blender production"]
        TL3["Browser / Playwright — inspection + QA"]
    end

    TECH --> INTEG["INTEGRATION"]
    TOOLS --> INTEG
    INTEG --> RENDER["RENDER / BROWSER / RUNTIME INSPECTION<br/>mandatory evidence before visual signoff"]

    RENDER --> QA

    subgraph QA["EVALUATION LAYER — independent critics"]
        direction TB
        Q1["Functional QA"]
        Q2["Visual QA + Creative QA"]
        Q3["Domain Critics — 3D / Motion when relevant"]
        Q4["Performance + Accessibility QA"]
    end

    QA --> FQG{"FINAL QUALITY GATE<br/>acos-quality-gate"}
    FQG -->|REJECT| ROUTE["Route defect to responsible upstream skill<br/>creative · engineering · 3D · motion · responsive · webgl-performance"]
    ROUTE --> PROD
    FQG -->|APPROVE| SHIP["SHIP — release candidate"]
    SHIP --> MEM["PROJECT / FAILURE / SUCCESS MEMORY<br/>acos-failure-learning · memory policy"]
```

---

## Canonical alignment notes

1. **Creative phase only before Design Gate** — no full specialist production before gate pass (Constitution #6).
2. **Anti-Generic Review** is explicit — not merged into art direction.
3. **Technical skills activate after Design Gate PASS** — availability ≠ activation.
4. **Tools are separate** — Browser/Playwright primarily for inspection/QA; Blender MCP for Blender execution.
5. **Render/browser inspection** is mandatory before visual QA signoff (Constitution #14).
6. **Rejections route to responsible skill** — functional failures do not always return to creative layer.
7. **End state includes memory writeback** — not only “release candidate.”

## What this diagram is not

- Not a foundation implementation checklist (Phase A–J).
- Not a skill import map (Phase B).
- Not a benchmark or sample project workflow.

For machine-readable skill inventory see `registry/SKILLS.yaml`.
