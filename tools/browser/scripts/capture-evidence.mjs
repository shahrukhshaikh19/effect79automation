#!/usr/bin/env node
/**
 * Deterministic multi-viewport browser evidence capture for ACOS.
 * Captures evidence only — no quality judgments.
 * Requested vs effective DPR must match or runtime_healthy=false.
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

function attachListeners(page, consoleErrors, pageErrors, networkFailures, consoleLog) {
  page.on("console", (msg) => {
    const entry = { type: msg.type(), text: msg.text(), timestamp: new Date().toISOString() };
    consoleLog.push(entry);
    if (msg.type() === "error") consoleErrors.push(msg.text());
  });
  page.on("pageerror", (err) => pageErrors.push(String(err)));
  page.on("requestfailed", (req) => {
    networkFailures.push(
      `${req.method()} ${req.url()} — ${req.failure()?.errorText ?? "failed"}`,
    );
  });
}

async function captureViewport(browser, browserVersion, vp, target, config, outputDir) {
  const requestedDpr = vp.device_scale_factor ?? 1;
  const contextOptions = {
    viewport: { width: vp.width, height: vp.height },
    deviceScaleFactor: requestedDpr,
  };
  if (config.reduced_motion) contextOptions.reducedMotion = "reduce";

  const context = await browser.newContext(contextOptions);
  const page = await context.newPage();

  const consoleErrors = [];
  const pageErrors = [];
  const networkFailures = [];
  const consoleLog = [];
  attachListeners(page, consoleErrors, pageErrors, networkFailures, consoleLog);

  const readiness = config.readiness ?? {};
  await page.goto(target, {
    waitUntil: readiness.wait_until ?? "networkidle",
    timeout: readiness.timeout_ms ?? 30000,
  });
  if (readiness.animation_settle_ms) {
    await page.waitForTimeout(readiness.animation_settle_ms);
  }

  const effectiveDpr = await page.evaluate(() => window.devicePixelRatio);
  const dprMatch = Math.abs(effectiveDpr - requestedDpr) < 0.01;

  const vpDir = path.join(outputDir, vp.name);
  fs.mkdirSync(vpDir, { recursive: true });

  const captureRecords = [];
  const baseEntry = {
    viewport: {
      name: vp.name,
      width: vp.width,
      height: vp.height,
      requested_device_scale_factor: requestedDpr,
      effective_device_scale_factor: effectiveDpr,
      dpr_integrity: dprMatch,
    },
    browser: "chromium",
    browser_version: browserVersion,
    reduced_motion: Boolean(config.reduced_motion),
    readiness_condition: readiness.wait_until ?? "networkidle",
    console_errors: [...consoleErrors],
    page_errors: [...pageErrors],
    network_failures: [...networkFailures],
  };

  const viewportPath = path.join(vpDir, "viewport.png");
  await page.screenshot({ path: viewportPath, fullPage: false });
  captureRecords.push({
    ...baseEntry,
    capture_type: "viewport",
    screenshot_path: path.relative(outputDir, viewportPath).replace(/\\/g, "/"),
  });

  if (config.capture?.full_page) {
    const fullPath = path.join(vpDir, "full_page.png");
    await page.screenshot({ path: fullPath, fullPage: true });
    captureRecords.push({
      ...baseEntry,
      capture_type: "full_page",
      screenshot_path: path.relative(outputDir, fullPath).replace(/\\/g, "/"),
    });
  }

  const selector = vp.element_selector ?? config.element_capture?.selector;
  if (selector) {
    const locator = page.locator(selector);
    const count = await locator.count();
    if (count === 0) {
      await context.close();
      throw new Error(`Element capture failed: selector not found: ${selector}`);
    }
    const elementPath = path.join(vpDir, "element.png");
    await locator.first().screenshot({ path: elementPath });
    captureRecords.push({
      ...baseEntry,
      capture_type: "element",
      selector,
      screenshot_path: path.relative(outputDir, elementPath).replace(/\\/g, "/"),
    });
  }

  await context.close();
  return { captureRecords, consoleLog, dprMatch };
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
  const browserVersion = browser.version();
  const captures = [];
  const allConsoleLog = [];
  let allDprMatch = true;

  try {
    for (const vp of config.viewports ?? [
      { name: "default", width: 1280, height: 720, device_scale_factor: 1 },
    ]) {
      const result = await captureViewport(
        browser,
        browserVersion,
        vp,
        target,
        config,
        outputDir,
      );
      captures.push(...result.captureRecords);
      allConsoleLog.push(...result.consoleLog.map((e) => ({ ...e, viewport: vp.name })));
      if (!result.dprMatch) allDprMatch = false;
    }
  } finally {
    await browser.close();
  }

  const consoleLogPath = path.join(outputDir, "console_log.json");
  fs.writeFileSync(consoleLogPath, JSON.stringify(allConsoleLog, null, 2), "utf8");

  const hasErrors = captures.some(
    (c) =>
      c.console_errors.length > 0 ||
      c.page_errors.length > 0 ||
      c.network_failures.length > 0,
  );

  const runtimeHealthy = !hasErrors && allDprMatch;

  const manifest = {
    run_id: runId,
    timestamp: new Date().toISOString(),
    target,
    browser: "chromium",
    browser_version: browserVersion,
    page_state: "loaded",
    reduced_motion: Boolean(config.reduced_motion),
    readiness_condition: config.readiness?.wait_until ?? "networkidle",
    duration_ms: Date.now() - start,
    runtime_healthy: runtimeHealthy,
    dpr_integrity: allDprMatch,
    visual_quality_approved: false,
    console_log_json: path.relative(outputDir, consoleLogPath).replace(/\\/g, "/"),
    captures,
    notes:
      "Evidence capture only — critics interpret; quality gate decides approval. runtime_healthy requires DPR integrity.",
  };

  const manifestPath = path.join(outputDir, "manifest.yaml");
  fs.writeFileSync(manifestPath, stringifyYaml(manifest), "utf8");
  console.log(
    stringifyYaml({
      status: "complete",
      manifest_path: manifestPath,
      runtime_healthy: runtimeHealthy,
      dpr_integrity: allDprMatch,
    }),
  );
}

main().catch((err) => {
  console.error(JSON.stringify({ status: "error", message: String(err) }));
  process.exit(1);
});
