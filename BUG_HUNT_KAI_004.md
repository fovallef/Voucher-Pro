# Bug Hunt #004 — Post Brief 2, pre Brief 3
**Hunter:** Kai
**Fecha origen:** 2026-05-18 · **Última actualización:** 2026-05-19
**Versiones bajo prueba:** v5.85 → v5.91 (extendido durante reparación SW)
**Status:** EN CURSO — M4 cerrado, M2 parcial, M1 y M3 pendientes

---

## Contexto

Brief 2 cerró con 24 deploys en 2 días (v5.56-v5.84). Brief 3 arranca esta semana. Antes de meter más features, necesito barrer la superficie actual con cabeza fresca. **Particular foco en lo que se rompió silenciosamente durante el ritmo intenso.**

---

## Charter (90 min timeboxed)

Cuatro misiones cortas. Ordenadas por valor de información, no por probabilidad.

### M1 — Migrations sin persist (verificar daño residual)

`validate_deploy.py` reportó **7 migrations con potencial daño**:
- vp_v541_repair
- vp_v547_stmt_dedup
- vp_v550_stx_side_repair
- vp_v552_stx_side_lax
- vp_v554_diag_normalize
- vp_v555_unignore
- vp_v559_unlink_suspects

**Hipótesis:** Si cualquiera de estas dejó datos en estado inconsistente que el persist global de v5.61 no agarró, hay daño latente.

**Acción:** correr `auditInvariants()` exhaustivo + checks adicionales:
- Bidireccional broken (`tx.statementRef.statementTxId` no existe en statement)
- Lifecycle reconciled sin statementRef (no _legacyReconciled)
- Statement con paidAt malformado

**Reportar:** suspicious linkages encontradas + paths para reparar.

### M2 — Service Worker fresh (v5.86) — **PARCIAL (replanteada)**

**Hallazgo 2026-05-19:** SW NO funciona en iOS Safari PWA standalone (limitación conocida del platform). Tras v5.86-v5.88 con barra de update no apareciendo, se replanteó la estrategia:
- v5.90 eliminó el SW y reemplazó por fetch directo de `index.html?_t=<ts>` cada 3 min + on visibilitychange
- v5.91 deployado como dummy version-bump para verificar el banner azul
- **Pendiente:** Francisco confirma visualmente si la barra "✨ Nueva versión (v5.91) disponible" aparece en su iPhone PWA

Riesgos típicos de SW originalmente identificados:
- **Cache stuck**: usuario actualiza pero ve versión vieja por días (lo que se quería resolver, paradójicamente puede empeorar si SW se queda con caché stale)
- **Race condition**: SW instala v2 mientras app v1 está activa → estado mixto
- **Offline broken**: si SW falla, ¿la app sigue funcionando o ladrillo?
- **Update prompt loop**: barra "Nueva versión" aparece pero update no toma efecto

**Acción:** test sequence
1. Cargar v5.86 fresh
2. Hacer commit + push v5.87 dummy (solo bump version)
3. Esperar 1-2 min
4. Recargar app — debe aparecer barra "Nueva versión"
5. Tap "Actualizar" — debe recargar y mostrar v5.87
6. Cerrar/abrir 5 veces seguidas → no debe haber loops ni errores

**Reportar:** comportamiento SW vs. esperado.

### M3 — UX iOS bug aún visible (.am 17px→14px en v5.85)

Francisco dijo en v5.84 que "el texto del monto sigue demasiado grande". v5.85 lo bajó a 14px. **¿Es suficiente?**

**Acción:** test visual en iPhone 17 Pro Max real:
- Listas con montos de 1-5 dígitos
- Listas mixed (algunos con currency MXN, otros USD)
- Pulse en swipe-delete → animación clean (no asomar rojo)
- Alignment vertical de currency

**Reportar:** issue específicos por pantalla (Historial, Conciliar) o aprobar.

### M5 — isDupe rechaza match contra recurrente con merchant variante — **✅ CERRADA 2026-05-23**

