#!/usr/bin/env python3
"""
fix_sprint6.py — Sofía · Sprint 6 + 7
Sprint 6: Dashboard hero numbers (44px bold, mes en texto, mini stats row con USD)
Sprint 7: Hardcoded colors → CSS vars en velocity + empty state SVG
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ── SPRINT 6: DASHBOARD HERO CARD ────────────────────────────────────────────
# Replace the 2-col sgrid (small boxes) with a full-width hero card
OLD_HERO = (
    'return\'<div class="sgrid"><div class="sbox"><div class="sl">Gasto MXN este mes</div>'
    '<div class="sv"style="font-size:16px">\'+fS(tot)+\'</div>\''
    '+(diff!==null?\'<p style="font-size:10px;margin-top:2px;color:\''
    '+(parseFloat(diff)>0?\'#ef4444\':\'#10b981\')+\'">\''
    '+(parseFloat(diff)>0?\'▲\':\'▼\')+Math.abs(diff)+\'% vs anterior</p>\':\'\')'
    '+\'</div><div class="sbox"><div class="sl">Promedio por cargo</div>'
    '<div class="sv"style="font-size:16px">\''
    '+(mxn.length?fS(tot/mxn.length):\'$0\')+\'</div>'
    '<p style="font-size:10px;color:#64748b;margin-top:2px">\''
    '+(mxn.length+usd.length)+\' transacciones</p></div></div>\''
)

NEW_HERO = (
    'return\'<div class="card"style="padding:22px;margin-bottom:14px">\''
    '+\'<p style="font-size:10px;font-weight:700;color:var(--tx3);text-transform:uppercase;letter-spacing:.8px;margin-bottom:8px">Gasto total \xb7 \''
    '+new Date().toLocaleString(\'es-MX\',{month:\'long\'})+\'</p>\''
    '+\'<p style="font-size:44px;font-weight:800;letter-spacing:-.04em;line-height:1;color:var(--tx)">\'+fS(tot)+\'</p>\''
    '+(diff!==null?\'<p style="font-size:12px;font-weight:600;margin-top:6px;color:\'+(parseFloat(diff)>0?\'var(--rd)\':\'var(--em)\')+\'">\'+(parseFloat(diff)>0?\'&#x25B2;\':\'&#x25BC;\')+Math.abs(diff)+\'% vs mes anterior</p>\':\'\')'
    '+\'<div style="display:flex;gap:20px;margin-top:16px;padding-top:12px;border-top:1px solid rgba(255,255,255,.06)">\''
    '+\'<div><p style="font-size:10px;color:var(--tx3);margin-bottom:2px">Transacciones</p><p style="font-size:17px;font-weight:700">\''
    '+(mxn.length+usd.length)+\'</p></div>\''
    '+\'<div><p style="font-size:10px;color:var(--tx3);margin-bottom:2px">Promedio</p><p style="font-size:17px;font-weight:700">\''
    '+(mxn.length?fS(tot/mxn.length):\'&#x2014;\')+\'</p></div>\''
    '+(usd.length?\'<div><p style="font-size:10px;color:var(--tx3);margin-bottom:2px">USD</p><p style="font-size:17px;font-weight:700;color:var(--am)">\'+fS(usd.reduce((s,t)=>s+parseFloat(t.amount||0),0))+\'</p></div>\':\'\')'
    '+\'</div></div>\''
)

if OLD_HERO in content:
    content = content.replace(OLD_HERO, NEW_HERO, 1)
    changes += 1
    print('OK 1: Dashboard hero card — 44px total spend + mini stats row')
else:
    print('FAIL 1: sgrid hero pattern not found')
    idx = content.find('return\'<div class="sgrid">')
    if idx > 0:
        print(f'  sgrid at {idx}: {repr(content[idx:idx+100])}')

# ── SPRINT 7A: Velocity hardcoded color → CSS var ────────────────────────────
OLD_VEL = '\'<p style="font-size:10px;color:#64748b">Al ritmo actual (d\xeda \''
NEW_VEL = '\'<p style="font-size:10px;color:var(--tx3)">Al ritmo actual (d\xeda \''

if OLD_VEL in content:
    content = content.replace(OLD_VEL, NEW_VEL, 1)
    changes += 1
    print('OK 2: Velocity color → var(--tx3)')
else:
    print('SKIP 2: velocity color pattern not found')

# ── SPRINT 7B: Empty state — bigger icon, better copy ────────────────────────
OLD_EMPTY = (
    '\'<div class="empty"><div class="ei">&#x1F4CA;</div>'
    '<p style="font-size:14px">Sin datos este mes</p>'
    '<p style="font-size:12px;margin-top:4px">Ve a &#x2795; para agregar gastos</p></div>\''
)
# The emoji in source might be unicode
OLD_EMPTY2 = (
    "return'<div class=\"empty\"><div class=\"ei\">\U0001f4ca</div>"
    "<p style=\"font-size:14px\">Sin datos este mes</p>"
    "<p style=\"font-size:12px;margin-top:4px\">Ve a ➕ para agregar gastos</p></div>';"
)
NEW_EMPTY = (
    "return'<div class=\"empty\"><div class=\"ei\">&#x1F4CA;</div>"
    "<p style=\"font-size:15px;font-weight:600\">Sin gastos este mes</p>"
    "<p style=\"font-size:12px;margin-top:6px;color:var(--tx3)\">Escanea un voucher o agrega un gasto manual</p></div>';"
)

if OLD_EMPTY2 in content:
    content = content.replace(OLD_EMPTY2, NEW_EMPTY, 1)
    changes += 1
    print('OK 3: Empty state copy mejorado')
else:
    # Try the raw emoji
    idx = content.find('Sin datos este mes')
    if idx > 0:
        # Find the full return statement
        ret_start = content.rfind("return'", 0, idx)
        ret_end = content.find("';", idx)
        if ret_start > 0 and ret_end > 0:
            old_seg = content[ret_start:ret_end+2]
            new_seg = (
                "return'<div class=\"empty\"><div class=\"ei\">&#x1F4CA;</div>"
                "<p style=\"font-size:15px;font-weight:600\">Sin gastos este mes</p>"
                "<p style=\"font-size:12px;margin-top:6px;color:var(--tx3)\">Escanea un voucher o agrega un gasto manual</p></div>';"
            )
            content = content.replace(old_seg, new_seg, 1)
            changes += 1
            print('OK 3: Empty state copy mejorado (fallback)')
        else:
            print('SKIP 3: empty state not found')
    else:
        print('SKIP 3: empty state not found')

# ── SPRINT 7C: Budgets section — remove emoji, use icon span ─────────────────
OLD_BUD_TIT = '\'<div class="card"style="padding:12px;margin-bottom:12px"><p class="stit">\U0001f4b0 Presupuestos</p>\''
NEW_BUD_TIT = '\'<div class="card"style="padding:12px;margin-bottom:12px"><p class="stit">Presupuestos del mes</p>\''

if OLD_BUD_TIT in content:
    content = content.replace(OLD_BUD_TIT, NEW_BUD_TIT, 1)
    changes += 1
    print('OK 4: Budgets title — emoji removed, cleaner label')
else:
    # Try with HTML entity
    OLD_BUD_TIT2 = '\'<div class="card"style="padding:12px;margin-bottom:12px"><p class="stit">&#x1F4B0; Presupuestos</p>\''
    if OLD_BUD_TIT2 in content:
        content = content.replace(OLD_BUD_TIT2, NEW_BUD_TIT, 1)
        changes += 1
        print('OK 4: Budgets title (entity form) — cleaned')
    else:
        print('SKIP 4: budgets title not found')

# ── SPRINT 7D: Charts section stit label clean ────────────────────────────────
OLD_CHART = '\'<div class="card"style="padding:12px"><p class="stit">Por Categor\xeda(MXN)</p><canvas id="pCha'
NEW_CHART = '\'<div class="card"style="padding:14px"><p class="stit">Por Categor\xeda</p><canvas id="pCha'

if OLD_CHART in content:
    content = content.replace(OLD_CHART, NEW_CHART, 1)
    changes += 1
    print('OK 5: Charts card padding + label (removed MXN from stit)')
else:
    print('SKIP 5: chart card label not found')

# ── SPRINT 7E: History empty state ───────────────────────────────────────────
OLD_HIST_EMPTY = (
    "'<div class=\"empty\"><div class=\"ei\">&#x1F4CB;</div>"
    "<p style=\"font-size:14px\">Sin transacciones</p>"
    "<p style=\"font-size:12px;margin-top:4px\">Agrega gastos desde las otras pesta&#xF1;as</p></div>'"
)
NEW_HIST_EMPTY = (
    "'<div class=\"empty\"><div class=\"ei\">&#x1F4CB;</div>"
    "<p style=\"font-size:15px;font-weight:600\">Sin transacciones</p>"
    "<p style=\"font-size:12px;margin-top:6px;color:var(--tx3)\">Escanea un voucher o importa desde Gmail</p></div>'"
)
if OLD_HIST_EMPTY in content:
    content = content.replace(OLD_HIST_EMPTY, NEW_HIST_EMPTY, 1)
    changes += 1
    print('OK 6: History empty state copy mejorado')
else:
    idx = content.find('Sin transacciones')
    if idx > 0:
        print(f'SKIP 6: history empty not exact match, at {idx}: {repr(content[idx-20:idx+80])}')
    else:
        print('SKIP 6: history empty not found')

print(f'\nTotal changes: {changes}/6')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
