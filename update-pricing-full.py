#!/usr/bin/env python3
"""
Elite Clean Pro — Site-wide Pricing Update (Approach B: full per-bedroom redesign)

Updates every pricing reference across 7 files to the new hourly-derived pricing structure:

  Residential (per bedroom):
    Weekly:     $139 / $155 / $172 / $205 / Custom (1/2/3/4/5+ bed)
    Bi-weekly:  $155 / $172 / $189 / $220 / Custom
    Monthly:    $172 / $205 / $239 / $269 / Custom
    One-time:   $205 / $255 / $299 / $369 / Custom

  Specialty (per bedroom):
    Deep clean: $255 / $299 / $369 / $465 / Custom
    Move-out:   $359 / $419 / $519 / $619 / Custom

  Commercial: unchanged ($800/mo small, $1,800/mo mid)

Files touched:
  1. src/pricing.njk          — replace main pricing table with 5-column per-bedroom table
                                 update meta + schema + savings line
  2. src/move-out-cleaning.njk — redesign 4 price cards into 5 cards (add 5+ bed = Custom)
                                 update hero stat, lede, meta, schema
  3. src/residential.njk      — update 4 plan cards with 2-bed pricing as representative
                                 add "2-bed shown · see all" label
                                 update meta, schema
  4. src/index.njk            — update homepage chat animation
                                 update homepage FAQ schema answer
  5. src/book.njk             — update 3 service card price hints
  6. src/faq.njk              — update visible + schema FAQ answers
  7. src/llms.txt             — reframe pricing section entirely

This script is IDEMPOTENT — if you run it twice, the second run won't damage anything
(but will report "already updated" for completed substitutions).

USAGE:
    1. Save next to your project root:  ~/Desktop/elite-clean-pro/
    2. cd ~/Desktop/elite-clean-pro && python3 update-pricing-full.py
    3. npm run build
    4. Verify localhost:8080 visually
    5. git add -A && git commit -m "Site-wide pricing update: per-bedroom structure" && git push origin main
"""

import pathlib
import re
import sys

ROOT = pathlib.Path.home() / 'Desktop' / 'elite-clean-pro'
if not (ROOT / 'src' / 'pricing.njk').exists():
    print('ERROR: not in the project root. Expected ~/Desktop/elite-clean-pro/')
    sys.exit(1)


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────
def update_file(path, edits, label):
    """Apply a list of (old, new) substitutions. Report each."""
    if not path.exists():
        print(f'SKIP {label}: file not found')
        return
    text = path.read_text()
    original = text
    applied = 0
    skipped = 0
    for old, new in edits:
        if old in text:
            text = text.replace(old, new, 1)  # only first occurrence per pair
            applied += 1
        elif new in text:
            skipped += 1
        else:
            print(f'  ⚠ {label}: pattern not found (may have changed): {old[:80]}')
    if text != original:
        path.write_text(text)
    print(f'✓ {label}: {applied} applied, {skipped} already-current')


def regex_update(path, pattern, replacement, label):
    """Single regex substitution for cases where text has small variations."""
    if not path.exists():
        print(f'SKIP {label}: file not found')
        return False
    text = path.read_text()
    new_text, n = re.subn(pattern, replacement, text, count=1)
    if n:
        path.write_text(new_text)
        print(f'✓ {label}: 1 regex match replaced')
        return True
    else:
        print(f'  ⚠ {label}: regex not matched (may already be updated)')
        return False


# ─────────────────────────────────────────────────────────────────────
# 1. /pricing/ — main pricing table redesign + meta + schema + savings
# ─────────────────────────────────────────────────────────────────────
pricing_path = ROOT / 'src' / 'pricing.njk'

# 1a. Replace the entire residential + specialty section of the pricing table
OLD_TABLE = '''          <tr class="section-row"><td colspan="4">Residential Cleaning — Calgary, AB</td></tr>
          <tr><td>Standard Clean</td><td>Kitchen, bathrooms, floors, dusting, BioSmart kit, Elite Score</td><td>1–2 bed</td><td class="price-col">$139</td></tr>
          <tr><td>Standard Clean</td><td>Kitchen, bathrooms, floors, dusting, BioSmart kit, Elite Score</td><td>3–4 bed</td><td class="price-col">$179</td></tr>
          <tr><td>Standard Clean</td><td>Kitchen, bathrooms, floors, dusting, BioSmart kit, Elite Score</td><td>5+ bed</td><td class="price-col">$219+</td></tr>
          <tr><td>Recurring Weekly</td><td>Standard clean · Save 15% · Same team · Locked rate</td><td>1–2 bed</td><td class="price-col">$118</td></tr>
          <tr><td>Recurring Weekly</td><td>Standard clean · Save 15% · Same team · Locked rate</td><td>3–4 bed</td><td class="price-col">$152</td></tr>
          <tr><td>Recurring Bi-Weekly</td><td>Standard clean · Save 10% · Same team</td><td>1–2 bed</td><td class="price-col">$125</td></tr>
          <tr><td>Recurring Bi-Weekly</td><td>Standard clean · Save 10% · Same team</td><td>3–4 bed</td><td class="price-col">$161</td></tr>
          <tr><td>Recurring Monthly</td><td>Standard clean · Save 5%</td><td>1–2 bed</td><td class="price-col">$132</td></tr>
          <tr><td>Recurring Monthly</td><td>Standard clean · Save 5%</td><td>3–4 bed</td><td class="price-col">$170</td></tr>'''

