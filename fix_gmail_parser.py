#!/usr/bin/env python3
"""
fix_gmail_parser.py — Alex · Bugfix Gmail parser
Two-part fix:
  1. parseEmail: "Entregado: X" subject (Amazon delivery notification) → 'otro'
     These are delivery confirmations, not charges. Charge happens at order/ship time.
  2. doGmailImport: amount=0 cargo_real guard — never show zero-amount as approvable.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ── 1. parseEmail: add "^entregado[:\s]" to early 'otro' filter ──────────────
# Current early filter (beginning of parseEmail):
OLD_EARLY = (
    "async function parseEmail(em){const s=(em.subj||'').toLowerCase();"
    "const fromL=(em.from||'').toLowerCase();"
    "if(/programad|scheduled|en camino|out for delivery|enviado|shipped|tracking/i.test(s)"
    "||/hemos recibido|order received|pedido recibido/.test(s)"
    "||s.includes('cancelad')){"
    "return{tipo:'otro',merchant:'',amount:0,currency:'MXN',"
    "date:(em.date||'').slice(0,10),category:'otro'};}"
)
# Add: /^entregado[:\s]/i — Amazon delivery notification format
# "Entregado: 1 producto | Pedido #..." → delivery notification, not charge
NEW_EARLY = (
    "async function parseEmail(em){const s=(em.subj||'').toLowerCase();"
    "const fromL=(em.from||'').toLowerCase();"
    "if(/programad|scheduled|en camino|out for delivery|enviado|shipped|tracking/i.test(s)"
    "||/hemos recibido|order received|pedido recibido/.test(s)"
    "||s.includes('cancelad')"
    "||/^entregado[:\\s]/i.test(em.subj||'')){"
    "return{tipo:'otro',merchant:'',amount:0,currency:'MXN',"
    "date:(em.date||'').slice(0,10),category:'otro'};}"
)

if OLD_EARLY in content:
    content = content.replace(OLD_EARLY, NEW_EARLY, 1)
    changes += 1
    print('OK 1: parseEmail early filter — "Entregado:" subject → otro')
else:
    print('FAIL 1: early filter pattern not found')
    idx = content.find('async function parseEmail(em)')
    if idx > 0:
        print(f'  Found parseEmail at {idx}: {repr(content[idx:idx+200])}')

# ── 2. doGmailImport: guard against zero-amount cargo_real reaching review ────
# After parseEmail, if tipo=cargo_real/reembolso but amount=0 → treat as otro
# Current code pushes to results unconditionally when tipo=cargo_real|reembolso
OLD_PUSH = (
    "if(p.tipo==='cargo_real'||p.tipo==='reembolso'){"
    "results.push({emailId:msg.id,tipo:p.tipo,app:p.app||'',"
    "merchant:p.merchant||em.subj.replace(/^tu pedido de/i,'').replace(/your receipt from\\s*/i,'').replace(/tu recibo de\\s*/i,'').trim().slice(0,50)||'Sin nombre',"
    "amount:parseFloat(p.amount||0),"
)
NEW_PUSH = (
    "if((p.tipo==='cargo_real'||p.tipo==='reembolso')&&parseFloat(p.amount||0)>0){"
    "results.push({emailId:msg.id,tipo:p.tipo,app:p.app||'',"
    "merchant:p.merchant||em.subj.replace(/^tu pedido de/i,'').replace(/your receipt from\\s*/i,'').replace(/tu recibo de\\s*/i,'').trim().slice(0,50)||'Sin nombre',"
    "amount:parseFloat(p.amount||0),"
)

if OLD_PUSH in content:
    content = content.replace(OLD_PUSH, NEW_PUSH, 1)
    changes += 1
    print('OK 2: doGmailImport — zero-amount cargo_real guard added')
else:
    print('FAIL 2: push pattern not found')
    idx = content.find("if(p.tipo==='cargo_real'||p.tipo==='reembolso')")
    if idx > 0:
        print(f'  Found at {idx}: {repr(content[idx:idx+150])}')

# ── 3. Bump APP_VERSION to v5.1 ───────────────────────────────────────────────
import re
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.1', old_ver_str)
    new_ver = f"APP_VERSION='{new_ver_str}'"
    content = content.replace(old_ver, new_ver, 1)
    changes += 1
    print(f'OK 3: {old_ver_str} → {new_ver_str}')
else:
    print('SKIP 3: APP_VERSION not found')

print(f'\nTotal changes: {changes}')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