**Reporte de Francisco:** Gmail import de Amazon Prime $99 (mensual). El recurrente ya existía y processRecurring ya había creado la instancia del mes. El Gmail import NO detectó el duplicado y creó un cargo adicional. Resultado visible: dos cargos casi idénticos en el historial (21-may y 22-may, ambos $99 AmEx).

**Causa raíz:** `isDupe(c, txs)` en index.html requería match **exacto** de merchant (lowercase). El recurrente tenía merchant = `"Amazon Prime"` (o similar) mientras que el Gmail parser trajo `"la membresía Amazon Prime"` (extraído por Claude del subject/body del email). Lowercase: `'amazon prime' !== 'la membresía amazon prime'` → no matchea → no detecta duplicado.

**Fix aplicado (v5.92):** substring bidireccional. Si uno está contenido en el otro (y ambos >2 chars), considerar match. Los otros filtros (amount ±$0.01, mismo currency, misma card, ventana 3 días, mismo signo) siguen previniendo falsos positivos.

```javascript
// Antes:
if((ex.merchant||'').toLowerCase()!==cm)return false;

// Después:
const em=(ex.merchant||'').toLowerCase();
if(em!==cm && em.length>2 && cm.length>2 && !em.includes(cm) && !cm.includes(em)) return false;
```

**Cleanup pendiente del usuario:** el cargo duplicado del 22-may (el creado erróneamente por Gmail import) sigue existiendo en localStorage. El fix NO lo borra automáticamente (no tocamos datos del usuario, solo el código futuro). Francisco tiene que borrarlo manualmente en la app (swipe-delete o desde la edición).

**Verificación recomendada:** próximo mes, al recibir email Amazon Prime + correr Gmail import, debe marcar dup-skip en lugar de crear cargo.

### M4 — Bug latente: Mercado Libre $189 no visible — **✅ CERRADA 2026-05-18**

**Causa raíz:** Búsqueda de Historial limitada a `byMonth` (transacciones del mes activo). El tx Mercado Libre $189 existía en `S.txs` pero su fecha caía fuera del mes que Francisco veía cuando buscaba "Mercad".

**Fix aplicado (v5.87):** El search expande el pool de búsqueda a todas las transacciones de la entidad activa cuando hay query — no solo el mes actual.

```javascript
const _searchPool = srch ? S.txs.filter(t=>t.entity===S.entity) : byMonth;
```

Validado por Francisco visualmente. No requiere fix adicional.

---

## Fuera de scope

- Generación de podcasts/videos NotebookLM (eso es producto, no QA)
- Performance benchmarks (no hay quejas)
- Cross-browser testing (Safari iOS es target único)

---

## Cronograma

| Misión | Tiempo | Inicio |
|---|---|---|
| M1 audit invariantes | 20 min | Inmediato — solo lectura de código |
| M2 SW testing | 30 min | Requiere deploy v5.87 dummy |
| M3 UX visual | 10 min | Francisco verifica visualmente |
| M4 Mercado Libre filter | 30 min | Análisis estático |

**Cierre:** reporte consolidado al final de la sesión.

---

## Reglas de auto-delegación (per skill Kai)

- Bugs triviales → fix auto delegado a Alex (no preguntar)
- Bugs recurrentes (mismo patrón) → escalar a Valentina (mejora pre-deploy gate)
- Bugs sistémicos (arquitectura) → escalar a Sebastián (input a Brief 3)

---

*Kai — Bug Hunter · Charter #004, 2026-05-18 · Última edición 2026-05-19*

---

## Resumen ejecutivo del estado (2026-05-19)

| Misión | Status | Próximo paso |
|---|---|---|
| M1 invariantes | 🔴 Abierta | Correr auditInvariants() sobre las 7 migrations sin persist |
| M2 SW → fetch | 🟡 Parcial | Francisco confirma visualmente banner v5.91/v5.92 en iPhone PWA |
| M3 .am 14px | 🔴 Abierta | Validar visualmente si la reducción es suficiente |
| M4 Mercado Libre | ✅ Cerrada | — (fix en v5.87) |
| M5 isDupe merchant | ✅ Cerrada | — (fix en v5.92) |

**Recomendación Kai:** cerrar M2 (confirmar banner) antes de abrir M1, porque M1 requiere baseline limpio sin updates en curso.
