#!/usr/bin/env python3
"""
fix_gmail_card_required.py — Alex · UX: tarjeta requerida en Gmail import
1. doGmailImport: card default = '' (no asumir Amex)
2. rGmailDetail: select empieza con placeholder vacío + label en amarillo cuando vacío
3. Lista Gmail: badge "⚠ Tarjeta" cuando card está vacía
4. attachGmailDetail: bloquear Aprobar si no se eligió tarjeta
5. toggleAllGm ("Aprobar todo"): saltar registros sin tarjeta
6. doConfirmGmail: safety net — no registrar si card vacía
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ── 1. doGmailImport: card default = '' ──────────────────────────────────────
OLD_CARD_DEFAULT = (
    "category:p.category||'restaurantes',"
    "card:S.pCards[0]?.name||'',"
    "subj:em.subj,"
)
NEW_CARD_DEFAULT = (
    "category:p.category||'restaurantes',"
    "card:'',"
    "subj:em.subj,"
)
if OLD_CARD_DEFAULT in content:
    content = content.replace(OLD_CARD_DEFAULT, NEW_CARD_DEFAULT, 1)
    changes += 1
    print('OK 1: doGmailImport — card default = ""')
else:
    print('FAIL 1: card default pattern not found')
    idx = content.find("card:S.pCards[0]?.name")
    if idx > 0:
        print(f'  Found at {idx}: {repr(content[idx-30:idx+60])}')

# ── 2. rGmailDetail: select con placeholder vacío + label warning ─────────────
OLD_CARD_SELECT = (
    "'<div class=\"fld\"><label>Tarjeta</label>"
    "<select class=\"inp\" id=\"gd_card\">"
    "'+cdsList.map(c=>'<option value=\"'+c+'\"'+(r.card===c?' selected':'')+'>'+c+'</option>').join('')+"
    "'</select></div>'"
)
# Label en amarillo cuando no hay tarjeta; primera option vacía como placeholder
NEW_CARD_SELECT = (
    "'<div class=\"fld\"><label style=\"color:'+(r.card?'var(--tx2)':'var(--am))+'\">Tarjeta'+(r.card?'':' ⚠ requerida')+'</label>"
    "<select class=\"inp\" id=\"gd_card\" style=\"border-color:'+(r.card?'':'var(--am)')+'\">"
    "'+(!r.card?'<option value=\"\">— Elige tarjeta —</option>':'')"
    "+cdsList.map(c=>'<option value=\"'+c+'\"'+(r.card===c?' selected':'')+'>'+c+'</option>').join('')+"
    "'</select></div>'"
)
if OLD_CARD_SELECT in content:
    content = content.replace(OLD_CARD_SELECT, NEW_CARD_SELECT, 1)
    changes += 1
    print('OK 2: rGmailDetail — card select con placeholder + warning label')
else:
    print('FAIL 2: card select pattern not found')
    idx = content.find('"gd_card"')
    if idx > 0:
        print(f'  gd_card at {idx}: {repr(content[idx-60:idx+60])}')

# ── 3. Lista Gmail: badge "⚠ Tarjeta" cuando card vacía ─────────────────────
OLD_LIST_HINT = (
    "'<p style=\"font-size:10px;color:#475569;margin-top:4px\">Toca para revisar y aprobar</p>'"
)
NEW_LIST_HINT = (
    "'<p style=\"font-size:10px;color:'+(r.card?'#475569':'var(--am)')+';margin-top:4px\">'"
    "+(r.card?'Toca para revisar y aprobar':'⚠ Toca para elegir tarjeta antes de aprobar')+"
    "'</p>'"
)
if OLD_LIST_HINT in content:
    content = content.replace(OLD_LIST_HINT, NEW_LIST_HINT, 1)
    changes += 1
    print('OK 3: Lista Gmail — badge warning cuando card vacía')
else:
    print('FAIL 3: list hint pattern not found')

# ── 4. attachGmailDetail: bloquear Aprobar si no hay tarjeta ─────────────────
OLD_APPROVE_HANDLER = (
    "document.getElementById('gd_approve')?.addEventListener('click',()=>{"
    "save();"
    "r.status=r.status==='approved'?'pending':'approved';"
    "S.gmailDetail=null;"
    "render();"
    "});"
)
NEW_APPROVE_HANDLER = (
    "document.getElementById('gd_approve')?.addEventListener('click',()=>{"
    "save();"
    "if(!r.card){"
    "alert('Selecciona una tarjeta de pago antes de aprobar este cargo.');"
    "return;"
    "}"
    "r.status=r.status==='approved'?'pending':'approved';"
    "S.gmailDetail=null;"
    "render();"
    "});"
)
if OLD_APPROVE_HANDLER in content:
    content = content.replace(OLD_APPROVE_HANDLER, NEW_APPROVE_HANDLER, 1)
    changes += 1
    print('OK 4: attachGmailDetail — bloquea Aprobar sin tarjeta')
else:
    print('FAIL 4: approve handler pattern not found')
    idx = content.find("'gd_approve'")
    if idx > 0:
        print(f'  gd_approve at {idx}: {repr(content[idx-10:idx+120])}')

# ── 5. "Aprobar todo": saltar registros sin tarjeta ──────────────────────────
OLD_TOGGLE_ALL = (
    "im.forEach(r=>{"
    "r.status=allApproved?'pending':'approved';"
    "});"
)
NEW_TOGGLE_ALL = (
    "im.forEach(r=>{"
    "if(allApproved)r.status='pending';"
    "else if(r.card)r.status='approved';"
    "});"
)
if OLD_TOGGLE_ALL in content:
    content = content.replace(OLD_TOGGLE_ALL, NEW_TOGGLE_ALL, 1)
    changes += 1
    print('OK 5: toggleAllGm — saltar registros sin tarjeta')
else:
    print('FAIL 5: toggleAllGm pattern not found')

# ── 6. doConfirmGmail: safety net — no registrar si card vacía ───────────────
OLD_CONFIRM_GUARD = (
    "if(gmDupe){console.log('[Gmail] Dupe skipped:',r.merchant);return;}"
)
NEW_CONFIRM_GUARD = (
    "if(gmDupe){console.log('[Gmail] Dupe skipped:',r.merchant);return;}"
    "if(!r.card){console.warn('[Gmail] No card — skipped:',r.merchant);return;}"
)
if OLD_CONFIRM_GUARD in content:
    content = content.replace(OLD_CONFIRM_GUARD, NEW_CONFIRM_GUARD, 1)
    changes += 1
    print('OK 6: doConfirmGmail — safety net card vacía')
else:
    print('FAIL 6: confirm guard not found')

# ── 7. Bump APP_VERSION → v5.3 ────────────────────────────────────────────────
import re
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.3', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK 7: {old_ver_str} → {new_ver_str}')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
