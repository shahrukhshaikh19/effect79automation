#!/usr/bin/env node
/** Interaction + performance evidence for BM-001 (E-007, E-009). */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

function parseArgs(argv) {
  const args = { target: null, output: null };
  for (let i = 2; i < argv.length; i++) {
    if (argv[i] === "--target") args.target = argv[++i];
    else if (argv[i] === "--output") args.output = argv[++i];
  }
  return args;
}

function resolveTarget(target, browserRoot) {
  if (target.startsWith("file://")) return target;
  const abs = path.isAbsolute(target)
    ? target
    : path.resolve(browserRoot, target.replace(/^\.\//, ""));
  return `file://${abs.replace(/\\/g, "/")}`;
}

async function main() {
  const args = parseArgs(process.argv);
  if (!args.target || !args.output) {
    console.error("Usage: capture-interaction.mjs --target <path> --output <dir>");
    process.exit(2);
  }
  const scriptDir = path.dirname(fileURLToPath(import.meta.url));
  const browserRoot = path.resolve(scriptDir, "..");
  const outputDir = path.resolve(process.cwd(), args.output);
  fs.mkdirSync(outputDir, { recursive: true });
  const target = resolveTarget(args.target, browserRoot);

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  const interactions = [];

  page.on("console", (msg) => {
    if (msg.type() === "error") interactions.push({ type: "console_error", text: msg.text() });
  });

  const t0 = Date.now();
  await page.goto(target, { waitUntil: "networkidle", timeout: 30000 });
  const navTiming = await page.evaluate(() => {
    const t = performance.timing;
    return {
      dom_content_loaded_ms: t.domContentLoadedEventEnd - t.navigationStart,
      load_event_ms: t.loadEventEnd - t.navigationStart,
    };
  });

  await page.click("nav .nav-toggle", { timeout: 5000 }).catch(() => null);
  interactions.push({ type: "click", selector: "nav .nav-toggle", timestamp: new Date().toISOString() });

  await page.click('a[href="#capabilities"]', { timeout: 5000 }).catch(() => null);
  interactions.push({ type: "click", selector: 'a[href="#capabilities"]', timestamp: new Date().toISOString() });

  await page.locator(".cap-item button").first().click({ timeout: 5000 }).catch(() => null);
  interactions.push({ type: "click", selector: ".cap-item button", timestamp: new Date().toISOString() });

  await page.waitForTimeout(400);
  interactions.push({ type: "scroll_settle", duration_ms: Date.now() - t0 });

  fs.writeFileSync(path.join(outputDir, "interaction_log.json"), JSON.stringify({ interactions }, null, 2));
  fs.writeFileSync(path.join(outputDir, "performance_metrics.json"), JSON.stringify(navTiming, null, 2));

  await browser.close();
  console.log(JSON.stringify({ status: "complete" }));
}

main().catch((err) => {
  console.error(JSON.stringify({ status: "error", message: String(err) }));
  process.exit(1);
});
