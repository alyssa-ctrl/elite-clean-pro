#!/usr/bin/env python3
"""
Wire the external quote-calculator.js into src/index.njk
- Removes any inline calculator scripts (anything containing 'basePrices')
- Adds a <script src="/assets/quote-calculator.js" defer></script> tag
- Idempotent: safe to run twice
"""

import pathlib
import re
import sys

PROJECT_ROOT = pathlib.Path.home() / 'Desktop' / 'elite-clean-pro'
INDEX = PROJECT_ROOT / 'src' / 'index.njk'

if not INDEX.exists():
    print('ERROR: ' + str(INDEX) + ' not found')
    sys.exit(1)

content = INDEX.read_text()

# Strip every <script> block containing basePrices
pattern = re.compile(
    r'<script[^>]*>(?:(?!</script>).)*?basePrices(?:(?!</script>).)*?</script>',
    re.DOTALL
)
inline_removed = len(pattern.findall(content))
content = pattern.sub('', content)
print('Removed ' + str(inline_removed) + ' inline calculator script(s)')

# Add the external script reference if not already present
tag = '<script src="/assets/quote-calculator.js" defer></script>'
if tag in content:
    print('External script tag already present')
else:
    content = content.rstrip() + '\n' + tag + '\n'
    print('Added external script tag')

INDEX.write_text(content)
print('basePrices remaining in source: ' + str(content.count('basePrices')))
print('Done. Run npm run build or wait for dev server to reload.')
