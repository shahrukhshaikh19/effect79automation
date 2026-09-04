# ACOS Browser Tool (Playwright)

Phase D browser evidence layer. **Captures facts; does not judge visual quality.**

## Pin

- **Playwright:** `1.49.1` (`package.json`)
- **Browser engine:** Chromium (installed via explicit bootstrap)

## Bootstrap (explicit — not run by validators)

```bash
cd tools/browser
npm ci
npm run bootstrap
```

`bootstrap.mjs` runs `npx playwright install chromium` when invoked explicitly.

## Capture

```bash
node scripts/capture-evidence.mjs --config viewport-config.example.yaml --output ../../validation/evidence/browser-health
```

## Capabilities

- Local `file://` and authorized HTTP(S) targets
- Multi-viewport matrix from config
- Console errors, uncaught page errors, critical network failures
- Reduced-motion emulation (optional)
- Deterministic readiness waits
- YAML evidence manifest per run

## Security

- No credentials in repo
- No TLS bypass by default
- No arbitrary domain crawling
- Targets must be supplied explicitly

## Handoff

```text
Browser/Playwright → render/runtime evidence → Visual/Creative/3D Critics → Quality Gate
```

Browser must NOT emit: "approved", "premium", quality scores.

See `schemas/browser-evidence.schema.yaml`.
