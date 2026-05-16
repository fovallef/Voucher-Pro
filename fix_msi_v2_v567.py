#!/usr/bin/env python3
"""
fix_msi_v2_v567.py — MSI propagation v2 + diagnostico v5.67

v5.66 reporto 0 propagaciones. Hipotesis: el stx tiene el monto
MENSUAL del cargo MSI (lo que aparece en el statement de ese mes),
mientras msi.amount tiene el TOTAL del cargo. Comparison falla.

Fix v5.67:
1. Diagnostic dump por msi_charge: merchant, total, monthly, installments
2. Logica corregida: comparar stx.amount contra monthly_amount
   (preferred) o amount/installments (fallback)
3. Nuevo flag vp_v567_msi_v2
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

OLD_MARKER = "localStorage.setItem('vp_v566_msi_propagation','1');}"

NEW_MARKER = OLD_MARKER + (
    "if(!localStorage.getItem('vp_v567_msi_v2')){"
    "let _msiNew=0;let _msiOver=0;let _msiSame=0;"
    "let _diagTotal=0;let _diagNoStx=0;let _diagNoMid=0;let _diagNoTx=0;"
    "let _details=[];let _diag=[];"
    "const _norm=function(m){return(m||'').toLowerCase().replace(/[^a-z0-9]/g,'').slice(0,12);};"
    "S.statements.forEach(s=>{"
    "if(!s.msi_charges||!s.msi_charges.length)return;"
    "if(!s.statement_txs)return;"
    "s.msi_charges.forEach(msi=>{"
    "_diagTotal++;"
    "const _N=parseInt(msi.installments||0);"
    "if(!_N||_N<2)return;"
    "const _nm=_norm(msi.merchant);"
    "if(!_nm)return;"
    "const _total=Math.abs(parseFloat(msi.amount||0));"
    "const _monthly=Math.abs(parseFloat(msi.monthly_amount||0))||(_total>0&&_N>0?_total/_N:0);"
    "if(!_monthly)return;"
    "_diag.push((s.bank||'?').slice(0,12)+' '+(msi.merchant||'').slice(0,18)+' tot=$'+_total.toFixed(0)+' mes=$'+_monthly.toFixed(0)+' x'+_N);"
    "const _stx=s.statement_txs.find(stx=>{"
    "if(!stx.matched_id)return false;"
    "const _stxnm=_norm(stx.merchant);"
    "if(_stxnm!==_nm)return false;"
    "const _stxam=Math.abs(parseFloat(stx.amount||0));"
    "return Math.abs(_stxam-_monthly)<2||Math.abs(_stxam-_total)<2;"
    "});"
    "if(!_stx){"
    "_diagNoStx++;"
    "const _anyStx=s.statement_txs.find(x=>_norm(x.merchant)===_nm);"
    "if(_anyStx&&!_anyStx.matched_id)_diagNoMid++;"
    "return;"
    "}"
    "const _tx=S.txs.find(t=>t.id===_stx.matched_id);"
    "if(!_tx){_diagNoTx++;return;}"
    "const _now=new Date().toISOString();"
    "if(!_tx.msi){"
    "_tx.msi=_N;_tx.msiSource='statement';_tx.msiVerifiedAt=_now;"
    "_msiNew++;"
    "_details.push((s.bank||'?').slice(0,12)+' '+(msi.merchant||'').slice(0,20)+' -> '+_N+'MSI');"
    "}else if(_tx.msi!==_N){"
    "_tx.msiUserClaimed=_tx.msi;_tx.msi=_N;_tx.msiSource='statement';_tx.msiVerifiedAt=_now;"
    "_msiOver++;"
    "_details.push((s.bank||'?').slice(0,12)+' '+(msi.merchant||'').slice(0,20)+': '+_tx.msiUserClaimed+'->'+_N+'MSI');"
    "}else{"
    "if(!_tx.msiSource)_tx.msiSource='statement';"
    "_tx.msiVerifiedAt=_now;_msiSame++;"
    "}"
    "});"
    "});"
    "if(_msiNew>0||_msiOver>0){try{persist();}catch(_pe){console.warn('msi persist failed',_pe);}}"
    "console.log('[VoucherPro] v5.67 MSI v2: '+_msiNew+' nuevos, '+_msiOver+' overrides, '+_msiSame+' iguales');"
    "console.log('[VoucherPro] v5.67 diag: '+_diagTotal+' msi_charges total, '+_diagNoStx+' sin stx match, '+_diagNoMid+' stx encontrado pero sin matched_id, '+_diagNoTx+' tx fantasma');"
    "_diag.slice(0,15).forEach(d=>console.log('[VoucherPro]   '+d));"
    "if(_diag.length>15)console.log('[VoucherPro]   ... ('+(_diag.length-15)+' mas)');"
    "_details.slice(0,15).forEach(d=>console.log('[VoucherPro]   propagated: '+d));"
    "localStorage.setItem('vp_v567_msi_v2','1');"
    "}"
)

if OLD_MARKER in content:
    content = content.replace(OLD_MARKER, NEW_MARKER, 1)
    changes += 1
    print('OK 1: MSI v2 with diag + monthly_amount compare')
else:
    print('FAIL 1: v5.66 marker not found')

ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.67', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK Version: {old_ver_str} -> v5.67')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
