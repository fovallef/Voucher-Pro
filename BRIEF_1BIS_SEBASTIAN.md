# Brief 1-bis · Arquitectura canónica · VoucherPro · Sebastián · 2026-05-14

Francisco, los parches v5.22 funcionan. La deuda no. Bugs 04/05/06/07/11 son sintomas de dos huecos primitivos: (a) no hay identidad canonica de tarjeta y (b) no hay FSM de transaccion. Cada feature nueva reinventa el mapeo `bank↔card` inline y el set de transiciones permitidas. Esto es el diseno para tapar ambos huecos de forma estructural sin romper los datos de las ultimas dos semanas en localStorage.

Tres principios guia:
1. **Un solo lugar donde se decide la identidad.** Ni `rReconcile` ni `rHistory` ni `doPDF` mapean tarjetas. Llaman a un helper.
2. **El estado es una FSM declarada, no una cadena libre.** `lifecycle` es un enum. Las transiciones son una tabla. Los efectos colaterales viven dentro del helper de transicion.
3. **Migracion idempotente o no se hace.** Si el helper corre dos veces sobre la misma data, el resultado es identico. Sin esto Francisco pierde sus datos en el primer rollback.

---

## 1. Identidad canonica de tarjeta

### Problema concreto
Hoy conviven cuatro representaciones del concepto "tarjeta":
- `t.card` en transacciones: `"American Express"`, `"Amex Platinum 1006"`, `"AMEX **1006"`, `"American Express 4003"`
- `s.bank` en statements: lo que Claude extrajo del PDF, libre
- `c.name` en `S.pCards` / `S.eCards`: la forma "oficial" registrada por el usuario
- `voucher.card_type` del scan: lo que el modelo vision saco del ticket

`mCard()` ya existe pero es un best-effort que solo encuentra por primera palabra y solo se llama en scan. Conciliacion no lo usa: por eso v5.22 tuvo que canonicalizar inline en dos lugares (`rReconcile._rcCards` + `rHistory._hCards`). Cada nueva feature va a copiar ese patron mal.

### Helper canonico

**Firma:**
```javascript
// Resuelve cualquier string a un card.name registrado en S.pCards o S.eCards.
// Sin side effects. Pure function. Idempotente: canonicalCard(canonicalCard(x))===canonicalCard(x).
function canonicalCard(raw, opts){
  // opts = { entity?: 'personal'|'empresarial', strict?: bool }
  // strict=true: si no hay match, return null (caller decide que hacer)
  // strict=false (default): si no hay match, return raw (preserva data del usuario)
  // entity: si se pasa, restringe el search; si no, busca en pCards+eCards
  // Return: string (card.name canonico) | null si strict y no hay match
}
```

**Algoritmo (en orden de confianza, primer hit gana):**
1. **Exact match** case-insensitive contra `c.name`.
2. **Last-4 match**: si `raw` contiene `\d{4}` y existe `c.last4` igual, gana ese. (Requiere extender `pCard`/`eCard` con `last4` opcional — Fase A no lo exige aun.)
3. **First-token contains**: `raw.toLowerCase().includes(c.name.toLowerCase().split(' ')[0])` — lo que hace v5.22 hoy.
4. **Alias table** explicita para casos que no caen en 1-3:
   ```javascript
   const CARD_ALIASES = {
     'amex': 'American Express',
     'american express': 'American Express',
     'bbva bancomer': 'BBVA',
     'banamex': 'Banamex',
     'citibanamex': 'Banamex',
     'morgan': 'Morgan Stanley',
     'tech': 'Clara',          // Clara reporta "TECH/MasterCard" en algunos vouchers
     'mastercard': null         // ambiguo: no resolver solo por marca
   };
   ```
   Pero solo si el alias resuelto existe en `c.name` de las tarjetas registradas. Si Francisco no tiene Clara, `'tech'` no resuelve.
5. **Sin match**: `strict?null:raw`.

