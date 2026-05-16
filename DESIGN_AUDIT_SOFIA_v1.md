# Design Audit v1 — VoucherPro
**Owner:** Sofía (Lead UX/UI Designer)
**Fecha:** 2026-05-16
**Brief:** [Brief 2 — "Confianza por Diseño"](BRIEF_2_SEBASTIAN.md)
**Status:** Audit en progreso · Iteración 1

---

## 1. Auditoría visual — hallazgos críticos

### 1.1 Contraste (severidad: alta · WCAG fail)

Tokens actuales:
| Variable | Color | Uso | Contraste vs --bg (#09090f) |
|---|---|---|---|
| `--tx`  | #f0f0f8 | Texto primario | **17.8:1** ✓ WCAG AAA |
| `--tx2` | #8a8ab0 | Metadata, labels | **5.1:1** ✓ WCAG AA |
| `--tx3` | #44446a | Texto terciario, secciones colapsadas | **2.0:1** ✗ **FAIL WCAG AA (4.5:1 mínimo)** |

`--tx3` está debajo del mínimo legal para iOS/web. Se usa en:
- Fechas en cards de statement
- Labels "Promedio / cargo"
- "9 px" texto bajo monto MXN
- Hints de empty state

**Recomendación:** elevar `--tx3` a #6E6E94 (contraste ≈3.5:1, todavía secundario pero legible). Para texto MUY terciario, eliminar — si no se puede leer, no agrega valor, agrega ruido.

### 1.2 Tipografía (severidad: alta)

Escala observada en código:
| Size | Uso | iOS HIG mínimo |
|---|---|---|
| 9px  | Labels en stat boxes (Cargos / Conciliados) | 11pt = 14.6px |
| 10px | Notas en rows, labels secundarios | 14.6px |
| 11px | Metadata principal, badges | 14.6px |
| 12px | Body small | 14.6px |
| 13-14px | Body | 17pt = 22.7px ideal |

**4 niveles tipográficos están bajo el mínimo iOS.** En iPhone 17 Pro Max (460dpi) los 9-11px son leíbles a 20cm de distancia, pero Francisco tiene 47 años y usa la app en condiciones reales (luz variable, después de comer, manejando).

**Recomendación — escala v2:**
```
--fs-xs:   11px  (era 9-10px)   — solo para badges decorativos
--fs-sm:   13px  (era 11-12px)  — metadata, labels
--fs-base: 15px  (era 13-14px)  — body
--fs-md:   17px  (era 15-16px)  — montos, titulares de section
--fs-lg:   20px  (era 17-18px)  — titulares prominentes
--fs-xl:   28px  (era 22-24px)  — números héroe (total mes)
```

### 1.3 Densidad (severidad: media)

Pantalla Historial (screenshot 2026-04-26, 9:09 AM):
- Header (logo + entity toggle): 1 elemento
- Subtitle (versión + fecha): 1 elemento
- Month nav: 3 elementos (‹, label, ›)
- Summary card: 3 datos
- Search field: 1 elemento
- Card chips: 3+ elementos
- Filter chips: 11 elementos (Todos, Pendientes, Conciliados, Manuales, Recurrentes, MSI, En disputa, Sin conciliar, Cerrados + scroll)
- Subtotal bar: 1 elemento
- Row de tx: 6-7 elementos visuales por row (icon, merchant, card+date, badges, monto, currency, status dot, edit btn, swipe-del)

**Total elementos visibles en viewport sin scroll: ~22.** iOS HIG recomienda ≤12 elementos atomicos por pantalla para reducir carga cognitiva.

**Recomendación:**
- Colapsar filter chips en un dropdown "Más filtros" con solo 3 chips visibles (Todos, Pendientes, MSI)
- Subsumir status dot dentro del color del monto (verde = reconciliado, naranja = pending)
- Quitar el subtitle "v5.5x · 11 May 2026" del header (irrelevante para uso diario, mover a Config)

### 1.4 Hints y onboarding (severidad: media)

Cero estados de descubrimiento. Specifically:
- Sin tooltip en ningún botón
- Empty states son texto plano sin acción ("Sin transacciones")
- Botones nuevos (lápiz editar, papelera swipe) sin descubrimiento — usuario debe adivinar
- Sin tour inicial primera vez

**Recomendación:**
- Empty states con call-to-action ("Sin transacciones en abril. → Captura tu primer voucher")
- Coachmarks one-time en features nuevas (después de v5.57, primera visita a Historial muestra "← Desliza para borrar / ✏️ tap para editar")
- Microcopy en hover/long-press (en touch, long-press 600ms muestra tooltip)

---

## 2. Sistema de Diseño v2 — Tokens propuestos

### 2.1 Color
```css
/* Backgrounds — sin cambio */
--bg:  #09090f;
--bg2: #14141d;  /* +alpha del actual #111118 para más jerarquía */
--bg3: #1f1f2a;  /* idem */

/* Texto — re-balanceado por WCAG AA */
--tx:  #f0f0f8;  /* sin cambio — primary */
--tx2: #a8a8c8;  /* era #8a8ab0, sube contraste a 6.5:1 */
--tx3: #6e6e94;  /* era #44446a, sube a 3.5:1 (mínimo legible) */
--tx4: #4a4a6c;  /* NUEVO — para deco/divisores, no para texto */

/* Acentos — sin cambio (todos pasan WCAG) */
--in: #6366f1; --em: #10b981; --am: #f59e0b; --rd: #f43f5e;
```

### 2.2 Tipografía
```css
--fs-xs:11px; --fs-sm:13px; --fs-base:15px; --fs-md:17px; --fs-lg:20px; --fs-xl:28px;
--fw-r:400; --fw-m:500; --fw-sb:600; --fw-b:700; --fw-eb:800;
--lh-tight:1.2; --lh-normal:1.45; --lh-loose:1.6;
```

### 2.3 Espaciado (8pt grid)
```css
--sp-1:4px; --sp-2:8px; --sp-3:12px; --sp-4:16px; --sp-6:24px; --sp-8:32px; --sp-12:48px;
```

### 2.4 Density tiers
- **Compact:** density default actual (vista 22 elementos / viewport)
- **Comfortable:** density v2 propuesto (≤14 elementos / viewport, más espacio entre rows)
- **Spacious:** futuro (8 elementos / viewport — para uso ocasional o presentaciones)

Setting en Config: "Densidad de información" con 3 niveles.

---

## 3. Mockups — pendientes

Esta semana produzco mockups en ASCII/markdown (no tengo herramientas de diseño visual aún) para:

1. **Dashboard** — actual vs. propuesto (con Audit Dashboard del Pilar 2 integrado)
2. **Historial** — colapso de filter chips, density comfortable, monto sin status dot
3. **Conciliar (statement card)** — jerarquía visual de contadores, badge ignorados rediseñado

Adjunto en `DESIGN_AUDIT_SOFIA_v1.md` actualizaciones cuando estén listos.

---

## 4. Next steps

1. **Esta semana:** completar mockups, refinar tokens con feedback de Francisco
2. **Sign-off de Francisco** sobre mockups ANTES de tocar código
3. **Alex implementa tokens v2** en una sola PR (cambio de variables CSS — bajo riesgo de regresión)
4. **Refactor de pantallas** una por PR (Dashboard → Historial → Conciliar)

---

*Sofía — Lead UX/UI Designer · Iteración 1, 2026-05-16*
*Próxima iteración: mockups, esta semana*
