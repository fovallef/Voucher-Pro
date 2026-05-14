# Audit Report — VoucherPro · Sebastián · 2026-05-13

Francisco, antes de entrar al detalle: la app no está "batida". Está en el umbral donde un producto deja de ser una herramienta personal y empieza a comportarse como un sistema. Lo que sientes como caos es la ausencia de un modelo mental único. En siete tabs estás sosteniendo cuatro productos distintos cosidos a mano. Esta auditoría te dice cuál es el producto, qué corre el riesgo de hundirlo, y dónde está la palanca.

---

## 1. Job-to-be-Done principal

> **Cuando** termina el ciclo de mi tarjeta y llega el estado de cuenta, **quiero** saber al instante qué cargos son míos, cuáles son sospechosos y cuánto debo pagar con confianza, **para** cerrar el mes en cinco minutos y no en dos horas — y dormir tranquilo de que ningún cargo se me escapó.

Eso es el job principal. No es "tracking de gastos". El tracking es el **costo del job**, no el job. Nadie escanea vouchers por placer; los escanea para no tener que pelearse con BBVA o Amex días después.

**Jobs secundarios:**
1. *Anticipar el daño:* "saber cuánto voy a deber antes de que llegue el corte" — necesidad del CFO interno (velocidad de gasto, presupuestos, MSI acumulados).
2. *Separar mundos:* "no mezclar lo personal con ONESEC" — toggle entidad personal/empresarial es ya el rasgo más diferencial del producto.
3. *Defenderme:* "cuando veo algo raro, poder disputarlo con evidencia" — la foto del voucher es la prueba contra el banco.

**North Star Metric propuesta:**
**% de cargos del estado de cuenta del mes conciliados con confianza dentro de las 48h post-corte**, ponderado por monto.

---

## 2. Mapa actual de la experiencia

| Tab | Propósito declarado | Uso real probable | Peso en el JTBD principal |
|---|---|---|---|
| **Dashboard** | Foto del mes | Apertura diaria casual | Medio — informativo, no accionable |
| **Escanear** | Capturar voucher físico | Pico al final del día | Alto — input crudo del job |
| **Manual** | Capturar gasto sin voucher | Sporádico, defensivo | Medio |
| **Gmail** | Importar cargos Rappi/Uber | Una vez por semana | Alto — captura long tail digital |
| **Historial** | Ver y editar transacciones | Búsqueda específica | Bajo (apoyo) |
| **Conciliar** | Subir PDF y emparejar | **El momento de la verdad** | **Crítico — JTBD** |
| **Config** | Ajustes, categorías, presupuestos | Setup inicial y rescate | Bajo (utilitario) |

### Journey crítico: "Cierre de mes"

Puntos de fricción estructurales:
- El estado tx es plano (`pending`/`reconciled`/`disputed`), pero el journey real tiene 7+ estados implícitos. **No hay máquina de estados.** Los bugs v5.6→v5.14 no son accidentes: son entropía estructural.
- Reanudar conciliación requiere re-subir el PDF; `reconRes` (sesión) y `statement_txs` (histórico) divergen.
- **Duplicados:** tres mecanismos paralelos (`dismissedDupes`, `importedEmailIds`, `auditDupBtn`). Ningún `tx_hash` canónico al insertar.
- **Sin estado "cierre afirmado":** no hay objeto `MonthCloseSession`. Tu confianza al cerrar es implícita.

---

## 3. Hallazgos

### Críticos

**H1 · Funcional · No existe el concepto de "ciclo cerrado"**
La app no tiene noción de "mes/tarjeta cerrado con confianza". Solo transacciones individuales con `status`. → Introducir `CardCycle` (tarjeta + corte) con estados `open → reconciling → closed`.

**H2 · Arquitectura · `status` plano no representa el dominio**
Una tx puede ser simultáneamente "manual + recurrente + gmail + dismissed + disputed-rectificada". 7 banderas booleanas dispersas. → Refactor a `Transaction { source, lifecycle: FSM, flags: {recurring, msi, refund} }`.

**H3 · UX · Siete tabs en nav inferior sin jerarquía**
iOS HIG recomienda 3-5 max. Tres son inputs, uno es **el outcome** (Conciliar), uno panorama, uno archivo, uno setup. → Reducir a **4 tabs**: Hoy / Bandeja / Cierre / Más.

### Altos

**H4 · UX · No existe Bandeja de "cosas por procesar"** — Inbox unificado con `lifecycle: 'captured'`.

**H5 · Funcional · Conciliación con dos fuentes de verdad** — `reconRes` vs `statement_txs` divergen. → Una sola fuente; `reconRes` pasa a ser `activeStatementId`.

**H6 · UX · Toggle Personal/Empresa es mode-switch peligroso** — modal global no etiquetado. → Color fuerte por entidad + toast confirmatorio.

**H7 · Funcional · Tres mecanismos paralelos de duplicados** — Hash canónico al insertar.

**H8 · Oportunidad no resuelta · No hay confirmación de pago efectivo** — Conciliar ≠ pagar. Trivial agregar `paidAt` en `CardCycle`.

### Medios

