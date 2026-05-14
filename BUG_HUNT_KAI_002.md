# Bug Hunt Session #002 — VoucherPro v5.25 · Kai · 2026-05-14

## Charter
Explorar v5.25 con foco en regresiones de Brief 1-bis Fases A/B/C y de 11 fixes en v5.21/v5.22. Tours: Bad Neighborhood (migraciones, persist sync) + Money (cierre con FSM) + Soap Opera (datos legacy).

## Bug Log

| # | Sev | Dim | Título |
|---|---|---|---|
| 12 | **P0** | Migración | Migración v0→v1 statements y v2→v3 corren con `S.statements=[]` (no cargado aún) → no-op silencioso |
| 13 | **P0** | FSM | `transitionTx` definido pero **nunca llamado** — todos los handlers usan mutación directa, FSM decorativa |
| 14 | P1 | FSM | `lifecycle='cancelled'` estado sumidero — sin transición de regreso |
| 15 | P1 | Persistencia | `data-ignorar` muta `statement_tx.status='ignored'` sin `persist()` — se pierde en reload |
| 16 | P1 | FSM | `tdCancelRec` setea `isRecurring:false` sin tocar lifecycle |
| 17 | P1 | FSM | `processRecurring` crea instancias sin `lifecycle` |
| 18 | P2 | Datos | `purgeOldImages` filtra por `status` legacy, debería usar `lifecycle` |
| 19 | P2 | Invariantes | `statement_tx.status` desincronizado con `tx.lifecycle` post-doPDF |
| 20 | P2 | Faltante | `auditInvariants()` y rollback UI no implementados (Brief §4-§5) |
| 21 | P3 | Migración | Backup v1→v2 solo incluye `vp_t`, no `vp_st` (inconsistente) |

## Validación de invariantes (lectura estática)
- **I1** RIESGO — `matched` no alcanzable en código actual; statementRef en datos legacy falla por Bug-12
- **I2** RIESGO — sin soft delete, statementRef puede quedar huérfano
- **I3** FAIL — `tdDel` no propaga al statement_tx vinculado
- **I4** PASS (por tolerancia explícita del invariante)
- **I5** PASS condicional — `txStatus` nunca emite `'ignored'`

## Síntesis ejecutiva
Las 3 fases de Brief 1-bis están en código pero solo Fase A llega al runtime real. Bug-12 anula 60% (statements nunca canonicalizados); Bug-13 anula la FSM (helper muerto, transiciones no validadas). canonicalCard/deriveLifecycle/txStatus funcionan bien donde se les llama.

## Fixes desplegados v5.26
- **Bug-12 (P0)** — migration block reubicado tras dedup; repair flag `vp_b1bis_repaired` fuerza re-corrida una vez sobre datos parcialmente migrados
- **Bug-15 (P1)** — `persist()` agregado en data-ignorar
- **Bug-16 (P1)** — `tdCancelRec` setea `lifecycle:'cancelled'` + `cancelReason`
- **Bug-17 (P1)** — `processRecurring` instancia con `lifecycle:'captured'`

## Cola pendiente
- **Bug-13 (P0)** — refactor de 4 handlers a `transitionTx()` exclusivo. Diferido a Sebastián para Fase D (decisión arquitectónica: tabla FSM permite que la UI bypasse temporalmente; o forzar gateway estricto).
- **Bug-14** — decisión de diseño: ¿`cancelled` terminal o reversible? Sebastián.
- **Bug-18/19/20/21** — cleanup acumulado, defer.

Próximas sesiones de Kai:
- #003 ejecutar `auditInvariants` runtime cuando exista
- #004 storage stress test
- #005 fuzz canonicalCard con strings reales
- #006 verificar idempotencia con backups manuales
