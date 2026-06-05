# Brief 4 — "Ejecución de Liberación Operativa" (Retrospectiva v5.53 → v5.91)

**Owner:** Sebastián (CPO/Strategist)
**Fecha:** 2026-06-05
**Cubre:** commits v5.53 → v5.91 (post Brief 3)
**Status:** EN EJECUCIÓN — cierre objetivo Brief 3 sigue siendo 2026-06-08
**Versión productiva actual:** v5.91

---

## Propósito de este documento

Brief 3 (2026-05-18) definió el *plan* de los 3 Pilares de Liberación Operativa. Este Brief 4 documenta **lo que realmente se construyó** en las ~3 semanas siguientes, mapea avance vs. plan, y deja registro de dos incidentes de ingeniería relevantes (dedup MSI y Service Worker) cuyos aprendizajes deben informar Briefs futuros.

No reemplaza a Brief 3; lo continúa.

---

## Avance por Pilar (plan vs. realidad)

### Pilar 1 — Conciliación Asistida + rediseño "hero"  🟢 Mayor avance
Lo planeado era auto-match de alta confianza, sugerencias top-3 y auto-create con badge. Lo entregado se concentró en **propagación MSI** y en el **rediseño de las pantallas principales a layout "hero"**:

- **Dashboard v2** (v5.62) — hero summary + audit colapsado por defecto
- **Historial v2** (v5.63) — filtros colapsados + empty-state con CTA
- **Conciliar v2** (v5.65) — hero counter + preview de cargos no reconocidos ("rojos")
- **Propagación MSI statement→tx** (v5.66→v5.73) — el statement ahora empuja el plan MSI al tx, con matching que evolucionó: exacto → fuzzy (v5.68) → tx-side directo (v5.70) → auto-crear txs faltantes desde `msi_charges` (v5.71)

> ⚠️ v5.64 fue un **revert**: el refactor del hero rompió Historial (`diff undefined`). Aprendizaje: los refactors de layout deben validarse pantalla por pantalla antes de push.

### Pilar 2 — Cierre de Mes Asistido  🟡 No iniciado como wizard
El wizard guiado de 4 pasos **no se implementó** en este periodo. Sí avanzaron sus cimientos indirectos: integridad de datos del Audit Dashboard (ver Pilar transversal abajo) y el diario de fricción. **Pendiente para cerrar Brief 3.**

### Pilar 3 — Memoria + Insights  🟡 Parcial
La card "Insights del mes" y la integración recurrente con NotebookLM **no se implementaron** como feature de la app. La pieza de MSI próximos a terminar quedó cubierta indirectamente por el tracking MSI. La integración NotebookLM sigue siendo manual (este mismo flujo). **Pendiente.**

---

## Pilar transversal no planeado: Integridad de datos (confianza)

Surgió como necesidad urgente y consumió esfuerzo significativo. Es el trabajo de mayor riesgo contable del periodo:

- **Audit linkage** (v5.55, v5.57, v5.59–v5.61): excluir `ignored` del denominador, validar fecha en `isTxClosed`, des-vincular linkages sospechosas (Path A), persist global defensivo + check "sin-persist" en el validator.
- **Diario de fricción** (v5.53, v5.54, v5.56): edición/limpieza de entradas, normalización de status raros, ocultar botones editar/borrar en tx cerrados.

---

## 🔴 Incidente 1 — Saga de deduplicación MSI (v5.74 → v5.80)

**Qué pasó:** v5.74 relajó la llave de dedup a solo `amount+entity` (msi opcional). El matcher quedó **demasiado laxo** y causó daño de datos: un cargo UBER fue pisado con `msi=6` y un Mercado Libre fue eliminado.

**Respuesta:** v5.76 hizo UNDO del daño; v5.77–v5.80 reconstruyeron la mecánica de dismiss con base sólida: `setItem` directo, llave simplificada sin fechas + verificación de existencia del tx (v5.78), logging extenso (v5.79) y finalmente **`vp_dd` merge-on-persist** (v5.80) — nunca se pierden las llaves "dismissed".

**Aprendizaje (ya anticipado en Brief 3, Riesgo 1):** todo matcher automático arranca con threshold alto y baja gradual. La llave de identidad de un tx debe basarse en **datos invariantes**, no en campos que el propio proceso puede mutar.

---

## 🔴 Incidente 2 — Saga del Service Worker (v5.85 → v5.91)

**Qué pasó:** K-7 introdujo un Service Worker para auto-update (v5.85/86). v5.88 fue un **hotfix**: el script del SW tenía comentarios `//` que causaban `SyntaxError` en L380. v5.89 y v5.91 fueron *dummy version bumps* para probar el mecanismo en vivo.

**Resolución:** v5.90 **reemplazó el Service Worker por un version-check directo** (fetch-based update banner) por compatibilidad con PWA en iOS. El SW completo resultó frágil en el contexto Safari/iOS PWA.

**Aprendizaje:** consistente con las restricciones de `CLAUDE.md` — Safari iOS PWA castiga soluciones "estándar" de web. Preferir mecanismos simples y verificables sobre Service Workers completos.

---

## Otros entregables de UX (v5.58, v5.81–v5.84, v5.87)

- v5.58 — contraste `--tx3` elevado a WCAG AA mínimo
- v5.81 — UX-01: validación de fechas inusuales en captura manual
- v5.82 — UX-02: auto-save de presupuestos al editar cada rubro
- v5.83 — K-6: reducir verbosidad del audit log
- v5.84 — tx row UX "iOS-like" (monto no se desborda, swipe-del oculto en reposo)
- v5.87 — M4: búsqueda cross-month en Historial (hallazgo de Kai)

---

## Estado vs. cierre de Brief 3 (objetivo 2026-06-08)

| Pilar | Plan | Realidad | Gap para cerrar |
|---|---|---|---|
| 1 — Conciliación asistida | Auto-match + top-3 + auto-create | Hero redesign + propagación MSI | Falta el motor de auto-match por confianza |
| 2 — Cierre de mes | Wizard 4 pasos | No iniciado | Todo el wizard |
| 3 — Memoria + Insights | Card Insights + NotebookLM | Parcial (MSI) | Card Insights + integración recurrente |

**Lectura estratégica:** el periodo se desvió del plan hacia **integridad de datos** (no planeada pero necesaria) y **rediseño visual hero**. Los Pilares 2 y 3 — los que más "liberan" a Francisco del trabajo operativo — siguen pendientes. Recomendación: Brief 5 debe re-priorizar el wizard de Cierre de Mes como el unlock de mayor valor restante.

---

## Riesgos abiertos

1. **Deuda de Pilar 2/3:** el objetivo central de Brief 3 (liberar tiempo operativo) aún no se materializa en features.
2. **Fragilidad de identidad de tx:** la saga MSI mostró que la llave de dedup sigue siendo delicada; cualquier cambio futuro debe pasar por Kai antes de push.
3. **Mecanismo de update:** v5.90 es nuevo; validar en campo que el banner de versión funcione en el PWA de iPhone de Francisco.

---

*Sebastián — CPO/Strategist · Brief 4 retrospectivo, 2026-06-05 · fuente: reflog git v5.53→v5.91*
