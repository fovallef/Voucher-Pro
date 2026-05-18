# Bug Hunt #004 — Post Brief 2, pre Brief 3
**Hunter:** Kai
**Fecha:** 2026-05-18
**Versiones bajo prueba:** v5.85 + v5.86 (post UX polish + K-7 Service Worker)
**Status:** ARRANCANDO

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

### M2 — Service Worker fresh (v5.86)

Recién deployado. Riesgos típicos de SW:
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

### M4 — Bug latente: Mercado Libre $189 no visible

Pendiente desde v5.78. El tx existe en `S.txs` (confirmado por audit dump) pero no aparece en search "Mercad" en abril 2026.

**Acción:** debug filter de Historial:
- `S.txs.filter(t=>t.merchant.includes("MERCADO"))` desde consola del log viewer
- ¿El tx tiene flag que lo excluye? `_legacyReconciled`, `_autoCreatedFromMSI`, `lifecycle`, etc.
- ¿La fecha es de un mes que Francisco no está viendo?
- ¿El search es case-sensitive accidentalmente?

**Reportar:** causa raíz + fix recomendado.

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

*Kai — Bug Hunter · Charter #004, 2026-05-18*
