#!/usr/bin/env node
/** Minimal browser runtime health — launches Chromium against neutral fixture. */
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const scriptDir = path.dirname(fileURLToPath(import.meta.url));
const browserRoot = path.resolve(scriptDir, "..");
const fixture = path.join(browserRoot, "fixtures", "blank.html");
const target = `file://${fixture.replace(/\\/g, "/")}`;

async function main() {
  try {
    const browser = await chromium.launch({ headless: true });
    const page = await browser.newPage();
    await page.goto(target, { waitUntil: "domcontentloaded", timeout: 15000 });
    const title = await page.title();
    await browser.close();
    console.log(JSON.stringify({
      tool: "TOOL-BROWSER-01",
      structural: "CONFIGURED",
      runtime: "AVAILABLE",
      browser: "chromium",
      playwright: "1.49.1",
      fixture: path.basename(fixture),
      page_title: title,
      message: "Browser launch and neutral fixture load succeeded",
    }));
  } catch (err) {
    console.log(JSON.stringify({
      tool: "TOOL-BROWSER-01",
      structural: "CONFIGURED",
      runtime: "BLOCKED",
      reason: String(err),
      message: "Configuration present but runtime unavailable — install deps and run bootstrap",
    }));
    process.exit(0);
  }
}

main();
