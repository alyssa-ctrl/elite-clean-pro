#!/usr/bin/env python3
"""
Wire Google Calendar booking links into the site.

What this does:
  1. Updates src/_data/site.json — adds bookingLinks object (keeps existing fields)
  2. Adds src/book.njk — the /book/ chooser landing page
  3. Repoints booking links across all pages:
     - homepage and shared partials → /book/ (chooser)
     - /residential/ page → residential booking URL via {{ site.bookingLinks.residential }}
     - /commercial/ page → commercial URL
     - /move-out-cleaning/ → moveOut URL
     - /pricing/ → /book/ (since pricing covers all services)
     - other pages → /book/

After running, the booking URLs are placeholders. Edit src/_data/site.json
to swap in real Google Calendar URLs when you have them, then rebuild and push.

Idempotent: safe to run twice.
"""

import json
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path.home() / 'Desktop' / 'elite-clean-pro'

if not (ROOT / 'src' / 'index.njk').exists():
    print('ERROR: ' + str(ROOT) + ' is not the project root')
    sys.exit(1)

# ────────────────────────────────────────────────────────────────
# 1. Update site.json with bookingLinks
# ────────────────────────────────────────────────────────────────
site_json = ROOT / 'src' / '_data' / 'site.json'
site = json.loads(site_json.read_text())

if 'bookingLinks' not in site:
    site['bookingLinks'] = {
        'chooser':     '/book/',
        'residential': 'https://calendar.app.google/REPLACE_RESIDENTIAL_LINK',
        'commercial':  'https://calendar.app.google/REPLACE_COMMERCIAL_LINK',
        'moveOut':     'https://calendar.app.google/REPLACE_MOVEOUT_LINK',
        'consult':     'https://calendar.app.google/REPLACE_CONSULT_LINK',
    }
    site_json.write_text(json.dumps(site, indent=2) + '\n')
    print('Updated site.json: added bookingLinks (with placeholder URLs)')
else:
    print('site.json already has bookingLinks (leaving as-is)')

# ────────────────────────────────────────────────────────────────
# 2. The /book/ chooser page — copied from the bundled book.njk
# ────────────────────────────────────────────────────────────────
script_dir = pathlib.Path(__file__).parent
bundled_book = script_dir / 'book.njk'
dest_book = ROOT / 'src' / 'book.njk'

if dest_book.exists():
    print('src/book.njk already exists (leaving as-is)')
elif bundled_book.exists():
    shutil.copy(bundled_book, dest_book)
    print('Created src/book.njk (chooser landing page)')
else:
    print('WARNING: book.njk not found next to this script. Skipping page creation.')
    print('         Make sure both files are in the same folder before running.')

# ────────────────────────────────────────────────────────────────
# 3. Rewire booking links across all pages
# ────────────────────────────────────────────────────────────────
# Mapping: page filename -> where its booking links should go
# Use Nunjucks variable so future URL changes happen in site.json only
PAGE_TARGETS = {
    'residential.njk':       '{{ site.bookingLinks.residential }}',
    'commercial.njk':        '{{ site.bookingLinks.commercial }}',
    'move-out-cleaning.njk': '{{ site.bookingLinks.moveOut }}',
    # Everything else routes to the chooser
}
DEFAULT_TARGET = '/book/'

# Patterns to replace — match href="#book" or href="#quote" only
# (we don't want to break in-page anchors that aren't booking links)
patterns = [
    re.compile(r'href="#book"'),
    re.compile(r"href='#book'"),
    re.compile(r'href="#quote"'),
    re.compile(r"href='#quote'"),
]

# Also matches when href is followed by additional attributes — re-anchor the URL
def rewire_file(path, target):
    text = path.read_text()
    original = text
    count = 0
    for p in patterns:
        new_text, n = p.subn('href="' + target + '"', text)
        count += n
        text = new_text
    if count > 0:
        path.write_text(text)
    return count

src_dir = ROOT / 'src'
total_changes = 0
for njk in sorted(src_dir.glob('*.njk')):
    target = PAGE_TARGETS.get(njk.name, DEFAULT_TARGET)
    changes = rewire_file(njk, target)
    if changes:
        print('  ' + njk.name + ': rewired ' + str(changes) + ' booking link(s) → ' + target)
    total_changes += changes

# Also rewire the shared CTA partial that's on every page
cta_partial = ROOT / 'src' / '_includes' / 'partials' / 'book-cta.njk'
if cta_partial.exists():
    changes = rewire_file(cta_partial, DEFAULT_TARGET)
    if changes:
        print('  book-cta.njk: rewired ' + str(changes) + ' booking link(s) → /book/')
    total_changes += changes

# Rewire the header partial too (the "Book Now" button in the nav)
header_partial = ROOT / 'src' / '_includes' / 'partials' / 'header.njk'
if header_partial.exists():
    changes = rewire_file(header_partial, DEFAULT_TARGET)
    if changes:
        print('  header.njk: rewired ' + str(changes) + ' booking link(s) → /book/')
    total_changes += changes

print('')
print('Total booking links rewired: ' + str(total_changes))
print('')
print('NEXT STEPS:')
print('  1. Run: npm run build')
print('  2. Test locally: open localhost:8080/book/ to see the chooser page')
print('  3. When you have real Google Calendar URLs:')
print('     edit src/_data/site.json and replace the four REPLACE_* placeholder URLs')
print('  4. Rebuild and push: git add -A && git commit -m "Wire Google Calendar booking" && git push origin main')
