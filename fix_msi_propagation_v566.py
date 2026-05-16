#!/usr/bin/env python3
"""
fix_msi_propagation_v566.py — Pilar 3 MSI propagation v5.66

Brief 2 Pilar 3: estado de cuenta = fuente de verdad para MSI.

Migración retroactiva idempotente:
- Para cada statement.msi_charges detectado por Claude:
  - Encuentra el stx correspondiente (merchant + amount match)
  - Si stx tiene matched_id, obtén el tx vinculado
  - Aplica reglas:
    1. tx.msi=null + statement detecta -> propagar (msiSource='statement')
    2. tx.msi=M + statement detecta N != M -> statement gana
       (conservar msiUserClaimed=M, msiSource='statement')
    3-5. otros casos: no-op
- Persist al final.

Filtro MSI en historial ya funciona — solo lee t.msi truthy.
Una vez propagado retroactivamente, el filtro mostrara los reales.
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# Insertar migration block despues del v5.60 unlink_v2 block + v5.61 global persist
OLD_MARKER = "try{persist();console.log('[VoucherPro] v5.61 global persist defensivo OK');}catch(_pe){console.warn('[VoucherPro] v5.61 global persist failed',_pe);}"

NEW_MARKER = OLD_MARKER + (
    "if(!localStorage.getItem('vp_v566_msi_propagation')){"
    "let _msiNew=0;let _msiOver=0;let _msiSame=0;let _details=[];"
    "const _norm=function(m){return(m||'').toLowerCase().replace(/[^a-z0-9]/g,'').slice(0,12);};"
    "S.statements.forEach(s=>{"
    "if(!s.msi_charges||!s.msi_charges.length)return;"
    "if(!s.statement_txs)return;"
    "s.msi_charges.forEach(msi=>{"
    "const _N=parseInt(msi.installments||0);"
    "if(!_N||_N<2)return;"
    "const _nm=_norm(msi.merchant);"
    "const _am=Math.abs(parseFloat(msi.amount||0));"
    "if(!_nm||!_am)return;"
    "const _stx=s.statement_txs.find(stx=>{"
    "if(!stx.matched_id)return false;"
    "const _stxnm=_norm(stx.merchant);"
    "const _stxam=Math.abs(parseFloat(stx.amount||0));"
    "return _stxnm===_nm&&Math.abs(_stxam-_am)<1.5;"
    "});"
    "if(!_stx)return;"
    "const _tx=S.txs.find(t=>t.id===_stx.matched_id);"
    "if(!_tx)return;"
    "const _now=new Date().toISOString();"
    "if(!_tx.msi){"
    "_tx.msi=_N;_tx.msiSource='statement';_tx.msiVerifiedAt=_now;"
    "_msiNew++;"
    "_details.push((s.bank||'?').slice(0,12)+' '+(msi.merchant||'').slice(0,20)+' -> '+_N+'MSI (nuevo)');"
    "}else if(_tx.msi!==_N){"
    "_tx.msiUserClaimed=_tx.msi;_tx.msi=_N;_tx.msiSource='statement';_tx.msiVerifiedAt=_now;"
    "_msiOver++;"
    "_details.push((s.bank||'?').slice(0,12)+' '+(msi.merchant||'').slice(0,20)+': '+_tx.msiUserClaimed+'->'+_N+'MSI (override)');"
    "}else{"
    "if(!_tx.msiSource)_tx.msiSource='statement';"
    "_tx.msiVerifiedAt=_now;"
    "_msiSame++;"
    "}"
    "});"
    "});"
    "if(_msiNew>0||_msiOver>0){try{persist();}catch(_pe){console.warn('msi persist failed',_pe);}}"
    "console.log('[VoucherPro] v5.66 MSI propagation: '+_msiNew+' nuevos, '+_msiOver+' overrides, '+_msiSame+' confirmados (mismo valor)');"
    "_details.slice(0,20).forEach(d=>console.log('[VoucherPro]   '+d));"
    "if(_details.length>20)console.log('[VoucherPro]   ... ('+(_details.length-20)+' mas omitidos)');"
    "localStorage.setItem('vp_v566_msi_propagation','1');"
    "}"
)

if OLD_MARKER in content:
    content = content.replace(OLD_MARKER, NEW_MARKER, 1)
    changes += 1
    print('OK 1: MSI propagation migration agregada')
else:
    print('FAIL 1: v5.61 persist marker not found')

# Bump APP_VERSION -> v5.66
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.66', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK Version: {old_ver_str} -> v5.66')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