**H9** — Dashboard sin jerarquía narrativa (6 widgets apilados). Working Backwards: "¿voy bien?" merece un solo widget hero.
**H10** — Pantalla Review post-scan demasiado fría. Falta el wow-moment.
**H11** — Gmail oculta su valor diferencial. Promover a Bandeja + import automático en background.
**H12** — `localStorage` cerca del límite con vouchers en base64. Mover imágenes a IndexedDB.

### Bajos

**H13** — Render por innerHTML completo. Dividir por tab.
**H14** — Status visualmente ambiguo (pending recurrente vs gmail-sin-matching). Color = nivel de atención.
**H15** — Destructive actions sin protected confirmation.

---

## 4. Oportunidades nuevas

| # | Idea | Job | Esfuerzo |
|---|---|---|---|
| **O1** | **Asistente de cierre** — wizard guiado mensual, notifica 24h antes del corte | "no recordar el orden de los pasos" | S/M |
| **O2** | Forecast del corte en vivo | "saber cuánto voy a deber antes del banco" | M |
| **O3** | Modo evidencia — paquete PDF de disputa con voucher | "defenderme con prueba" | S |
| **O4** | Detector de fugas — alerta trimestral de suscripciones | "saber qué pago que ya no uso" | M |
| **O5** | Cierre conjunto ONESEC — export CFDI a contador | "no llevar a mano lo empresarial" | L |

---

## 5. Roadmap propuesto (4 semanas)

**Track 1 — Limpiar (s1-2):** Frena el ciclo de bugs estructurales.
1. H5 + H7: Una fuente única de verdad + hash de duplicados al insertar.
2. H3: Reducir nav a 4 tabs.
3. H6: Color de entidad fuerte + confirmación de cambio.

**Track 2 — Profundizar (s2-3):** Validar **O1 Asistente de cierre**. Respuesta directa al "la app está batida": no agrega features, agrega *secuencia*.

**Track 3 — Arquitectura (s3-4):** H1 + H2 — Introducir `CardCycle` y `Transaction.lifecycle` como FSM. Migración de `localStorage` con flag de versión. Esto desbloquea O2, O3, O5.

---

## 6. Briefs de delegación (Track 1)

### Brief 1 — Fuente única de verdad para conciliación
- **Resp:** Alex (principal) + Watson (semántica migración)
- **Problema:** Conciliación tiene dos representaciones que se contradicen.
- **Éxito medible:** Cero divergencias entre `reconRes.statement_txs` y `statements[i].statement_txs` en test de 10 ciclos abrir/cerrar/reanudar.
- **Restricciones:** Migración no-destructiva. Safari iOS. Single-file.
- **Pista técnica:** `S.reconRes` deja de ser objeto; pasa a ser `S.activeStatementId`. Lecturas van a `S.statements.find(s=>s.id===S.activeStatementId)`.

### Brief 2 — Hash de duplicados al insertar
- **Resp:** Alex
- **Problema:** Tres mecanismos paralelos, ninguno previene en inserción.
- **Éxito medible:** Re-importar mismo PDF no crea duplicados. Escanear mismo voucher dispara modal de merge. `auditDupBtn` no encuentra nada tras 30 días.
- **Restricciones:** No invalidar `importedEmailIds` ni `dismissedDupes` (legacy).
- **Pista técnica:** `txHash(tx)` = `slug(merchant) + amount + date(±2d)`. Set en memoria al cargar.

### Brief 3 — Navegación reducida a 4 tabs
- **Resp:** Sofía (principal) + Alex (impl)
- **Problema:** Usuario decide entre 7 destinos cada apertura.
- **Éxito medible:** Heurística Nielsen #2 cumplida. "Cerrar el mes de septiembre" debería tomar ≤3 taps.
- **Restricciones:** Mantener FAB scan y toggle Personal/Empresa. iOS HIG.
- **Pista técnica:** `NAV` de 7 a 4. "Más" como secondary list. Bandeja unifica pending de scan + gmail + manual.

### Brief 4 — Entidad personal/empresa con identidad visual
- **Resp:** Sofía
- **Problema:** Toggle 👤/🏢 cambia todo sin registro consciente.
- **Éxito medible:** Francisco identifica entidad activa en <1s desde cualquier pantalla. Cero capturas accidentales en una semana.
- **Restricciones:** Sin cambiar data model. WCAG AA.
- **Pista técnica:** Tinte de fondo por entidad + transición + microcopy "Cambiaste a Personal" 2s.

---

## 7. Gap analysis del equipo

El equipo actual cubre Tracks 1 y 2. **No reclutar todavía.**

Q3 evaluar: **Domain Expert Fiscal MX** si Track 2 valida O5 (CFDI 4.0, conciliación PYME, SAT).

---

## Cierre

La app no está batida. Está pidiéndote que dejes de tratarla como un script y empieces a tratarla como un producto. El JTBD es claro, el journey crítico está identificado, y los próximos 14 días de Alex y Sofía pueden reducir 60% de la fricción sin agregar una sola feature nueva.

**La pregunta no es "qué construimos". Es: ¿qué dejamos de construir para que el job principal se cumpla en cinco minutos?**
