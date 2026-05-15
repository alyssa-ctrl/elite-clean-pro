#!/usr/bin/env python3
"""
Migrate elite-pro-clean's 11 HTML pages to Eleventy .njk templates.

For each HTML file:
  1. Pull metadata (title, description, OG tags, JSON-LD) into YAML frontmatter
  2. Strip everything now handled by the base layout / partials:
     - <head> boilerplate (font links, favicon, skip link, viewport)
     - Ticker strip, nav, mobile menu, footer, shared <script>
     - Shared CSS that's now in site.css (header, ticker, mobile menu, footer, tokens)
  3. Keep page-specific styles (hero, sections) and page-specific content
  4. Write src/<page>.njk
"""

import re
import os
import sys
from pathlib import Path

SOURCE_DIR = Path("/mnt/user-data/uploads")
DEST_DIR = Path("/home/claude/elite-pro/src")

PAGES = [
    "index.html",
    "residential.html",
    "commercial.html",
    "the-standard.html",
    "pricing.html",
    "quality-reporting.html",
    "move-out-cleaning.html",
    "biosmart.html",
    "faq.html",
    "about.html",
    "promise.html",
]

# CSS selectors / rules that live in site.css now — strip from page styles
SHARED_CSS_RULES = [
    r":root\s*\{[^}]*\}",
    r"\*\s*\{\s*box-sizing[^}]*\}",
    r"html\s*\{[^}]*\}",
    r"body\s*\{[^}]*\}",
    r"a\s*\{\s*color:\s*inherit[^}]*\}",
    r"::selection[^}]*\{[^}]*\}",
    r"\[id\]\s*\{[^}]*\}",
    r"\.skip-link[^{]*\{[^}]*\}",
    r"\.skip-link:focus[^{]*\{[^}]*\}",
    r"\*:focus-visible[^{]*\{[^}]*\}",
    r"\.ticker-strip[^{]*\{[^}]*\}",
    r"\.ticker-live[^{]*\{[^}]*\}",
    r"\.ticker-dot[^{]*\{[^}]*\}",
    r"@keyframes pulse-dot[^{]*\{[^{}]*(?:\{[^}]*\}[^{}]*)*\}",
    r"\.ticker-div[^{]*\{[^}]*\}",
    r"\.ticker-strip\s+a[^{]*\{[^}]*\}",
    r"\.ticker-strip\s+a:hover[^{]*\{[^}]*\}",
    r"nav\.main\s*\{[^}]*\}",
    r"nav\.main\.scrolled[^{]*\{[^}]*\}",
    r"\.workmark[^{]*\{[^}]*\}",
    r"\.workmark\s+em[^{]*\{[^}]*\}",
    r"\.workmark\s+\.small[^{]*\{[^}]*\}",
    r"\.nav-list[^{]*\{[^}]*\}",
    r"\.nav-list\s+a[^{]*\{[^}]*\}",
    r"\.nav-list\s+a::after[^{]*\{[^}]*\}",
    r"\.nav-list\s+a:hover[^{]*\{[^}]*\}",
    r"\.nav-list\s+a:hover::after[^{]*\{[^}]*\}",
    r"\.nav-list\s+a\.active[^{]*\{[^}]*\}",
    r"\.btn-book[^{]*\{[^}]*\}",
    r"\.btn-book:hover[^{]*\{[^}]*\}",
    r"\.btn-book\s+\.arrow[^{]*\{[^}]*\}",
    r"\.btn-book:hover\s+\.arrow[^{]*\{[^}]*\}",
    r"\.hamburger[^{]*\{[^}]*\}",
    r"\.hamburger:hover[^{]*\{[^}]*\}",
    r"\.mobile-menu[^{]*\{[^}]*\}",
    r"\.mobile-menu\.open[^{]*\{[^}]*\}",
    r"\.mobile-menu\s+a[^{]*\{[^}]*\}",
    r"\.mobile-menu\s+a:hover[^{]*\{[^}]*\}",
    r"\.mobile-menu\s+\.mobile-book[^{]*\{[^}]*\}",
    r"\.mobile-menu-close[^{]*\{[^}]*\}",
    r"\.mobile-menu-close:hover[^{]*\{[^}]*\}",
    r"\.mobile-menu-overlay[^{]*\{[^}]*\}",
    r"\.mobile-menu-overlay\.open[^{]*\{[^}]*\}",
    r"body\.menu-open[^{]*\{[^}]*\}",
    r"footer\s*\{[^}]*\}",
    r"\.footer-top[^{]*\{[^}]*\}",
    r"\.footer-mark[^{]*\{[^}]*\}",
    r"\.footer-mark\s+em[^{]*\{[^}]*\}",
    r"\.footer-bio[^{]*\{[^}]*\}",
    r"\.footer-col\s+h4[^{]*\{[^}]*\}",
    r"\.footer-col\s+ul[^{]*\{[^}]*\}",
    r"\.footer-col\s+li[^{]*\{[^}]*\}",
    r"\.footer-col\s+a[^{]*\{[^}]*\}",
    r"\.footer-col\s+a:hover[^{]*\{[^}]*\}",
    r"\.footer-bottom[^{]*\{[^}]*\}",
]

def extract_title(html):
    m = re.search(r"<title>(.*?)</title>", html, re.DOTALL)
    return m.group(1).strip() if m else ""

def extract_description(html):
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html)
    return m.group(1) if m else ""

