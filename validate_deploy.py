#!/usr/bin/env python3
"""
validate_deploy.py — VoucherPro pre-deploy gate
Valentina (DevOps & QA) — ejecutar ANTES de cualquier git push

Retorna exit code 0 si todo OK, 1 si hay errores.
"""
import sys, io, re, subprocess, tempfile, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PASS = '\033[92m✅\033[0m'
FAIL = '\033[91m❌\033[0m'
WARN = '\033[93m⚠️ \033[0m'

errors = []
warnings = []

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

print('=' * 60)
print('  VoucherPro Deploy Validator — Valentina')
print('=' * 60)

# ── 1. EXTRAER BLOQUES <script> ───────────────────────────────
script_starts = [m.start() for m in re.finditer(r'<script[^>]*>', content)]
script_ends = [m.start() for m in re.finditer(r'</script>', content)]
js_blocks = []
for s, e in zip(script_starts, script_ends):
    tag_end = content.index('>', s) + 1
    js = content[tag_end:e]
    if js.strip():
        js_blocks.append(js)

print(f'\n[1] Script blocks encontrados: {len(js_blocks)}')

# ── 2. SYNTAX CHECK CON NODE.JS ──────────────────────────────
print('\n[2] Syntax check (Node.js)...')
node_ok = True
for i, js in enumerate(js_blocks):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.js',
                                     encoding='utf-8', delete=False) as tmp:
        tmp.write(js)
        tmp_path = tmp.name
    try:
        result = subprocess.run(
            ['node', '--check', tmp_path],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode != 0:
            msg = result.stderr.strip()
            errors.append(f'Script {i}: Syntax error — {msg}')
            print(f'  {FAIL} Script {i}: {msg}')
        else:
            print(f'  {PASS} Script {i}: OK ({len(js):,} chars)')
    except FileNotFoundError:
        warnings.append('Node.js no encontrado — syntax check omitido')
        print(f'  {WARN} Node.js no disponible, omitiendo syntax check')
        node_ok = False
        break
    except subprocess.TimeoutExpired:
        warnings.append(f'Script {i}: Node.js timeout')
    finally:
        os.unlink(tmp_path)

# ── 3. BRACE BALANCE ──────────────────────────────────────────
print('\n[3] Brace balance {/}...')
for i, js in enumerate(js_blocks):
    opens = js.count('{')
    closes = js.count('}')
    diff = opens - closes
    if diff != 0:
        errors.append(f'Script {i}: Brace imbalance — opens={opens} closes={closes} diff={diff}')
        print(f'  {FAIL} Script {i}: diff={diff}')
    else:
        print(f'  {PASS} Script {i}: {opens} opens = {closes} closes')

# ── 4. PATRONES SAFARI PROHIBIDOS (Marco's list) ──────────────
print('\n[4] Patrones Safari incompatibles (Marco)...')

SAFARI_FORBIDDEN = [
    # Pattern, description, severity
    # ERRORS: patrones con crash confirmado en producción
    (r'const\s+const\s+', 'Doble const — SyntaxError (historial: card filter commit)', 'error'),
    (r'let\s+let\s+|var\s+var\s+', 'Doble declaración de variable', 'error'),
    # ERROR: ([k,v])=> con DOS vars nombradas dentro de IIFE +(()=>{...})()
    # Marco: safe en return`...` pero crash confirmado en string concat + IIFE context
    (r'\+\s*\(\(\)\s*=>\s*\{[^\{\}]{0,2000}\(\[\w+,\w+\]\)\s*=>',
     'Destructuring ([k,v])=> dentro de IIFE +(()=>{}) — crash Safari confirmado', 'error'),
    # WARNINGS: patrones de riesgo que requieren revisión de Marco
    (r'\(\s*\[\s*\w+\s*,\s*\w+\s*\]\s*\)\s*=>',
     'Destructuring ([x,y])=> detectado — verificar que NO esté dentro de IIFE (Marco)', 'warning'),
    (r'\$\{[^}]*`[^`]{1,100}`[^}]*\}',
     'Template literal dentro de ${} — posible anidado, Marco debe revisar contexto', 'warning'),
    (r'(?<!\w)async\s+\*', 'Async generator — verificar soporte iOS', 'warning'),
    (r'import\s*\(', 'Dynamic import() — no soportado en PWA context', 'warning'),
    # FSM enforcement (Brief 1-bis Fase D): direct lifecycle writes outside FSM helpers
    # Allowlist: transitionTx, deriveLifecycle, txStatus, migration block (escape via comment marker)
    (r't\.lifecycle\s*=\s*[\'"]', 'Asignación directa de t.lifecycle (usar transitionTx en su lugar — FSM Fase D)', 'warning'),
]

all_js = '\n'.join(js_blocks)

for pattern, desc, severity in SAFARI_FORBIDDEN:
    matches = list(re.finditer(pattern, all_js))
    if matches:
        if severity == 'error':
            errors.append(f'Patrón prohibido: {desc} ({len(matches)} ocurrencia(s))')
            print(f'  {FAIL} {desc}')
            for m in matches[:2]:
                ctx = all_js[max(0, m.start()-20):m.end()+20].replace('\n', ' ')
                print(f'       → ...{ctx}...')
        else:
            warnings.append(f'Patrón de riesgo: {desc}')
            print(f'  {WARN} {desc}')
    else:
        print(f'  {PASS} {desc[:55]}')

# ── 5. BACKTICK BALANCE EN RRECONRESULT ───────────────────────
print('\n[5] Template literal structure en rReconResult...')
rr_start = all_js.find('function rReconResult()')
rr_end = all_js.find('function attachReconResult', rr_start)
if rr_start > 0 and rr_end > 0:
    rr = all_js[rr_start:rr_end]
    bt_count = rr.count('`')
    if bt_count % 2 != 0:
        errors.append(f'rReconResult: backtick count impar ({bt_count}) — template literal no cerrado')
        print(f'  {FAIL} backtick count impar: {bt_count}')
    else:
        print(f'  {PASS} backtick count par: {bt_count}')
else:
    warnings.append('rReconResult no encontrado — omitido')

# ── 6. VERIFICAR APP_VERSION ──────────────────────────────────
print('\n[6] APP_VERSION...')
ver_match = re.search(r"APP_VERSION='([^']+)'", all_js)
if ver_match:
    print(f'  {PASS} {ver_match.group(1)}')
else:
    warnings.append('APP_VERSION no encontrado')
    print(f'  {WARN} APP_VERSION no encontrado')

# ── 7. TAMAÑO DEL ARCHIVO ─────────────────────────────────────
print('\n[7] Tamaño del archivo...')
size_kb = len(content) / 1024
if size_kb > 300:
    warnings.append(f'index.html muy grande: {size_kb:.0f}KB — revisar si Safari puede cargarlo')
    print(f'  {WARN} {size_kb:.0f}KB — monitorear')
else:
    print(f'  {PASS} {size_kb:.0f}KB — dentro del límite seguro')

# ── RESUMEN FINAL ──────────────────────────────────────────────
print('\n' + '=' * 60)
if errors:
    print(f'  {FAIL} DEPLOY BLOQUEADO — {len(errors)} error(es)')
    for e in errors:
        print(f'     • {e}')
    if warnings:
        print(f'\n  {WARN} Además {len(warnings)} advertencia(s):')
        for w in warnings:
            print(f'     • {w}')
    print('=' * 60)
    sys.exit(1)
elif warnings:
    print(f'  {WARN} DEPLOY CON ADVERTENCIAS — {len(warnings)} aviso(s)')
    for w in warnings:
        print(f'     • {w}')
    print('\n  Revisa las advertencias con Marco antes de continuar.')
    print('=' * 60)
    sys.exit(0)
else:
    print(f'  {PASS} SEMÁFORO VERDE — todos los checks pasaron')
    print('  Watson puede proceder con la revisión de lógica.')
    print('=' * 60)
    sys.exit(0)
