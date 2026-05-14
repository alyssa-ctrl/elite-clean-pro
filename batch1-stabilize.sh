#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# Elite Clean Pro — Stabilization Batch 1
# Fixes three things across all pages:
#   1. Clock: 9 subpages use local browser time; switch to America/Edmonton
#   2. Dead code: remove orphan updateTime() in index.html (targets non-existent #now-time)
#   3. Meta theme-color: replace invalid `var(--paper)` with literal #F1F1F1
#
# Idempotent: safe to run twice. Will report "already fixed" if so.
# Read-only on git; only edits .html files in current directory.
# To revert: `git checkout .` before committing.
# ─────────────────────────────────────────────────────────────

set -e

REPO_ROOT="$(pwd)"
echo "Running in: $REPO_ROOT"
echo ""

# Sanity: must be in repo root with at least index.html
if [ ! -f "index.html" ]; then
  echo "ERROR: index.html not found. cd to your repo root first."
  exit 1
fi

# ─────────────────────────────────────────────────────────────
# FIX 1 — Clock function: 9 subpages
# Replace the local-time clock with America/Edmonton-locked version.
# ─────────────────────────────────────────────────────────────

echo "━━━ FIX 1: Clock function (timezone lock) ━━━"

SUBPAGES=(
  "residential.html"
  "commercial.html"
  "the-standard.html"
  "faq.html"
  "biosmart.html"
  "quality-reporting.html"
  "about.html"
  "move-out-cleaning.html"
  "promise.html"
)

for f in "${SUBPAGES[@]}"; do
  if [ ! -f "$f" ]; then
    echo "  ⚠️  $f not found, skipping"
    continue
  fi

  # Check if already fixed
  if grep -q "America/Edmonton" "$f"; then
    echo "  $f: already timezone-locked"
    continue
  fi

  # Use python for the multi-line replace — safer than sed
  python3 - "$f" <<'PYEOF'
import sys
import re

path = sys.argv[1]
with open(path) as fh:
    content = fh.read()

# Match the old clock function (with or without surrounding (function(){...})())
# Old shape:
#   var d = new Date();
#   var h = d.getHours(), m = d.getMinutes();
#   var hh = (h < 10 ? '0' : '') + h;
#   var mm = (m < 10 ? '0' : '') + m;
#   el.textContent = hh + ':' + mm + ' MT';

new_body = """    var opts = { timeZone: 'America/Edmonton', hour: '2-digit', minute: '2-digit', hour12: false };
    el.textContent = new Date().toLocaleTimeString('en-CA', opts) + ' MT';"""

pattern = re.compile(
    r"    var d = new Date\(\);\s*\n"
    r"    var h = d\.getHours\(\), m = d\.getMinutes\(\);\s*\n"
    r"    var hh = \(h < 10 \? '0' : ''\) \+ h;\s*\n"
    r"    var mm = \(m < 10 \? '0' : ''\) \+ m;\s*\n"
    r"    el\.textContent = hh \+ ':' \+ mm \+ ' MT';"
)

new_content, n = pattern.subn(new_body, content)

if n == 0:
    print(f"  ⚠️  Could not match clock pattern in {path}")
    sys.exit(1)

with open(path, 'w') as fh:
    fh.write(new_content)

print(f"  ✓ {path}: replaced {n} clock function")
PYEOF
done

echo ""

# ─────────────────────────────────────────────────────────────
# FIX 2 — Remove dead orphan clock function in index.html
# It targets #now-time which doesn't exist (homepage uses #ticker-clock)
# ─────────────────────────────────────────────────────────────

echo "━━━ FIX 2: Remove dead orphan clock in index.html ━━━"

python3 - <<'PYEOF'
import re

path = "index.html"
with open(path) as fh:
    content = fh.read()

# The orphan function. We identify it by the unique combination:
# - function updateTime() {  (NOT inside an IIFE — bare top-level)
# - targets getElementById('now-time')
# - homepage actually has #ticker-clock, so this targets nothing
#
# The working homepage clock is a different function lower in the file
# that targets #ticker-clock.

