#!/usr/bin/env python3
"""
fix_safari_all.py — Elimina TODOS los patrones de destructuring en arrow function params
que pueden causar SyntaxError en Safari iOS.
También añade no-cache meta tags para forzar refresh de PWA.
También actualiza APP_VERSION a v4.8.
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ── 1. detectRecurring: ([,l])=> → Object.keys con acceso directo ──────────
OLD_DETREC = (
    'return Object.entries(g).filter(([,l])=>l.length>=2).map(([,l])=>{'
)
NEW_DETREC = (
    'return Object.keys(g).filter(function(k){return g[k].length>=2;}).map(function(k){var l=g[k];{'
)

if OLD_DETREC in content:
    content = content.replace(OLD_DETREC, NEW_DETREC, 1)
    changes += 1
    print('OK 1: detectRecurring — ([,l])=> reemplazado con function(k)')
else:
    print('SKIP 1: detectRecurring pattern not found')
    idx = content.find('Object.entries(g)')
    if idx > 0:
        print(f'  Object.entries(g) at {idx}: {repr(content[idx:idx+120])}')

# ── 2. rTxDetail: ([k,v])=> → function(pair) ───────────────────────────────
OLD_TXDETAIL = (
    '].map(([k,v])=>\'<div style="display:flex;justify-content:space-between;align-items:center;'
    'padding:10px 14px;border-bottom:1px solid var(--bg3)">\'+\n'
    '\'<p style="font-size:11px;color:#94a3b8;flex-shrink:0;margin-right:12px">\'+k+\'</p>\'+\n'
    '\'<p style="font-size:13px;text-align:right">\'+v+\'</p></div>\')'
)
NEW_TXDETAIL = (
    '].map(function(pair){var k=pair[0],v=pair[1];return\'<div style="display:flex;justify-content:space-between;align-items:center;'
    'padding:10px 14px;border-bottom:1px solid var(--bg3)">\'+\n'
    '\'<p style="font-size:11px;color:#94a3b8;flex-shrink:0;margin-right:12px">\'+k+\'</p>\'+\n'
    '\'<p style="font-size:13px;text-align:right">\'+v+\'</p></div>\'})'
)

if OLD_TXDETAIL in content:
    content = content.replace(OLD_TXDETAIL, NEW_TXDETAIL, 1)
    changes += 1
    print('OK 2: rTxDetail — ([k,v])=> reemplazado con function(pair)')
else:
    print('SKIP 2: rTxDetail pattern not found')
    idx = content.find('.map(([k,v])')
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx:idx+150])}')

# ── 3. rHistory filter pills: ([v,l])=> → function(pair) ───────────────────
OLD_PILLS = (
    "].map(([v,l])=>'<button class=\"fp '+(S.hFilter===v?'fa':'')+\\'\"data-hf=\"'+v+'\">'+l+'</button>').join('')+'</div>';"
)
NEW_PILLS = (
    "].map(function(pair){var v=pair[0],l=pair[1];return'<button class=\"fp '+(S.hFilter===v?'fa':'')+\\'\"data-hf=\"'+v+'\">'+l+'</button>';}).join('')+'</div>';"
)

if OLD_PILLS in content:
    content = content.replace(OLD_PILLS, NEW_PILLS, 1)
    changes += 1
    print('OK 3: rHistory pills — ([v,l])=> reemplazado con function(pair)')
else:
    print('SKIP 3: rHistory pills pattern not found')
    idx = content.find('.map(([v,l])')
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx:idx+150])}')

# ── 4. APP_VERSION: v4.7 → v4.8 ────────────────────────────────────────────
OLD_VER = "APP_VERSION='v4.7 \xb7 10 May 2026'"
NEW_VER = "APP_VERSION='v4.8 \xb7 11 May 2026'"

if OLD_VER in content:
    content = content.replace(OLD_VER, NEW_VER, 1)
    changes += 1
    print('OK 4: APP_VERSION → v4.8 · 11 May 2026')
else:
    print('SKIP 4: APP_VERSION v4.7 not found')
    idx = content.find('APP_VERSION=')
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx:idx+60])}')

# ── 5. No-cache meta tags ───────────────────────────────────────────────────
OLD_META = '<meta name="theme-color" content="#020617">'
NEW_META = (
    '<meta name="theme-color" content="#09090f">'
    '<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">'
    '<meta http-equiv="Pragma" content="no-cache">'
    '<meta http-equiv="Expires" content="0">'
)

if OLD_META in content:
    content = content.replace(OLD_META, NEW_META, 1)
    changes += 1
    print('OK 5: No-cache meta tags añadidos + theme-color actualizado')
else:
    print('SKIP 5: theme-color meta not found')
    idx = content.find('theme-color')
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx:idx+80])}')

print(f'\nTotal changes: {changes}/5')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
