#!/usr/bin/env python3
"""
fix_gmail_fx.py — Alex · Conversión USD→MXN automática en Gmail import
1. fetchFXRate(): Frankfurter API (libre, sin auth) para tipo de cambio histórico
2. doGmailImport: convierte USD → MXN (rate × 1.035 est. Amex) al parsear cada email
3. rGmailDetail: card informativa de conversión si hay originalUSD
4. rGmailList: badge 💱 USD $xx → MXN $yy en items convertidos
5. persist() vp_gmr: guarda originalUSD y fxRate
6. Bump v5.6
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ── 1. Add fetchFXRate helper (after extractDate, before cleanEmailBody) ──
OLD_EXTRACT_END = "return null;}\nfunction cleanEmailBody(html){"
NEW_EXTRACT_END = (
    "return null;}\n"
    "async function fetchFXRate(date){"
    "try{"
    "const d=(date||td()).slice(0,10);"
    "const res=await fetch('https://api.frankfurter.app/'+d+'?from=USD&to=MXN');"
    "const j=await res.json();"
    "return j.rates&&j.rates.MXN?j.rates.MXN:null;"
    "}catch(e){return null;}}\n"
    "function cleanEmailBody(html){"
)
if OLD_EXTRACT_END in content:
    content = content.replace(OLD_EXTRACT_END, NEW_EXTRACT_END, 1)
    changes += 1
    print('OK 1: fetchFXRate helper added')
else:
    print('FAIL 1: extraction point not found')
    idx = content.find('function cleanEmailBody')
    if idx > 0:
        print(f'  cleanEmailBody at {idx}: {repr(content[idx-40:idx+20])}')

# ── 2. doGmailImport: USD conversion before results.push ──────────────────
OLD_PUSH = (
    "S.importedEmailIds.push(msg.id);"
    "if((p.tipo==='cargo_real'||p.tipo==='reembolso')&&parseFloat(p.amount||0)>0){"
    "results.push({emailId:msg.id,tipo:p.tipo,app:p.app||'',"
    "merchant:p.merchant||em.subj.replace(/^tu pedido de/i,'').replace(/your receipt from\\s*/i,'').replace(/tu recibo de\\s*/i,'').trim().slice(0,50)||'Sin nombre',"
    "amount:parseFloat(p.amount||0),currency:p.currency||'MXN',"
)
NEW_PUSH = (
    "S.importedEmailIds.push(msg.id);"
    "if((p.tipo==='cargo_real'||p.tipo==='reembolso')&&parseFloat(p.amount||0)>0){"
    "let _amt=parseFloat(p.amount||0);"
    "let _cur=p.currency||'MXN';"
    "let _origUSD=null;"
    "let _fxRate=null;"
    "if(_cur==='USD'&&_amt>0){"
    "const _rate=await fetchFXRate(p.date||em.date);"
    "if(_rate){"
    "_origUSD=_amt;"
    "_fxRate=parseFloat((_rate*1.035).toFixed(4));"
    "_amt=parseFloat((_amt*_fxRate).toFixed(2));"
    "_cur='MXN';}}"
    "results.push({emailId:msg.id,tipo:p.tipo,app:p.app||'',"
    "merchant:p.merchant||em.subj.replace(/^tu pedido de/i,'').replace(/your receipt from\\s*/i,'').replace(/tu recibo de\\s*/i,'').trim().slice(0,50)||'Sin nombre',"
    "amount:_amt,currency:_cur,originalUSD:_origUSD,fxRate:_fxRate,"
)
if OLD_PUSH in content:
    content = content.replace(OLD_PUSH, NEW_PUSH, 1)
    changes += 1
    print('OK 2: doGmailImport — USD conversion added')
else:
    print('FAIL 2: push header not found')
    idx = content.find('S.importedEmailIds.push(msg.id)')
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx:idx+200])}')

# ── 3. rGmailDetail: card informativa de conversión USD ───────────────────
# Inserted as a new line between the notes field and the button row.
# Pattern matches lines 361+362 exactly (including newlines).
OLD_NOTES_BTNS = (
    "'<div class=\"fld\"><label>Notas</label>"
    "<input class=\"inp\" id=\"gd_notes\" value=\"'+esc(r.notes||r.items||'')+'\" placeholder=\"Opcional...\"></div>'+\n"
    "'<div style=\"display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px\">'+\n"
)
# The USD card ternary — all on one inserted line
_USD_CARD = (
    "(r.originalUSD?"
    "'<div style=\"background:rgba(99,102,241,.08);border:1px solid rgba(99,102,241,.3);border-radius:10px;padding:10px;margin-top:8px\">"
    "<p style=\"font-size:11px;color:#a5b4fc;font-weight:600;margin-bottom:4px\">💱 Cargo en USD convertido</p>"
    "<p style=\"font-size:12px;color:var(--tx2)\">USD $'"
    "+parseFloat(r.originalUSD||0).toFixed(2)"
    "+'  convertido a MXN $'"
    "+parseFloat(r.amount||0).toFixed(2)"
    "+' (tipo cambio est. $'"
    "+parseFloat(r.fxRate||0).toFixed(2)"
    "+'/USD · Amex)</p>"
    "<p style=\"font-size:10px;color:var(--tx3);margin-top:2px\">Ajusta el monto si tu estado de cuenta difiere.</p></div>'"
    ":'')+\n"
)
NEW_NOTES_BTNS = (
    "'<div class=\"fld\"><label>Notas</label>"
    "<input class=\"inp\" id=\"gd_notes\" value=\"'+esc(r.notes||r.items||'')+'\" placeholder=\"Opcional...\"></div>'+\n"
    + _USD_CARD +
    "'<div style=\"display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:8px\">'+\n"
)
if OLD_NOTES_BTNS in content:
    content = content.replace(OLD_NOTES_BTNS, NEW_NOTES_BTNS, 1)
    changes += 1
    print('OK 3: rGmailDetail — USD conversion card added')
else:
    print('FAIL 3: notes+buttons pattern not found')
    idx = content.find('"gd_notes"')
    if idx > 0:
        print(f'  gd_notes at {idx}: {repr(content[idx-30:idx+80])}')

# ── 4. rGmailList: badge USD en items convertidos ─────────────────────────
OLD_LIST_HINT = (
    "'<p style=\"font-size:10px;color:'+(r.card?'#475569':'var(--am)')+';margin-top:4px\">'+"
    "(r.card?'Toca para revisar y aprobar':'⚠ Toca para elegir tarjeta antes de aprobar')+"
    "'</p>'+"
)
NEW_LIST_HINT = (
    "(r.originalUSD?"
    "'<p style=\"font-size:10px;color:#a5b4fc;margin-top:2px\">💱 USD $'"
    "+parseFloat(r.originalUSD).toFixed(2)"
    "+'  → MXN $'"
    "+parseFloat(r.amount).toFixed(2)"
    "+'</p>':'')+"
    "'<p style=\"font-size:10px;color:'+(r.card?'#475569':'var(--am)')+';margin-top:4px\">'+"
    "(r.card?'Toca para revisar y aprobar':'⚠ Toca para elegir tarjeta antes de aprobar')+"
    "'</p>'+"
)
if OLD_LIST_HINT in content:
    content = content.replace(OLD_LIST_HINT, NEW_LIST_HINT, 1)
    changes += 1
    print('OK 4: rGmailList — USD badge added')
else:
    print('FAIL 4: list hint pattern not found')
    idx = content.find('Toca para elegir tarjeta antes de aprobar')
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx-80:idx+60])}')

# ── 5. persist(): add originalUSD and fxRate to vp_gmr ────────────────────
OLD_VPG = (
    "emailId:r.emailId,tipo:r.tipo,merchant:r.merchant,amount:r.amount,currency:r.currency,"
    "date:r.date,time:r.time,category:r.category,card:r.card,subj:r.subj,from:r.from,"
    "app:r.app,items:r.items,notes:r.notes,status:r.status,skip:false"
)
NEW_VPG = (
    "emailId:r.emailId,tipo:r.tipo,merchant:r.merchant,amount:r.amount,currency:r.currency,"
    "originalUSD:r.originalUSD||null,fxRate:r.fxRate||null,"
    "date:r.date,time:r.time,category:r.category,card:r.card,subj:r.subj,from:r.from,"
    "app:r.app,items:r.items,notes:r.notes,status:r.status,skip:false"
)
if OLD_VPG in content:
    content = content.replace(OLD_VPG, NEW_VPG, 1)
    changes += 1
    print('OK 5: persist() — originalUSD + fxRate added to vp_gmr')
else:
    print('FAIL 5: vp_gmr map not found')

# ── 6. Bump APP_VERSION → v5.6 ────────────────────────────────────────────
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.6', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK 6: {old_ver_str} → {new_ver_str}')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
