#!/usr/bin/env python3
"""
fix_recon_reupload.py — Alex · Protección al re-subir estado de cuenta
Root cause: al re-subir el mismo PDF (o borrar y re-subir), los cargos ya
conciliados no están en `pend` (filtrados), por lo que Claude los marca como
"unrecognized". Si el usuario los vuelve a aprobar → DUPLICADO.

Fix:
1. Tercer pass post-Claude: revisa unrecognized contra S.txs reconciled.
   Si hay match (monto ±5%, palabra clave, fecha ±14 días) → status='matched'.
   Esto evita que cargos ya conciliados reaparezcan como "No reconocidos".

2. Statement delete: advertencia explícita de que los cargos conciliados
   quedan intactos (no se revierten) — el usuario sabe qué espera si re-sube.

3. dupIdx dedup: ampliar tolerancia — comparar también por fecha ±3 días
   para capturar estados del mismo período aunque Claude devuelva fechas
   ligeramente distintas.

4. Bump v5.12
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ── 1. Tercer pass: reconciled vs unrecognized ────────────────────────────────
# Se inserta DESPUÉS del local matching pass y ANTES del bloque de IDs
OLD_AFTER_LOCAL = (
    "console.log('[Recon] Local match:',st.merchant,'->',_m.merchant);}}})"
    ";"
    "}"
    # Original reconcile-by-IDs block
    "if(res.statement_txs){const ids=res.statement_txs.filter(t=>t.matched_id)"
)
NEW_AFTER_LOCAL = (
    "console.log('[Recon] Local match:',st.merchant,'->',_m.merchant);}}})"
    ";"
    "}"
    # Tercer pass: protección re-subida — cargos ya conciliados
    "if(res.statement_txs){"
    "const _rc=S.txs.filter(t=>t.entity===S.entity&&t.status==='reconciled');"
    "res.statement_txs.forEach(st=>{"
    "if(st.status==='unrecognized'&&!st.matched_id){"
    "const _sa=parseFloat(st.amount||0);"
    "const _sw=(st.merchant||'').toLowerCase().replace(/[^a-z0-9]/g,' ').split(/\\s+/).filter(w=>w.length>=3);"
    "const _sd=new Date(st.date||'');"
    "const _m=_rc.find(tx=>{"
    "const _ta=Math.abs(parseFloat(tx.amount||0));"
    "const _tw=(tx.merchant||'').toLowerCase().replace(/[^a-z0-9]/g,' ').split(/\\s+/).filter(w=>w.length>=3);"
    "const _td=new Date(tx.date||'');"
    "return _sa>0&&Math.abs(_ta-_sa)/_sa<0.05"
    "&&_sw.some(w=>_tw.some(tw=>tw.includes(w)||w.includes(tw)))"
    "&&!isNaN(_sd)&&!isNaN(_td)&&Math.abs(_sd-_td)/864e5<=14;"
    "});"
    "if(_m){st.status='matched';st.matched_id=_m.id;"
    "console.log('[Recon] Already reconciled:',st.merchant);}"
    "}});"
    "}"
    # Original reconcile-by-IDs block
    "if(res.statement_txs){const ids=res.statement_txs.filter(t=>t.matched_id)"
)
if OLD_AFTER_LOCAL in content:
    content = content.replace(OLD_AFTER_LOCAL, NEW_AFTER_LOCAL, 1)
    changes += 1
    print('OK 1: tercer pass — reconciled vs unrecognized agregado')
else:
    print('FAIL 1: local pass end not found')
    idx = content.find('console.log(\'[Recon] Local match:\'')
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx:idx+80])}')

# ── 2. Statement delete: mejorar advertencia ──────────────────────────────────
OLD_DEL_STMT = (
    "if(!confirm('¿Eliminar este registro de estado de cuenta?'))return;"
    "S.statements=S.statements.filter(s=>s.id!==id);persist();render();"
)
NEW_DEL_STMT = (
    "if(!confirm('\\u00bfEliminar este registro de estado de cuenta?\\n\\n"
    "Los cargos ya conciliados permanecen en tu historial con estatus \\\"Conciliado\\\" "
    "\\u2014 no se revertir\\u00e1n.\\n\\n"
    "Si vuelves a subir el mismo PDF, los cargos ya conciliados "
    "ser\\u00e1n reconocidos autom\\u00e1ticamente y no se duplicar\\u00e1n.'))return;"
    "S.statements=S.statements.filter(s=>s.id!==id);persist();render();"
)
if OLD_DEL_STMT in content:
    content = content.replace(OLD_DEL_STMT, NEW_DEL_STMT, 1)
    changes += 1
    print('OK 2: delete statement — advertencia mejorada')
else:
    print('FAIL 2: delete statement pattern not found')
    idx = content.find('Eliminar este registro de estado de cuenta')
    if idx > 0:
        print(f'  at {idx}: {repr(content[max(0,idx-30):idx+100])}')

# ── 3. dupIdx: comparar bank Y fecha de corte con tolerancia ─────────────────
# Actualmente compara bank===stmt.bank && cutDate===stmt.cutDate (exacto)
# Mejora: también acepta si cutDate difiere ≤3 días (Claude puede redondear)
OLD_DUPIDX = (
    "const _dupIdx=S.statements.findIndex(s=>s.entity===S.entity&&s.bank===stmt.bank&&s.cutDate===stmt.cutDate);"
)
NEW_DUPIDX = (
    "const _dupIdx=S.statements.findIndex(s=>{"
    "if(s.entity!==S.entity||s.bank!==stmt.bank)return false;"
    "const _dd=Math.abs(new Date(s.cutDate)-new Date(stmt.cutDate))/864e5;"
    "return _dd<=3;"
    "});"
)
if OLD_DUPIDX in content:
    content = content.replace(OLD_DUPIDX, NEW_DUPIDX, 1)
    changes += 1
    print('OK 3: dupIdx — tolerancia ±3 días en fecha de corte')
else:
    print('FAIL 3: dupIdx pattern not found')
    idx = content.find('_dupIdx=S.statements.findIndex')
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx:idx+100])}')

# ── 4. Bump APP_VERSION → v5.12 ───────────────────────────────────────────────
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.12', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK 4: {old_ver_str} → v5.12')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
