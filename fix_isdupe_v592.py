#!/usr/bin/env python3
"""
fix_isdupe_v592.py - isDupe acepta substring bidireccional de merchant.

Bug: isDupe requeria match EXACTO de merchant (lowercase). Cuando el
recurrente decia "Amazon Prime" y Gmail import traia "la membresia Amazon
Prime", no matcheaba => duplicado.

Fix: si uno contiene al otro, considerar match. Los otros filtros
(amount, card, currency, ventana de 3 dias) siguen filtrando para evitar
falsos positivos.
"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

OLD = "if((ex.merchant||'').toLowerCase()!==cm)return false;"
NEW = "{const em=(ex.merchant||'').toLowerCase();if(em!==cm&&em.length>2&&cm.length>2&&!em.includes(cm)&&!cm.includes(em))return false;}"

if OLD not in c:
    print('FAIL: no se encontro el patron de isDupe. Aborto.')
    exit(1)

count = c.count(OLD)
if count != 1:
    print(f'FAIL: patron aparece {count} veces, deberia ser 1. Aborto.')
    exit(1)

c = c.replace(OLD, NEW)
print(f'OK: isDupe parche aplicado (substring bidireccional)')

# Bump version v5.91 -> v5.92
m = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", c)
if m:
    new = re.sub(r'v[\d.]+', 'v5.92', m.group(1))
    c = c.replace(m.group(0), f"APP_VERSION='{new}'", 1)
    print(f'Version: {m.group(1)} -> {new}')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)
print(f'Written {len(c):,} bytes')
