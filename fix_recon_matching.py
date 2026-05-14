#!/usr/bin/env python3
"""
fix_recon_matching.py — Alex · Conciliación: transacciones pendientes no encontradas
Root cause: Claude falla el matching cuando:
  a) la lista incluye cargos ya conciliados (ruido)
  b) tolerancia de fecha/monto demasiado estricta (7 días, ±1%)
  c) el nombre del comercio difiere levemente entre el PDF y el voucher

Fix:
1. pend filter: excluir reconciled → lista más limpia para Claude
2. Prompt: ampliar a 14 días y ±5%, pedir coincidencia parcial de nombre
3. Local matching pass post-Claude: sweep JS que detecta lo que Claude omitió
   (match local: monto ±5%, alguna palabra clave común, fecha ≤14 días)
4. Bump v5.10
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ── 1. pend filter: excluir reconciled ───────────────────────────────────────
OLD_PEND = (
    "const pend=S.txs.filter(t=>t.entity===S.entity);"
)
NEW_PEND = (
    "const pend=S.txs.filter(t=>t.entity===S.entity&&t.status!=='reconciled');"
)
if OLD_PEND in content:
    content = content.replace(OLD_PEND, NEW_PEND, 1)
    changes += 1
    print('OK 1: pend filter — excluye reconciled')
else:
    print('FAIL 1: pend filter not found')

# ── 2. Prompt: ampliar tolerancias de matching ────────────────────────────────
OLD_RULES = (
    "cada cargo compara:-Nombre similar(ignora mayúsculas)"
    "-Monto igual(±1%)-Fecha dentro de 7 días"
)
NEW_RULES = (
    "cada cargo compara:-Nombre similar(ignora mayúsculas,"
    "ignora acentos y caracteres especiales,coincidencia parcial de palabras)"
    "-Monto igual(±5%,considera equivalencia USD↔MXN si aplica)"
    "-Fecha dentro de 14 días"
)
if OLD_RULES in content:
    content = content.replace(OLD_RULES, NEW_RULES, 1)
    changes += 1
    print('OK 2: prompt — tolerancias ampliadas a 14 días / ±5%')
else:
    print('FAIL 2: matching rules not found')
    idx = content.find('cada cargo compara')
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx:idx+100])}')

# ── 3. Local matching pass post-Claude (antes del reconcile de IDs) ───────────
# Se inserta ANTES del bloque if(res.statement_txs){const ids=...} existente
OLD_IDS_BLOCK = (
    "));if(res.statement_txs){const ids=res.statement_txs.filter(t=>t.matched_id)"
)
NEW_IDS_BLOCK = (
    "));"
    # Local matching pass
    "if(res.statement_txs){"
    "const _pt=S.txs.filter(t=>t.entity===S.entity&&t.status!=='reconciled');"
    "res.statement_txs.forEach(st=>{"
    "if(st.status==='unrecognized'&&!st.matched_id){"
    "const _sa=parseFloat(st.amount||0);"
    "const _sw=(st.merchant||'').toLowerCase().replace(/[^a-z0-9]/g,' ').split(/\\s+/).filter(w=>w.length>=3);"
    "const _sd=new Date(st.date||'');"
    "const _m=_pt.find(tx=>{"
    "const _ta=Math.abs(parseFloat(tx.amount||0));"
    "const _tw=(tx.merchant||'').toLowerCase().replace(/[^a-z0-9]/g,' ').split(/\\s+/).filter(w=>w.length>=3);"
    "const _td=new Date(tx.date||'');"
    "const _amtOk=_sa>0&&Math.abs(_ta-_sa)/_sa<0.05;"
    "const _wOk=_sw.some(w=>_tw.some(tw=>tw.includes(w)||w.includes(tw)));"
    "const _dOk=!isNaN(_sd)&&!isNaN(_td)&&Math.abs(_sd-_td)/864e5<=14;"
    "return _amtOk&&_wOk&&_dOk;"
    "});"
    "if(_m){st.status='matched';st.matched_id=_m.id;"
    "console.log('[Recon] Local match:',st.merchant,'->',_m.merchant);}"
    "}});"
    "}"
    # Original block
    "if(res.statement_txs){const ids=res.statement_txs.filter(t=>t.matched_id)"
)
if OLD_IDS_BLOCK in content:
    content = content.replace(OLD_IDS_BLOCK, NEW_IDS_BLOCK, 1)
    changes += 1
    print('OK 3: local matching pass agregado post-Claude')
else:
    print('FAIL 3: ids block not found')
    idx = content.find('if(res.statement_txs){const ids=')
    if idx > 0:
        print(f'  at {idx}: {repr(content[max(0,idx-40):idx+60])}')

# ── 4. Bump APP_VERSION → v5.10 ───────────────────────────────────────────────
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.10', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK 4: {old_ver_str} → {new_ver_str}')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