def extract_og_tags(html):
    tags = {}
    for prop, key in [("og:title","ogTitle"),("og:description","ogDescription"),
                      ("og:image","ogImage"),("og:type","ogType")]:
        m = re.search(rf'<meta\s+property="{prop}"\s+content="([^"]*)"', html)
        if m:
            val = m.group(1)
            if key == "ogImage" and val.startswith("https://elitecleanpro.ca"):
                val = val.replace("https://elitecleanpro.ca", "")
            tags[key] = val
    return tags

def extract_json_ld(html):
    blocks = re.findall(
        r'<script\s+type="application/ld\+json">(.*?)</script>',
        html, re.DOTALL
    )
    return blocks

def extract_page_styles(html):
    """Pull <style>...</style>, strip shared rules, return only page-specific CSS."""
    m = re.search(r"<style>(.*?)</style>", html, re.DOTALL)
    if not m:
        return ""
    css = m.group(1)

    for pattern in SHARED_CSS_RULES:
        css = re.sub(pattern, "", css, flags=re.DOTALL)

    # Clean up: collapse 3+ blank lines, strip whitespace
    css = re.sub(r"\n\s*\n\s*\n+", "\n\n", css)
    return css.strip()

def extract_page_body(html):
    """Get body content, stripping skip-link, ticker, nav, mobile menu, footer, scripts."""
    m = re.search(r"<body[^>]*>(.*?)</body>", html, re.DOTALL)
    if not m:
        return ""
    body = m.group(1)

    # Strip skip link
    body = re.sub(r'<a[^>]*class="skip-link"[^>]*>.*?</a>', "", body, flags=re.DOTALL)
    # Strip ticker
    body = re.sub(r'<div\s+class="ticker-strip"[^>]*>.*?</div>\s*(?=<)', "", body, flags=re.DOTALL)
    # Strip <nav class="main"> ... </nav> (only the main nav, not jump-navs)
    body = re.sub(
        r'<nav\s+class="main"[^>]*>.*?</nav>',
        "", body, flags=re.DOTALL
    )
    # Strip mobile menu overlay and aside
    body = re.sub(r'<div\s+class="mobile-menu-overlay"[^>]*></div>', "", body)
    body = re.sub(r'<aside\s+class="mobile-menu"[^>]*>.*?</aside>', "", body, flags=re.DOTALL)
    # Strip footer
    body = re.sub(r'<footer[^>]*>.*?</footer>', "", body, flags=re.DOTALL)
    # Strip the shared scripts at end of body (mobile menu, clock, year, scroll)
    body = re.sub(
        r'<script>\s*(?://[^\n]*\n)?\s*\(?function\(\)\s*\{.*?</script>\s*$',
        "", body, flags=re.DOTALL
    )
    # Catch any remaining trailing <script> blocks that are just IIFEs
    body = re.sub(
        r'<script>(?:[^<]|<(?!/script>))*</script>\s*$',
        "", body, flags=re.DOTALL
    )

    return body.strip()

def yaml_escape(s):
    """Escape a string for YAML single-line value."""
    if not s:
        return '""'
    # If contains special chars, wrap in single quotes and escape internal quotes
    if any(c in s for c in [':','#','"',"'",'\n']):
        return "'" + s.replace("'", "''") + "'"
    return s

def build_njk(src_file, dest_file):
    html = src_file.read_text()

    title = extract_title(html)
    description = extract_description(html)
    og_tags = extract_og_tags(html)
    json_ld_blocks = extract_json_ld(html)
    page_css = extract_page_styles(html)
    page_body = extract_page_body(html)

    # Build frontmatter
    fm_lines = ["---"]
    fm_lines.append("layout: layouts/base.njk")
    fm_lines.append(f"title: {yaml_escape(title)}")
    if description:
        fm_lines.append(f"description: {yaml_escape(description)}")
    for k, v in og_tags.items():
        fm_lines.append(f"{k}: {yaml_escape(v)}")

    # JSON-LD goes in extraHead so it lands in <head>
    if json_ld_blocks:
        fm_lines.append("extraHead: |")
        for block in json_ld_blocks:
            fm_lines.append('  <script type="application/ld+json">')
            for line in block.strip().split("\n"):
                fm_lines.append(f"  {line}")
            fm_lines.append("  </script>")

    fm_lines.append("---")
    frontmatter = "\n".join(fm_lines)

    # Build body — inline style block (page-specific only) + content
    parts = [frontmatter, ""]
    if page_css:
        parts.append("<style>")
        parts.append(page_css)
        parts.append("</style>")
        parts.append("")
    parts.append(page_body)

    out = "\n".join(parts) + "\n"
    dest_file.write_text(out)
    return len(page_css), len(page_body)

def main():
    DEST_DIR.mkdir(parents=True, exist_ok=True)
    print(f"{'Page':<30} {'CSS chars':>10} {'Body chars':>11}")
    print("─" * 55)
    for page in PAGES:
        src = SOURCE_DIR / page
        if not src.exists():
            print(f"  ⚠  {page} not found, skipping")
            continue
        dest = DEST_DIR / (page.replace(".html", ".njk"))
        css_len, body_len = build_njk(src, dest)
        print(f"  {page:<28} {css_len:>10,} {body_len:>11,}")
    print()
    print("✓ Migration complete")

if __name__ == "__main__":
    main()
