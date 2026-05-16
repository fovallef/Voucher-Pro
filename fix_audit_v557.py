#!/usr/bin/env python3
"""
fix_audit_v557.py — Audit linkage + paidAt validation v5.57

Kai-M1: audit dump retroactivo que escanea todos los statements y
reporta linkages sospechosas (matched stx con tx fantasma, bidirectional
roto, merchant/amount disjoint).

Kai-M2: isTxClosed valida paidAt como fecha real, no solo truthy.
Previene que strings corruptos bloqueen edicion permanente.
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# 1. v5.57 audit dump despues del v5.55 unignore
OLD_UNIGNORE_END = (
    "console.log('[VoucherPro] v5.55 unignore: '+_unignored+' stx revertidos ignored->matched (matched_id valido); '+_keptIgnored+' kept as ignored (sin link o tx perdida)');"
    "localStorage.setItem('vp_v555_unignore','1');"
    "}"
)
NEW_AUDIT = (
    "console.log('[VoucherPro] v5.55 unignore: '+_unignored+' stx revertidos ignored->matched (matched_id valido); '+_keptIgnored+' kept as ignored (sin link o tx perdida)');"
    "localStorage.setItem('vp_v555_unignore','1');"
    "}"
    "if(!localStorage.getItem('vp_v557_audit_dump')){"
    "let _audit=[];"
    "let _suspicious=0;"
    "S.statements.forEach(s=>{"
    "if(!s.statement_txs)return;"
    "s.statement_txs.forEach(stx=>{"
    "if(stx.status!=='matched'&&stx.status!=='reconciled')return;"
    "if(!stx.matched_id)return;"
    "const _t=S.txs.find(x=>x.id===stx.matched_id);"
    "if(!_t){_audit.push((s.bank||'?').slice(0,15)+': stx '+(stx.merchant||'?').slice(0,18)+' apunta a tx fantasma');_suspicious++;return;}"
    "const _ref=_t.statementRef;"
    "if(!_ref||_ref.statementId!==s.id||_ref.statementTxId!==stx.id){"
    "_audit.push((s.bank||'?').slice(0,15)+': stx '+(stx.merchant||'?').slice(0,18)+' $'+stx.amount+' linkage bidir roto');"
    "_suspicious++;"
    "}else{"
    "if(Math.abs(parseFloat(stx.amount||0)-parseFloat(_t.amount||0))>0.5){"
    "_audit.push((s.bank||'?').slice(0,15)+': stx '+(stx.merchant||'?').slice(0,15)+' $'+stx.amount+' vs tx $'+_t.amount+' amount mismatch');"
    "_suspicious++;"
    "}"
    "const _stxM=(stx.merchant||'').toLowerCase().replace(/[^a-z0-9]/g,'').slice(0,6);"
    "const _txM=(_t.merchant||'').toLowerCase().replace(/[^a-z0-9]/g,'').slice(0,6);"
    "if(_stxM&&_txM&&_stxM[0]!==_txM[0]&&!_stxM.includes(_txM.slice(0,3))&&!_txM.includes(_stxM.slice(0,3))){"
    "_audit.push((s.bank||'?').slice(0,15)+': stx '+(stx.merchant||'?').slice(0,15)+' vs tx '+(_t.merchant||'?').slice(0,15)+' merchants disjoint');"
    "_suspicious++;"
    "}"
    "}"
    "});"
    "});"
    "console.log('[VoucherPro] v5.57 audit Kai-M1: '+_suspicious+' linkages sospechosas en '+S.statements.length+' statements');"
    "_audit.slice(0,30).forEach(a=>console.log('[VoucherPro]   '+a));"
    "if(_audit.length>30)console.log('[VoucherPro]   ... ('+(_audit.length-30)+' mas omitidas)');"
    "localStorage.setItem('vp_v557_audit_dump','1');"
    "}"
)
if OLD_UNIGNORE_END in content:
    content = content.replace(OLD_UNIGNORE_END, NEW_AUDIT, 1)
    changes += 1
    print('OK 1: v5.57 audit dump agregado tras v5.55 unignore')
else:
    print('FAIL 1: v5.55 unignore marker not found')

# 2. Kai-M2: isTxClosed valida paidAt como fecha
OLD_ISCLOSED = (
    "function isTxClosed(t){if(!t||!t.statementRef||!t.statementRef.statementId)return false;"
    "const _s=S.statements.find(x=>x.id===t.statementRef.statementId);"
    "return !!(_s&&_s.paidAt);}"
)
NEW_ISCLOSED = (
    "function isTxClosed(t){if(!t||!t.statementRef||!t.statementRef.statementId)return false;"
    "const _s=S.statements.find(x=>x.id===t.statementRef.statementId);"
    "if(!_s||!_s.paidAt)return false;"
    "const _d=new Date(_s.paidAt);"
    "return !isNaN(_d.getTime());}"
)
if OLD_ISCLOSED in content:
    content = content.replace(OLD_ISCLOSED, NEW_ISCLOSED, 1)
    changes += 1
    print('OK 2: isTxClosed valida paidAt como fecha real')
else:
    print('FAIL 2: isTxClosed pattern not found')

# Bump APP_VERSION -> v5.57
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.57', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK Version: {old_ver_str} -> v5.57')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
