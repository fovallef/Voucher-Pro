#!/usr/bin/env python3
"""
fix_audit_duplicados.py — Alex · Auditoría y limpieza de duplicados
Agrega sección "Auditoría de datos" en Settings con:
1. rSettings: card con botón "🔍 Buscar duplicados"
2. attachSettings: handler que:
   a) Agrupa txs por (entity, card, monto ±5%, palabra clave, fecha ±7 días)
   b) Muestra reporte: N grupos, M transacciones a eliminar
   c) Con confirmación: elimina duplicados priorizando
      reconciled > pending, y dentro de cada estatus el más antiguo
3. Bump v5.11
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ── 1. rSettings: agregar sección Auditoría ───────────────────────────────────
OLD_SETTINGS_END = (
    "Motor:Claude claude-sonnet-4-20250514</p></div>`;"
    "}"
)
NEW_SETTINGS_END = (
    "Motor:Claude claude-sonnet-4-20250514</p></div>"
    "<div class=\"card\" style=\"margin-top:12px\">"
    "<p style=\"font-weight:700;font-size:12px;margin-bottom:6px\">&#x1F50D; Auditor&#xED;a de datos</p>"
    "<p style=\"font-size:11px;color:var(--tx3);margin-bottom:10px\">"
    "Detecta cargos duplicados entre escaneos, Gmail e importaciones. "
    "Prioriza conciliados sobre pendientes como fuente de verdad.</p>"
    "<button class=\"btn bs\" id=\"auditDupBtn\" style=\"font-size:13px\">"
    "&#x1F50D; Buscar y limpiar duplicados</button>"
    "</div>`;"
    "}"
)
if OLD_SETTINGS_END in content:
    content = content.replace(OLD_SETTINGS_END, NEW_SETTINGS_END, 1)
    changes += 1
    print('OK 1: rSettings — sección Auditoría agregada')
else:
    print('FAIL 1: rSettings end not found')
    idx = content.find('Motor:Claude')
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx:idx+80])}')

# ── 2. attachSettings: handler auditDupBtn ────────────────────────────────────
OLD_ATTACH_END = (
    "1500);}});"
    "}"
    "\nfunction rTxEditModal"
)
NEW_ATTACH_END = (
    "1500);}});"
    # --- audit handler ---
    "document.getElementById('auditDupBtn')?.addEventListener('click',()=>{"
    # Step 1: build duplicate groups
    "const _txs=S.txs;"
    "const _seen=new Set();"
    "const _groups=[];"
    "for(let _i=0;_i<_txs.length;_i++){"
    "if(_seen.has(_txs[_i].id))continue;"
    "const _a=_txs[_i];"
    "const _grp=[_a];"
    "_seen.add(_a.id);"
    "for(let _j=_i+1;_j<_txs.length;_j++){"
    "if(_seen.has(_txs[_j].id))continue;"
    "const _b=_txs[_j];"
    "if(_a.entity!==_b.entity||_a.card!==_b.card)continue;"
    "const _aA=Math.abs(parseFloat(_a.amount||0));"
    "const _bA=Math.abs(parseFloat(_b.amount||0));"
    "if(_aA===0||Math.abs(_aA-_bA)/_aA>0.05)continue;"
    "const _aW=(_a.merchant||'').toLowerCase().replace(/[^a-z0-9]/g,' ').split(/\\s+/).filter(w=>w.length>=3);"
    "const _bW=(_b.merchant||'').toLowerCase().replace(/[^a-z0-9]/g,' ').split(/\\s+/).filter(w=>w.length>=3);"
    "if(!_aW.some(w=>_bW.some(bw=>bw.includes(w)||w.includes(bw))))continue;"
    "const _dd=Math.abs(new Date(_a.date)-new Date(_b.date))/864e5;"
    "if(_dd>7)continue;"
    "_grp.push(_b);_seen.add(_b.id);"
    "}"
    "if(_grp.length>1)_groups.push(_grp);"
    "}"
    # No duplicates
    "if(!_groups.length){alert('\\u2705 Sin duplicados detectados.\\nTodas las transacciones parecen \\u00fanicas.');return;}"
    # Build removal set
    "const _toRem=new Set();"
    "const _detail=[];"
    "_groups.forEach(_grp=>{"
    "const _rec=_grp.filter(t=>t.status==='reconciled').sort((a,b)=>new Date(a.createdAt)-new Date(b.createdAt));"
    "const _pnd=_grp.filter(t=>t.status==='pending').sort((a,b)=>new Date(a.createdAt)-new Date(b.createdAt));"
    "_detail.push(_grp[0].merchant+'  $'+parseFloat(_grp[0].amount||0).toFixed(2)+'  ('+_grp.length+' cop.)');"
    "if(_rec.length>0){"
    "_pnd.forEach(t=>_toRem.add(t.id));"
    "_rec.slice(1).forEach(t=>_toRem.add(t.id));"
    "}else if(_pnd.length>1){"
    "_pnd.slice(1).forEach(t=>_toRem.add(t.id));"
    "}"
    "});"
    # Confirm dialog
    "const _msg='Encontr\\u00e9 '+_groups.length+' grupo(s) de posibles duplicados:\\n'"
    "+_detail.slice(0,8).join('\\n')+(_detail.length>8?'\\n...y '+(_detail.length-8)+' m\\u00e1s':'')+'\\n\\n'"
    "+'Se eliminar\\u00e1n '+_toRem.size+' transacci\\u00f3n(es) duplicada(s).\\n'"
    "+'Estrategia: conciliado > pendiente; m\\u00e1s antiguo gana.\\n\\n'"
    "+'\\u00bfLimpiar autom\\u00e1ticamente?';"
    "if(!confirm(_msg))return;"
    "S.txs=S.txs.filter(t=>!_toRem.has(t.id));"
    "persist();"
    "alert('\\u2705 Limpieza completa.\\n'+_toRem.size+' duplicado(s) eliminado(s).\\nTransacciones restantes: '+S.txs.length);"
    "render();"
    "});"
    "}"
    "\nfunction rTxEditModal"
)
if OLD_ATTACH_END in content:
    content = content.replace(OLD_ATTACH_END, NEW_ATTACH_END, 1)
    changes += 1
    print('OK 2: attachSettings — handler auditDupBtn agregado')
else:
    print('FAIL 2: attachSettings end not found')
    idx = content.find('1500);}});')
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx:idx+50])}')

# ── 3. Bump APP_VERSION → v5.11 ───────────────────────────────────────────────
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.11', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK 3: {old_ver_str} → v5.11')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
