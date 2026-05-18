# Brief 3 — "Liberación Operativa"
**Owner:** Sebastián (CPO/Strategist)
**Fecha:** 2026-05-18
**Target cierre:** 2026-06-08 (3 semanas)
**Status:** ARRANCANDO

---

## Contexto: por qué este brief, por qué ahora

Brief 1-bis cerró arquitectura. Brief 2 cerró diseño + confianza en datos. **VoucherPro técnicamente funciona, visualmente está limpio, y los datos son auditables.** La barra ahora se mueve a otro lado.

El feedback implícito de Francisco a lo largo de mayo:
- *"Cierre de mes en 5 min"* (JTBD principal) — todavía no comprobado bajo presión real
- *"Anticipar deuda"* — funciona pero requiere navegar a 3 pantallas distintas
- *"Defensa ante cargos raros"* — el audit dashboard está pero pasivo

**La hipótesis estratégica de Brief 3:** *El siguiente unlock no es features, es **liberar a Francisco de tareas operativas repetitivas** y darle el rol que quiere: revisor estratégico, no operador.*

---

## Los 3 pilares de Liberación Operativa

### Pilar 1 — Conciliación Asistida por IA (Owner: Sebastián + Alex + Watson)

**Problema:** Cuando subes un PDF de estado de cuenta, la app detecta cargos pero la conciliación requiere que TÚ:
- Revises uno por uno cuáles ya están en tu historial
- Marques manualmente "Ignorar — ya está registrado" para los duplicados
- Crees txs nuevos para los que faltan

**Output esperado:**
- **Auto-match de alta confianza**: si merchant+monto+fecha hacen match exacto con un tx existente → reconciliar SIN preguntar
- **Sugerencias para revisión humana**: cuando hay ambigüedad (3 candidatos posibles), mostrarte top-3 con confianza %
- **Auto-create con flag "verificación pendiente"**: cargos sin match auto-create como tx pero con badge amarillo "📋 Verifica este"

**Criterio de éxito:** Subir un PDF Amex de 60 transacciones debe requerir **≤10 taps** del usuario (vs. ~60 actuales).

### Pilar 2 — Cierre de Mes Asistido (Owner: Sebastián + Sofía + Alex)

**Problema:** El "Cierre de mes en 5 min" del JTBD principal nunca se ha medido. Hoy es un proceso ad-hoc.

**Output esperado:**
- **"Cierre de mes" como flujo guiado** (wizard 4 pasos):
  1. *Verificar*: tu Audit Dashboard dice "✅ todo limpio" o lista issues
  2. *Conciliar*: revisar cargos no-reconocidos (con asistente IA del Pilar 1)
  3. *Categorizar*: txs sin categoría asignar en bulk con sugerencias IA
  4. *Confirmar*: reporte ejecutivo del mes (descargable PDF/markdown)
- **Botón "Cerrar Mes [Mes Anterior]"** prominente en Dashboard durante días 1-5 del mes nuevo
- **Métrica visible**: "Cierre mes último: X días después del corte. Promedio: Y días"

**Criterio de éxito:** Cierre de abril (a hacer en mayo) toma <15 min reales con cronómetro. Cierre de mayo (junio) baja a <10 min.

### Pilar 3 — Memoria + Insights (Owner: Sebastián + integración NotebookLM)

**Problema:** La app tiene 6+ meses de transacciones pero **no aprende**. No te avisa de patrones, gastos crecientes, MSIs que terminan, suscripciones zombies.

**Output esperado:**
- **Card "Insights del mes"** en Dashboard con 3 hallazgos algorítmicos:
  - *Categoría que creció >30%* vs. mes anterior
  - *MSI próximos a terminar* (último mes de plazo) — para considerar capacidad nueva
  - *Suscripciones recurrentes inactivas* — recurring que no se ha cargado en 60+ días
- **Integración con NotebookLM AI Brain**: cada cierre mensual genera un session summary que va al Brain. Después puedes consultarlo:
  > *"¿Cómo evolucionó mi gasto en restaurantes en 2026?"*
- **Reporte ejecutivo mensual** (auto-generado, descargable): tabla por categoría, top 10 cargos, MSI activos, comparativa vs. mes anterior

**Criterio de éxito:** Al cerrar 3 meses consecutivos, NotebookLM puede responder *"¿En qué gasto más este trimestre vs. el anterior?"* con datos accionables.

---

## Cronograma propuesto

| Semana | Pilar 1 | Pilar 2 | Pilar 3 |
|---|---|---|---|
| 18-24 may | Diseño algoritmo auto-match (Watson + Sebastián) | Mockups wizard Cierre Mes (Sofía) | Spec card Insights (Sebastián) |
| 25-31 may | Implementación auto-match (Alex) | Implementación wizard fase 1 (Alex) | Implementación Insights (Alex) |
| 1-8 jun | Testing + ajustes (Kai exploratory) | Testing + ajustes | Integración NotebookLM |

**Cierre objetivo:** 2026-06-08 con cierre de mayo realizado bajo nuevo flujo.

---

## Dependencias y riesgos

**Dependencia crítica:** NotebookLM AI Brain reorganizado (memo `project_notebooklm_reorg_pendiente`). Sin esto, Pilar 3 funciona parcialmente.

**Riesgo 1:** Auto-match falsos positivos = daño contable. Mitigación: empezar con threshold muy alto (95%+ confianza), bajar gradualmente. Aprendizaje del incidente v5.74 (matcher demasiado laxo) aplicado.

**Riesgo 2:** Wizard de cierre de mes puede sentirse "infantilizante" para Francisco que es expert user. Mitigación: opt-in en primer uso, accesible vía menú después; no obligar.

**Riesgo 3:** Insights triviales o ruidosos. Mitigación: empezar con 3 insights bien diseñados, agregar más solo si demuestran valor.

---

## Lo que NO está en Brief 3

- Export contable formal (CFDI, contador): candidato Brief 4
- Multi-currency mejoras (USD, EUR): backlog
- iCloud sync entre dispositivos: backlog largo plazo
- Tema claro (light theme): backlog
- App nativa iOS (más allá de PWA): no en roadmap

---

## Próximos pasos inmediatos

1. **Sebastián (yo):** este brief publicado hoy 2026-05-18. Refino Pilar 1 algoritmo con Watson esta semana.
2. **Sofía:** mockups del wizard Cierre Mes — entregable 2026-05-24.
3. **Alex:** standby hasta tener specs de Pilar 1 y mockups de Pilar 2.
4. **Kai:** mientras tanto, **bug hunt #004 fresh** sobre v5.85/v5.86 (siguiente sección).

---

*Sebastián — CPO/Strategist · Brief 3 oficial, 2026-05-18*
