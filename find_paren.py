#!/usr/bin/env python3
"""find_paren.py - Find unclosed parentheses in script blocks"""
import re, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BACKSLASH = chr(92)

with open('index.html', encoding='utf-8') as f:
    content = f.read()

script_starts = [m.start() for m in re.finditer(r'<script[^>]*>', content)]
script_ends = [m.start() for m in re.finditer(r'</script>', content)]

for si in range(len(script_starts)):
    s, e = script_starts[si], script_ends[si]
    tag_end = content.index('>', s) + 1
    js = content[tag_end:e]
    if not js.strip():
        continue

    depth = 0
    in_str = None
    i = 0
    stack = []

    while i < len(js):
        c = js[i]

        if in_str:
            if c == BACKSLASH:
                i += 2
                continue
            if c == in_str:
                in_str = None
            i += 1
            continue

        if c in ("'", '"'):
            in_str = c
            i += 1
            continue

        if c == '`':
            i += 1
            tmpl_depth = 1
            while i < len(js) and tmpl_depth > 0:
                tc = js[i]
                if tc == BACKSLASH:
                    i += 2
                    continue
                if tc == '`':
                    tmpl_depth -= 1
                elif js[i:i+2] == '${':
                    tmpl_depth += 1
                    i += 2
                    continue
                i += 1
            continue

        if c == '(':
            depth += 1
            stack.append(i)
        elif c == ')':
            if stack:
                stack.pop()
            depth -= 1
            if depth < 0:
                print(f'  EXTRA ) at pos {i}: {repr(js[max(0,i-40):i+40])}')
                depth = 0

        i += 1

    open_count = js.count('(')
    close_count = js.count(')')
    print(f'Script {si} ({len(js)} chars): raw_parens_diff={open_count-close_count}, real_depth={depth}')
    if depth > 0 and stack:
        print(f'  Unclosed ( at positions: {stack[-5:]}')
        for pos in stack[-3:]:
            print(f'  pos {pos}: {repr(js[max(0,pos-30):pos+100])}')
