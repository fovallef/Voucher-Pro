# Bug Hunt Session #003 — VoucherPro v5.26 · Kai · 2026-05-14

## Charter
Verificar que los fixes de v5.26 cierran lo levantado en Sesión #002 sin introducir regresiones. Foco específico en el reorder del migration block + repair flag.

## A. Verificación de fixes v5.26

| Fix | Status | Notas |
|---|---|---|
| Bug-12 (P0) reorder migration + repair flag | **PASS** | Orden correcto. Repair flag idempotente. Migraciones siguen siendo idempotentes con re-corrida forzada. |
| Bug-15 (P1) `persist()` en data-ignorar | **PASS** | Orden correcto persist→render. Doble cobertura vía `vp_recon` y `vp_st`. |
| Bug-16 (P1) tdCancelRec lifecycle:'cancelled' | **PASS** | Transición válida desde captured/reconciled/disputed/resolved. |
| Bug-17 (P1) processRecurring lifecycle:'captured' | **PASS** | Cobertura parcial — ver K3-01. |

## B. Nuevos hallazgos

### K3-01 (P2) · Lifecycle confiado al backfill de persist en 6 sitios
Mismo anti-patrón que Bug-17 pero en otras rutas: L162 (manual save), L172/L286 (scan review), L292 (CSV import), L369/L370/L372 (gmail 3 rutas). Las txs nacen sin `lifecycle`; `persist()` lo rescata. Funciona, pero código frágil ante lecturas pre-persist.

### K3-02 (P3) · `canceledAt` typo legacy coexiste con `cancelledAt`
L191 tdCancelRec setea ambos en el mismo spread. `canceledAt` no se lee en ningún lugar del codebase. Code smell — eliminar el typo.

### K3-03 (P3) · Repair flag se setea ANTES de que la migración corra
L131: si la migración falla a mitad, el flag queda en `'1'` y el observable next-reload se pierde. Las migraciones convergen igual por idempotencia (catch absorbe), pero mover el set al FINAL del try block es mejor.

## C. Síntesis ejecutiva
v5.26 es deploy limpio. Bug-12 sólido. 3 hallazgos P2/P3 son hygiene, no bloqueantes. Aplicables en una pasada.