**Donde se llama:**
| Sitio | Hoy | Despues |
|---|---|---|
| `doPDF` (al guardar statement) | `s.bank = res.card_name` libre | `s.bank = canonicalCard(res.card_name, {entity:S.entity}) \|\| res.card_name` |
| `rReconcile` latestCut | inline canon dentro del map | `latestCut[canonicalCard(s.bank)] = ...` |
| `rHistory` _hlc | inline canon idem | `_hlc[canonicalCard(s.bank)] = ...` |
| `doImg` (scan) save | `card: mCard(res.card_type)` | `card: canonicalCard(res.card_type, {entity:'personal'}) \|\| S.pCards[0].name` |
| `isDupe` | `ex.card===tx.card` | `canonicalCard(ex.card)===canonicalCard(tx.card)` |
| Gmail import | `card: r.card \|\| S.pCards[0]?.name` | `card: canonicalCard(r.card, {strict:false}) \|\| S.pCards[0].name` |
| Manual entry | bind directo al `select` | sigue igual (`select` ya tiene `c.name`) pero el value se pasa por `canonicalCard` antes de persist como red de seguridad |
| `processRecurring` template→instance | copia `tpl.card` | `card: canonicalCard(tpl.card)` |

**Sin match en doPDF (statement de tarjeta no registrada):**
Comportamiento explicito: se guarda `s.bank` con el valor raw + flag `s.bankUnresolved=true`. La UI muestra una banderita en el card del statement: *"Esta tarjeta no esta en tu lista. ¿Agregarla?"* con CTA directa a Config. **Nunca crear tarjetas auto.** Francisco decide.

**Migracion de datos existentes:**
En `loadState`, despues de leer `vp_t` y `vp_st`, correr **una vez** (gated por `vp_schema_version`):
```javascript
// Pseudocodigo
function migrateCardsToCanonical(){
  S.txs = S.txs.map(t => {
    const c = canonicalCard(t.card, {strict:true});
    return c ? {...t, card: c, _cardRaw: t._cardRaw || t.card} : t;
  });
  S.statements = S.statements.map(s => {
    const c = canonicalCard(s.bank, {strict:true});
    return c ? {...s, bank: c, _bankRaw: s._bankRaw || s.bank} : {...s, bankUnresolved: true};
  });
}
```
`_cardRaw` / `_bankRaw` preservan la forma original. **Nunca se pierde data.** Si Francisco renombra una tarjeta en Config, una segunda corrida resuelve mejor.

---

## 2. FSM explicita de `Transaction.lifecycle`

### Set canonico de estados

Despues de revisar los handlers que tocan `t.status` hoy y los estados implicitos del journey (auditoria H2), el set minimo correcto es:

| Estado | Significado | Quien lo setea hoy |
|---|---|---|
| `captured` | Tx existe, no esta vinculada a ningun statement. Default de scan/manual/gmail. | Scan, manual, gmail import |
| `matched` | Aparecio en un statement Y el usuario (o el algoritmo) la vinculo, pero el ciclo no esta cerrado. | reconResult al hacer match |
| `reconciled` | Statement cerrado, tx confirmada como cargo legitimo del usuario. | "Aceptar conciliacion" / cierre de ciclo |
| `disputed` | Statement_tx aparecio sin tx, usuario la marca como sospechosa. Espera respuesta del banco. | Dispute desde reconResult / Manual desde detail |
| `resolved` | Disputed cuya investigacion termino (banco rectifico o usuario acepto). Es un cargo legitimo. **Termina disputed.** | tdRectify, data-resolve |
| `cancelled` | Tx que el usuario decidio ignorar (suscripcion cancelada, error de captura, etc.). No cuenta en totales. | (nuevo) cancelar recurrente, eliminar manual |
| `ignored` | Statement_tx detectada por Claude pero el usuario afirma que no es suya (no la disputa, solo la oculta — ej. cargo de oficina del corporativo). | (nuevo) "ocultar" en reconResult |

**Lo que NO esta en el enum a proposito:**
- `'pending'`: ambiguo (¿pre-match? ¿post-rectify?). Se reemplaza por `captured` (nunca vinculada) o `resolved` (post-disputa).
- `'unrecognized'`: solo existe en `statement_tx.status`, no en `tx.lifecycle`.
- `'credit'`: refund. No es lifecycle; es flag (`tx.isRefund`). Vive en `flags`.

### Mapa de transiciones

