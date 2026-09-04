#!/usr/bin/env node
/**
 * Deterministic multi-viewport browser evidence capture for ACOS.
 * Captures evidence only — no quality judgments.
 */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { parse as parseYaml, stringify as stringifyYaml } from "yaml";
import { chromium } from "playwright";

function parseArgs(argv) {
  const args = { config: null, output: null };
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === "--config") args.config = argv[++i];
    else if (argv[i] === "--output") args.output = argv[++i];
  }
  return args;
}

function resolveTarget(target, browserRoot) {
  if (target.startsWith("file://")) {
    const raw = target.slice("file://".length);
    if (raw.startsWith("./") || raw.startsWith(".\\") || !path.isAbsolute(raw)) {
      const abs = path.resolve(browserRoot, raw.replace(/^\.\//, ""));
      return `file://${abs.replace(/\\/g, "/")}`;
    }
    return target;
  }
  if (target.startsWith("http://") || target.startsWith("https://")) return target;
  const abs = path.resolve(browserRoot, target);
  return `file://${abs.replace(/\\/g, "/")}`;
}

async function main() {
  const args = parseArgs(process.argv);
  if (!args.config || !args.output) {
    console.error("Usage: capture-evidence.mjs --config <yaml> --output <dir>");
    process.exit(2);
  }

  const scriptDir = path.dirname(fileURLToPath(import.meta.url));
  const browserRoot = path.resolve(scriptDir, "..");
  const configPath = path.resolve(process.cwd(), args.config);
  const outputDir = path.resolve(process.cwd(), args.output);
  const config = parseYaml(fs.readFileSync(configPath, "utf8"));

  fs.mkdirSync(outputDir, { recursive: true });
  const runId = `browser-${Date.now()}`;
  const start = Date.now();
  const target = resolveTarget(config.target, browserRoot);

  const browser = await chromium.launch({ headless: true });
  const contextOptions = config.reduced_motion
    ? { reducedMotion: "reduce" }
    : {};
  const context = await browser.newContext(contextOptions);
  const page = await context.newPage();

  const consoleErrors = [];
  const pageErrors = [];
  const networkFailures = [];

  page.on("console", (msg) => {
    if (msg.type() === "error") consoleErrors.push(msg.text());
  });
  page.on("pageerror", (err) => pageErrors.push(String(err)));
  page.on("requestfailed", (req) => {
    networkFailures.push(`${req.method()} ${req.url()} — ${req.failure()?.errorText ?? "failed"}`);
  });

  const readiness = config.readiness ?? {};
  await page.goto(target, {
    waitUntil: readiness.wait_until ?? "networkidle",
    timeout: readiness.timeout_ms ?? 30000,
  });
  if (readiness.animation_settle_ms) {
    await page.waitForTimeout(readiness.animation_settle_ms);
  }

  const browserVersion = browser.version();
  const captures = [];

  for (const vp of config.viewports ?? [{ name: "default", width: 1280, height: 720, device_scale_factor: 1 }]) {
    await page.setViewportSize({
      width: vp.width,
      height: vp.height,
    });
    const vpDir = path.join(outputDir, vp.name);
    fs.mkdirSync(vpDir, { recursive: true });

    const viewportPath = path.join(vpDir, "viewport.png");
    await page.screenshot({ path: viewportPath, fullPage: false });

    const entry = {
      viewport: {
        name: vp.name,
        width: vp.width,
        height: vp.height,
        device_scale_factor: vp.device_scale_factor ?? 1,
      },
      capture_type: "viewport",
      screenshot_path: path.relative(outputDir, viewportPath).replace(/\\/g, "/"),
      console_errors: [...consoleErrors],
      page_errors: [...pageErrors],
      network_failures: [...networkFailures],
    };

    if (config.capture?.full_page) {
      const fullPath = path.join(vpDir, "full_page.png");
      await page.screenshot({ path: fullPath, fullPage: true });
      captures.push({
        ...entry,
        capture_type: "full_page",
        screenshot_path: path.relative(outputDir, fullPath).replace(/\\/g, "/"),
      });
    }

    captures.push(entry);
  }

  await browser.close();

  const runtimeHealthy =
    consoleErrors.length === 0 &&
    pageErrors.length === 0 &&
    networkFailures.length === 0;

  const manifest = {
    run_id: runId,
    timestamp: new Date().toISOString(),
    target,
    browser: "chromium",
    browser_version: browserVersion,
    page_state: "loaded",
    reduced_motion: Boolean(config.reduced_motion),
    readiness_condition: readiness.wait_until ?? "networkidle",
    duration_ms: Date.now() - start,
    runtime_healthy: runtimeHealthy,
    visual_quality_approved: false,
    captures,
    notes: "Evidence capture only — critics interpret; quality gate decides approval.",
  };

  const manifestPath = path.join(outputDir, "manifest.yaml");
  fs.writeFileSync(manifestPath, stringifyYaml(manifest), "utf8");
  console.log(stringifyYaml({ status: "complete", manifest_path: manifestPath, runtime_healthy: runtimeHealthy }));
}

main().catch((err) => {
  console.error(JSON.stringify({ status: "error", message: String(err) }));
  process.exit(1);
});
