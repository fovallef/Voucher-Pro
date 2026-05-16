#!/usr/bin/env python3
"""
fix_audit_dashboard_v560.py — Pilar 2: Audit Dashboard visible v5.60

Brief 2 Pilar 2: card en Dashboard con estado de integridad.

Implementacion:
1. Helper getAuditSummary() retorna:
   - issues: count de auditInvariants()
   - migrations: count de localStorage keys vp_v5*
   - unrecognized: total stx con status unrecognized en todos statements
   - lastAt: timestamp ISO de ultima verificacion
2. Auto-run auditInvariants en load + store timestamp en localStorage vp_last_audit
3. Card visual al inicio de rDash con los 4 indicadores
4. Click en card -> tab Config (donde esta el panel de invariantes existente)
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# 1. Helper getAuditSummary - insertar antes de function rDash
OLD_RDASH_START = "function rDash(){"
NEW_HELPER = (
    "function getAuditSummary(){"
    "const issues=auditInvariants();"
    "let migrations=0;"
    "for(let i=0;i<localStorage.length;i++){"
    "const k=localStorage.key(i);"
    "if(k&&k.startsWith('vp_v5'))migrations++;"
    "}"
    "let unrec=0;"
    "S.statements.forEach(s=>{"
    "if(!s.statement_txs)return;"
    "s.statement_txs.forEach(stx=>{if(stx.status==='unrecognized')unrec++;});"
    "});"
    "const lastAt=localStorage.getItem('vp_last_audit')||null;"
    "return{issues:issues.length,migrations,unrec,lastAt};"
    "}"
    "function fmtRelTime(iso){"
    "if(!iso)return 'nunca';"
    "const d=new Date(iso);"
    "if(isNaN(d))return 'desconocido';"
    "const sec=Math.floor((Date.now()-d.getTime())/1000);"
    "if(sec<60)return 'hace '+sec+'s';"
    "if(sec<3600)return 'hace '+Math.floor(sec/60)+' min';"
    "if(sec<86400)return 'hace '+Math.floor(sec/3600)+' h';"
    "return 'hace '+Math.floor(sec/86400)+' d';"
    "}"
    "function rDash(){"
)
if OLD_RDASH_START in content:
    content = content.replace(OLD_RDASH_START, NEW_HELPER, 1)
    changes += 1
    print('OK 1: helpers getAuditSummary + fmtRelTime agregados')
else:
    print('FAIL 1: rDash start not found')

# 2. Card visual al inicio del Dashboard (despues del dashNav, antes del check de empty)
OLD_DASHNAV_RETURN = (
    "if(!mxn.length&&!usd.length)return dashNav+"
    "'<div class=\"empty\"><div class=\"ei\">\U0001F4CA</div>"
    "<p style=\"font-size:15px;font-weight:600\">Sin gastos en '+mLabel+'</p>"
    "<p style=\"font-size:12px;margin-top:6px;color:var(--tx3)\">Escanea un voucher o agrega un gasto manual</p></div>';"
)
NEW_WITH_AUDIT_CARD = (
    "const _au=getAuditSummary();"
    "const _auBg=_au.issues>0?'rgba(239,68,68,.08)':'rgba(16,185,129,.06)';"
    "const _auBd=_au.issues>0?'rgba(239,68,68,.25)':'rgba(16,185,129,.2)';"
    "const _auIcon=_au.issues>0?'⚠️':'✅';"
    "const _auColor=_au.issues>0?'#ef4444':'#10b981';"
    "const _auCard='<div id=\"auCard\" style=\"background:'+_auBg+';border:1px solid '+_auBd+';border-radius:14px;padding:11px 13px;margin-bottom:12px;cursor:pointer\">"
    "<div style=\"display:flex;justify-content:space-between;align-items:center;margin-bottom:6px\">"
    "<div style=\"display:flex;align-items:center;gap:6px\">"
    "<span style=\"font-size:14px\">🔍</span>"
    "<span style=\"font-size:12px;font-weight:700;color:var(--tx)\">Integridad de datos</span>"
    "</div>"
    "<span style=\"font-size:10px;color:var(--tx3)\">'+fmtRelTime(_au.lastAt)+'</span>"
    "</div>"
    "<div style=\"display:flex;justify-content:space-between;gap:8px\">"
    "<div style=\"flex:1;text-align:center\"><p style=\"font-size:16px;font-weight:700;color:'+_auColor+'\">'+_auIcon+' '+_au.issues+'</p><p style=\"font-size:9px;color:var(--tx2)\">Invariantes</p></div>"
    "<div style=\"flex:1;text-align:center\"><p style=\"font-size:16px;font-weight:700;color:var(--tx)\">'+_au.migrations+'</p><p style=\"font-size:9px;color:var(--tx2)\">Migraciones</p></div>"
    "<div style=\"flex:1;text-align:center\"><p style=\"font-size:16px;font-weight:700;color:'+(_au.unrec>0?'#f59e0b':'var(--tx)')+'\">'+_au.unrec+'</p><p style=\"font-size:9px;color:var(--tx2)\">Sin reconocer</p></div>"
    "</div>"
    "<p style=\"font-size:10px;color:var(--tx3);margin-top:6px;text-align:center\">Tap para ver detalle en Config</p>"
    "</div>';"
    "if(!mxn.length&&!usd.length)return dashNav+_auCard+"
    "'<div class=\"empty\"><div class=\"ei\">\U0001F4CA</div>"
    "<p style=\"font-size:15px;font-weight:600\">Sin gastos en '+mLabel+'</p>"
    "<p style=\"font-size:12px;margin-top:6px;color:var(--tx3)\">Escanea un voucher o agrega un gasto manual</p></div>';"
)
if OLD_DASHNAV_RETURN in content:
    content = content.replace(OLD_DASHNAV_RETURN, NEW_WITH_AUDIT_CARD, 1)
    changes += 1
    print('OK 2: audit card insertado en empty-state path')
else:
    print('FAIL 2: dashNav empty return pattern not found')

# 3. Insertar _auCard tambien en el path NO-empty (donde se construye el dashboard normal)
# Buscar el return principal del rDash que no es empty. Probablemente termina con 'return dashNav+...'
# Vamos a buscar 'return dashNav+summaryCard' o similar
OLD_NORMAL_RETURN = "return dashNav+summaryCard"
NEW_NORMAL_RETURN = "return dashNav+_auCard+summaryCard"
if OLD_NORMAL_RETURN in content:
    content = content.replace(OLD_NORMAL_RETURN, NEW_NORMAL_RETURN, 1)
    changes += 1
    print('OK 3: audit card insertado en normal path')
else:
    # Maybe it's a different pattern - try alternative
    m = re.search(r'return dashNav\+(\w+)', content)
    if m:
        print(f'   debug: found return dashNav+{m.group(1)}, trying that')
        old_alt = f"return dashNav+{m.group(1)}"
        new_alt = f"return dashNav+_auCard+{m.group(1)}"
        # only replace first (skip the empty path one already done)
        idx = content.find(old_alt)
        if idx > 0:
            content = content[:idx] + new_alt + content[idx+len(old_alt):]
            changes += 1
            print(f'OK 3 (alt): audit card insertado antes de {m.group(1)}')
    else:
        print('FAIL 3: normal rDash return pattern not found')

# 4. Auto-run audit + store timestamp en load - despues del v5.59 unlink block
OLD_V559_END = (
    "console.log('[VoucherPro] v5.59 Path A: '+_unlinked+' linkages sospechosas des-vinculadas (status=unrecognized)');"
    "_details.forEach(d=>console.log('[VoucherPro]   '+d));"
    "localStorage.setItem('vp_v559_unlink_suspects','1');"
    "}"
)
NEW_AUTOAUDIT = (
    "console.log('[VoucherPro] v5.59 Path A: '+_unlinked+' linkages sospechosas des-vinculadas (status=unrecognized)');"
    "_details.forEach(d=>console.log('[VoucherPro]   '+d));"
    "localStorage.setItem('vp_v559_unlink_suspects','1');"
    "}"
    "try{const _aiss=auditInvariants();localStorage.setItem('vp_last_audit',new Date().toISOString());console.log('[VoucherPro] v5.60 audit auto: '+_aiss.length+' invariantes en sesion');}catch(e){console.warn('audit auto failed',e);}"
)
if OLD_V559_END in content:
    content = content.replace(OLD_V559_END, NEW_AUTOAUDIT, 1)
    changes += 1
    print('OK 4: auto-audit + timestamp en load')
else:
    print('FAIL 4: v5.59 end marker not found')

# 5. Click handler para auCard -> tab settings
# Find attachDash or similar
OLD_ATTACHDASH = "function attachDash()"
if OLD_ATTACHDASH in content:
    # Insert click handler at start of function body
    idx = content.find(OLD_ATTACHDASH)
    body_start = content.find('{', idx)+1
    handler_code = "document.getElementById('auCard')?.addEventListener('click',()=>{S.tab='settings';render();});"
    content = content[:body_start] + handler_code + content[body_start:]
    changes += 1
    print('OK 5: click handler auCard -> tab settings')
else:
    print('FAIL 5: attachDash function not found')

# Bump APP_VERSION -> v5.60
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.60', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK Version: {old_ver_str} -> v5.60')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