```
captured --[match]--> matched
captured --[dispute]--> disputed
matched --[acceptCycle]--> reconciled
matched --[dispute]--> disputed
matched --[unmatch]--> captured
disputed --[rectify]--> resolved
disputed --[acceptAsValid]--> reconciled    (banco confirmo el cargo, el usuario lo acepta)
disputed --[cancel]--> cancelled            (cargo nunca debio existir, banco lo bajo)
reconciled --[reopen]--> matched            (raro: error retroactivo)
* --[cancel]--> cancelled                    (admin override; solo via UI explicita)
captured --[ignore]--> ignored
ignored --[restore]--> captured
```

Todas las demas transiciones son ilegales y deben tirar warning en consola + `return false` del helper.

### Helper de transicion

**Firma:**
```javascript
// Aplica una transicion validada con efectos colaterales declarados.
// Retorna true si la transicion fue valida y aplicada, false si fue rechazada.
// NUNCA muta S directamente; retorna una nueva tx. El caller hace el splice.
function transitionTx(tx, newLifecycle, ctx){
  // ctx = { event, reason?, statementId?, statementTxId?, disputeNotes?, by?:'user'|'system' }
  // Retorno: { ok:bool, tx:Tx|null, sideEffects:Array<{op,target,patch}> }
}
```

**`sideEffects`** es la lista de mutaciones que el caller debe aplicar a OTRAS partes del estado (statements, otros tx). Esto desacopla la decision (que transicion) del barrido (que mas hay que tocar). Ejemplos:

| Transicion | Efectos sobre tx | sideEffects |
|---|---|---|
| `captured → matched` | `lifecycle='matched'`, set `statementRef`, set `matchedAt` | `[{op:'patch', target:'statementTx', selector:{statementId, statementTxId}, patch:{status:'matched', matched_id:tx.id}}]` |
| `matched → reconciled` | `lifecycle='reconciled'`, set `reconciledAt` | `[{op:'patch', target:'statementTx', ..., patch:{status:'reconciled'}}]` |
| `* → disputed` | `lifecycle='disputed'`, set `disputeDate`, set `disputeNotes` | `[{op:'patch', target:'statementTx', ..., patch:{status:'disputed', matched_id:tx.id}}]` |
| `disputed → resolved` | `lifecycle='resolved'`, `disputeNotes=null`, set `resolvedAt`, **mantiene** `disputeDate` para historico | `[{op:'patch', target:'statementTx', ..., patch:{status:'unrecognized', matched_id:null}}]` |
| `disputed → reconciled` | `lifecycle='reconciled'`, `disputeNotes=null`, set `acceptedAsValidAt` | `[{op:'patch', target:'statementTx', ..., patch:{status:'reconciled', matched_id:tx.id}}]` |
| `* → cancelled` | `lifecycle='cancelled'`, set `cancelledAt`, set `cancelReason` | `[{op:'patch', target:'statementTx', ..., patch:{status:'unrecognized', matched_id:null}}]` |

El caller hace algo asi:
```javascript
const result = transitionTx(t, 'reconciled', {event:'acceptCycle', statementId:sid, statementTxId:stxid});
if(!result.ok){ console.warn('ilegal'); return; }
const idx = S.txs.findIndex(x=>x.id===t.id);
S.txs[idx] = result.tx;
applyEffects(result.sideEffects);   // helper que recorre y aplica los patches
persistDebounced();
```

`applyEffects` vive junto a `transitionTx` y es el unico lugar que muta `statement_txs`. Esto cierra Bug-05/06/07: hoy esos bugs son cada handler reinventando "ah, y ademas el _dtx".

### Migracion de `status` plano a `lifecycle`

```javascript
// vp_schema_version: 0 -> 1 (FSM)
// Idempotente: si ya tiene lifecycle, no toca.
function migrateStatusToLifecycle(){
  S.txs = S.txs.map(t => {
    if(t.lifecycle) return t;   // ya migrada
    let lc = 'captured';
    if(t.status === 'reconciled') lc = 'reconciled';
    else if(t.status === 'disputed') lc = 'disputed';
    else if(t.status === 'pending'){
      if(t.rectifiedAt) lc = 'resolved';        // pending post-rectify
      else if(t.resolvedAt) lc = 'resolved';    // pending post-data-resolve
      else lc = 'captured';
    }
    return {...t, lifecycle: lc, _statusLegacy: t.status};
  });
}
```