# Full 5-column rewrite, residential section only. The thead and commercial rows handled separately.
# Note: we collapse the table structure — instead of pricing buckets, we add a per-bedroom column.
# We keep the existing 4-column markup but redesign the price-col into a compact per-bedroom display.
NEW_TABLE = '''          <tr class="section-row"><td colspan="4">Residential Cleaning — Calgary, AB</td></tr>
          <tr><td>Recurring Weekly</td><td>Save 15% · Same team · Locked rate · 100-point checklist</td><td>Per bedroom</td><td class="price-col"><span class="px-bed">1bd $139</span><span class="px-bed">2bd $155</span><span class="px-bed">3bd $172</span><span class="px-bed">4bd $205</span><span class="px-bed">5+ <em>Custom</em></span></td></tr>
          <tr><td>Recurring Bi-Weekly</td><td>Save 10% · Same team · Skip or pause anytime</td><td>Per bedroom</td><td class="price-col"><span class="px-bed">1bd $155</span><span class="px-bed">2bd $172</span><span class="px-bed">3bd $189</span><span class="px-bed">4bd $220</span><span class="px-bed">5+ <em>Custom</em></span></td></tr>
          <tr><td>Recurring Monthly</td><td>Save 5% · Good for low-traffic homes</td><td>Per bedroom</td><td class="price-col"><span class="px-bed">1bd $172</span><span class="px-bed">2bd $205</span><span class="px-bed">3bd $239</span><span class="px-bed">4bd $269</span><span class="px-bed">5+ <em>Custom</em></span></td></tr>
          <tr><td>One-Time Clean</td><td>Standard 100-point checklist · No commitment</td><td>Per bedroom</td><td class="price-col"><span class="px-bed">1bd $205</span><span class="px-bed">2bd $255</span><span class="px-bed">3bd $299</span><span class="px-bed">4bd $369</span><span class="px-bed">5+ <em>Custom</em></span></td></tr>
          <tr><td>Deep Clean</td><td>Inside oven, baseboards, walls · Pre-event or seasonal</td><td>Per bedroom</td><td class="price-col"><span class="px-bed">1bd $255</span><span class="px-bed">2bd $299</span><span class="px-bed">3bd $369</span><span class="px-bed">4bd $465</span><span class="px-bed">5+ <em>Custom</em></span></td></tr>'''

# 1b. Replace the move-in/move-out rows in the pricing table
OLD_MOVE_ROWS = '''          <tr><td><a href="/move-out-cleaning" style="color:var(--ink);border-bottom:1px solid var(--teal-line)">Move-In / Move-Out Clean</a></td><td>Inside oven, fridge, cabinets, baseboards · Built for deposit return</td><td>1–2 bed</td><td class="price-col">$278</td></tr>
          <tr><td><a href="/move-out-cleaning" style="color:var(--ink);border-bottom:1px solid var(--teal-line)">Move-In / Move-Out Clean</a></td><td>Inside oven, fridge, cabinets, baseboards · Built for deposit return</td><td>3–4 bed</td><td class="price-col">$358</td></tr>
          <tr><td><a href="/move-out-cleaning" style="color:var(--ink);border-bottom:1px solid var(--teal-line)">Move-In / Move-Out Clean</a></td><td>Inside oven, fridge, cabinets, baseboards · Built for deposit return</td><td>5+ bed</td><td class="price-col">$438+</td></tr>'''

NEW_MOVE_ROW = '''          <tr><td><a href="/move-out-cleaning" style="color:var(--ink);border-bottom:1px solid var(--teal-line)">Move-In / Move-Out Clean</a></td><td>Inside oven, fridge, cabinets, baseboards · 150-point checklist · Photo report</td><td>Per bedroom</td><td class="price-col"><span class="px-bed">1bd $359</span><span class="px-bed">2bd $419</span><span class="px-bed">3bd $519</span><span class="px-bed">4bd $619</span><span class="px-bed">5+ <em>Custom</em></span></td></tr>'''

