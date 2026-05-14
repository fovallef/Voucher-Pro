#!/usr/bin/env python3
"""
fix_dispute_rectify.py — Alex · Rectificar cargo en disputa
1. rTxDetail: botón "🔄 Rectificar" visible solo cuando status='disputed'
2. attachTxDetail: handler tdRectify → status='pending', limpia disputeNotes/date
3. Bump v5.9
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ── 1. rTxDetail: insertar botón Rectificar tras tdCancelRec ─────────────────
# El botón solo aparece cuando t.status === 'disputed'
OLD_TD_END = (
    "n recurrente</button>':'')+\\'</div>\\';"
    "}"
)
NEW_TD_END = (
    "n recurrente</button>':'')"
    "+(t.status==='disputed'?"
    "'<button class=\"btn\" id=\"tdRectify\" style=\"width:100%;margin-top:8px;"
    "background:rgba(16,185,129,.12);border:1px solid rgba(16,185,129,.35);"
    "color:#10b981\">&#x1F504; Rectificar &#x2014; quitar de disputa</button>'"
    ":'')"
    "+\\'</div>\\';"
    "}"
)
if OLD_TD_END in content:
    content = content.replace(OLD_TD_END, NEW_TD_END, 1)
    changes += 1
    print('OK 1: rTxDetail — botón tdRectify agregado')
else:
    print('FAIL 1: rTxDetail end pattern not found')
    idx = content.find("n recurrente</button>")
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx:idx+60])}')

# ── 2. attachTxDetail: handler tdRectify ────────────────────────────────────
OLD_HANDLER_END = (
    "ticamente.\'),100);});const img="
)
NEW_HANDLER_END = (
    "ticamente.\'),100);});"
    "document.getElementById('tdRectify')?.addEventListener('click',()=>{"
    "const t=S.txs.find(x=>x.id===S.txDetail);"
    "if(!t)return;"
    "if(!confirm('\\u00bfRectificar \"'+t.merchant+'\"?\\n\\n"
    "El cargo regresar\\u00e1 a estado Pendiente y podr\\u00e1 ser conciliado.'))return;"
    "const ri=S.txs.findIndex(x=>x.id===S.txDetail);"
    "if(ri>=0)S.txs[ri]={...S.txs[ri],status:'pending',disputeNotes:null,disputeDate:null,rectifiedAt:new Date().toISOString()};"
    "persist();S.txDetail=null;render();"
    "setTimeout(()=>alert('\\u2705 Cargo rectificado. Ya aparece como Pendiente.'),100);"
    "});const img="
)
if OLD_HANDLER_END in content:
    content = content.replace(OLD_HANDLER_END, NEW_HANDLER_END, 1)
    changes += 1
    print('OK 2: attachTxDetail — handler tdRectify agregado')
else:
    print('FAIL 2: handler end pattern not found')
    idx = content.find("ticamente.')")
    if idx > 0:
        print(f'  at {idx}: {repr(content[idx:idx+60])}')

# ── 3. Bump APP_VERSION → v5.9 ────────────────────────────────────────────────
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.9', old_ver_str)
    content = content.replace(old_ver, f"APP_VERSION='{new_ver_str}'", 1)
    changes += 1
    print(f'OK 3: {old_ver_str} → {new_ver_str}')

print(f'\nTotal changes: {changes}')
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
