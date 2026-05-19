#!/usr/bin/env python3
"""
Pricing update follow-up patch — catches the visible FAQ on /move-out-cleaning/
that the main script missed (there were two copies of the cost answer).
"""

import pathlib

ROOT = pathlib.Path.home() / 'Desktop' / 'elite-clean-pro'
p = ROOT / 'src' / 'move-out-cleaning.njk'

if not p.exists():
    print('ERROR: not in project root')
    raise SystemExit(1)

text = p.read_text()

old = 'Move-out cleaning in Calgary in 2026 typically costs $200 to $500 per unit. <strong>Elite Clean Pro charges $278 for a 1\u20132 bedroom unit, $358 for 3\u20134 bedroom, and $438+ for 5+ bedroom.</strong> Flat rate, locked at booking, includes inside oven, inside fridge, inside cabinets, baseboards, and a written 150-point inspection report with photos. No hourly billing. No deposit-deduction surprises.'

new = 'Move-out cleaning in Calgary in 2026 typically costs $300 to $700 per unit depending on bedroom count. <strong>Elite Clean Pro charges per bedroom: $359 (1-bed), $419 (2-bed), $519 (3-bed), $619 (4-bed).</strong> 5+ bedroom homes are custom quoted within 24 hours of walkthrough. Flat rate, locked at booking, includes inside oven, inside fridge, inside cabinets, baseboards, and a written 150-point inspection report with photos. No hourly billing. No deposit-deduction surprises.'

if old in text:
    text = text.replace(old, new)
    p.write_text(text)
    print('Updated visible move-out FAQ answer with new pricing')
elif new in text:
    print('Already updated — nothing to do')
else:
    print('Pattern not found — paste me lines 1295-1300 of src/move-out-cleaning.njk so I can see what is there')