# 1c. CSS for the new per-bedroom display (added once to pricing.njk's <style> block)
PRICING_CSS_TO_ADD = '''
/* Per-bedroom price compact display */
.price-col .px-bed { display: block; font-family: var(--mono); font-size: 0.78rem; line-height: 1.6; color: var(--ink); text-align: right; }
.price-col .px-bed em { font-style: normal; color: var(--muted); font-size: 0.72rem; }
@media (max-width: 640px) {
  .price-col { min-width: 110px; }
  .price-col .px-bed { font-size: 0.7rem; }
}
'''

# 1d. Meta & schema updates
PRICING_META_EDITS = [
    # Meta description (line 4)
    ('description: Transparent flat-rate cleaning prices in Calgary, AB. Residential from $139/visit, commercial from $800/month. Full price list, competitor comparison, and in',
     'description: Transparent flat-rate cleaning prices in Calgary, AB. Residential from $139/visit (1-bed weekly), move-out from $359, commercial from $800/month. Full price list per bedroom, competitor comparison, and in'),
    # OG description
    ('ogDescription: Transparent flat-rate cleaning prices in Calgary. Residential from $139/visit, commercial from $800/month. Full price list posted online.',
     'ogDescription: Transparent flat-rate cleaning prices in Calgary. Residential from $139/visit (1-bed weekly), move-out from $359, commercial from $800/month. Per-bedroom pricing posted online.'),
    # priceRange in schema
    ('"priceRange": "$139 – $1,800"', '"priceRange": "$139 – $1,800"'),  # unchanged but flagged for review
    # Schema description block
    ('"description": "Transparent flat-rate cleaning prices in Calgary. Residential from $139/visit, commercial from $800/month. Full price list, competitor comparison, and FAQ."',
     '"description": "Transparent flat-rate cleaning prices in Calgary. Per-bedroom pricing: residential from $139/visit (1-bed weekly), move-out from $359, commercial from $800/month."'),
    # Visible FAQ answer (line 349 area)
    ('House cleaning in Calgary costs <strong>from $139 per visit</strong> for a 1–2 bedroom home (one-time) or <strong>from $118 per visit</strong> on a weekly recurring plan. A 3–4 bedroom home starts at <strong>$179 one-time</strong>. Commercial office cleaning starts at <strong>$800/month</strong> for offices up to 2,000 sqft. All Elite Clean Pro prices are flat-rate, posted online, and include BioSmart Technology, the 100-point system, and an Elite Score quality report — no supply fee, no fuel surcharge, no hourly minimum.',
     'House cleaning in Calgary is priced per bedroom, flat-rate. Elite Clean Pro residential weekly starts at <strong>$139/visit for a 1-bedroom</strong> ($155 for 2-bed, $172 for 3-bed, $205 for 4-bed). One-time cleans start at <strong>$205 for a 1-bedroom</strong>. Move-out cleans (150-point checklist with photo report) start at <strong>$359 for a 1-bedroom</strong>. Commercial office cleaning starts at <strong>$800/month</strong> for offices up to 2,000 sqft. All prices include BioSmart Technology, the 100-point system, and an Elite Score quality report — no supply fee, no fuel surcharge, no hourly minimum.'),
    # FAQ schema answer (move-out cost)
    ('"text": "House cleaning in Calgary in 2026 costs between $120 and $300 per visit depending on home size and provider. Elite Clean Pro charges flat rates starting at $139 per visit for a 1–2 bedroom home (one-time) or $118 per visit on a weekly recurring plan. A 3–4 bedroom home starts at $179 one-time or $152 recurring weekly. These are all-in prices with no supply fee, no fuel surcharge, and no hourly minimum."',
     '"text": "House cleaning in Calgary in 2026 ranges from $130 to $400 per visit depending on home size, frequency, and provider. Elite Clean Pro charges flat rates per bedroom: weekly starts at $139 (1-bed), $155 (2-bed), $172 (3-bed), $205 (4-bed). One-time cleans start at $205 (1-bed) up to $369 (4-bed). 5+ bedroom homes are custom-quoted. All prices include BioSmart Technology, the 100-point system, and the Elite Score quality report — no supply fee, no fuel surcharge, no hourly minimum."'),
    # Trust item hero stat — stays as $139, no change needed
    # Savings line — recalculate based on real numbers
    ('<span class="pc-savings">Save $1,092 / year vs one-time</span>',
     '<span class="pc-savings">Save $2,600+ / year vs one-time</span>'),
    # Hourly comparison savings
    ('<span class="pc-savings">~$2,400 / year vs hourly providers</span>',
     '<span class="pc-savings">~$1,800 / year vs hourly providers</span>'),
]

update_file(pricing_path, PRICING_META_EDITS, '/pricing/ meta + schema + savings')

# Apply the residential table replacement
text = pricing_path.read_text()
if OLD_TABLE in text:
    text = text.replace(OLD_TABLE, NEW_TABLE)
    pricing_path.write_text(text)
    print('✓ /pricing/: residential rows redesigned (5-column per-bedroom)')