### Coexistencia con `status`

**Recomendacion: mantener `status` como derived field, deprecar lectura directa.**

```javascript
// getter que vive en helpers
function txStatus(t){
  // Retorna el string legacy que el codigo viejo espera.
  const lc = t.lifecycle || 'captured';
  if(lc === 'reconciled' || lc === 'matched') return 'reconciled';
  if(lc === 'disputed') return 'disputed';
  if(lc === 'cancelled' || lc === 'ignored') return 'cancelled';
  return 'pending';  // captured, resolved
}
```

En `persist`, antes de serializar, recalcular `t.status = txStatus(t)`. Esto mantiene retrocompatibilidad de cualquier lectura inline que quede (no se va a auditar todo en Fase B). En Fase C se elimina el field `status` del schema.

**Reglas para el equipo:**
- Codigo nuevo lee `t.lifecycle`, nunca `t.status`.
- Codigo nuevo escribe via `transitionTx`, nunca por asignacion directa.
- Valentina agrega regla a `validate_deploy.py`: cualquier `t.status=` o `t.status:` literal en code nuevo es ERROR (con allowlist de las funciones que aun no se refactorearon).

---

## 3. Link bidireccional `tx ↔ statement_tx`

### Estado actual (post v5.22)
- `statement_tx.matched_id = tx.id` cuando hay match.
- `tx` no apunta de regreso al statement_tx. Por eso `tdRectify` tiene que hacer fallback `merchant+date` para encontrar el _stx vinculado.

### Propuesta

```javascript
tx.statementRef = {
  statementId: string,      // S.statements[i].id
  statementTxId: string,    // statement.statement_txs[j].id (introducir si no existe)
  linkedAt: ISO
} | null
```

Y en `statement_tx` mantenemos `matched_id: tx.id`. Es redundante a proposito (mejor que recorrer todo `S.statements`).

**Requisito previo:** cada `statement_tx` necesita un `id` estable. Hoy no lo tienen — se identifican por indice. Migracion los siembra:

```javascript
function ensureStatementTxIds(){
  S.statements.forEach(s => {
    if(!s.statement_txs) return;
    s.statement_txs.forEach(stx => {
      if(!stx.id) stx.id = uid();
    });
  });
}
```

### `propagateToStatements(tx, prevTx)`
Helper que `applyEffects` invoca cuando el caller no pasa side effects explicitos (caso degradado, p.ej. importacion legacy):
```javascript
function propagateToStatements(tx, prevTx){
  // Si tx.statementRef existe, busca el statement_tx y lo sincroniza con tx.lifecycle.
  // Si no existe statementRef pero existia en prevTx, lo desvincula.
  // Idempotente: si statement_tx ya esta en el estado correcto, no hace nada.
}
```

### Cuando un statement se elimina
Hoy: nada pasa. Las txs quedan con `statementRef` apuntando a un id muerto.

Politica: **soft delete** de statement → marca `s.deletedAt`, no se filtra de `S.statements` (preserva auditoria). Las txs con `statementRef.statementId === s.id`:
- Si `lifecycle === 'reconciled'`: se degradan a `matched` (no se pierde la reconciliacion pero queda visible que el respaldo se borro).
- Si `lifecycle === 'matched'`: vuelven a `captured`, `statementRef = null`.
- Si `lifecycle === 'disputed'`: se mantienen disputed pero `statementRef` queda con flag `orphaned:true`.

Hard delete solo desde Config con confirmacion explicita.

---

## 4. Plan de migracion no-destructiva

### Versionado de schema
```javascript
const SCHEMA_VERSION = 2;   // bump en cada migracion estructural
// localStorage: 'vp_schema_version' = '0' | '1' | '2'
```

