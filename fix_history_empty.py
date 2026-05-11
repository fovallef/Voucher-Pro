#!/usr/bin/env python3
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

idx = content.find("Sin transacciones en '+mLabel")
if idx < 0:
    print('not found')
    sys.exit(1)

seg_start = content.rfind("'<div", 0, idx)
seg_end = content.find("</div>'", idx) + len("</div>'")
old_seg = content[seg_start:seg_end]
print(f'old: {repr(old_seg)}')

new_seg = ("'<div class=\"empty\"><div class=\"ei\">&#x1F4CB;</div>"
           "<p style=\"font-size:15px;font-weight:600\">Sin transacciones</p>"
           "<p style=\"font-size:12px;margin-top:6px;color:var(--tx3)\">Nada registrado en '"
           "+mLabel+'</p></div>'")
print(f'new: {repr(new_seg)}')

content = content.replace(old_seg, new_seg, 1)
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'OK: Written {len(content):,} bytes')