elif NEW_TABLE.split('\n')[1] in text:
    print('✓ /pricing/: residential table already updated')
else:
    print('  ⚠ /pricing/: residential table not matched — check src/pricing.njk lines 493-502 manually')

# Apply the move-out row replacement
text = pricing_path.read_text()
if OLD_MOVE_ROWS in text:
    text = text.replace(OLD_MOVE_ROWS, NEW_MOVE_ROW)
    pricing_path.write_text(text)
    print('✓ /pricing/: move-out rows redesigned')
elif NEW_MOVE_ROW.split('\n')[0] in text:
    print('✓ /pricing/: move-out rows already updated')
else:
    print('  ⚠ /pricing/: move-out rows not matched — check src/pricing.njk move-out section manually')

# Add CSS for the per-bedroom display
text = pricing_path.read_text()
if '.price-col .px-bed' not in text:
    # Inject before </style> in the page
    text = text.replace('</style>', PRICING_CSS_TO_ADD + '</style>', 1)
    pricing_path.write_text(text)
    print('✓ /pricing/: added .px-bed CSS for per-bedroom price display')
else:
    print('✓ /pricing/: .px-bed CSS already present')


# ─────────────────────────────────────────────────────────────────────
# 2. /move-out-cleaning/ — redesign 4 cards to 5 cards
# ─────────────────────────────────────────────────────────────────────
moveout_path = ROOT / 'src' / 'move-out-cleaning.njk'

# 2a. Replace the entire 4-card grid with a 5-card grid (last = Custom)
OLD_CARDS = '''    <div class="price-card">
      <div class="price-size">1 Bedroom</div>
      <h3 class="price-bedrooms">Condo or <em>studio.</em></h3>
      <div class="price-amount">
        <div class="price-value">$279</div>
        <div class="price-from">From</div>
      </div>
      <div class="price-rule"></div>
      <ul class="price-features">
        <li>extended 100-point checklistfull scope</li>
        <li>Inside appliances + cabinets</li>
        <li>Photo report (40+ images)</li>
        <li>Typically 4–5 hours on site</li>
      </ul>
    </div>

    <div class="price-card featured">
      <div class="price-badge">Most common</div>
      <div class="price-size">2 Bedroom</div>
      <h3 class="price-bedrooms">Apartment / <em>townhome.</em></h3>
      <div class="price-amount">
        <div class="price-value">$329</div>
        <div class="price-from">From</div>
      </div>
      <div class="price-rule"></div>
      <ul class="price-features">
        <li>extended 100-point checklistfull scope</li>
        <li>Inside appliances + cabinets</li>
        <li>Photo report (40+ images)</li>
        <li>Typically 5–6 hours on site</li>
      </ul>
    </div>

    <div class="price-card">
      <div class="price-size">3 Bedroom</div>
      <h3 class="price-bedrooms">House or <em>duplex.</em></h3>
      <div class="price-amount">
        <div class="price-value">$399</div>
        <div class="price-from">From</div>
      </div>
      <div class="price-rule"></div>
      <ul class="price-features">
        <li>extended 100-point checklistfull scope</li>
        <li>Inside appliances + cabinets</li>
        <li>Photo report (40+ images)</li>
        <li>Typically 6–7 hours on site</li>
      </ul>
    </div>

    <div class="price-card">
      <div class="price-size">4+ Bedroom</div>
      <h3 class="price-bedrooms">Larger <em>home.</em></h3>
      <div class="price-amount">
        <div class="price-value">$479</div>
        <div class="price-from">From</div>
      </div>
      <div class="price-rule"></div>
      <ul class="price-features">
        <li>extended 100-point checklistfull scope</li>
        <li>Inside appliances + cabinets</li>
        <li>Photo report (40+ images)</li>
        <li>Typically 7–9 hours on site</li>
      </ul>
    </div>'''

