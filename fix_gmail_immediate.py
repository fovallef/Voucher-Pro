#!/usr/bin/env python3
"""
fix_gmail_immediate.py — Alex · UX: registro inmediato al aprobar en Gmail
1. gd_approve → registro inmediato en S.txs + elimina de S.gmailResults
2. gd_reject  → r.skip=true (mueve a Ignorados, persiste)
3. rGmailDetail: labels actualizados ("Aprobar y registrar" / "Ignorar cargo")
4. rGmail: eliminar approvedCount (ya no se usa)
5. rGmail: eliminar botón "Registrar N aprobadas"
6. rGmail: toggleAllGm label → "Registrar todo"
7. attachGmail: reemplazar confirmGmailBtn+toggleAllGm → registro inmediato en bloque
8. Bump v5.5
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ── 1. attachGmailDetail: gd_approve → registro inmediato ──────────────────
OLD_APPROVE = (
    "document.getElementById('gd_approve')?.addEventListener('click',()=>{"
    "save();"
    "if(!r.card){alert('Selecciona una tarjeta de pago antes de aprobar este cargo.');return;}"
    "r.status=r.status==='approved'?'pending':'approved';"
    "S.gmailDetail=null;"
    "render();"
    "});"
)
NEW_APPROVE = (
    "document.getElementById('gd_approve')?.addEventListener('click',()=>{"
    "save();"
    "if(!r.card){alert('Selecciona una tarjeta de pago antes de aprobar este cargo.');return;}"
    "const _amt=r.tipo==='reembolso'?-Math.abs(r.amount||0):Math.abs(r.amount||0);"
    "const _dupe=S.txs.find(ex=>(ex.merchant||'').toLowerCase()===(r.merchant||'').toLowerCase()"
    "&&Math.abs(parseFloat(ex.amount||0)-Math.abs(_amt))<0.01"
    "&&Math.abs(new Date(ex.date)-new Date(r.date||td()))/(864e5)<=3&&!ex.isRecurring);"
    "if(_dupe){alert('Este cargo ya fue registrado ('+esc(_dupe.merchant)+' '+fS(Math.abs(parseFloat(_dupe.amount||0)))+').');return;}"
    "S.txs.unshift({id:uid(),entity:'personal',card:r.card,"
    "merchant:r.merchant||r.app||'',category:r.category||'restaurantes',"
    "amount:_amt,currency:r.currency||'MXN',date:r.date||td(),time:r.time||nt(),"
    "msi:null,cfdi:null,status:'pending',isManual:true,isRefund:r.tipo==='reembolso',"
    "gmailImport:true,notes:r.notes||r.items||'',createdAt:new Date().toISOString()});"
    "const _ri=S.gmailResults.findIndex(x=>x.emailId===r.emailId);"
    "if(_ri>=0)S.gmailResults.splice(_ri,1);"
    "S.gmailDetail=null;"
    "persist();"
    "render();"
    "});"
)
if OLD_APPROVE in content:
    content = content.replace(OLD_APPROVE, NEW_APPROVE, 1)
    changes += 1
    print('OK 1: gd_approve → registro inmediato')
else:
    print('FAIL 1: gd_approve handler not found')
    idx = content.find("'gd_approve'")
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx-10:idx+200])}')

# ── 2. attachGmailDetail: gd_reject → r.skip=true ────────────────────────
OLD_REJECT = (
    "document.getElementById('gd_reject')?.addEventListener('click',()=>{"
    "save();"
    "r.status=r.status==='rejected'?'pending':'rejected';"
    "S.gmailDetail=null;"
    "render();"
    "});"
)
NEW_REJECT = (
    "document.getElementById('gd_reject')?.addEventListener('click',()=>{"
    "save();"
    "r.skip=true;"
    "r.status='rejected';"
    "S.gmailDetail=null;"
    "persist();"
    "render();"
    "});"
)
if OLD_REJECT in content:
    content = content.replace(OLD_REJECT, NEW_REJECT, 1)
    changes += 1
    print('OK 2: gd_reject → r.skip=true')
else:
    print('FAIL 2: gd_reject handler not found')
    idx = content.find("'gd_reject'")
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx-10:idx+120])}')

# ── 3. rGmailDetail: botón gd_approve label ──────────────────────────────
OLD_APPROVE_BTN = (
    "'<button class=\"btn bp\" id=\"gd_approve\" style=\"margin:0\">'+"
    "(r.status==='approved'?'✅ Aprobado - Toca para quitar':'✅ Aprobar')+'</button>'"
)
NEW_APPROVE_BTN = (
    "'<button class=\"btn bp\" id=\"gd_approve\" style=\"margin:0\">✅ Aprobar y registrar</button>'"
)
if OLD_APPROVE_BTN in content:
    content = content.replace(OLD_APPROVE_BTN, NEW_APPROVE_BTN, 1)
    changes += 1
    print('OK 3: gd_approve label → "Aprobar y registrar"')
else:
    print('FAIL 3: gd_approve label not found')
    idx = content.find('"gd_approve"')
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx-5:idx+100])}')

# ── 4. rGmailDetail: botón gd_reject label ───────────────────────────────
OLD_REJECT_BTN = (
    "'<button class=\"btn bs\" id=\"gd_reject\" style=\"margin:0\">'+"
    "(r.status==='rejected'?'↩️ Quitar rechazo':'❌ Rechazar')+'</button>'"
)
NEW_REJECT_BTN = (
    "'<button class=\"btn bs\" id=\"gd_reject\" style=\"margin:0\">❌ Ignorar cargo</button>'"
)
if OLD_REJECT_BTN in content:
    content = content.replace(OLD_REJECT_BTN, NEW_REJECT_BTN, 1)
    changes += 1
    print('OK 4: gd_reject label → "Ignorar cargo"')
else:
    print('FAIL 4: gd_reject label not found')
    idx = content.find('"gd_reject"')
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx-5:idx+100])}')

# ── 5. rGmail: eliminar approvedCount ────────────────────────────────────
OLD_APPROVED_COUNT = (
    "function rGmail(){const imp=S.gmailResults.filter(r=>r.emailId&&!r.skip);"
    "const skipped=S.gmailResults.filter(r=>r.emailId&&r.skip);"
    "const approvedCount=imp.filter(r=>r.status==='approved').length;"
)
NEW_APPROVED_COUNT = (
    "function rGmail(){const imp=S.gmailResults.filter(r=>r.emailId&&!r.skip);"
    "const skipped=S.gmailResults.filter(r=>r.emailId&&r.skip);"
)
if OLD_APPROVED_COUNT in content:
    content = content.replace(OLD_APPROVED_COUNT, NEW_APPROVED_COUNT, 1)
    changes += 1
    print('OK 5: rGmail — eliminado approvedCount')
else:
    print('FAIL 5: approvedCount declaration not found')

# ── 6. rGmail: eliminar botón "Registrar N aprobadas" ────────────────────
OLD_CONFIRM_BTN = (
    "}).join('')+\n"
    "'<button class=\"btn bp\" id=\"confirmGmailBtn\" style=\"margin-top:4px\" '+(approvedCount?'':'disabled')+'>'+\n"
    "'✅ Registrar '+approvedCount+' aprobada'+(approvedCount!==1?'s':'')+\n"
    "'</button>':'')+\n"
)
NEW_CONFIRM_BTN = (
    "}).join(''):'')+\n"
)
if OLD_CONFIRM_BTN in content:
    content = content.replace(OLD_CONFIRM_BTN, NEW_CONFIRM_BTN, 1)
    changes += 1
    print('OK 6: rGmail — eliminado botón "Registrar N"')
else:
    print('FAIL 6: confirmGmailBtn button not found')
    idx = content.find('"confirmGmailBtn"')
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx-40:idx+80])}')

# ── 7. rGmail: toggleAllGm label ─────────────────────────────────────────
OLD_TOGGLE_LABEL = (
    "'<button id=\"toggleAllGm\" style=\"background:none;border:none;color:var(--in);font-size:12px;cursor:pointer\">'"
    "+(imp.every(r=>r.status==='approved')?'Quitar todo':'Aprobar todo')+'</button></div>'"
)
NEW_TOGGLE_LABEL = (
    "'<button id=\"toggleAllGm\" style=\"background:none;border:none;color:var(--in);font-size:12px;cursor:pointer\">'"
    "+(imp.some(r=>r.card)?'✅ Registrar todo':'⚠ Asigna tarjeta primero')+'</button></div>'"
)
if OLD_TOGGLE_LABEL in content:
    content = content.replace(OLD_TOGGLE_LABEL, NEW_TOGGLE_LABEL, 1)
    changes += 1
    print('OK 7: toggleAllGm label → "Registrar todo"')
else:
    print('FAIL 7: toggleAllGm label not found')
    idx = content.find('"toggleAllGm"')
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx-5:idx+150])}')

# ── 8. attachGmail: reemplazar confirmGmailBtn + toggleAllGm ─────────────
OLD_ATTACH_END = (
    "document.getElementById('confirmGmailBtn')?.addEventListener('click',doConfirmGmail);"
    "document.getElementById('toggleAllGm')?.addEventListener('click',()=>{"
    "const im=S.gmailResults.filter(r=>r.emailId&&!r.skip);"
    "const allApproved=im.every(r=>r.status==='approved');"
    "im.forEach(r=>{"
    "if(allApproved)r.status='pending';"
    "else if(r.card)r.status='approved';"
    "});"
    "render();"
    "});"
    "}"
)
NEW_ATTACH_END = (
    "document.getElementById('toggleAllGm')?.addEventListener('click',()=>{"
    "const im=S.gmailResults.filter(r=>r.emailId&&!r.skip&&r.card);"
    "if(!im.length){alert('Asigna tarjeta a cada cargo antes de registrar en bloque.');return;}"
    "let _n=0;"
    "im.forEach(r=>{"
    "const _amt=r.tipo==='reembolso'?-Math.abs(r.amount||0):Math.abs(r.amount||0);"
    "const _dupe=S.txs.find(ex=>(ex.merchant||'').toLowerCase()===(r.merchant||'').toLowerCase()"
    "&&Math.abs(parseFloat(ex.amount||0)-Math.abs(_amt))<0.01"
    "&&Math.abs(new Date(ex.date)-new Date(r.date||td()))/(864e5)<=3&&!ex.isRecurring);"
    "if(_dupe)return;"
    "S.txs.unshift({id:uid(),entity:'personal',card:r.card,"
    "merchant:r.merchant||r.app||'',category:r.category||'restaurantes',"
    "amount:_amt,currency:r.currency||'MXN',date:r.date||td(),time:r.time||nt(),"
    "msi:null,cfdi:null,status:'pending',isManual:true,isRefund:r.tipo==='reembolso',"
    "gmailImport:true,notes:r.notes||r.items||'',createdAt:new Date().toISOString()});"
    "_n++;"
    "});"
    "const _ids=new Set(im.map(r=>r.emailId));"
    "S.gmailResults=S.gmailResults.filter(r=>!_ids.has(r.emailId));"
    "persist();"
    "const _nc=S.gmailResults.filter(r=>r.emailId&&!r.skip).length;"
    "if(_nc)alert('✅ '+_n+' registrada'+(_n!==1?'s':'')+'. '+_nc+' sin tarjeta — revísalas individualmente.');"
    "else{const _d=S.txs.filter(t=>t.gmailImport).map(t=>t.date).filter(Boolean).sort().reverse();"
    "if(_d[0])S.histMonth=_d[0].slice(0,7);S.tab='history';}"
    "render();"
    "});"
    "}"
)
if OLD_ATTACH_END in content:
    content = content.replace(OLD_ATTACH_END, NEW_ATTACH_END, 1)
    changes += 1
    print('OK 8: attachGmail — toggleAllGm → registro inmediato en bloque')
else:
    print('FAIL 8: attachGmail end pattern not found')
    idx = content.find("'confirmGmailBtn'")
    if idx > 0:
        print(f'  confirmGmailBtn at {idx}: {repr(content[idx-10:idx+200])}')

# ── 9. Bump APP_VERSION → v5.5 ────────────────────────────────────────────
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.5', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK 9: {old_ver_str} → {new_ver_str}')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
