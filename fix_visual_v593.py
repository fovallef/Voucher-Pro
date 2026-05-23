#!/usr/bin/env python3
"""
fix_visual_v593.py - M3 visual fixes:
- .am 14px -> 13px (mas chico aun)
- Ocultar .cu cuando currency=='MXN' (implicito, evita solape con bote rojo)
"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. .am 14px -> 13px
OLD_AM = ".am{font-size:14px;font-weight:700;line-height:1.15;letter-spacing:-.2px;white-space:nowrap;font-feature-settings:\"tnum\"}"
NEW_AM = ".am{font-size:13px;font-weight:700;line-height:1.15;letter-spacing:-.2px;white-space:nowrap;font-feature-settings:\"tnum\"}"
if OLD_AM not in c:
    print('FAIL: no se encontro CSS .am. Aborto.')
    exit(1)
c = c.replace(OLD_AM, NEW_AM, 1)
print('OK: .am 14px -> 13px')

# 2. Render: ocultar .cu si MXN
OLD_RENDER = "'<div class=\"cu\">'+t.currency+'</div>'"
NEW_RENDER = "(t.currency!=='MXN'?'<div class=\"cu\">'+t.currency+'</div>':'')"
count = c.count(OLD_RENDER)
if count == 0:
    print('FAIL: no se encontro render de .cu. Aborto.')
    exit(1)
c = c.replace(OLD_RENDER, NEW_RENDER)
print(f'OK: .cu render condicionado a non-MXN ({count} ocurrencias)')

# 3. Bump version v5.92 -> v5.93
m = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", c)
if m:
    new = re.sub(r'v[\d.]+', 'v5.93', m.group(1))
    c = c.replace(m.group(0), f"APP_VERSION='{new}'", 1)
    print(f'Version: {m.group(1)} -> {new}')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print(f'Written {len(c):,} bytes')