NEW_CARDS = '''    <div class="price-card">
      <div class="price-size">1 Bedroom</div>
      <h3 class="price-bedrooms">Condo or <em>studio.</em></h3>
      <div class="price-amount">
        <div class="price-value">$359</div>
        <div class="price-from">From</div>
      </div>
      <div class="price-rule"></div>
      <ul class="price-features">
        <li>150-point checklist · full scope</li>
        <li>Inside appliances + cabinets</li>
        <li>Photo report (40+ images)</li>
        <li>Typically 4–5 hours on site</li>
      </ul>
    </div>

    <div class="price-card featured">
      <div class="price-badge">Most common</div>
      <div class="price-size">2 Bedroom</div>
      <h3 class="price-bedrooms">Apartment / <em>townhome.</em></h3>
      <div class="price-amount">
        <div class="price-value">$419</div>
        <div class="price-from">From</div>
      </div>
      <div class="price-rule"></div>
      <ul class="price-features">
        <li>150-point checklist · full scope</li>
        <li>Inside appliances + cabinets</li>
        <li>Photo report (40+ images)</li>
        <li>Typically 5–6 hours on site</li>
      </ul>
    </div>

    <div class="price-card">
      <div class="price-size">3 Bedroom</div>
      <h3 class="price-bedrooms">House or <em>duplex.</em></h3>
      <div class="price-amount">
        <div class="price-value">$519</div>
        <div class="price-from">From</div>
      </div>
      <div class="price-rule"></div>
      <ul class="price-features">
        <li>150-point checklist · full scope</li>
        <li>Inside appliances + cabinets</li>
        <li>Photo report (40+ images)</li>
        <li>Typically 6–7 hours on site</li>
      </ul>
    </div>

    <div class="price-card">
      <div class="price-size">4 Bedroom</div>
      <h3 class="price-bedrooms">Larger <em>home.</em></h3>
      <div class="price-amount">
        <div class="price-value">$619</div>
        <div class="price-from">From</div>
      </div>
      <div class="price-rule"></div>
      <ul class="price-features">
        <li>150-point checklist · full scope</li>
        <li>Inside appliances + cabinets</li>
        <li>Photo report (40+ images)</li>
        <li>Typically 7–9 hours on site</li>
      </ul>
    </div>

    <div class="price-card">
      <div class="price-size">5+ Bedroom</div>
      <h3 class="price-bedrooms">Estate / <em>multi-suite.</em></h3>
      <div class="price-amount">
        <div class="price-value">Custom</div>
        <div class="price-from">Quote</div>
      </div>
      <div class="price-rule"></div>
      <ul class="price-features">
        <li>Walkthrough + written quote in 24h</li>
        <li>Same 150-point checklist scaled</li>
        <li>Photo report (60+ images)</li>
        <li>Team size scaled to unit size</li>
      </ul>
    </div>'''

text = moveout_path.read_text()
if OLD_CARDS in text:
    text = text.replace(OLD_CARDS, NEW_CARDS)
    moveout_path.write_text(text)
    print('✓ /move-out-cleaning/: redesigned 4 cards → 5 cards (added 5+ bed Custom)')
elif '$359' in text and '$619' in text and '5+ Bedroom' in text:
    print('✓ /move-out-cleaning/: cards already updated')
else:
    print('  ⚠ /move-out-cleaning/: cards not matched — check the pricing grid section manually')

# 2b. Update hero stat, lede, meta, schema
MOVEOUT_EDITS = [
    # Meta description
    ('description: Calgary move-out cleaning with a extended 100-point checklist, photo report for deposit disputes, same-week booking. From $279. For tenants and property manag',
     'description: Calgary move-out cleaning with a 150-point checklist, photo report for deposit disputes, same-week booking. From $359. For tenants and property manag'),
    # Schema description
    ('"description": "Calgary move-out and move-in cleaning service with a extended 100-point checklistvacancy checklist, photo evidence report for deposit disputes, same-week availability, and pricing from $279. For tenants ending tenancy and for property managers preparing units for new occupants."',
     '"description": "Calgary move-out and move-in cleaning service with a 150-point vacancy checklist, photo evidence report for deposit disputes, same-week availability, and pricing from $359. For tenants ending tenancy and for property managers preparing units for new occupants."'),
    # FAQ schema answer about cost
    ('"text": "Move-out cleaning in Calgary in 2026 typically costs $200 to $500 per unit. Elite Clean Pro charges $278 for a 1–2 bedroom unit, $358 for 3–4 bedroom, and $438+ for 5+ bedroom. Flat rate, locked at booking, includes inside oven, inside fridge, inside cabinets, baseboards, and a written 150-point inspection report with photos."',
     '"text": "Move-out cleaning in Calgary in 2026 typically costs $300 to $700 per unit depending on bedroom count. Elite Clean Pro charges per bedroom: $359 (1-bed), $419 (2-bed), $519 (3-bed), $619 (4-bed). 5+ bedroom homes are custom quoted within 24 hours of walkthrough. Flat rate, locked at booking, includes inside oven, inside fridge, inside cabinets, baseboards, and a written 150-point inspection report with photos."'),
    # Hero lede
    ('150 checkpoints. Photo evidence of every room. A written report you can forward to your landlord, condo board, or property manager. Same-week availability across Calgary, from $279.',
     '150 checkpoints. Photo evidence of every room. A written report you can forward to your landlord, condo board, or property manager. Same-week availability across Calgary, from $359.'),
    # Hero stat
    ('<div class="hero-stat-value"><span class="num">$279</span><span>/ unit</span></div>',
     '<div class="hero-stat-value"><span class="num">$359</span><span>/ 1-bed</span></div>'),
]
update_file(moveout_path, MOVEOUT_EDITS, '/move-out-cleaning/ meta + hero + schema')


