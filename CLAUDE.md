# CLAUDE.md — VoucherPro Project Context

> This file is the authoritative context document for Claude Code.  
> Read this entirely before making any changes to the codebase.

---

## Project Overview

**VoucherPro** is a personal + business expense tracking PWA for Francisco Ovalle Félix (CDMX, México).  
- Scans physical payment vouchers via camera (Claude Vision API)
- Imports transactions from Gmail (Rappi, Uber Eats, DiDi Food, Amazon)
- Reconciles bank statements (PDF → Claude AI)
- Hosted on GitHub Pages: `https://fovallef.github.io/Voucher-Pro/`
- Installed as PWA on iPhone 17 Pro Max (iOS 18, Safari)

---

## Repository

```
github.com/fovallef/Voucher-Pro  (public, branch: main)
├── index.html    (~8KB)    Shell: CSS + Chart.js CDN + JS loader
├── app.js        (~106KB)  Full application logic
├── README.md               User-facing documentation
└── CLAUDE.md               This file — Claude Code context
```

**Live URL:** `https://fovallef.github.io/Voucher-Pro/`  
**Deploy time:** ~2 minutes after push to main

---

## CRITICAL — Safari iOS Constraints

> Violating these will cause silent blank screen failures. Francisco has spent hours debugging these.

1. **No inline scripts > ~80KB** — Safari iOS kills them silently with no error
2. **Solution in use:** `<script type="text/plain" id="vp-code">` — JS embedded as non-executable text, tiny 3-line inline script reads `.textContent` and appends it as a real `<script>` tag
3. **Blob URL approach — REJECTED** — Safari blocks `URL.createObjectURL()` for script loading
4. **fetch() for app.js — REJECTED** — returns 404 in Safari PWA context
5. **External `<script src="app.js">` alone — REJECTED** — also failed in testing
6. **Nested template literals** — crash Safari parser. Always extract to helper functions instead
7. **`'use strict'`** — keep it, it works fine
8. **Chart.js CDN must load BEFORE app.js** in index.html

---

## Architecture

### index.html structure
```html
<head>
  <!-- meta tags, CSS inline -->
</head>
<body>
  <div id="root"><!-- static splash screen --></div>
  <script src="Chart.js CDN"></script>
  <script type="text/plain" id="vp-code">
    <!-- ENTIRE app.js content embedded here -->
  </script>
  <script>
    // 3-line loader: reads vp-code.textContent, creates script tag
    var c = document.getElementById('vp-code').textContent;
    var s = document.createElement('script');
    s.textContent = c;
    document.head.appendChild(s);
  </script>
</body>
```

### app.js structure (106KB, vanilla JS)
- `'use strict'` at top
- Global error handlers (`window.onerror`, `unhandledrejection`)
- CONSTANTS section (APP_VERSION, DEFAULT_PCARDS, TEMPLATES, etc.)
- STATE object `S` — single source of truth
- `loadState()` / `persist()` — localStorage read/write
- `render()` + `attach*()` — main render loop (innerHTML replacement)
- Feature modules: scan, manual, gmail, history, reconcile, dashboard, settings
- Helper functions at bottom

### State Object `S`
```javascript
S = {
  tab, screen, entity,           // navigation
  apiKey, gmailClientId,         // credentials
  txs,                           // all transactions array
  pCards, eCards, msiCards,      // card lists
  pCats, eCats,                  // category lists
  statements,                    // statement history array
  reconRes, insRes,              // reconciliation results
  cur, manualForm,               // current voucher / form state
  gmailToken, importedEmailIds,  // gmail state
  gmailImportResults,            // gmail scan results
  loading, error,                // UI state
  templates                      // expense templates
}
```

### localStorage Keys
| Key | Content |
|---|---|
| `vp_k` | Anthropic API key |
| `vp_t` | Transactions array (JSON) |
| `vp_pc` | Personal cards |
| `vp_ec` | Business cards |
| `vp_pcat` | Personal categories |
| `vp_ecat` | Business categories |
| `vp_en` | Current entity (personal/empresarial) |
| `vp_st` | Statement history |
| `vp_gcid` | Google OAuth Client ID |
| `vp_emids` | Processed Gmail email IDs |

