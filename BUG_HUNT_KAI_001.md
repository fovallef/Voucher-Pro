# Bug Hunt Session #001 — VoucherPro v5.20 · Kai · 2026-05-14

## A. Session Report SBTM

**Charter:** Explorar VoucherPro v5.20 con foco en cambios recientes (v5.15-v5.20) y áreas de alto riesgo histórico (state machine, persistencia, conciliación, duplicados) para descubrir defectos funcionales, regresiones e inconsistencias.

**Tours aplicados:** Feature, Back Alley, Bad Neighborhood, Soap Opera, Money.

**Áreas cubiertas:** loadState/persist/processRecurring, isDupe, doPDF, rReconcile, rReconResult, attachReconcile (resolve/resume), attachReconResult, attachDisputeModal, attachTxDetail (rectify/cancelRec), purgeOldImages, smartResetBtn, auditDupBtn, Gmail toggleAllGm, Amex CR credits, history filter pills.

**Áreas NO cubiertas:** ejecución dinámica (no browser), Safari-specific, Charts.js, PWA offline, fuzz real de parseEmail.

**Charters de seguimiento:**
- #002 fuzz parseEmail/extractAmount con 30 emails reales
- #003 state-machine canonical de Transaction.status
- #004 storage stress test al 95%
- #005 duplicado cross-flow soap opera

---

## B. Bug Log (priorizado)

| # | Sev | Dim | Título |
|---|---|---|---|
| 01 | **P0** | Datos | "Reinicio controlado" borra silenciosamente vouchers escaneados |
| 02 | **P0** | Persistencia | Re-stitch `_stmtId` falla para statements pre-v5.16 |
| 03 | **P0** | Funcional | `processRecurring` genera fechas inválidas (día 31 en feb) |
| 04 | P1 | Funcional | `classify()` falla por mismatch `s.bank` vs `t.card` |
| 05 | P1 | State machine | Dispute desde reconResult deja statement_tx huérfano |
| 06 | P1 | State machine | Rectify no revierte `_dtx.status='disputed'` en statement |
| 07 | **P0** | Funcional | `data-resolve` corrompe `status='reconciled'` sin haber conciliado |
| 08 | P1 | Datos | `purgeOldImages` borra evidencia b64 de cargos disputados >60d |
| 09 | P1 | Funcional | isDupe excluye instances → Gmail duplica recurrentes |
| 10 | P2 | UX/Datos | `totalAmt` del header del PDF incluye credits |
| 11 | P2 | Funcional | "Sin conciliar" pill en History siempre 0 por bug-04 |

**Patrón sistémico (escalado a Sebastián):**
Bugs 04, 05, 06, 07, 11 son la misma falla: ausencia de FSM `Transaction.lifecycle` (H2 auditoría) + ausencia de identidad canónica `bank↔card`. Validar Brief 1-bis: "Identidad canónica de tarjeta" + lifecycle FSM antes de seguir parchando.

---

## C. Bug detalle: P0s

### Bug-01 · P0 · Smart Reset destructivo
**Repro:** Escanear 3 vouchers → ir a Config → "🔄 Reinicio controlado" → confirmar. Los 3 escaneados desaparecen.
**Evidencia:** Línea 112363 `S.cur = {id,entity,card,merchant,...,status:'pending'}` sin `isManual:true`. Filtro de smart reset `t=>t.isManual||t.gmailImport` (línea 210) nunca matchea scaneos.
**Fix:** `t=>t.b64||t.scanRaw||t.gmailImport||t.isManual`

### Bug-02 · P0 · Migración _stmtId pre-v5.16
**Repro:** Usuario con `vp_recon` guardado en v5.14 → upgrade a v5.20 → editar unrecognized → cerrar app → reabrir → divergencia.
**Evidencia:** Línea 131 `if(S.reconRes&&S.reconRes._stmtId)` excluye datos legacy.
**Fix:** Si no hay `_stmtId`, buscar statement por `(bank===card_name && cutDate===cut_date && entity===S.entity)` y stitchear.

### Bug-03 · P0 · processRecurring fecha inválida
**Repro:** Template día 31 (ej. Renta) → app inicia en febrero → `newDate = '2026-02-31'` → rollover JS a `2026-03-03` → double-register en marzo.
**Evidencia:** Línea 132 `const newDate=\`${thisMonth}-${day}\`` sin validación.
**Fix:** Clamp `day` al último día válido del mes destino.

### Bug-07 · P0 · data-resolve → reconciled fantasma
**Repro:** Crear tx disputada → Conciliar → sección "Disputas activas" → "✅ Marcar como resuelto". Tx pasa a `reconciled` aunque nunca matched a un PDF.
**Evidencia:** Línea 288 `S.txs=S.txs.map(t=>t.id===id?{...t,status:'reconciled',resolvedDate:td()}:t)`.
**Fix:** Patrón tdRectify: `status:'pending', disputeNotes:null, disputeDate:null, resolvedAt:td()`.

---

## D. Asignaciones

- **Alex:** P0 batch (Bug-01, 02, 03, 07). Coordinar Bug-02 con Watson.
- **Valentina:** 4 reglas regression en validate_deploy.py — smart reset filter consistency, fechas válidas, status enum cerrado, `_stmtId` siempre presente.
- **Watson:** semántica de migración pre-v5.16 (clave `bank+cutDate+entity`).
- **Sebastián:** patrón sistémico cluster 04/05/06/07/11.
- **Próxima sesión Kai:** #004 storage stress tras P0 fixes.
