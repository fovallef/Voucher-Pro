#!/usr/bin/env python3
"""
fix_closed_no_edit_v556.py — Tx cerrados sin botones edit/delete v5.56

Bug: en historial, las filas con badge cerrado (statement pagado) siguen
mostrando el boton de editar (lapiz) y el de borrar (swipe izquierda
revela papelera). Esto rompe la integridad de los statements ya
liquidados.

Fix: en rTxRow, condicionar ambos botones a !isTxClosed(t):
- sw-del: no se renderiza si cerrado (swipe no revela nada)
- txedit: no se renderiza si cerrado
- el boton WhatsApp data-wa se mantiene (es de compartir, no edita)
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# 1. Ocultar boton txedit si cerrado
# Patron: '<button class="rib"data-txedit="'+t.id+'"style="font-size:14px">EMOJI</button>'
# Solo hay una ocurrencia del data-txedit en rTxRow
OLD_EDIT = "'<button class=\"rib\"data-txedit=\"'+t.id+'\"style=\"font-size:14px\">✏️</button></div>'"
NEW_EDIT = "(isTxClosed(t)?'':'<button class=\"rib\"data-txedit=\"'+t.id+'\"style=\"font-size:14px\">✏️</button>')+'</div>'"

if OLD_EDIT in content:
    content = content.replace(OLD_EDIT, NEW_EDIT, 1)
    changes += 1
    print('OK 1: boton txedit condicionado a !isTxClosed')
else:
    print('FAIL 1: txedit button pattern not found')

# 2. Ocultar swipe-delete button si cerrado
OLD_SWDEL = "'<div class=\"sw-wrap\">'+'<button class=\"sw-del\"data-swdel=\"'+t.id+'\">\U0001F5D1️</button>'+"
NEW_SWDEL = "'<div class=\"sw-wrap\">'+(isTxClosed(t)?'':'<button class=\"sw-del\"data-swdel=\"'+t.id+'\">\U0001F5D1️</button>')+"

if OLD_SWDEL in content:
    content = content.replace(OLD_SWDEL, NEW_SWDEL, 1)
    changes += 1
    print('OK 2: swipe-delete condicionado a !isTxClosed')
else:
    print('FAIL 2: sw-del button pattern not found')
    # Debug: find sw-del
    idx = content.find('sw-del')
    print(f'  debug: sw-del found at {idx}')
    if idx > 0:
        print(f'  context: {content[max(0,idx-100):idx+200]!r}')

# Bump APP_VERSION -> v5.56
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.56', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK Version: {old_ver_str} -> v5.56')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