# Match the orphan block precisely
orphan_pattern = re.compile(
    r"// — Live time in masthead —\s*\n"
    r"function updateTime\(\) \{\s*\n"
    r"  const now = new Date\(\);\s*\n"
    r"  const opts = \{ timeZone: 'America/Edmonton', hour: '2-digit', minute: '2-digit', hour12: false \};\s*\n"
    r"  const time = now\.toLocaleTimeString\('en-CA', opts\);\s*\n"
    r"  const el = document\.getElementById\('now-time'\);\s*\n"
    r"  if \(el\) el\.textContent = time \+ ' MT';\s*\n"
    r"\}\s*\n"
    r"updateTime\(\);\s*\n"
    r"setInterval\(updateTime, 30000\);\s*\n"
)

new_content, n = orphan_pattern.subn("", content)

if n == 0:
    # Try a looser fallback match
    fallback = re.compile(
        r"// — Live time in masthead —.*?setInterval\(updateTime, 30000\);\s*\n",
        re.DOTALL
    )
    new_content, n = fallback.subn("", content)

if n == 0:
    print(f"  ⚠️  No orphan clock found in index.html (may already be removed)")
else:
    # Verify we still have the working clock (targets #ticker-clock)
    if "getElementById('ticker-clock')" not in new_content:
        print(f"  ❌ ABORT: removing orphan would also remove working clock. Not saving.")
    else:
        with open(path, 'w') as fh:
            fh.write(new_content)
        print(f"  ✓ index.html: removed {n} dead orphan clock function")
PYEOF

echo ""

# ─────────────────────────────────────────────────────────────
# FIX 3 — Meta theme-color: replace var(--paper) with literal color
# Browsers ignore CSS variables in <meta>; this must be a real color.
# ─────────────────────────────────────────────────────────────

echo "━━━ FIX 3: Meta theme-color literal value ━━━"

for f in *.html; do
  if grep -q 'theme-color" content="var(--paper)"' "$f"; then
    sed -i.bak 's|theme-color" content="var(--paper)"|theme-color" content="#F1F1F1"|g' "$f"
    rm -f "$f.bak"
    echo "  ✓ $f: theme-color → #F1F1F1"
  fi
done

# Catch any that just say --paper with different quoting
for f in *.html; do
  if grep -q 'theme-color.*var(--paper)' "$f"; then
    sed -i.bak 's|var(--paper)|#F1F1F1|g' "$f"
    rm -f "$f.bak"
    echo "  ✓ $f: theme-color fallback fix"
  fi
done

echo ""

# ─────────────────────────────────────────────────────────────
# VERIFICATION
# ─────────────────────────────────────────────────────────────

echo "━━━ VERIFICATION ━━━"
echo ""
echo "Mountain TZ clock across all pages:"
for f in index.html residential.html commercial.html the-standard.html faq.html biosmart.html quality-reporting.html about.html move-out-cleaning.html promise.html pricing.html; do
  if [ -f "$f" ]; then
    count=$(grep -c "America/Edmonton" "$f" || echo 0)
    status="✓"
    [ "$count" -eq 0 ] && status="✗"
    printf "  %s %-30s %d ref(s)\n" "$status" "$f" "$count"
  fi
done

echo ""
echo "Local-time (d.getHours) leftovers (should all be 0):"
leftovers=0
for f in *.html; do
  if grep -q "d\.getHours()" "$f"; then
    echo "  ✗ $f: still has local-time clock"
    leftovers=$((leftovers + 1))
  fi
done
[ "$leftovers" -eq 0 ] && echo "  ✓ none found"

echo ""
echo "Invalid theme-color (should all be 0):"
invalid=0
for f in *.html; do
  if grep -q 'theme-color.*var(--' "$f"; then
    echo "  ✗ $f: invalid theme-color"
    invalid=$((invalid + 1))
  fi
done
[ "$invalid" -eq 0 ] && echo "  ✓ none found"

echo ""
echo "━━━ DONE ━━━"
echo ""
echo "Next steps:"
echo "  1. git diff --stat              (see what changed)"
echo "  2. git diff index.html          (review dead-code removal)"
echo "  3. If anything looks wrong:  git checkout ."
echo "  4. If good:"
echo "       git add -A"
echo "       git commit -m 'Lock clock to Mountain Time, remove dead code, fix theme-color meta'"
echo "       git push origin main"
