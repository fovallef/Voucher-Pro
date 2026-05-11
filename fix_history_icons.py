#!/usr/bin/env python3
"""
fix_history_icons.py — Sofía · Sprint 9
Fix duplicate trash icons in History rows:
  - Remove inline data-del 🗑 button (duplicate of sw-del swipe)
  - Keep ✏️ data-txedit (opens edit modal) and 📲 data-wa (empresarial)
Also normalize dot status colors to CSS vars in rTxRow.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# ── 1. Remove duplicate 🗑 data-del button (keep ✏️ and 📲) ──────────────────
# Old: shows 📲 (empresarial) + ✏️ + 🗑 in a row
OLD_BTNS = (
    '+(showDel?\'<div style="display:flex;gap:6px;justify-content:flex-end;margin-top:4px">\''
    '+(t.entity===\'empresarial\'?\'<button class="rib"data-wa="\'+t.id+\'"style="font-size:15px">\U0001f4f2</button>\':\'\')'
    '+\'<button class="rib"data-txedit="\'+t.id+\'"style="font-size:14px">✏️</button>\''
    '+\'<button class="rib"data-del="\'+t.id+\'"style="font-size:14px;color:#ef4444">\U0001f5d1</button></div>\':\'\')'
)
# New: keep ✏️ and 📲, drop 🗑
NEW_BTNS = (
    '+(showDel?\'<div style="display:flex;gap:6px;justify-content:flex-end;margin-top:4px">\''
    '+(t.entity===\'empresarial\'?\'<button class="rib"data-wa="\'+t.id+\'"style="font-size:15px">\U0001f4f2</button>\':\'\')'
    '+\'<button class="rib"data-txedit="\'+t.id+\'"style="font-size:14px">✏️</button></div>\':\'\')'
)

if OLD_BTNS in content:
    content = content.replace(OLD_BTNS, NEW_BTNS, 1)
    changes += 1
    print('OK 1: Removed duplicate data-del button from rTxRow (kept ✏️ + 📲)')
else:
    print('FAIL 1: inline button pattern not found')
    # Debug: show surrounding context
    idx = content.find('data-del')
    if idx > 0:
        print(f'  data-del at {idx}: {repr(content[idx-40:idx+80])}')

# ── 2. Dot status colors → CSS vars in rTxRow ────────────────────────────────
OLD_DOT = (
    "const dot=t.status==='reconciled'?'<span style=\"color:#10b981;font-size:11px\">●</span>'"
    ":t.status==='disputed'?'<span style=\"color:#ef4444;font-size:11px\">\U0001f6a8</span>'"
    ":t.status==='unrecognized'?'<span style=\"color:#f59e0b;font-size:11px\">⚠</span>'"
    ":'<span style=\"color:#f59e0b;font-size:11px\">○</span>';"
)
NEW_DOT = (
    "const dot=t.status==='reconciled'?'<span style=\"color:var(--em);font-size:11px\">●</span>'"
    ":t.status==='disputed'?'<span style=\"color:var(--rd);font-size:11px\">\U0001f6a8</span>'"
    ":t.status==='unrecognized'?'<span style=\"color:var(--am);font-size:11px\">⚠</span>'"
    ":'<span style=\"color:var(--am);font-size:11px\">○</span>';"
)

if OLD_DOT in content:
    content = content.replace(OLD_DOT, NEW_DOT, 1)
    changes += 1
    print('OK 2: Dot colors → var(--em) / var(--rd) / var(--am)')
else:
    print('SKIP 2: dot color pattern not found (may already use CSS vars)')

# ── 3. Bump APP_VERSION to v5.0 ───────────────────────────────────────────────
import re
ver_match = re.search(r"APP_VERSION='(v[\d.]+\s*\xb7\s*[^']+)'", content)
if ver_match:
    old_ver = ver_match.group(0)
    # Extract current version number and bump
    old_ver_str = ver_match.group(1)
    new_ver_str = re.sub(r'v[\d.]+', 'v5.0', old_ver_str)
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