### Pipeline en `loadState`
```
1. Leer vp_schema_version (default '0' si no existe)
2. Si es < SCHEMA_VERSION:
   a. Crear backup: localStorage['vp_t_backup_v'+SCHEMA_VERSION] = localStorage['vp_t']
                    localStorage['vp_st_backup_v'+SCHEMA_VERSION] = localStorage['vp_st']
   b. Aplicar migraciones en orden:
      - migrateCardsToCanonical()   (v0 -> v1)
      - ensureStatementTxIds()      (v0 -> v1)
      - migrateStatusToLifecycle()  (v1 -> v2)
   c. persist()
   d. localStorage['vp_schema_version'] = SCHEMA_VERSION
   e. Log a console: '[VoucherPro] schema migrado v'+prev+' -> v'+SCHEMA_VERSION
3. Continuar con el resto de loadState como hoy
```

### Idempotencia
Cada migracion individual checa "ya esta migrado" como primera linea. Si Francisco abre la app dos veces seguidas con la misma version, las migraciones son no-ops.

### Rollback
Solo si Francisco lo pide explicito (no auto):
```javascript
function rollbackSchema(toVersion){
  // 1. Confirmar con el usuario.
  // 2. Si existe localStorage['vp_t_backup_v'+toVersion+1], restaurar a vp_t.
  // 3. Idem statements.
  // 4. localStorage['vp_schema_version'] = String(toVersion).
  // 5. location.reload()
}
```
Boton en Config bajo "Avanzado", oculto detras de un confirm con texto explicito ("perderas cambios desde la ultima migracion").

### Tiempo maximo en background
Migracion completa sobre 500 txs + 12 statements: estimado <50ms en iPhone 17. Aceptable on-startup. Si crece a >1000 txs, mover a `requestIdleCallback`.

---

## 5. Invariantes del sistema

Validate_deploy.py debe poder expresar estos. Marcados con **[runtime]** los que requieren ejecucion (no estaticos).

1. **[runtime]** Toda `tx` con `lifecycle ∈ {matched, reconciled}` tiene `statementRef !== null`.
2. **[runtime]** Toda `tx` con `statementRef !== null` apunta a un `(statement, statement_tx)` que existe (no orphaned).
3. **[runtime]** Para todo `statement_tx` con `matched_id !== null`, existe `tx` con `id === matched_id` Y `tx.statementRef.statementTxId === statement_tx.id`. (bidireccionalidad)
4. **[runtime]** No existe `statement_tx.status === 'disputed'` sin una `tx` vinculada en `lifecycle === 'disputed'`.
5. **[runtime]** `tx.card` siempre esta en el conjunto `[...S.pCards, ...S.eCards].map(c=>c.name)` **O** `tx._cardRaw` existe (significa: tarjeta no registrada, preservada original).
6. **[runtime]** `tx.lifecycle` siempre esta en el enum declarado. Cualquier otro valor = corrupcion.
7. **[runtime]** Si `originalAmount` existe, `Math.sign(amount) === Math.sign(originalAmount)`. (refund consistency)
8. **[runtime]** Toda `tx` tiene `id`, `createdAt`, `entity`, `card`, `amount`, `date`. Faltantes = corrupcion.
9. **[runtime]** `lifecycle === 'resolved'` implica `disputeDate !== null` y `resolvedAt !== null`.
10. **[static]** En `index.html`, ninguna asignacion directa a `t.lifecycle =` fuera de `transitionTx`. Grep regex: `/\.lifecycle\s*=\s*['"]/` en codigo nuevo (allowlist transitionTx body).
11. **[static]** Ninguna lectura de `t.status` fuera de la zona deprecated. (allowlist `txStatus`, `persist`)
12. **[runtime]** `vp_schema_version` en localStorage **igual** a `SCHEMA_VERSION` en codigo despues de loadState.

Helper de auditoria nuevo: `auditInvariants()` que recorre todos y reporta. Boton en Config > Avanzado. Output legible.

---

## 6. Test plan para Kai (Sesion #002 post-arquitectura)

**Charter sugerido:** Validar que la arquitectura canonica resuelve cluster 04/05/06/07/11 sin introducir regresiones en flujos felices.

