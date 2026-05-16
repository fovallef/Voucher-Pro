#!/usr/bin/env python3
"""
fix_unignore_v555.py — Reverter ignored→matched + excluir ignored del denominador v5.55

Diagnostico v5.54 reveló: 5 stx en Amex con status='ignored' (Francisco los
marcó como "Ignorar - ya está registrado" en sesion previa). 3 de los 5
tienen matched_id apuntando a tx valido (recuperables); los otros 2 son
ignorados intencionales sin link.

Plan:
1. One-time migration: stx.status='ignored' + matched_id apunta a tx
   existente → status='matched' (recupera los 3 reversibles)
2. Cambiar totalCharges filter para excluir 'ignored' del denominador
3. stmtCard: agregar liveIgnored y mostrar como badge cuando > 0
4. stmtCard: recalcular totalCharges dinamicamente excluyendo ignored y credit

Resultado esperado Amex: 54 Conciliados / 54 Cargos · 2 ignorados aparte
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# 1. Data migration v5.55: ignored con matched_id valido -> matched
OLD_DIAG_END = (
    "console.log('[VoucherPro] v5.54 normalize: '+_normalized+' stx con matched_id set + status raro normalizados a matched');"
    "localStorage.setItem('vp_v554_diag_normalize','1');"
    "}"
)
NEW_DIAG_END = (
    "console.log('[VoucherPro] v5.54 normalize: '+_normalized+' stx con matched_id set + status raro normalizados a matched');"
    "localStorage.setItem('vp_v554_diag_normalize','1');"
    "}"
    "if(!localStorage.getItem('vp_v555_unignore')){"
    "let _unignored=0;"
    "let _keptIgnored=0;"
    "S.statements.forEach(s=>{"
    "if(!s.statement_txs)return;"
    "s.statement_txs.forEach(stx=>{"
    "if(stx.status!=='ignored')return;"
    "if(!stx.matched_id){_keptIgnored++;return;}"
    "const _t=S.txs.find(x=>x.id===stx.matched_id);"
    "if(_t){stx.status='matched';_unignored++;}"
    "else{_keptIgnored++;}"
    "});"
    "});"
    "console.log('[VoucherPro] v5.55 unignore: '+_unignored+' stx revertidos ignored->matched (matched_id valido); '+_keptIgnored+' kept as ignored (sin link o tx perdida)');"
    "localStorage.setItem('vp_v555_unignore','1');"
    "}"
)
if OLD_DIAG_END in content:
    content = content.replace(OLD_DIAG_END, NEW_DIAG_END, 1)
    changes += 1
    print('OK 1: v5.55 unignore migration agregada tras v5.54 block')
else:
    print('FAIL 1: v5.54 normalize marker not found')

# 2. Cambiar totalCharges del guardado inicial (excluir ignored)
OLD_TC = "totalCharges:(res.statement_txs||[]).filter(t=>t.status!=='credit').length,"
NEW_TC = "totalCharges:(res.statement_txs||[]).filter(t=>t.status!=='credit'&&t.status!=='ignored').length,"
if OLD_TC in content:
    content = content.replace(OLD_TC, NEW_TC, 1)
    changes += 1
    print('OK 2: totalCharges del guardado excluye ignored')
else:
    print('FAIL 2: totalCharges initial save pattern not found')

# 3. stmtCard: agregar liveIgnored y recalcular cargos dinamicamente
OLD_LIVE_DEFS = (
    "const liveUnrec=s.statement_txs?s.statement_txs.filter(t=>t.status==='unrecognized').length:(s.unrecognized||0);"
    "const liveMatch=s.statement_txs?s.statement_txs.filter(t=>t.status==='matched'||t.status==='reconciled').length:(s.matched||0);"
)
NEW_LIVE_DEFS = (
    "const liveUnrec=s.statement_txs?s.statement_txs.filter(t=>t.status==='unrecognized').length:(s.unrecognized||0);"
    "const liveMatch=s.statement_txs?s.statement_txs.filter(t=>t.status==='matched'||t.status==='reconciled').length:(s.matched||0);"
    "const liveIgnored=s.statement_txs?s.statement_txs.filter(t=>t.status==='ignored').length:0;"
    "const liveCharges=s.statement_txs?s.statement_txs.filter(t=>t.status!=='credit'&&t.status!=='ignored').length:(s.totalCharges||0);"
)
if OLD_LIVE_DEFS in content:
    content = content.replace(OLD_LIVE_DEFS, NEW_LIVE_DEFS, 1)
    changes += 1
    print('OK 3: liveIgnored + liveCharges agregados a stmtCard')
else:
    print('FAIL 3: stmtCard liveMatch/liveUnrec defs not found')

# 4. stmtCard render: usar liveCharges en lugar de s.totalCharges
# Need to find the Cargos card and replace s.totalCharges with liveCharges
OLD_CARGOS_RENDER = '"<div style=\\"text-align:center;background:var(--bg3);border-radius:8px;padding:5px\\"><p style=\\"font-size:14px;font-weight:700\\">\'+s.totalCharges+\'</p><p style=\\"font-size:9px;color:var(--tx2)\\">Cargos</p></div>\''
# Search literally for s.totalCharges in render
TOTAL_IDX = content.find('s.totalCharges')
print(f'   debug: s.totalCharges found at index {TOTAL_IDX}')
# Replace s.totalCharges with liveCharges in stmtCard render (1 occurrence expected for the card itself)
if 's.totalCharges' in content:
    # Count occurrences
    n_occ = content.count('s.totalCharges')
    print(f'   debug: s.totalCharges total occurrences = {n_occ}')
    # We want to replace only the render one, not the save one (already renamed in step 2)
    # Find context "Cargos</p>" - the totalCharges right before it
    cargos_pos = content.find("font-size:9px;color:var(--tx2)\">Cargos</p>")
    if cargos_pos > 0:
        # Search backwards for s.totalCharges
        prefix = content[max(0,cargos_pos-200):cargos_pos]
        last_tc = prefix.rfind('s.totalCharges')
        if last_tc >= 0:
            abs_pos = max(0,cargos_pos-200)+last_tc
            content = content[:abs_pos] + 'liveCharges' + content[abs_pos+len('s.totalCharges'):]
            changes += 1
            print('OK 4: render Cargos usa liveCharges')
        else:
            print('FAIL 4a: s.totalCharges no encontrado cerca de Cargos card')
    else:
        print('FAIL 4: Cargos label no encontrado')

# 5. stmtCard: agregar badge ignorados si > 0
# Insertar despues del summary y antes del boton, mostrar mini-badge
OLD_SUMMARY_PLUS = "+summary+(s.statement_txs&&s.statement_txs.length>0&&liveUnrec>0?"
NEW_SUMMARY_PLUS = (
    "+(liveIgnored>0?'<div style=\"font-size:10px;color:var(--tx3);margin-top:4px;text-align:center\">'+liveIgnored+' ignorado'+(liveIgnored>1?'s':'')+' (no contados)</div>':'')"
    "+summary+(s.statement_txs&&s.statement_txs.length>0&&liveUnrec>0?"
)
if OLD_SUMMARY_PLUS in content:
    content = content.replace(OLD_SUMMARY_PLUS, NEW_SUMMARY_PLUS, 1)
    changes += 1
    print('OK 5: badge ignorados agregado a stmtCard')
else:
    print('FAIL 5: summary+ junction pattern not found')

# Bump APP_VERSION -> v5.55
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.55', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK Version: {old_ver_str} -> v5.55')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