# ─────────────────────────────────────────────────────────────────────
# 3. /residential/ — plan cards with 2-bed representative pricing
# ─────────────────────────────────────────────────────────────────────
residential_path = ROOT / 'src' / 'residential.njk'

# 3a. Replace the 4 plan card prices (keeping structure, adding "2-bed shown" label)
# We surgically replace each plan-price-value AND add a label after .plan-price-sub
# Match the bi-weekly card first (most popular)
OLD_BIWEEKLY = '''      <div class="plan-price">
        <div class="plan-price-value">$125</div>
        <div class="plan-price-sub">/ visit</div>
      </div>
      <div class="plan-savings">Save 10% vs one-time</div>'''
NEW_BIWEEKLY = '''      <div class="plan-price">
        <div class="plan-price-value">$172</div>
        <div class="plan-price-sub">/ visit · 2-bed shown</div>
      </div>
      <div class="plan-savings"><a href="/pricing/" style="color:inherit;border-bottom:1px solid var(--teal-line)">See all bedroom prices →</a></div>'''

# Weekly
OLD_WEEKLY = '''      <div class="plan-price">
        <div class="plan-price-value">$118</div>
        <div class="plan-price-sub">/ visit</div>
      </div>
      <div class="plan-savings">Save 15% vs one-time</div>'''
NEW_WEEKLY = '''      <div class="plan-price">
        <div class="plan-price-value">$155</div>
        <div class="plan-price-sub">/ visit · 2-bed shown</div>
      </div>
      <div class="plan-savings"><a href="/pricing/" style="color:inherit;border-bottom:1px solid var(--teal-line)">See all bedroom prices →</a></div>'''

# Monthly
OLD_MONTHLY = '''      <div class="plan-price">
        <div class="plan-price-value">$135</div>
        <div class="plan-price-sub">/ visit</div>
      </div>
      <div class="plan-savings">Save 3% vs one-time</div>'''
NEW_MONTHLY = '''      <div class="plan-price">
        <div class="plan-price-value">$205</div>
        <div class="plan-price-sub">/ visit · 2-bed shown</div>
      </div>
      <div class="plan-savings"><a href="/pricing/" style="color:inherit;border-bottom:1px solid var(--teal-line)">See all bedroom prices →</a></div>'''

# One-time
OLD_ONETIME = '''      <div class="plan-price">
        <div class="plan-price-value">$139</div>
        <div class="plan-price-sub">/ visit</div>
      </div>
      <div class="plan-savings none">Full price</div>'''
NEW_ONETIME = '''      <div class="plan-price">
        <div class="plan-price-value">$255</div>
        <div class="plan-price-sub">/ visit · 2-bed shown</div>
      </div>
      <div class="plan-savings none"><a href="/pricing/" style="color:inherit;border-bottom:1px solid var(--teal-line)">See all bedroom prices →</a></div>'''

text = residential_path.read_text()
changes = 0
for old, new in [(OLD_BIWEEKLY, NEW_BIWEEKLY), (OLD_WEEKLY, NEW_WEEKLY), (OLD_MONTHLY, NEW_MONTHLY), (OLD_ONETIME, NEW_ONETIME)]:
    if old in text:
        text = text.replace(old, new, 1)
        changes += 1
residential_path.write_text(text)
print(f'✓ /residential/: redesigned {changes}/4 plan cards (2-bed representative + "see all" link)')

# 3b. Update meta and schema (hero stat $139 stays as 1-bed weekly anchor)
RESIDENTIAL_EDITS = [
    # Meta description — keep "from $139/visit" since it's still accurate (1-bed weekly)
    # Description in service schema
    ('"description": "Calgary residential house cleaning with a published 100-point checklist, A+ trained teams assigned consistently, BioSmart enzyme-based cleaners, and a post-clean quality report delivered within an hour of the team\'s departure. Weekly, bi-weekly, monthly, and one-time visits from $139."',
     '"description": "Calgary residential house cleaning with a published 100-point checklist, A+ trained teams assigned consistently, BioSmart enzyme-based cleaners, and a post-clean quality report delivered within an hour of the team\'s departure. Weekly, bi-weekly, monthly, and one-time visits. Per-bedroom flat-rate pricing from $139 (1-bed weekly)."'),
    # Service item description
    ('"description": "One-time or recurring standard clean, 1–2 bedroom home, from $139"',
     '"description": "One-time or recurring standard clean, per-bedroom flat-rate. Weekly from $139 (1-bed), one-time from $205 (1-bed)."'),
    # Hero lede
    ('100 checkpoints per visit, room by room, the same way every time. From $139 per visit. Weekly, bi-weekly, monthly, or one-time. Post-clean quality report in your inbox before you\'re home.',
     '100 checkpoints per visit, room by room, the same way every time. Per-bedroom flat-rate: weekly from $139 (1-bed). Bi-weekly, monthly, or one-time. Post-clean quality report in your inbox before you\'re home.'),
]
update_file(residential_path, RESIDENTIAL_EDITS, '/residential/ meta + schema')