---

## Credentials & Config

| Item | Value |
|---|---|
| Google OAuth Client ID | `497771173219-3nimahamn6rb2jtnmlvc0nru1btbjrqk.apps.googleusercontent.com` |
| Google OAuth authorized origin | `https://fovallef.github.io` |
| Google OAuth test user | `frovfe@gmail.com` |
| Google OAuth status | Testing mode (not published) |
| WhatsApp facturación Clara | `+525629152062` |
| Anthropic model | `claude-sonnet-4-20250514` |

---

## Personal Cards
`American Express, BBVA, Santander, Banamex, Morgan Stanley`

## Business Cards
`Clara`

## MSI Cards (Meses Sin Intereses)
`American Express, BBVA, Banamex`

---

## Key Functions

| Function | Purpose |
|---|---|
| `callClaude(msgs, maxTok)` | Base API call to Anthropic |
| `doImg(e)` | Two-pass voucher scanning (camera/gallery) |
| `doPDF(e)` | Bank statement reconciliation via Claude |
| `doGmailImport()` | Gmail OAuth + search + Claude parsing |
| `parseEmailWithClaude(email)` | Classify email as cargo_real/programado/reembolso/otro |
| `gmailCard(r,i)` | Render Gmail result card (helper, avoids nested templates) |
| `stmtCard(s)` | Render statement history card (helper, avoids nested templates) |
| `mCard(str)` | Map card type string → known card name |
| `mCat(hint,cats,entity)` | Map category hint → category ID |
| `processRecurring()` | Auto-register monthly recurrences on startup |
| `sj(raw)` | Safe JSON parser, strips markdown fences |
| `b64(f)` | FileReader → base64 string |
| `uid()` | Generate unique ID |
| `esc(s)` | HTML escape string |

---

## Release Protocol

```bash
# NEVER have Francisco uninstall or re-anchor the PWA — localStorage data will be lost

# 1. Edit app.js and/or index.html
# 2. Commit and push to main
git add .
git commit -m "feat: description of change"
git push origin main
# 3. Wait 2 minutes for GitHub Pages
# 4. Francisco: close app from multitasking → reopen from home screen icon
# 5. Verify APP_VERSION in header
```

---

## v4.5 Features (implemented May 9, 2026)

- **Dashboard tab primero** — reordenado como tab default
- **FAB escaneo persistente** — botón flotante 📷 siempre visible, abre cámara directamente
- **Navegador de mes en historial** — botones ‹ › para navegar entre meses, label con nombre del mes
- **Resumen mensual** — card con total MXN/USD y número de transacciones por mes
- **Buscador en historial** — input de búsqueda por nombre de comercio o tarjeta
- **Swipe-to-delete** — deslizar fila en historial revela botón 🗑️ (touch events)
- **Estados :active CSS** — feedback táctil en filas, botones nav, stats boxes
- **Monto más prominente** — refunds en verde, montos visualmente resaltados
- **Header gradiente** — fondo degradado indigo en header
- **Velocidad de gasto** — Dashboard muestra proyección al cierre del mes
- **Presupuestos por categoría** — Config permite definir límites; Dashboard muestra barra de progreso por categoría con colores semáforo
- **Fix Amex PDF** — pdfPrompt ahora incluye instrucción JSON-only crítica + formato narrativo Amex MX explícito → Claude siempre devuelve JSON válido

## v4.6 Features (implemented May 10, 2026)

- **Gmail: fallthrough a prompt completo si fast-path devuelve amount=0** — antes devolvía cargo_real con monto 0; ahora cae al prompt completo para extraer monto correctamente
- **Gmail: prompt mejorado** — amtQ usa `150.00` como ejemplo numérico (antes `monto_numerico` literal confundía a Claude); instrucción explícita para buscar monto
- **Gmail: FORMATOS ampliados** — agrega secciones Amazon y Stripe/Servicios con patrones de clasificación; reglas más estrictas para evitar false positives (shipping, order received, etc.)
- **Gmail: extractAmount +6 patrones** — order total, grand total, importe, monto, subtotal, amount charged
- **Gmail: 60 días** — window de búsqueda extendido de 45 a 60 días
- **Gmail: reset automático historial en v4.6** — `vp_gv6` key: primer load limpia `vp_emids` para re-parsear todos los correos con la lógica mejorada
- **Duplicados: dismiss por par** — banner interactivo con "✓ No es duplicado" (persiste en `vp_dd`) y "🗑 Eliminar el más nuevo"
- **Chart Por Tarjeta: brace fix** — `bChart` estaba fuera de `initCharts()` por llave extra; resuelto

