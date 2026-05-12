#!/usr/bin/env python3
"""
fix_gmail_date.py — Alex · Bugfix fecha Gmail
Root cause: email Date header está en UTC; app la usa cruda → día +1 para correos
nocturnos. Fix: parseGmailDate convierte a America/Mexico_City. extractDate lee
la fecha real del cuerpo (Rappi incluye timestamp local en el body).
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ── 1. Agregar parseGmailDate + extractDate helpers (after extractAmount) ─────
OLD_EXTRACT_AMT_END = (
    "return null;}"
    "function cleanEmailBody(html){"
)
NEW_EXTRACT_AMT_END = (
    "return null;}"

    # parseGmailDate: RFC 2822 header → YYYY-MM-DD en Mexico City
    "function parseGmailDate(rawDate){"
    "if(!rawDate)return td();"
    "try{"
    "const d=new Date(rawDate);"
    "if(!isNaN(d.getTime())){"
    "return d.toLocaleDateString('en-CA',{timeZone:'America/Mexico_City'});"
    "}"
    "}catch(e){}"
    "const m=(rawDate||'').match(/(\\d{4}-\\d{2}-\\d{2})/);"
    "return m?m[1]:td();}"

    # extractDate: fecha real del cuerpo del email (YYYY-MM-DD o variantes)
    "function extractDate(body){"
    "const patterns=["
    "/(\\d{4}-\\d{2}-\\d{2})\\s+\\d{2}:\\d{2}/,"  # 2026-04-18 19:45
    "/(\\d{4}-\\d{2}-\\d{2})/"                      # 2026-04-18 standalone
    "];"
    "for(const p of patterns){"
    "const m=(body||'').match(p);"
    "if(m){const dt=new Date(m[1]);if(!isNaN(dt.getTime()))return m[1];}}"
    "return null;}"

    "function cleanEmailBody(html){"
)

if OLD_EXTRACT_AMT_END in content:
    content = content.replace(OLD_EXTRACT_AMT_END, NEW_EXTRACT_AMT_END, 1)
    changes += 1
    print('OK 1: parseGmailDate + extractDate helpers added')
else:
    print('FAIL 1: insertion point not found')
    idx = content.find('function cleanEmailBody(html)')
    if idx > 0:
        print(f'  cleanEmailBody at {idx}: {repr(content[idx-40:idx+40])}')

# ── 2. gmailFetch: normalizar date con parseGmailDate al momento de fetch ─────
OLD_FETCH_RETURN = "return{id,subj,from,date,body:body.slice(0,6000)};}"
NEW_FETCH_RETURN = "return{id,subj,from,date:parseGmailDate(date),body:body.slice(0,6000)};}"

if OLD_FETCH_RETURN in content:
    content = content.replace(OLD_FETCH_RETURN, NEW_FETCH_RETURN, 1)
    changes += 1
    print('OK 2: gmailFetch normalizes date via parseGmailDate')
else:
    print('FAIL 2: gmailFetch return not found')
    idx = content.find('return{id,subj,from,date')
    if idx > 0:
        print(f'  Found at {idx}: {repr(content[idx:idx+80])}')

# ── 3. parseEmail fast-path: prefer extractDate(body) over email header date ──
# Fast-path returns date:(em.date||'').slice(0,10) — after fix 2, em.date is
# already YYYY-MM-DD but body date is even more accurate (actual tx timestamp).
OLD_FAST_DATE = (
    "date:(em.date||'').slice(0,10),"
    "category:isDeliverySubj?'restaurantes':'suscripciones'};}"
)
NEW_FAST_DATE = (
    "date:extractDate(em.body)||em.date,"
    "category:isDeliverySubj?'restaurantes':'suscripciones'};}"
)

if OLD_FAST_DATE in content:
    content = content.replace(OLD_FAST_DATE, NEW_FAST_DATE, 1)
    changes += 1
    print('OK 3: parseEmail fast-path uses extractDate(body) || em.date')
else:
    print('FAIL 3: fast-path date pattern not found')
    idx = content.find("category:isDeliverySubj?'restaurantes'")
    if idx > 0:
        print(f'  Found at {idx}: {repr(content[idx-60:idx+60])}')

# ── 4. Bump APP_VERSION to v5.2 ───────────────────────────────────────────────
import re
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.2', old_ver_str)
    new_ver = f"APP_VERSION='{new_ver_str}'"
    content = content.replace(old_ver, new_ver, 1)
    changes += 1
    print(f'OK 4: {old_ver_str} → {new_ver_str}')
else:
    print('SKIP 4: APP_VERSION not found')

print(f'\nTotal changes: {changes}')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
