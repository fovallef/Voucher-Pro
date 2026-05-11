#!/usr/bin/env python3
"""
fix_sprint8.py — Sofía · Sprint 8
Color normalization pass: replace legacy hardcoded colors with CSS vars.
Scan page hero improvements. Gmail + Reconcile minor polish.
"""
import sys, io, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# We only touch the JS/HTML inside <script> blocks, not the <style>
# Find the style block end so we don't touch CSS
style_end = content.find('</style>') + len('</style>')

js_part = content[style_end:]
changes = 0

# ── 1. SCAN HERO: hardcoded colors → CSS vars ──────────────────────────────
OLD_SCAN_ICON = (
    '"width:60px;height:60px;border-radius:18px;background:#1e293b;'
    'border:1px solid #334155;display:flex;align-items:center;'
    'justify-content:center;font-size:26px;margin:0 auto 10px">📷</div>'
)
NEW_SCAN_ICON = (
    '"width:60px;height:60px;border-radius:18px;background:var(--bg3);'
    'border:1px solid rgba(255,255,255,.1);display:flex;align-items:center;'
    'justify-content:center;font-size:26px;margin:0 auto 10px">&#x1F4F7;</div>'
)
if OLD_SCAN_ICON in js_part:
    js_part = js_part.replace(OLD_SCAN_ICON, NEW_SCAN_ICON, 1)
    changes += 1
    print('OK 1: Scan icon container → CSS vars')
else:
    print('SKIP 1: scan icon not found')

OLD_SCAN_SUB = '"font-size:11px;color:#94a3b8;margin-bottom:14px">'
NEW_SCAN_SUB = '"font-size:11px;color:var(--tx2);margin-bottom:14px">'
if OLD_SCAN_SUB in js_part:
    js_part = js_part.replace(OLD_SCAN_SUB, NEW_SCAN_SUB, 1)
    changes += 1
    print('OK 2: Scan subtitle color → var(--tx2)')
else:
    print('SKIP 2: scan subtitle color not found')

# ── 2. GLOBAL: #94a3b8 → var(--tx2) in JS strings ──────────────────────────
# Only in HTML string content (inside quotes after color:)
c94 = js_part.count('#94a3b8')
js_part = js_part.replace('#94a3b8', 'var(--tx2)')
if c94:
    changes += 1
    print(f'OK 3: #94a3b8 → var(--tx2) ({c94} occurrences)')

# ── 3. GLOBAL: #64748b → var(--tx3) ─────────────────────────────────────────
c64 = js_part.count('#64748b')
js_part = js_part.replace('#64748b', 'var(--tx3)')
if c64:
    changes += 1
    print(f'OK 4: #64748b → var(--tx3) ({c64} occurrences)')

# ── 4. GLOBAL: #1e293b → var(--bg3) ─────────────────────────────────────────
c1e = js_part.count('#1e293b')
js_part = js_part.replace('#1e293b', 'var(--bg3)')
if c1e:
    changes += 1
    print(f'OK 5: #1e293b → var(--bg3) ({c1e} occurrences)')

# ── 5. GLOBAL: #0f172a → var(--bg2) (dark bg in gradients) ──────────────────
c0f = js_part.count('#0f172a')
js_part = js_part.replace('#0f172a', 'var(--bg2)')
if c0f:
    changes += 1
    print(f'OK 6: #0f172a → var(--bg2) ({c0f} occurrences)')

# ── 6. GLOBAL: #334155 border → var(--bd) ────────────────────────────────────
# Only in border contexts (avoid replacing other uses)
c33 = js_part.count('border:1px solid #334155')
js_part = js_part.replace('border:1px solid #334155', 'border:1px solid var(--bd)')
if c33:
    changes += 1
    print(f'OK 7: border #334155 → var(--bd) ({c33} occurrences)')

# ── 7. Scan gradient backgrounds → use var(--bg2) ────────────────────────────
# The hs string in rScan uses rgba(...)  + hardcoded #0f172a (already replaced above)
# Check remaining
remaining_0f = js_part.count('#0f172a')
if remaining_0f:
    print(f'  Note: {remaining_0f} remaining #0f172a (should be 0 after step 6)')

# ── 8. Gmail section: color-coded import status boxes ─────────────────────────
# Already uses rgba() patterns which are fine.
# Fix the iok/ir/id classes usage - already mapped in CSS, nothing to do

# ── 9. rReconcile stats numbers: minor size boost ─────────────────────────────
OLD_RECON_PEND = '"font-size:28px;font-weight:700;color:var(--am)">'
NEW_RECON_PEND = '"font-size:32px;font-weight:800;letter-spacing:-.03em;color:var(--am)">'
if OLD_RECON_PEND in js_part:
    js_part = js_part.replace(OLD_RECON_PEND, NEW_RECON_PEND, 1)
    changes += 1
    print('OK 9: Reconcile pending count — bigger number')
else:
    print('SKIP 9: reconcile pending count style not found')

print(f'\nTotal changes: {changes}')
content = content[:style_end] + js_part

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Written {len(content):,} bytes')
