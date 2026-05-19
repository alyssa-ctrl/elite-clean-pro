#!/usr/bin/env python3
"""
Final pricing patches — homepage chat animation + /pricing/ FAQ answer.
"""
import pathlib, re

ROOT = pathlib.Path.home() / 'Desktop' / 'elite-clean-pro'

# ───────────────────────────────────────────────
# 1. Homepage chat animation
# ───────────────────────────────────────────────
hp = ROOT / 'src' / 'index.njk'
text = hp.read_text()
orig = text

text = text.replace(
    "Our bi-weekly rate for a 2 bedroom is <strong>$135/visit</strong> \u2014 10% off the one-time rate, locked in. No contract, cancel anytime.",
    "Our bi-weekly rate for a 2 bedroom is <strong>$172/visit</strong> \u2014 saving you ~$2,158/year vs one-time. No contract, cancel anytime."
)

text = text.replace(
    "<strong>$125 saved</strong> per year vs one-time",
    "<strong>$2,158 saved</strong> per year vs one-time"
)

if text != orig:
    hp.write_text(text)
    print('✓ index.njk: chat animation updated ($172/visit + $2,158 saved)')
else:
    print('  index.njk: no changes (already updated?)')

# ───────────────────────────────────────────────
# 2. /pricing/ FAQ answer
# ───────────────────────────────────────────────
pp = ROOT / 'src' / 'pricing.njk'
text = pp.read_text()
orig = text

old = 'House cleaning in Calgary in 2026 costs between $120 and $300 per visit at most providers. <strong>Elite Clean Pro charges flat rates from $139 per visit</strong> for a 1\u20132 bedroom home (one-time) or $118 per visit on a weekly recurring plan. A 3\u20134 bedroom home starts at $179 one-time or $152 recurring weekly. These are all-in prices \u2014 no supply fee, no fuel surcharge, no hourly minimum.'

new = 'House cleaning in Calgary in 2026 ranges from $130 to $400 per visit depending on home size, frequency, and provider. <strong>Elite Clean Pro charges per bedroom, flat-rate:</strong> weekly starts at $139 (1-bed), $155 (2-bed), $172 (3-bed), $205 (4-bed). One-time cleans start at $205 (1-bed) up to $369 (4-bed). 5+ bedroom homes are custom-quoted. All prices are all-in \u2014 no supply fee, no fuel surcharge, no hourly minimum.'

if old in text:
    text = text.replace(old, new)
    pp.write_text(text)
    print('✓ pricing.njk: FAQ answer updated to per-bedroom structure')
else:
    print('  pricing.njk: FAQ pattern not matched. Paste lines 580-585 if you see this message.')

print('')
print('Done. Run: npm run build')