---

## Known Issues / Watch Out

- **Nested template literals** crash Safari — always use helper functions or string concatenation
- **Gmail import marks ALL searched email IDs as processed** even if classified as "otro" — prevents re-processing on next import. This is intentional but means if Claude misclassifies an email, it won't be retried unless Francisco clears `vp_emids` from localStorage.
- **`r.children.length===0`** check in unhandledrejection handler may fail to show error if root has static content from splash screen
- **processRecurring()** runs on every startup — if clock is wrong it could double-register
- **Chart.js "Por Tarjeta"** — confirmed working as of v4.3 (was thought to be broken, isn't)
- **Statement on Claude failure** — resuelto: solo se guarda si `res.card_name` o `res.statement_txs.length > 0`, de lo contrario lanza error específico

---

## Email Samples Seen (Rappi MX)

### Type: pedido_programado (IGNORE)
- From: "Recibos de Rappi"  
- Subject: "Order Programada"  
- Body: "tu pedido ha sido creado con éxito", "Total costos: $592.90", "Descuentos: $21.90"  
- → NOT charged yet. Correctly ignored.

### Type: cargo_real (IMPORT)
- From: "Recibos de Rappi"  
- Subject: "Tu pedido de OFFICE DEPOT, 110 - SANTA FE fue entregado"  
- Body: "Pedido entregado", "Total pagado: $571.00"  
- → Actually charged. **Fixed in v4.4** via `preClassifySubject` (subject contains "fue entregado" → cargo_real without Claude) and `cleanEmailBody` (strips promo banner HTML before sending to Claude).

**Root cause of past misclassification:** HTML body started with ChatGPT promo banner, diluting the signal before Claude read the order data. Now resolved.

---

## Voucher Scanning — Terminals Known to Work

| Terminal | Merchant field | Amount field | Date field |
|---|---|---|---|
| Getnet | Line 1-3 (NOT "Getnet") | "Importe $X MXN" | "Fecha: DD/MM/AAAA HH:MM:SS" |
| Clip | Business name at top | "Monto $X" | "Fecha" |
| iZettle/Zettle | Business name | "Total $X" | Date field |
| Amex/bank vouchers | Merchant line | "Importe"/"Total" | Date line |

**TECH/MasterCard** in card type → Clara corporate card (empresarial profile)

---

## Development Workflow for Claude Code

```bash
# Clone the repo
git clone https://github.com/fovallef/Voucher-Pro.git
cd Voucher-Pro

# Files to edit:
# - app.js: all JavaScript logic
# - index.html: rebuild after changing app.js (embed app.js into <script type="text/plain">)

# After editing app.js, rebuild index.html:
python3 rebuild.py  # (create this script — see below)

# rebuild.py template:
# reads index.html template + app.js
# embeds app.js into <script type="text/plain" id="vp-code">
# writes final index.html
```

### rebuild.py (create this in the repo)
```python
#!/usr/bin/env python3
# rebuild.py — embeds app.js into index.html for Safari iOS compatibility

TEMPLATE = 'index_template.html'  # index.html without the vp-code content
APP_JS   = 'app.js'
OUTPUT   = 'index.html'

with open(TEMPLATE) as f: template = f.read()
with open(APP_JS) as f: js = f.read()

# Replace placeholder with actual JS
result = template.replace('<!-- APP_JS_PLACEHOLDER -->', js)

with open(OUTPUT, 'w') as f: f.write(result)
print(f'Built index.html ({len(result):,} bytes)')
```

---

## Team & Deploy Process (as of May 10, 2026)

All changes to VoucherPro go through this mandatory 4-step gate:

```
1. Alex    — Implements the change via Python fix script (string replacement in index.html)
2. Valentina — Runs: python validate_deploy.py
              → EXIT 1 (errors) = BLOCKED, Alex must fix
              → EXIT 0 with warnings = Marco reviews flagged patterns
              → EXIT 0 clean = proceed
3. Marco   — Reviews any Safari/iOS warnings from Valentina's report (APROBADO / RECHAZADO / CONDICIONAL)
4. Watson  — Logic & QA review (semantic correctness, edge cases, regressions)
5. Deploy  — git push origin main → GitHub Pages (~2 min)
```

### AI Team Members

| Member | Role | Activates when |
|---|---|---|
| **Jarvis** | Orchestrator | Always — coordinates all tasks |
| **Alex** | Senior Developer | Any code change in index.html |
| **Valentina** | DevOps & QA | After every Alex implementation, before deploy |
| **Marco** | Safari/iOS Specialist | Valentina flags Safari pattern warnings |
| **Watson** | Senior Researcher / QA | Logic review, deep investigation, pre-deploy semantic check |
| **Lucy** | HR | New team member recruitment |

### validate_deploy.py

Pre-deploy gate — runs 7 checks on index.html:
1. Extracts `<script>` blocks
2. Node.js syntax check (`node --check`) — skipped if Node not available
3. Brace balance `{` / `}`
4. Safari-forbidden pattern scan (errors block, warnings require Marco review)
5. Backtick balance in `rReconResult`
6. `APP_VERSION` present
7. File size < 300KB

**Safari-forbidden patterns (ERROR level — always block deploy):**
- `const const` / `let let` / `var var` — double declaration SyntaxError
- `([k,v])=>` destructuring inside IIFE `+(()=>{...})()` — confirmed Safari crash

**Warning patterns (require Marco review before deploy):**
- `([x,y])=>` general destructuring — safe in `return\`...\`` context, crash in IIFE context
- Template literal inside `${}` — check for true nesting
- `async *` generators — iOS support varies
- `import()` dynamic — not supported in PWA context

---

## Francisco's Profile (for context)

- **Role:** Director General, ONESEC (ciberseguridad CDMX/LATAM)
- **Device:** iPhone 17 Pro Max, iOS 18
- **Technical level:** Non-developer — cannot run local dev tools
- **Language:** Spanish preferred, technical English OK
- **Preference:** Decisive, structured, actionable responses
- **App usage:** Personal finance tracking, both personal and business expenses

---

## Version History

| Version | Date | Key changes |
|---|---|---|
| v4.7 | May 10, 2026 | MSI tracking (pdfPrompt detection, reconciliation section, dashboard card, persistence); card filter History; fix: reconciled txs in PDF context; fix: double-const Safari crash; fix: ([k,v])=> IIFE Safari crash; validate_deploy.py pre-deploy gate |
| v4.6 | May 10, 2026 | Gmail: amount fallthrough, prompt mejorado, +Amazon/Stripe formats, extractAmount+6, 60 días, auto-reset historial; duplicate dismiss; chart fix |
| v4.5 | May 9, 2026 | Dashboard first, FAB escaneo, month nav + search + summary in history, swipe-to-delete, spending velocity, budgets per category, Amex PDF fix |
| v4.4 | May 9, 2026 | PDF beta header fix, API widget (test/tokens/billing), history editing, Gmail expanded (Stripe/1Password/Amazon refined), email pre-classification, regex amount extraction |
| v4.3 | Apr 13, 2026 | Gmail OAuth, statement history, Meli+, Safari fix |
| v4.2 | Apr 2026 | Gmail foundation, refund detection |
| v4.1 | Apr 2026 | Statement history log, interest categories |
| v4.0 | Apr 2026 | Two-pass scanning, Getnet/iZettle prompt |
| v3.x | Apr 2026 | Split architecture (index.html + app.js) |
| v2.x | Apr 2026 | Single-file, Gmail integration start |
| v1.x | Apr 2026 | Initial version |
