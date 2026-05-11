#!/usr/bin/env python3
"""
fix_reconresult.py - Rewrite rReconResult to eliminate nested template literals.
Root cause of Safari SyntaxError: 3 levels of backtick nesting inside rReconResult.
Fix: extract unrecog, MSI, and matched sections into helper functions,
     rewrite rReconResult using string concatenation only (no nested backticks).
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Helper functions + new rReconResult (no nested template literals, string concat only)
NEW_RECONRESULT = (
    'function rReconUnrecogCard(t,i){'
    'return \'<div style="background:rgba(239,68,68,.06);border:1px solid rgba(239,68,68,.3);border-radius:16px;padding:14px;margin-bottom:10px"id="urCard_\'+i+\'">\''
    '+\'<div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:10px">\''
    '+\'<div><p style="font-weight:700;font-size:14px">\'+esc(t.merchant)+\'</p>\''
    '+\'<p style="font-size:11px;color:#94a3b8">\'+t.date+\'· \'+fS(t.amount)+(t.currency||\'MXN\')+\'</p></div>\''
    '+\'<span style="font-size:22px">&#x2753;</span></div>\''
    '+\'<p style="font-size:11px;color:#94a3b8;margin-bottom:8px">&#xBF;Qu&#xE9; es este cargo?</p>\''
    '+\'<div style="display:flex;flex-direction:column;gap:6px">\''
    '+\'<button class="btn be"style="margin:0;padding:10px;font-size:12px"data-alta="\'+i+\'">&#x2705; Darlo de alta como gasto nuevo</button>\''
    '+\'<button class="btn bp"style="margin:0;padding:10px;font-size:12px"data-recur="\'+i+\'">&#x1F501; Es una suscripci&#xF3;n recurrente</button>\''
    '+\'<button class="btn br"style="margin:0;padding:10px;font-size:12px"data-disputar="\'+i+\'">&#x1F6A8; No lo reconozco &#x2014; disputar con el banco</button>\''
    '+\'</div></div>\';}'

    'function rReconMSICard(m,i){'
    'return \'<div style="background:rgba(99,102,241,.08);border:1px solid rgba(99,102,241,.3);border-radius:14px;padding:13px;margin-bottom:9px">\''
    '+\'<div style="display:flex;justify-content:space-between;align-items:start;margin-bottom:8px">\''
    '+\'<div><p style="font-weight:700;font-size:13px">\'+esc(m.merchant)+\'</p>\''
    '+\'<p style="font-size:11px;color:#94a3b8">\'+m.date+\' \xb7 Total: \'+fS(m.amount)+\'</p>\''
    '+\'<p style="font-size:11px;color:#818cf8;margin-top:2px">\'+m.installments+\' meses \xb7 \'+fS(m.monthly_amount)+\'/mes</p></div>\''
    '+\'<span style="font-size:20px">&#x1F4B3;</span></div>\''
    '+\'<button class="btn"style="margin:0;padding:9px;font-size:12px;background:rgba(99,102,241,.15);border:1px solid rgba(99,102,241,.4);color:#818cf8"data-msi="\'+i+\'">&#x1F4C5; Registrar compromiso MSI</button>\''
    '+\'</div>\';}'

    'function rReconMatchedCard(t){'
    'return \'<div style="background:rgba(16,185,129,.06);border:1px solid rgba(16,185,129,.2);border-radius:12px;padding:11px;margin-bottom:7px;display:flex;justify-content:space-between;align-items:center">\''
    '+\'<div><p style="font-size:13px;font-weight:500">\'+esc(t.merchant)+\'</p>\''
    '+\'<p style="font-size:11px;color:#94a3b8">\'+t.date+\'</p></div>\''
    '+\'<p style="font-size:13px;font-weight:700">\'+fS(t.amount)+\'</p></div>\';}'

    'function rReconResult(){'
    'const r=S.reconRes;if(!r)return\'\';'
    'const matched=(r.statement_txs||[]).filter(t=>t.status===\'matched\');'
    'const unrecog=(r.statement_txs||[]).filter(t=>t.status===\'unrecognized\');'
    'const totalCharges=matched.length+unrecog.length;'
    'const totalAmt=(r.statement_txs||[]).reduce((s,t)=>s+parseFloat(t.amount||0),0);'
    'var summaryBlock=r.summary?\'<div style="background:#1e293b;border-radius:10px;padding:10px;margin-bottom:14px"><p style="font-size:12px;color:#94a3b8;line-height:1.5">&#x1F916; \'+esc(r.summary)+\'</p></div>\':\'\';\n'
    'var unrecogBlock=unrecog.length?\'<p class="stit"style="color:#ef4444">&#x1F6A8; Cargos no reconocidos &#x2014; elige una acci&#xF3;n</p>\'+unrecog.map(rReconUnrecogCard).join(\'\'):\'\';\n'
    'var msiBlock=(r.msi_charges||[]).length?\'<p class="stit"style="color:#818cf8;margin-top:4px">&#x1F4C5; Cargos MSI detectados en el estado de cuenta</p>\'+(r.msi_charges||[]).map(rReconMSICard).join(\'\'):\'\';\n'
    'var matchedBlock=matched.length?\'<p class="stit"style="color:#10b981;margin-top:4px">&#x2705; Conciliados correctamente (\'+matched.length+\')</p>\'+matched.map(rReconMatchedCard).join(\'\'):\'\';\n'
    'return \'<button class="bbk"id="reconBack">&#x2190; Volver</button>\''
    '+\'<div style="background:linear-gradient(135deg,rgba(139,92,246,.12),var(--bg2));border:1px solid rgba(139,92,246,.25);border-radius:16px;padding:14px;margin-bottom:14px">\''
    '+\'<p style="font-size:11px;color:#94a3b8;margin-bottom:2px">Estado de Cuenta analizado</p>\''
    '+\'<h2 style="font-weight:700;font-size:16px;margin-bottom:8px">\'+esc(r.card_name||\'Desconocido\')+\'</h2>\''
    '+\'<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">\''
    '+\'<div><p style="font-size:10px;color:#94a3b8">Fecha de corte</p><p style="font-weight:600;font-size:13px">\''
    '+(r.cut_date||\'N/A\')+\'</p></div>\''
    '+\'<div><p style="font-size:10px;color:#94a3b8">Total a pagar</p><p style="font-weight:700;font-size:14px;color:#10b981">\''
    '+fS(r.total_balance||0)+(r.currency||\'MXN\')+\'</p></div>\''
    '+\'<div><p style="font-size:10px;color:#94a3b8">Cargos identificados</p><p style="font-weight:600;font-size:13px">\'+totalCharges+\'</p></div>\''
    '+\'<div><p style="font-size:10px;color:#94a3b8">Suma de cargos</p><p style="font-weight:600;font-size:13px">\'+fS(totalAmt)+\'</p></div>\''
    '+\'</div></div>\''
    '+\'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:14px">\''
    '+\'<div class="sbox"style="text-align:center"><div class="sv"style="color:#10b981;font-size:20px">\'+matched.length+\'</div><div class="sl">Conciliados</div></div>\''
    '+\'<div class="sbox"style="text-align:center"><div class="sv"style="color:#ef4444;font-size:20px">\'+unrecog.length+\'</div><div class="sl">No reconoc.</div></div>\''
    '+\'<div class="sbox"style="text-align:center"><div class="sv"style="font-size:16px">\'+fS(r.total_balance||0)+\'</div><div class="sl">Saldo</div></div>\''
    '+\'</div>\''
    '+summaryBlock+unrecogBlock+msiBlock+matchedBlock;}'
)

# Find the old rReconResult function boundaries
start_marker = 'function rReconResult()'
end_marker = 'function attachReconResult'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx < 0:
    print('FAIL: rReconResult not found')
    sys.exit(1)
if end_idx < 0:
    print('FAIL: attachReconResult not found')
    sys.exit(1)

old_func = content[start_idx:end_idx]
print(f'Found rReconResult: {len(old_func)} chars at pos {start_idx}')
print(f'Old paren count: opens={old_func.count(chr(40))} closes={old_func.count(chr(41))} diff={old_func.count(chr(40))-old_func.count(chr(41))}')

content = content[:start_idx] + NEW_RECONRESULT + content[end_idx:]

# Verify new function is in place
new_start = content.find('function rReconResult()')
new_end = content.find('function attachReconResult', new_start)
new_func = content[new_start:new_end]
print(f'New rReconResult: {len(new_func)} chars')
print(f'New paren count: opens={new_func.count(chr(40))} closes={new_func.count(chr(41))} diff={new_func.count(chr(40))-new_func.count(chr(41))}')

# Also bump APP_VERSION to v4.9
OLD_VER = "APP_VERSION='v4.8 \xb7 11 May 2026'"
NEW_VER = "APP_VERSION='v4.9 \xb7 11 May 2026'"
if OLD_VER in content:
    content = content.replace(OLD_VER, NEW_VER, 1)
    print('OK: APP_VERSION -> v4.9')
else:
    print('SKIP: APP_VERSION v4.8 not found')
    idx = content.find('APP_VERSION=')
    if idx > 0:
        print(f'  Found: {repr(content[idx:idx+50])}')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
