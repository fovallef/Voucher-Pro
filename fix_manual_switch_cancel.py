#!/usr/bin/env python3
"""
fix_manual_switch_cancel.py — Alex · 3 fixes en formulario manual
1. m_rec switch: eliminar render() → fix switch atascado + scroll al top
   Root cause: render() usa requestAnimationFrame (async) → race condition en
   Safari iOS; además innerHTML replace resetea scroll. Se reemplaza por
   manipulación directa del DOM del switch sin re-render.
2. rManual: agregar botón ✕ Cancelar junto al botón Guardar
3. attachManual: handler cancel → limpia form y regresa a reconcile si aplica
4. Bump v5.7
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ── 1. m_rec change handler: eliminar sync()+render(), actualizar DOM directo ──
OLD_REC_HANDLER = (
    "document.getElementById('m_rec')?.addEventListener('change',e=>{"
    "S.manualForm.isRecurring=e.target.checked;sync();render();});"
)
NEW_REC_HANDLER = (
    "document.getElementById('m_rec')?.addEventListener('change',e=>{"
    "const _rc=e.target.checked;"
    "S.manualForm.isRecurring=_rc;"
    "const _sw=e.target.nextElementSibling;"
    "if(_sw){"
    "_sw.style.background=_rc?'var(--in)':'var(--bd)';"
    "const _kn=_sw.querySelector('span');"
    "if(_kn)_kn.style.left=_rc?'23px':'3px';"
    "}});"
)
if OLD_REC_HANDLER in content:
    content = content.replace(OLD_REC_HANDLER, NEW_REC_HANDLER, 1)
    changes += 1
    print('OK 1: m_rec handler — render() eliminado, DOM update directo')
else:
    print('FAIL 1: m_rec handler not found')
    idx = content.find("'m_rec')?.addEventListener")
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx:idx+120])}')

# ── 2. rManual: wrap save en grid + agregar botón Cancelar ───────────────────
OLD_SAVE_BTN = (
    '<button class="btn ${bc}"id="m_save"'
    'style="margin-top:4px;opacity:${(f.merchant&&f.amount)?1:.45};transition:opacity .2s"'
    '${(f.merchant&&f.amount)?"":" disabled"}>💾 Guardar Gasto</button>`;}'
)
NEW_SAVE_BTN = (
    '<div style="display:grid;grid-template-columns:1fr auto;gap:8px;margin-top:4px">'
    '<button class="btn ${bc}"id="m_save"'
    'style="opacity:${(f.merchant&&f.amount)?1:.45};transition:opacity .2s"'
    '${(f.merchant&&f.amount)?"":" disabled"}>💾 Guardar Gasto</button>'
    '<button class="btn bs"id="m_cancel"style="min-width:80px">✕ Cancelar</button>'
    '</div>`;}'
)
if OLD_SAVE_BTN in content:
    content = content.replace(OLD_SAVE_BTN, NEW_SAVE_BTN, 1)
    changes += 1
    print('OK 2: rManual — botón Cancelar agregado junto a Guardar')
else:
    print('FAIL 2: save button pattern not found')
    idx = content.find('"m_save"')
    if idx > 0:
        print(f'  at {idx}: {repr(content[max(0,idx-30):idx+120])}')

# ── 3. attachManual: insertar handler m_cancel ────────────────────────────────
# Se inserta después del NEW m_rec handler (cambio 1 ya aplicado),
# antes de document.querySelectorAll('[data-tmpl]')
OLD_TMPL_QUERY = (
    "});document.querySelectorAll('[data-tmpl]').forEach(el=>{"
)
NEW_TMPL_QUERY = (
    "});"
    "document.getElementById('m_cancel')?.addEventListener('click',()=>{"
    "const _wr=!!S._reconTx;"
    "S.manualForm={merchant:'',amount:'',currency:'MXN',date:'',time:'',"
    "card:'',msi:null,cfdi:{rfc:'',folio:''},isRecurring:false,notes:''};"
    "S._reconTx=null;"
    "S.error='';"
    "if(_wr){S.tab='reconcile';S.screen='reconResult';}"
    "render();"
    "});"
    "document.querySelectorAll('[data-tmpl]').forEach(el=>{"
)
if OLD_TMPL_QUERY in content:
    content = content.replace(OLD_TMPL_QUERY, NEW_TMPL_QUERY, 1)
    changes += 1
    print('OK 3: attachManual — handler m_cancel agregado')
else:
    print('FAIL 3: data-tmpl query not found')
    idx = content.find("'[data-tmpl]'")
    if idx > 0:
        print(f'  at {idx}: {repr(content[max(0,idx-40):idx+80])}')

# ── 4. Bump APP_VERSION → v5.7 ────────────────────────────────────────────────
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.7', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK 4: {old_ver_str} → {new_ver_str}')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
