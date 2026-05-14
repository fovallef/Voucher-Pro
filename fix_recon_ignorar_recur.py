#!/usr/bin/env python3
"""
fix_recon_ignorar_recur.py — Alex · 3 mejoras en reconciliación
1. rReconResult: 4.º botón "Ignorar — ya está registrado" en cargos no reconocidos
2. attachReconResult: handler data-ignorar (marca t.status='ignored', re-render)
3. processRecurring(): filtrar isRecurringInstance para que las instancias no
   generen más instancias (fix: cancelar recurrencia deja de crear cargos futuros)
   — La cancelación desde txDetail ya existe; este fix la hace efectiva
4. Bump v5.8
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ── 1. rReconResult: agregar botón Ignorar como 4.ª opción ───────────────────
OLD_DISPUTAR_BTN = (
    "data-disputar=\"'+i+'\">&#x1F6A8; No lo reconozco &#x2014; disputar con el banco</button>'+\\'</div></div>\\';"
)
NEW_DISPUTAR_BTN = (
    "data-disputar=\"'+i+'\">&#x1F6A8; No lo reconozco &#x2014; disputar con el banco</button>'+"
    "\\'<button class=\"btn\"style=\"margin:0;padding:10px;font-size:12px;"
    "background:rgba(100,116,139,.1);border:1px solid rgba(100,116,139,.3);color:var(--tx2)\""
    "data-ignorar=\"\\'+i+\\'\">"
    "&#x2713; Ignorar &#x2014; ya est&#xE1; registrado</button>'+\\'</div></div>\\';"
)
if OLD_DISPUTAR_BTN in content:
    content = content.replace(OLD_DISPUTAR_BTN, NEW_DISPUTAR_BTN, 1)
    changes += 1
    print('OK 1: rReconResult — botón Ignorar agregado')
else:
    print('FAIL 1: disputar button pattern not found')
    idx = content.find('data-disputar=')
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx:idx+100])}')

# ── 2. attachReconResult: handler data-ignorar ────────────────────────────────
OLD_MSI_HANDLER = (
    "));document.querySelectorAll('[data-msi]').forEach(b=>b.addEventListener('click',()=>{"
)
NEW_MSI_HANDLER = (
    "));"
    "document.querySelectorAll('[data-ignorar]').forEach(b=>b.addEventListener('click',()=>{"
    "const t=unrecog[parseInt(b.dataset.ignorar)];"
    "if(!t)return;"
    "t.status='ignored';"
    "render();"
    "}));"
    "document.querySelectorAll('[data-msi]').forEach(b=>b.addEventListener('click',()=>{"
)
if OLD_MSI_HANDLER in content:
    content = content.replace(OLD_MSI_HANDLER, NEW_MSI_HANDLER, 1)
    changes += 1
    print('OK 2: attachReconResult — handler data-ignorar agregado')
else:
    print('FAIL 2: data-msi handler pattern not found')
    idx = content.find("'[data-msi]'")
    if idx > 0:
        print(f'  at {idx}: {repr(content[max(0,idx-40):idx+80])}')

# ── 3. processRecurring(): excluir instancias del loop de creación ────────────
OLD_RECURRING_FILTER = (
    "const recurring=S.txs.filter(t=>t.isRecurring);"
)
NEW_RECURRING_FILTER = (
    "const recurring=S.txs.filter(t=>t.isRecurring&&!t.isRecurringInstance);"
)
if OLD_RECURRING_FILTER in content:
    content = content.replace(OLD_RECURRING_FILTER, NEW_RECURRING_FILTER, 1)
    changes += 1
    print('OK 3: processRecurring — filtro !isRecurringInstance aplicado')
else:
    print('FAIL 3: recurring filter not found')

# ── 4. Bump APP_VERSION → v5.8 ────────────────────────────────────────────────
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.8', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK 4: {old_ver_str} → {new_ver_str}')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