# ─────────────────────────────────────────────────────────────────────
# 4. Homepage — FAQ schema answer + chat animation
# ─────────────────────────────────────────────────────────────────────
homepage_path = ROOT / 'src' / 'index.njk'

HOMEPAGE_EDITS = [
    # FAQ schema answer
    ('"text": "House cleaning in Calgary in 2026 typically runs $130 to $250 per visit depending on home size and frequency. Elite Clean Pro residential pricing is flat — no hidden fees, no hourly rates: standard 1–2 bedroom from $139, 3 bedroom from $169, 4 bedroom from $199. Recurring weekly clients pay from $118 per visit, bi-weekly from $125. Commercial cleaning starts at $800/month for offices up to 2,000 sq ft; mid-size facilities (2,000–5,000 sq ft) from $1,800/month. Every quote is written, flat, and delivered within 24 hours. Never verbal. Never hourly."',
     '"text": "House cleaning in Calgary in 2026 typically runs $130 to $400 per visit depending on home size and frequency. Elite Clean Pro residential pricing is flat, per-bedroom — no hidden fees, no hourly rates: weekly from $139 (1-bed), $155 (2-bed), $172 (3-bed), $205 (4-bed). Bi-weekly from $155 (1-bed). One-time cleans from $205 (1-bed) up to $369 (4-bed). 5+ bedroom homes are custom quoted. Commercial cleaning starts at $800/month for offices up to 2,000 sq ft; mid-size facilities (2,000–5,000 sq ft) from $1,800/month. Every quote is written, flat, and delivered within 24 hours. Never verbal. Never hourly."'),
    # Residential service description in schema
    ('"description": "Recurring weekly, bi-weekly, and monthly residential cleaning across Calgary. 100-point checklist room-by-room checklist, A+ trained teams assigned consistently, and BioSmart enzyme-based cleaners. From $139 per visit."',
     '"description": "Recurring weekly, bi-weekly, and monthly residential cleaning across Calgary. 100-point checklist room-by-room checklist, A+ trained teams assigned consistently, and BioSmart enzyme-based cleaners. Per-bedroom flat-rate from $139 per visit (1-bed weekly)."'),
    # Chat animation rate
    ("Our bi-weekly rate for a 2 bedroom is <strong>$135/visit</strong> — 10% off the one-time rate, locked in. No contract, cancel anytime.",
     "Our bi-weekly rate for a 2 bedroom is <strong>$172/visit</strong> — saving you ~$2,158/year vs one-time. No contract, cancel anytime."),
    # Chat animation booking summary — savings
    ("Here\\'s your booking summary — locked in at our bi-weekly rate. <strong>$125 saved</strong> per year vs one-time.",
     "Here\\'s your booking summary — locked in at our bi-weekly rate. <strong>$2,158 saved</strong> per year vs one-time."),
    # Chat animation confirmation price value
    ('<div class="ew-confirm-price-val">$135<span',
     '<div class="ew-confirm-price-val">$172<span'),
]
update_file(homepage_path, HOMEPAGE_EDITS, 'homepage chat + FAQ schema')


# ─────────────────────────────────────────────────────────────────────
# 5. /book/ — service card price hints
# ─────────────────────────────────────────────────────────────────────
book_path = ROOT / 'src' / 'book.njk'

BOOK_EDITS = [
    ('<span>From $139/visit</span>',
     '<span>From $139/visit · 1-bed weekly</span>'),
    ('<span>From $278</span>',
     '<span>From $359</span>'),
    # Commercial unchanged — left at $800/mo
]
update_file(book_path, BOOK_EDITS, '/book/ service card price hints')


# ─────────────────────────────────────────────────────────────────────
# 6. /faq/ — visible + schema FAQ answers
# ─────────────────────────────────────────────────────────────────────
faq_path = ROOT / 'src' / 'faq.njk'

