#!/usr/bin/env python3
"""
fix_conciliar_v2_v565.py — Conciliar v2 (Pilar 1 fase 3) v5.65

Sofia mockup Conciliar:
1. Header: bank + cutDate + chip Pagado inline (no banner separado)
2. Hero counter: 51/54 grande con check verde
3. Sub-indicadores: 'N sin reconocer · M ignorados' debajo del hero
4. Lista preview de no-reconocidos (hasta 3 merchants) si liveUnrec > 0
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# 1. Eliminar paidBadge banner (se mueve a chip inline en header)
OLD_PAIDBADGE = "const paidBadge=s.paidAt?'<div style=\"background:rgba(16,185,129,.15);border:1px solid rgba(16,185,129,.4);border-radius:8px;padding:6px 10px;margin-bottom:8px;text-align:center;font-size:11px;color:#10b981;font-weight:600\">&#x1F49A; Pagado el '+s.paidAt+(s.paidAmount?' &middot; '+fS(s.paidAmount):'')+'</div>':'';"

NEW_PAID_CHIP = "const paidBadge='';const paidChip=s.paidAt?'<span style=\"font-size:10px;color:#10b981;background:rgba(16,185,129,.15);padding:2px 8px;border-radius:10px;margin-left:6px;font-weight:600\">&#x1F49A; Pagado</span>':'';"

if OLD_PAIDBADGE in content:
    content = content.replace(OLD_PAIDBADGE, NEW_PAID_CHIP, 1)
    changes += 1
    print('OK 1: paidBadge banner -> paidChip inline')
else:
    print('FAIL 1: paidBadge pattern not found')

# 2. Header: agregar paidChip junto al bank
OLD_HEADER = "'<div><p style=\"font-weight:700;font-size:13px\">'+esc(s.bank)+'</p>'"
NEW_HEADER = "'<div><p style=\"font-weight:700;font-size:14px\">'+esc(s.bank)+paidChip+'</p>'"
if OLD_HEADER in content:
    content = content.replace(OLD_HEADER, NEW_HEADER, 1)
    changes += 1
    print('OK 2: header bank con paidChip inline + size 14px')
else:
    print('FAIL 2: header bank pattern not found')

# 3. Reemplazar 3-col grid por hero counter + sub line
OLD_3COLS = "'<div style=\"display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;margin-bottom:6px\">'+'<div style=\"text-align:center;background:var(--bg3);border-radius:8px;padding:5px\"><p style=\"font-size:14px;font-weight:700\">'+(liveCharges||0)+'</p><p style=\"font-size:9px;color:var(--tx2)\">Cargos</p></div>'+'<div style=\"text-align:center;background:rgba(16,185,129,.1);border-radius:8px;padding:5px\"><p style=\"font-size:14px;font-weight:700;color:#10b981\">'+liveMatch+'</p><p style=\"font-size:9px;color:var(--tx2)\">Conciliados</p></div>'+'<div style=\"text-align:center;background:'+unrecBg+';border-radius:8px;padding:5px\"><p style=\"font-size:14px;font-weight:700;color:'+unrecColor+'\">'+liveUnrec+'</p><p style=\"font-size:9px;color:var(--tx2)\">No reconoc.</p></div></div>'"

NEW_HERO_COUNTER = (
    "'<div style=\"background:'+(liveUnrec>0?'rgba(239,68,68,.06)':'rgba(16,185,129,.06)')+';border-radius:10px;padding:10px;margin-bottom:8px;text-align:center\">"
    "<p style=\"font-size:24px;font-weight:800;color:'+(liveUnrec>0?'var(--tx)':'#10b981')+';letter-spacing:-.5px\">'+liveMatch+' <span style=\"color:var(--tx3);font-size:18px\">/</span> '+(liveCharges||0)+(liveUnrec===0?' <span style=\"font-size:16px\">&#x2713;</span>':'')+'</p>"
    "<p style=\"font-size:11px;color:var(--tx2);margin-top:2px\">conciliados de '+(liveCharges||0)+' cargos</p>"
    "'+(liveUnrec>0||liveIgnored>0?'<p style=\"font-size:10px;color:var(--tx3);margin-top:4px\">'+(liveUnrec>0?'<span style=\"color:'+unrecColor+'\">'+liveUnrec+' sin reconocer</span>':'')+(liveUnrec>0&&liveIgnored>0?' · ':'')+(liveIgnored>0?liveIgnored+' ignorado'+(liveIgnored>1?'s':''):'')+'</p>':'')+'"
    "</div>'"
)
if OLD_3COLS in content:
    content = content.replace(OLD_3COLS, NEW_HERO_COUNTER, 1)
    changes += 1
    print('OK 3: 3-col grid -> hero counter 51/54')
else:
    print('FAIL 3: 3-col grid pattern not found')

# 4. Quitar el badge "N ignorados (no contados)" que aparecia despues del hero
# (ahora ya esta integrado en el sub-line del hero)
OLD_IGN_BADGE = "+(liveIgnored>0?'<div style=\"font-size:10px;color:var(--tx3);margin-top:4px;text-align:center\">'+liveIgnored+' ignorado'+(liveIgnored>1?'s':'')+' (no contados)</div>':'')"
NEW_IGN_BADGE = ""
if OLD_IGN_BADGE in content:
    content = content.replace(OLD_IGN_BADGE, NEW_IGN_BADGE, 1)
    changes += 1
    print('OK 4: ignored badge separado eliminado (ya integrado en hero)')
else:
    print('FAIL 4: ignored badge pattern not found')

# 5. Agregar lista preview de no-reconocidos (despues del summary, antes del boton existente)
# Insertar antes de '+summary+(s.statement_txs&&s.statement_txs.length>0&&liveUnrec>0?'
OLD_PRE_BTN = "'+summary+(s.statement_txs&&s.statement_txs.length>0&&liveUnrec>0?"
NEW_PRE_BTN = (
    "'+(liveUnrec>0&&s.statement_txs?'<div style=\"margin-bottom:8px\">"
    "<p style=\"font-size:10px;color:var(--tx3);margin-bottom:4px;text-transform:uppercase;letter-spacing:.5px\">Sin reconocer</p>"
    "'+s.statement_txs.filter(t=>t.status===\"unrecognized\").slice(0,3).map(t=>'<p style=\"font-size:11px;color:var(--tx);margin-bottom:2px\">&#x2022; '+esc((t.merchant||\"?\").slice(0,30))+' <span style=\"color:var(--tx3)\">'+fS(Math.abs(parseFloat(t.amount||0)))+'</span></p>').join('')+'"
    "'+(s.statement_txs.filter(t=>t.status===\"unrecognized\").length>3?'<p style=\"font-size:10px;color:var(--tx3);margin-top:2px\">y '+(s.statement_txs.filter(t=>t.status===\"unrecognized\").length-3)+' más...</p>':'')+'"
    "</div>':'')+summary+(s.statement_txs&&s.statement_txs.length>0&&liveUnrec>0?"
)
if OLD_PRE_BTN in content:
    content = content.replace(OLD_PRE_BTN, NEW_PRE_BTN, 1)
    changes += 1
    print('OK 5: lista preview de no-reconocidos agregada')
else:
    print('FAIL 5: pre-btn pattern not found')

# Bump APP_VERSION -> v5.65
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.65', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK Version: {old_ver_str} -> v5.65')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