### Escenarios canonicalCard
- **CC-01** Statement con `bank = "Amex Platinum 1006"` → `s.bank` queda como `"American Express"`, `_bankRaw` preserva original.
- **CC-02** Tx con `card = "AMEX **1006"` post-migracion queda como `"American Express"`.
- **CC-03** Statement de tarjeta NO registrada (ej. "Inbursa 1234") → `s.bank` raw, `s.bankUnresolved = true`, UI muestra CTA "Agregar tarjeta".
- **CC-04** Pildora "Sin conciliar" en History muestra count correcto (>0 cuando hay txs sin reconciliar post-corte).
- **CC-05** Renombrar tarjeta en Config + reload + re-correr migracion → resuelve mejor sin romper data previa.
- **CC-06** `canonicalCard(canonicalCard("amex"))` === `canonicalCard("amex")` (idempotencia).

### Escenarios FSM
- **FSM-01** Scan → captured → conciliar PDF → matched → cerrar ciclo → reconciled. Verificar `statementRef` poblado.
- **FSM-02** Disputa desde reconResult → tx con `lifecycle='disputed'`, statement_tx con `status='disputed' + matched_id`.
- **FSM-03** Rectify desde detail → `lifecycle='resolved'`, statement_tx revierte a `unrecognized`, `matched_id=null`.
- **FSM-04** Transicion ilegal: intentar `captured → resolved` directo → `transitionTx` retorna `{ok:false}`, S no cambia.
- **FSM-05** Reload app despues de cada transicion → estado persiste correctamente.
- **FSM-06** Tx historica pre-migracion con `status='pending'` + `rectifiedAt` → post-migracion `lifecycle='resolved'`.

### Escenarios link bidireccional
- **LK-01** Match tx ↔ statement_tx → ambos apuntan entre si.
- **LK-02** Eliminar statement (soft) → tx reconciled degrada a matched, conserva data.
- **LK-03** Eliminar tx con `statementRef !== null` → statement_tx vuelve a `unrecognized`, `matched_id=null`.
- **LK-04** Migracion sobre data v5.22: statement_tx sin `id` recibe uno, txs reconciled obtienen `statementRef` por busqueda `matched_id`.

### Escenarios migracion
- **MIG-01** Primer boot post-deploy: schema v0 → v2, backups creados, log en consola, sin perdida.
- **MIG-02** Segundo boot: migraciones no-op, todo igual.
- **MIG-03** Forzar `vp_schema_version='0'` manualmente + reload → migracion corre de nuevo, idempotente.
- **MIG-04** Rollback v2→v1 desde Config → backup restaurado, app sigue funcionando degradada.

### Invariantes (auditInvariants())
- **INV-01** Despues de cualquier flujo feliz, `auditInvariants()` no reporta violaciones.
- **INV-02** Inyectar corrupcion manual (DevTools: `S.txs[0].lifecycle='wat'`) → auditoria la detecta.

### Regresiones criticas (no romper)
- **RG-01** Scan + manual + Gmail siguen guardando con `lifecycle='captured'` (era `status='pending'`).
- **RG-02** Dashboard widgets siguen calculando totales correctamente (validar contra dataset known).
- **RG-03** Pildoras History (pending/reconciled/disputed) cuentan via `txStatus(t)` derivado.
- **RG-04** `purgeOldImages` sigue purgando reconciled +60d, NO purga disputed.
- **RG-05** `processRecurring` no rompe (canonicaliza la tarjeta del template).

---

## 7. Plan de implementacion por fases

### Fase A — Identidad canonica (low risk)
**Scope:** `canonicalCard` helper + migracion de `S.txs[].card` y `S.statements[].bank`. Reemplazar canonicalizaciones inline de v5.22 por llamadas al helper.

**Lineas nuevas estimadas:** ~80 lineas (helper + tabla aliases + migracion + replace de inline canon en 2 sitios + extender a doPDF/doImg/isDupe).

**Cambios destructivos:** ninguno. `_cardRaw`/`_bankRaw` preservan original.

**Riesgos:**
- Alias incorrecto que canonicaliza algo que no deberia (ej. resolver "Mastercard" agresivo). Mitigacion: tabla conservadora, `strict:false` default preserva raw.
- Performance en arrays grandes. Mitigacion: helper es O(n cards) por llamada; cachear con Map `raw→canonical` si Kai detecta lag.