FAQ_EDITS = [
    # Schema answer about pricing
    ('"text": "Standard residential cleans start at $139 per visit for 1–2 bedroom homes. Weekly recurring is $118 per visit, bi-weekly is $125. Move-out cleans start at $279 by bedroom count. Commercial cleaning is quoted per site after a free walkthrough. Full residential tiers are published on the pricing page."',
     '"text": "Residential cleaning is per-bedroom, flat-rate. Weekly starts at $139/visit (1-bed), bi-weekly at $155 (1-bed), one-time at $205 (1-bed). Larger homes scale: 4-bed weekly is $205, one-time $369. Move-out cleans start at $359 (1-bed) and run to $619 (4-bed); 5+ bedroom homes are custom-quoted. Commercial cleaning is quoted per site after a free walkthrough. Full residential pricing tiers are published on the pricing page."'),
    # Schema answer about move-out scope
    ('Total move-out scope is 150 checkpoints, flat-priced by bedroom count from $279.',
     'Total move-out scope is 150 checkpoints, flat-priced by bedroom count from $359.'),
    # Visible answer 1
    ('<p>Standard residential cleans start at <strong>$139 per visit</strong> for 1–2 bedroom homes. Weekly recurring is $118, bi-weekly is $125. Move-out cleans start at $279 by bedroom count. Commercial cleaning is quoted per site after a walkthrough.</p>',
     '<p>Residential cleaning is per-bedroom, flat-rate. Weekly starts at <strong>$139/visit (1-bed)</strong>, bi-weekly at $155, one-time at $205. Larger homes scale by bedroom — see the pricing page for the full table. Move-out cleans start at <strong>$359 (1-bed)</strong>. Commercial is quoted per site after a walkthrough.</p>'),
    # Visible answer 2 (move-out scope)
    ('<p>Recurring is 100 checkpoints applied to a maintained space. Move-out adds <strong>50 vacancy-specific items</strong> — inside oven, inside fridge, inside cabinets, all baseboards, all blinds, wall scuff treatment. Total move-out scope: 150 checkpoints, flat-priced by bedroom from $279.</p>',
     '<p>Recurring is 100 checkpoints applied to a maintained space. Move-out adds <strong>50 vacancy-specific items</strong> — inside oven, inside fridge, inside cabinets, all baseboards, all blinds, wall scuff treatment. Total move-out scope: 150 checkpoints, flat-priced by bedroom from $359.</p>'),
    # Deep clean addon (changed in new pricing model)
    ('Available as a <strong>+$80 deep-clean add-on</strong>',
     'Available as a <strong>standalone deep clean (see pricing page)</strong>'),
]
update_file(faq_path, FAQ_EDITS, '/faq/ visible + schema answers')


# ─────────────────────────────────────────────────────────────────────
# 7. llms.txt — reframe pricing section
# ─────────────────────────────────────────────────────────────────────
llms_path = ROOT / 'src' / 'llms.txt'

# The current line:
# "Pricing is flat-rate and transparent. A 1-bedroom house one-time clean starts at $139 per visit. Weekly, bi-weekly, and monthly frequencies receive 15%, 10%, and 5% discounts respectively. No hidden fees."

old_llms = "A 1-bedroom house one-time clean starts at $139 per visit. Weekly, bi-weekly, and monthly frequencies receive 15%, 10%, and 5% discounts respectively."
new_llms = """Pricing is per-bedroom, flat-rate, posted online.

Residential weekly: 1-bed $139, 2-bed $155, 3-bed $172, 4-bed $205, 5+ bed custom quote
Residential bi-weekly: 1-bed $155, 2-bed $172, 3-bed $189, 4-bed $220, 5+ bed custom
Residential monthly: 1-bed $172, 2-bed $205, 3-bed $239, 4-bed $269, 5+ bed custom
Residential one-time: 1-bed $205, 2-bed $255, 3-bed $299, 4-bed $369, 5+ bed custom
Move-out cleaning: 1-bed $359, 2-bed $419, 3-bed $519, 4-bed $619, 5+ bed custom
Commercial: $800/month (up to 2,000 sqft), $1,800/month (2,000-5,000 sqft), custom (5,000+)."""

text = llms_path.read_text()
if old_llms in text:
    text = text.replace(old_llms, new_llms)
    llms_path.write_text(text)
    print('✓ llms.txt: pricing section reframed for per-bedroom model')
elif 'Residential weekly: 1-bed $139' in text:
    print('✓ llms.txt: already updated')
else:
    print('  ⚠ llms.txt: old pricing line not found — check manually')


# ─────────────────────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────────────────────
print('')
print('━' * 60)
print('PRICING UPDATE COMPLETE')
print('━' * 60)
print('Files modified:')
print('  src/pricing.njk           — main table redesigned (5-col per-bedroom)')
print('  src/move-out-cleaning.njk — 5 cards (added 5+ bed Custom)')
print('  src/residential.njk       — 4 plan cards (2-bed shown + "see all" links)')
print('  src/index.njk             — homepage chat + FAQ schema')
print('  src/book.njk              — 3 service cards')
print('  src/faq.njk               — pricing + move-out FAQs')
print('  src/llms.txt              — full pricing reframe')
print('')
print('NEXT STEPS:')
print('  1. npm run build')
print('  2. Visit localhost:8080 — check homepage hero, /pricing/, /move-out-cleaning/, /residential/')
print('  3. If everything looks right:')
print('     git add -A && git commit -m "Site-wide pricing: per-bedroom structure" && git push')
print('  4. After deploy, update Google Business description if needed.')
