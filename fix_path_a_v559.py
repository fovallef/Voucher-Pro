#!/usr/bin/env python3
"""
fix_path_a_v559.py — Path A: des-vincular linkages sospechosas v5.59

Kai bug hunt #004 cerro: 5 linkages sospechosas detectadas en Amex.
Francisco autoriza Path A: matched_id=null, status='unrecognized' para
todas las stx donde el audit detecta amount mismatch o merchants disjoint.

Misma logica que v5.57 audit pero con accion. Bidirectional cleanup
del tx.statementRef.

Adicional: bump --tx2 a #a8a8c8 (D4 aprobada).
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# 1. v5.59 Path A: des-vincular sospechosos
OLD_AUDIT_END = (
    "console.log('[VoucherPro] v5.57 audit Kai-M1: '+_suspicious+' linkages sospechosas en '+S.statements.length+' statements');"
    "_audit.slice(0,30).forEach(a=>console.log('[VoucherPro]   '+a));"
    "if(_audit.length>30)console.log('[VoucherPro]   ... ('+(_audit.length-30)+' mas omitidas)');"
    "localStorage.setItem('vp_v557_audit_dump','1');"
    "}"
)
NEW_PATH_A = (
    "console.log('[VoucherPro] v5.57 audit Kai-M1: '+_suspicious+' linkages sospechosas en '+S.statements.length+' statements');"
    "_audit.slice(0,30).forEach(a=>console.log('[VoucherPro]   '+a));"
    "if(_audit.length>30)console.log('[VoucherPro]   ... ('+(_audit.length-30)+' mas omitidas)');"
    "localStorage.setItem('vp_v557_audit_dump','1');"
    "}"
    "if(!localStorage.getItem('vp_v559_unlink_suspects')){"
    "let _unlinked=0;"
    "let _details=[];"
    "S.statements.forEach(s=>{"
    "if(!s.statement_txs)return;"
    "s.statement_txs.forEach(stx=>{"
    "if(stx.status!=='matched'&&stx.status!=='reconciled')return;"
    "if(!stx.matched_id)return;"
    "const _t=S.txs.find(x=>x.id===stx.matched_id);"
    "if(!_t){"
    "stx.matched_id=null;"
    "stx.status='unrecognized';"
    "_unlinked++;"
    "_details.push((s.bank||'?').slice(0,12)+' '+(stx.merchant||'?').slice(0,15)+' (tx fantasma)');"
    "return;"
    "}"
    "let _suspect=false;"
    "let _reason='';"
    "if(Math.abs(parseFloat(stx.amount||0)-parseFloat(_t.amount||0))>0.5){"
    "_suspect=true;"
    "_reason='amount $'+stx.amount+' vs $'+_t.amount;"
    "}"
    "const _stxM=(stx.merchant||'').toLowerCase().replace(/[^a-z0-9]/g,'').slice(0,6);"
    "const _txM=(_t.merchant||'').toLowerCase().replace(/[^a-z0-9]/g,'').slice(0,6);"
    "if(_stxM&&_txM&&_stxM[0]!==_txM[0]&&!_stxM.includes(_txM.slice(0,3))&&!_txM.includes(_stxM.slice(0,3))){"
    "_suspect=true;"
    "_reason=_reason?_reason+' + merchants disjoint':'merchants disjoint';"
    "}"
    "if(_suspect){"
    "stx.matched_id=null;"
    "stx.status='unrecognized';"
    "if(_t.statementRef&&_t.statementRef.statementId===s.id&&_t.statementRef.statementTxId===stx.id){"
    "_t.statementRef=null;"
    "}"
    "_unlinked++;"
    "_details.push((s.bank||'?').slice(0,12)+' '+(stx.merchant||'?').slice(0,15)+' ('+_reason+')');"
    "}"
    "});"
    "});"
    "console.log('[VoucherPro] v5.59 Path A: '+_unlinked+' linkages sospechosas des-vinculadas (status=unrecognized)');"
    "_details.forEach(d=>console.log('[VoucherPro]   '+d));"
    "localStorage.setItem('vp_v559_unlink_suspects','1');"
    "}"
)
if OLD_AUDIT_END in content:
    content = content.replace(OLD_AUDIT_END, NEW_PATH_A, 1)
    changes += 1
    print('OK 1: Path A des-vinculacion agregada tras v5.57 audit')
else:
    print('FAIL 1: v5.57 audit end marker not found')

# 2. D4: --tx2 de #8a8ab0 a #a8a8c8
OLD_TX2 = "--tx:#f0f0f8;--tx2:#8a8ab0;--tx3:#6e6e94;"
NEW_TX2 = "--tx:#f0f0f8;--tx2:#a8a8c8;--tx3:#6e6e94;"
if OLD_TX2 in content:
    content = content.replace(OLD_TX2, NEW_TX2, 1)
    changes += 1
    print('OK 2: --tx2 elevado a #a8a8c8 (D4)')
else:
    print('FAIL 2: --tx2 token pattern not found')

# Bump APP_VERSION -> v5.59
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.59', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK Version: {old_ver_str} -> v5.59')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
