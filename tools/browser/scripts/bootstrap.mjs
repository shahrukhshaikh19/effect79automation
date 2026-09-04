#!/usr/bin/env node
/**
 * Explicit Playwright browser bootstrap — NOT invoked by ACOS validators.
 */
import { execSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const root = path.dirname(fileURLToPath(import.meta.url));
const browserRoot = path.resolve(root, "..");

console.log("ACOS browser bootstrap: installing Chromium for pinned Playwright...");
execSync("npx playwright install chromium", {
  cwd: browserRoot,
  stdio: "inherit",
});
console.log("Bootstrap complete.");
