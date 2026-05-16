# Brief 2 — "Confianza por Diseño"
**Owner:** Sebastián (CPO/Strategist)
**Fecha:** 2026-05-16
**Target cierre:** 2026-05-25
**Status:** APROBADO por Francisco · arrancando

---

## Contexto: por qué este brief, por qué ahora

Brief 1-bis cerró con la arquitectura de datos sólida: canonicalCard, FSM lifecycle, invariantes auditables, MSI tracking, schema migration, bidirectional linkage. **El producto técnicamente funciona.**

Pero el feedback directo del usuario (2026-05-16) revela el siguiente cuello de botella, que NO es técnico:

> *"GUI saturado, letra muy pequeña con poco contraste, usabilidad confusa, no hay hints de uso"*

Esto NO es polish. Es la barrera que está impidiendo que VoucherPro sea **confiable para uso financiero serio**. Cuando un usuario duda de lo que está viendo, deja de usar la herramienta o (peor) la usa mal.

**La hipótesis estratégica de Brief 2:** *El siguiente unlock de valor no es más features, sino confianza por diseño — claridad visual + visibilidad de datos + integridad explícita.*

---

## Tres pilares

### Pilar 1 — Claridad Visual (Owner: Sofía)

**Problema:** Crecimiento orgánico produjo 11+ chips de filtro, 5 íconos por row, 3-4 contadores por card, paleta dark con contraste subóptimo, tipografía 9-11px.

**Output esperado:**
- `DESIGN_AUDIT_SOFIA_v1.md` con:
  - Auditoría visual completa (jerarquía, contraste, densidad, tipografía)
  - Sistema de Diseño v2 (tokens: escala tipográfica, contraste WCAG AA mínimo, density tiers, semáforo)
  - Mockups before/after de las 3 pantallas más visitadas (Dashboard, Historial, Conciliar)
- Refactor en código (post-aprobación de Francisco) — separado en PRs por pantalla para evitar regresión masiva

**Criterio de éxito:**
- Toda metadata legible sin acercar pantalla a >25cm
- Contraste WCAG AA en 100% del texto de información
- Densidad reducida ≥30% en pantallas críticas (medido en elementos visibles sin scroll)

### Pilar 2 — Confianza en Datos (Owner: Sebastián + Alex)

**Problema:** El usuario no sabe qué tan recientes/correctos son los datos que ve. ¿El contador 54/54 de Amex es de ahora, o de antes de la última migración? ¿Esos 4 stx revertidos por v5.55 son correctos? La auditoría existe pero está enterrada en logs.

**Output esperado:**
- **Audit Dashboard** visible: card en Dashboard que muestra
  - "Última verificación de integridad: hace X min"
  - "N invariantes activos (1 pendiente)" — clickable a detalle
  - "N migraciones aplicadas en esta sesión" — auditable
- **Source-of-truth indicators** en cada tx:
  - Badge sutil indicando origen (📷 scan, 📧 gmail, 📄 statement, ✏️ manual)
  - Tooltip con timestamp de última verificación contra statement
- **"Última verificación"** en cada statement card (no solo "subido el X")

**Criterio de éxito:** En 5 segundos, el usuario puede contestar "¿confío en lo que estoy viendo?" mirando un solo card del Dashboard.

### Pilar 3 — MSI como First-Class Citizen (Owner: Sebastián + Alex + Watson)

**Problema:** Bug arquitectónico identificado por Kai (M3): `t.msi`, `statement.msi_charges`, y `S.msiCommitments` son tres universos paralelos sin propagación. Filtro "MSI (0)" es engañoso porque siempre subreporta.

**Decisión de producto registrada (Francisco, 2026-05-16):** El estado de cuenta es la fuente de verdad para MSI.

**Reglas operativas a implementar:**

| Caso | Statement | Tx pre-existente | Resultado |
|---|---|---|---|
| 1 | MSI=N detectado | `tx.msi=null` | `tx.msi=N`, `msiSource='statement'` |
| 2 | MSI=N detectado | `tx.msi=M` (distinto) | `tx.msi=N` (statement gana), conservar `msiUserClaimed=M` |
| 3 | No detecta MSI | `tx.msi=N` (usuario marcó) | No tocar (asumir error de Claude al parsear) |
| 4 | No detecta MSI | `tx.msi=null` | No-op |
| 5 | Usuario edita manualmente después | (cualquier) | Usuario gana, `msiSource='user_override'` |

**Output esperado:**
- Función `propagateMSIFromStatement(statement, tx)` invocada en cada reconcile
- Migración retroactiva una sola vez sobre todos los statements existentes
- Schema: `tx.msi`, `tx.msiSource`, `tx.msiUserClaimed`, `tx.msiVerifiedAt`
- Filtro MSI en historial sigue igual (solo lee `t.msi`), pero ahora refleja realidad

**Criterio de éxito:**
- Filtro MSI muestra # real de cargos a meses sin intereses (esperado en datos actuales: ~5-15 entre Amex+BBVA)
- Dashboard MSI Commitments cuadra con suma de `tx.msi` truthy

---

## Cronograma propuesto

| Día | Sofía | Alex | Sebastián | Kai |
|---|---|---|---|---|
| 16-may (hoy) | Auditoría visual + tokens | v5.57-audit deployed ✓ | Brief 2 escrito ✓ | Esperando log v5.57 |
| 17-19 may | Mockups before/after | Pilar 2: Audit Dashboard | Refinamiento conflictos MSI | Análisis log Kai-M1 |
| 20-22 may | DESIGN_AUDIT_SOFIA_v1.md final | Pilar 3: propagación MSI | Revisar outputs Pilar 1+2 | Bug hunt #005 sobre Pilar 3 |
| 23-24 may | Implementar tokens (post-aprobación) | Pilar 3: migración retroactiva | Cierre y validación Brief 2 | Regression sweep |
| 25-may | Validación con Francisco | Deploy v5.6x final | Brief 3 candidato | — |

---

## Dependencias y riesgos

**Dependencia crítica:** Aprobación de Francisco para mockups de Sofía antes de implementar Pilar 1 en código. **NO** tocar UI sin sign-off visual.

**Riesgo 1:** Pilar 3 (MSI) puede destapar datos inconsistentes que requieran cleanup adicional. Mitigación: Kai hace bug hunt #005 sobre cada release de Pilar 3.

**Riesgo 2:** Sofía propone cambios que rompen muscle memory del usuario. Mitigación: cambios opt-in en Config inicialmente, opt-out después de 1 semana de uso.

**Riesgo 3:** Bundle de 3 pilares es grande. Si algo se atora, **cortar Pilar 3 primero** (es feature) y mantener Pilares 1+2 (son arquitectura de confianza).

---

## Lo que NO está en Brief 2

- Nuevas features de captura (camera, gmail, etc.)
- Nuevos bancos
- Export contable / reportes para contador
- iCloud sync entre devices
- Modo claro / light theme

Todo lo anterior es candidato para Brief 3.

---

## Próximos pasos inmediatos

1. **Sofía:** arranca auditoría visual hoy — produce el documento esta semana.
2. **Alex:** después de que Francisco verifique log v5.57, arranca Pilar 2 (Audit Dashboard).
3. **Yo (Sebastián):** refino reglas de conflicto MSI con Watson durante esta semana.
4. **Kai:** espera log v5.57, analiza M1, reporta findings al equipo.

---

*Sebastián — CPO/Strategist · Brief 2 oficial, 2026-05-16*
