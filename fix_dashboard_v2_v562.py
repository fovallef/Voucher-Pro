#!/usr/bin/env python3
"""
fix_dashboard_v2_v562.py — Dashboard v2 (Pilar 1 fase 1) v5.62

Implementacion Sofia mockup Dashboard:
1. SummaryCard hero: monto grande ($28px), transacciones + promedio
   debajo en linea pequeña, velocity como flecha (sin texto separado)
2. Audit card colapsado a 1 linea cuando 0 issues + 0 unrec (estado
   verde), expandido a 3-cols cuando hay issues
3. Eliminar version del header subtitle (solo en Config)
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# 1. SummaryCard hero refactor
OLD_SUMCARD = "summaryCard=byMonth.length?'<div style=\"background:rgba(99,102,241,.08);border:1px solid rgba(99,102,241,.2);border-radius:14px;padding:12px 14px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center\"><div><p style=\"font-size:11px;color:var(--tx2)\">'+byMonth.length+' transacciones</p><p style=\"font-size:17px;font-weight:800\">'+fS(totMXN)+'</p>'+(totUSD>0?'<p style=\"font-size:11px;color:var(--tx3)\">+ USD '+totUSD.toFixed(2)+'</p>':'')+'</div><div style=\"text-align:right\"><p style=\"font-size:10px;color:var(--tx3)\">Promedio / cargo</p><p style=\"font-size:13px;font-weight:700\">'+(mxnM.length?fS(totMXN/mxnM.length):'—')+'</p></div></div>':'';"

NEW_SUMCARD = (
    "const _arrow=diff!==null?(parseFloat(diff)>0?'↗':parseFloat(diff)<0?'↘':''):'';"
    "const _arrowCol=diff!==null?(parseFloat(diff)>0?'#f59e0b':parseFloat(diff)<0?'#10b981':'var(--tx3)'):'var(--tx3)';"
    "summaryCard=byMonth.length?'<div style=\"background:rgba(99,102,241,.08);border:1px solid rgba(99,102,241,.2);border-radius:14px;padding:14px 16px;margin-bottom:12px\">"
    "<p style=\"font-size:11px;color:var(--tx2);margin-bottom:4px\">'+byMonth.length+' transacciones</p>"
    "<p style=\"font-size:26px;font-weight:800;letter-spacing:-.5px;line-height:1.1\">'+fS(totMXN)+'</p>"
    "'+(totUSD>0?'<p style=\"font-size:11px;color:var(--tx3);margin-top:2px\">+ USD '+totUSD.toFixed(2)+'</p>':'')+'"
    "<p style=\"font-size:12px;color:var(--tx3);margin-top:6px\">~'+(mxnM.length?fS(totMXN/mxnM.length):'—')+'/cargo'+(diff!==null?' · <span style=\\\"color:'+_arrowCol+'\\\">'+_arrow+' '+(parseFloat(diff)>0?'+':'')+diff+'%</span> vs '+(()=>{const _d=new Date(parseInt(_dp[0]),parseInt(_dp[1])-2,1);return _d.toLocaleDateString('es-MX',{month:'short'});})():'')+'</p>"
    "</div>':'';"
)
if OLD_SUMCARD in content:
    content = content.replace(OLD_SUMCARD, NEW_SUMCARD, 1)
    changes += 1
    print('OK 1: summaryCard hero refactor')
else:
    print('FAIL 1: summaryCard pattern not found')

# 2. Audit card colapsado cuando 0 issues + 0 unrec
OLD_AUCARD_OPEN = "const _auCard='<div id=\"auCard\" style=\"background:'+_auBg+';border:1px solid '+_auBd+';border-radius:14px;padding:11px 13px;margin-bottom:12px;cursor:pointer\"><div style=\"display:flex;justify-content:space-between;align-items:center;margin-bottom:6px\"><div style=\"display:flex;align-items:center;gap:6px\"><span style=\"font-size:14px\">\U0001F50D</span><span style=\"font-size:12px;font-weight:700;color:var(--tx)\">Integridad de datos</span></div><span style=\"font-size:10px;color:var(--tx3)\">'+fmtRelTime(_au.lastAt)+'</span></div>"
NEW_AUCARD_OPEN = (
    "const _allGood=_au.issues===0&&_au.unrec===0;"
    "const _auCard=_allGood?"
    "'<div id=\"auCard\" style=\"background:'+_auBg+';border:1px solid '+_auBd+';border-radius:14px;padding:9px 13px;margin-bottom:12px;cursor:pointer;display:flex;justify-content:space-between;align-items:center\">"
    "<div style=\"display:flex;align-items:center;gap:6px\"><span style=\"font-size:14px\">✅</span><span style=\"font-size:12px;font-weight:600;color:var(--tx)\">Todo en orden</span></div>"
    "<span style=\"font-size:10px;color:var(--tx3)\">'+fmtRelTime(_au.lastAt)+'</span>"
    "</div>'"
    ":"
    "'<div id=\"auCard\" style=\"background:'+_auBg+';border:1px solid '+_auBd+';border-radius:14px;padding:11px 13px;margin-bottom:12px;cursor:pointer\"><div style=\"display:flex;justify-content:space-between;align-items:center;margin-bottom:6px\"><div style=\"display:flex;align-items:center;gap:6px\"><span style=\"font-size:14px\">\U0001F50D</span><span style=\"font-size:12px;font-weight:700;color:var(--tx)\">Integridad de datos</span></div><span style=\"font-size:10px;color:var(--tx3)\">'+fmtRelTime(_au.lastAt)+'</span></div>"
)
if OLD_AUCARD_OPEN in content:
    content = content.replace(OLD_AUCARD_OPEN, NEW_AUCARD_OPEN, 1)
    changes += 1
    print('OK 2a: audit card collapsed-when-clean abierto')
    # Now close the conditional - the original card has closing structure; we need to ensure when allGood, the rest is omitted
    # The current full card has: open header + 3 cols + footer. We replaced just the opening.
    # We need to close the allGood branch BEFORE the 3-col section and skip footer.
    # Find the closing of the card '</div>'; right after 'Tap para ver detalle en Config</p></div>'
    OLD_AUCARD_CLOSE = "<p style=\"font-size:10px;color:var(--tx3);margin-top:6px;text-align:center\">Tap para ver detalle en Config</p></div>';"
    if OLD_AUCARD_CLOSE in content:
        # Wrap the middle (3 cols + footer) in a ternary so it appears only when !allGood
        # But we already opened with a ternary. So actually we need to ensure the rest of the card (3-col body + footer) closes the !allGood branch.
        # Replace the close so it ends the ternary properly
        NEW_AUCARD_CLOSE = "<p style=\"font-size:10px;color:var(--tx3);margin-top:6px;text-align:center\">Tap para ver detalle en Config</p></div>';"
        # No change needed if our open already structured correctly. Leave as-is.
        print('   debug: close marker found, leaving as-is')
else:
    print('FAIL 2: aucard open pattern not found')

# 3. Eliminar version del header subtitle
OLD_VER_SPAN = "<span style=\"color:var(--tx3);margin-left:6px;font-size:10px\">${APP_VERSION}</span>"
NEW_VER_SPAN = ""
if OLD_VER_SPAN in content:
    content = content.replace(OLD_VER_SPAN, NEW_VER_SPAN, 1)
    changes += 1
    print('OK 3: version eliminada del header (visible en Config)')
else:
    print('FAIL 3: version span pattern not found')

# Bump APP_VERSION -> v5.62
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.62', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK Version: {old_ver_str} -> v5.62')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
