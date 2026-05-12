#!/usr/bin/env python3
"""
fix_gmail_persist.py — Alex · Bugfix crítico: S.gmailResults es volátil
Raíz: los registros aprobados en Gmail viven solo en memoria. Cualquier recarga
antes de "Registrar" los borra permanentemente (aunque el email ID ya quedó
marcado en vp_emids, bloqueando la re-importación).

Fix:
1. persist(): guarda S.gmailResults (solo los no-skip) en vp_gmr
2. loadState(): restaura vp_gmr a S.gmailResults al arrancar
3. doConfirmGmail(): limpia vp_gmr tras confirmar exitosamente
4. doGmailImport(): limpia vp_gmr al iniciar un import nuevo
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ── 1. persist(): agregar vp_gmr al final de las saves ───────────────────────
OLD_PERSIST_END = (
    "_save('vp_dd',JSON.stringify(S.dismissedDupes||[]));}"
)
NEW_PERSIST_END = (
    "_save('vp_dd',JSON.stringify(S.dismissedDupes||[]));"
    # Solo guardar registros no-skip (los que el usuario vio y potencialmente aprobó)
    # No guardar cuerpos de email — solo metadata
    "_save('vp_gmr',JSON.stringify((S.gmailResults||[]).filter(r=>!r.skip).map(r=>({emailId:r.emailId,tipo:r.tipo,merchant:r.merchant,amount:r.amount,currency:r.currency,date:r.date,time:r.time,category:r.category,card:r.card,subj:r.subj,from:r.from,app:r.app,items:r.items,notes:r.notes,status:r.status,skip:false}))));"
    "}"
)
if OLD_PERSIST_END in content:
    content = content.replace(OLD_PERSIST_END, NEW_PERSIST_END, 1)
    changes += 1
    print('OK 1: persist() — guarda S.gmailResults en vp_gmr')
else:
    print('FAIL 1: persist end not found')
    idx = content.find("_save('vp_dd'")
    if idx > 0:
        print(f'  Found at {idx}: {repr(content[idx:idx+80])}')

# ── 2. loadState(): restaurar vp_gmr a S.gmailResults ────────────────────────
# Insertar al final de loadState(), justo antes del cierre }catch(e){}
OLD_LOAD_END = (
    "processRecurring();}catch(e){console.warn('load error',e);}}"
)
NEW_LOAD_END = (
    "processRecurring();"
    "try{const _gmr=localStorage.getItem('vp_gmr');"
    "if(_gmr){const _gr=JSON.parse(_gmr);"
    "if(_gr&&_gr.length>0)S.gmailResults=_gr;}"
    "}catch(e){}"
    "}catch(e){console.warn('load error',e);}}"
)
if OLD_LOAD_END in content:
    content = content.replace(OLD_LOAD_END, NEW_LOAD_END, 1)
    changes += 1
    print('OK 2: loadState() — restaura vp_gmr a S.gmailResults')
else:
    print('FAIL 2: load end not found')
    idx = content.find('processRecurring();')
    if idx > 0:
        print(f'  Found at {idx}: {repr(content[idx:idx+60])}')

# ── 3. doConfirmGmail(): limpiar vp_gmr tras confirmar ───────────────────────
OLD_GMAIL_CLEAR = (
    "S.gmailResults=[];S.gmailInfo='';"
)
NEW_GMAIL_CLEAR = (
    "S.gmailResults=[];S.gmailInfo='';"
    "localStorage.removeItem('vp_gmr');"
)
if OLD_GMAIL_CLEAR in content:
    content = content.replace(OLD_GMAIL_CLEAR, NEW_GMAIL_CLEAR, 1)
    changes += 1
    print('OK 3: doConfirmGmail() — limpia vp_gmr tras confirmar')
else:
    print('FAIL 3: gmail clear not found')

# ── 4. doGmailImport(): limpiar vp_gmr al iniciar import nuevo ───────────────
# Al iniciar un import nuevo se descarta el estado previo
OLD_IMPORT_INIT = (
    "S.gmailImporting=true;S.gmailResults=[];S.gmailInfo='';S.gmailStep='Conectando...';"
)
NEW_IMPORT_INIT = (
    "S.gmailImporting=true;S.gmailResults=[];S.gmailInfo='';"
    "localStorage.removeItem('vp_gmr');"
    "S.gmailStep='Conectando...';"
)
if OLD_IMPORT_INIT in content:
    content = content.replace(OLD_IMPORT_INIT, NEW_IMPORT_INIT, 1)
    changes += 1
    print('OK 4: doGmailImport() — limpia vp_gmr al iniciar import')
else:
    print('FAIL 4: import init not found')

# ── 5. Bump APP_VERSION → v5.4 ────────────────────────────────────────────────
import re
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.4', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK 5: {old_ver_str} → {new_ver_str}')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
