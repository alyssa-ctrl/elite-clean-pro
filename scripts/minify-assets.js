#!/usr/bin/env node
/**
 * Post-build: minify standalone CSS and JS in _site/assets/
 * Only runs on production builds (NODE_ENV=production).
 */

const fs = require("fs");
const path = require("path");

if (process.env.NODE_ENV !== "production" && process.env.ELEVENTY_ENV !== "production") {
  console.log("[minify-assets] Skipped (not a production build)");
  process.exit(0);
}

const CleanCSS = require("clean-css");
const Terser = require("terser");

async function run() {
  const assetsDir = path.join(__dirname, "..", "_site", "assets");

  const cssPath = path.join(assetsDir, "site.css");
  if (fs.existsSync(cssPath)) {
    const before = fs.readFileSync(cssPath, "utf8");
    const result = new CleanCSS({ level: 2 }).minify(before);
    if (result.errors.length) {
      console.error("[minify-assets] CSS errors:", result.errors);
      process.exit(1);
    }
    fs.writeFileSync(cssPath, result.styles);
    const pct = Math.round((1 - result.styles.length / before.length) * 100);
    console.log(`[minify-assets] site.css  ${before.length} → ${result.styles.length} bytes (${pct}% smaller)`);
  }

  const jsPath = path.join(assetsDir, "site.js");
  if (fs.existsSync(jsPath)) {
    const before = fs.readFileSync(jsPath, "utf8");
    const result = await Terser.minify(before, {
      compress: { passes: 2 },
      mangle: true,
      format: { comments: false }
    });
    if (result.error) {
      console.error("[minify-assets] JS error:", result.error);
      process.exit(1);
    }
    fs.writeFileSync(jsPath, result.code);
    const pct = Math.round((1 - result.code.length / before.length) * 100);
    console.log(`[minify-assets] site.js   ${before.length} → ${result.code.length} bytes (${pct}% smaller)`);
  }
}

run().catch((err) => {
  console.error("[minify-assets]", err);
  process.exit(1);
});