**Salida Fase A:** v5.23. Bug-04 y Bug-11 dejan de ser parches inline; canonicalizacion vive en un solo sitio. Bug-09 (isDupe) se beneficia transitivamente.

### Fase B — FSM (medium risk)
**Scope:** `transitionTx` + `applyEffects` + `txStatus` derived + migracion `status → lifecycle` + reemplazar las ~8 asignaciones directas a `t.status` actuales por `transitionTx` calls. Mantener `t.status` recalculado en `persist`.

**Lineas nuevas estimadas:** ~180 lineas (helper FSM + tabla transiciones + 8 sitios reemplazados + migracion + audit invariants).

**Cambios destructivos:** ninguno. Reads viejos siguen funcionando via `t.status` derivado.

**Riesgos:**
- Side effect olvidado en alguna transicion → tx queda en estado correcto pero statement_tx no. Mitigacion: `auditInvariants` corre en cada persist en debug mode los primeros 7 dias.
- Algun `status==='pending'` en codigo viejo asume "no conciliada" pero ahora "resolved" tambien rinde `pending` por derived. Mitigacion: Watson hace pasada semantica en handlers de Dashboard, History.
- Performance: derived `txStatus` en cada persist sobre 500 txs es <2ms, aceptable.

**Salida Fase B:** v5.24. Bug-05/06/07 estructuralmente cerrados. Cualquier feature nueva que introduzca un estado lo agrega a la FSM, no inventa.

### Fase C — Link bidireccional (high risk)
**Scope:** `tx.statementRef` + `statement_tx.id` estable + `propagateToStatements` + soft delete de statements + politicas de orfandad + remover fallback `merchant+date` de v5.22.

**Lineas nuevas estimadas:** ~120 lineas (helper de propagacion + migracion ids + UI soft-delete + remover fallbacks que ya no aplican).

**Cambios destructivos:** **potencialmente alto**: si la migracion de `statementRef` falla en una tx reconciled vieja sin `matched_id` claro, queda en limbo. Mitigacion: si no se puede inferir, degradar a `lifecycle='captured'` con `_recoveryNeeded=true` y mostrar en UI un widget *"5 transacciones requieren tu revision"*. **Francisco decide**, no la maquina.

**Riesgos:**
- Eliminacion accidental de statement con muchas reconciliadas. Mitigacion: soft delete + warning con count ("vas a desvincular 23 transacciones").
- Migracion de ids de statement_tx no idempotente si se corre dos veces antes de persist. Mitigacion: checar `stx.id` antes de asignar.

**Salida Fase C:** v5.25. Ya no se necesita fallback `merchant+date`. Cualquier handler que mueva una tx sabe exactamente que statement_tx tocar.

### Orden y dependencias
A → B → C estricto. B depende de A (transiciones usan `canonicalCard` en algunos efectos). C depende de B (necesita la FSM declarada para definir politicas de orfandad).

Tiempo estimado realista (Alex+Watson+Kai+Valentina ciclo completo):
- Fase A: 1 sesion implementacion + 1 sesion QA.
- Fase B: 2 sesiones implementacion + 2 sesiones QA.
- Fase C: 1 sesion implementacion + 2 sesiones QA (la mas delicada).

---

## Cierre

Lo que esta tabla no dice y deberia decirse explicitamente: **estos tres helpers son la espina dorsal del producto a partir de aqui.** Si Alex los implementa bien, los proximos 6 meses de features (CardCycle de la auditoria H1, asistente de cierre O1, forecast O2, paquete de disputa O3) se construyen *encima* de la FSM en vez de pelearse con ella. Si los implementa mal, vamos a estar parchando Bug-12 / Bug-13 / Bug-14 que son la misma falla con otro disfraz.

La pregunta de la auditoria seguia siendo "que dejamos de construir". Esta es la respuesta operativa: dejamos de construir handlers ad-hoc. A partir de Fase B, cualquier feature pasa por `transitionTx` o no pasa.

Alex tiene luz verde para Fase A en cuanto Kai termine la Sesion #002 baseline. Yo reviso el fix_canonicalcard_v523.py antes de que Valentina corra el gate.

— Sebastián
