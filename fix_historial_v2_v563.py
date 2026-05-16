#!/usr/bin/env python3
"""
fix_historial_v2_v563.py — Historial v2 (Pilar 1 fase 2) v5.63

Sofia mockup Historial:
1. Filter chips primarios visibles: Todos, Pendientes, MSI + el activo
   si no es primario. "Más filtros ▾" toggle para resto (manual,
   recurring, disputed, stuck, closed, reconciled).
2. Empty state con CTA accionable
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# 1. Filter chips: split into primarios + secundarios with toggle
OLD_PILLS = "const pills='<div class=\"fpills\">'+[['all','Todos'],['pending','Pendientes'],['reconciled','Conciliados'],['manual','Manuales'],['recurring','Recurrentes'],['msi','MSI'],['disputed','En disputa'],['stuck','Sin conciliar'],['closed','Cerrados']].map(function(pair){var v=pair[0],l=pair[1];var n=_hc[v]||0;return'<button class=\"fp '+(S.hFilter===v?'fa':'')+'\"data-hf=\"'+v+'\">'+l+' ('+n+')</button>';}).join('')+'</div>';"

NEW_PILLS = (
    "const _primary=['all','pending','msi'];"
    "const _allPills=[['all','Todos'],['pending','Pendientes'],['msi','MSI'],['reconciled','Conciliados'],['manual','Manuales'],['recurring','Recurrentes'],['disputed','En disputa'],['stuck','Sin conciliar'],['closed','Cerrados']];"
    "const _showMore=S.hShowMoreFilters||(_primary.indexOf(S.hFilter)<0&&S.hFilter!=='all');"
    "const _visiblePills=_showMore?_allPills:_allPills.filter(p=>_primary.indexOf(p[0])>=0||p[0]===S.hFilter);"
    "const _pillsHtml=_visiblePills.map(function(pair){var v=pair[0],l=pair[1];var n=_hc[v]||0;return'<button class=\"fp '+(S.hFilter===v?'fa':'')+'\"data-hf=\"'+v+'\">'+l+' ('+n+')</button>';}).join('');"
    "const _toggleBtn='<button class=\"fp\" data-hftog=\"1\" style=\"opacity:.7\">'+(_showMore?'Menos ▴':'Más ▾')+'</button>';"
    "const pills='<div class=\"fpills\">'+_pillsHtml+_toggleBtn+'</div>';"
)
if OLD_PILLS in content:
    content = content.replace(OLD_PILLS, NEW_PILLS, 1)
    changes += 1
    print('OK 1: filter chips colapsados (primarios + toggle Más/Menos)')
else:
    print('FAIL 1: pills pattern not found')

# 2. Toggle handler en attachHistory
OLD_ATTACH_HF = "document.querySelectorAll('[data-hf]').forEach(b=>b.addEventListener('click',()=>{S.hFilter=b.dataset.hf;render();}));"
NEW_ATTACH_HF = (
    "document.querySelectorAll('[data-hf]').forEach(b=>b.addEventListener('click',()=>{S.hFilter=b.dataset.hf;render();}));"
    "document.querySelectorAll('[data-hftog]').forEach(b=>b.addEventListener('click',()=>{S.hShowMoreFilters=!S.hShowMoreFilters;render();}));"
)
if OLD_ATTACH_HF in content:
    content = content.replace(OLD_ATTACH_HF, NEW_ATTACH_HF, 1)
    changes += 1
    print('OK 2: toggle handler data-hftog agregado')
else:
    print('FAIL 2: attach hf handler not found')

# 3. Empty state con CTA
OLD_EMPTY = "'<div class=\"empty\"><div class=\"ei\">&#x1F4CB;</div><p style=\"font-size:15px;font-weight:600\">Sin transacciones</p><p style=\"font-size:12px;margin-top:6px;color:var(--tx3)\">Nada registrado en '+mLabel+'</p></div>'"

NEW_EMPTY = (
    "'<div class=\"empty\" style=\"padding:30px 20px;text-align:center\">"
    "<div class=\"ei\" style=\"font-size:42px;margin-bottom:10px\">&#x1F4CB;</div>"
    "<p style=\"font-size:15px;font-weight:600;margin-bottom:4px\">Sin transacciones en '+mLabel+'</p>"
    "<p style=\"font-size:12px;color:var(--tx3);margin-bottom:14px\">Aún no has capturado nada este mes</p>"
    "<button class=\"btn\" data-emptyscan=\"1\" style=\"padding:9px 16px;font-size:13px;font-weight:600\">&#x1F4F7; Capturar voucher</button>"
    "</div>'"
)
if OLD_EMPTY in content:
    content = content.replace(OLD_EMPTY, NEW_EMPTY, 1)
    changes += 1
    print('OK 3: empty state con CTA capturar voucher')
else:
    print('FAIL 3: empty state pattern not found')

# 4. Handler emptyscan -> tab scan
OLD_ATTACH_TOG = "document.querySelectorAll('[data-hftog]').forEach(b=>b.addEventListener('click',()=>{S.hShowMoreFilters=!S.hShowMoreFilters;render();}));"
NEW_ATTACH_TOG = (
    "document.querySelectorAll('[data-hftog]').forEach(b=>b.addEventListener('click',()=>{S.hShowMoreFilters=!S.hShowMoreFilters;render();}));"
    "document.querySelectorAll('[data-emptyscan]').forEach(b=>b.addEventListener('click',()=>{S.tab='scan';render();}));"
)
if OLD_ATTACH_TOG in content:
    content = content.replace(OLD_ATTACH_TOG, NEW_ATTACH_TOG, 1)
    changes += 1
    print('OK 4: handler emptyscan -> tab scan')
else:
    print('FAIL 4: toggle handler position not found')

# Bump APP_VERSION -> v5.63
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.63', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK Version: {old_ver_str} -> v5.63')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
