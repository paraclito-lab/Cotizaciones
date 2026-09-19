# Auditoría de arquitectura: qué patrones ya probados aplican, y qué falta (19/09/2026)

Encargo: buscar qué algoritmos, sistemas ya construidos y patrones de flujo existen para este
tipo de problema (cotización + pricing + aprobación), y recomendar cómo optimizar lo que ya se
tiene. Investigación real (fuentes al final), cruzada contra el código y los documentos de este
repo — no una lista genérica de buenas prácticas.

## Resumen ejecutivo

El repo ya reimplementó, sin nombrarlos, **tres patrones estándar de la industria de software de
ventas (CPQ) e ingeniería de costos**: reglas como datos (no como código), costeo por actividad
(ABC), y aprobación humana con vista previa antes de comprometerse. Eso es buena señal — no hubo
que rediseñar nada desde cero. La brecha real no es de arquitectura, es de **consistencia**: la
mitad de las reglas de precio viven en un documento de prosa (`criterios-actuales.md`) que un
humano o un asistente tiene que leer y aplicar de memoria cada vez, mientras la otra mitad
(`servicios.json`) ya vive como datos que el código valida solo. La sesión del 17–19/09 lo probó
en carne propia: la fórmula de mano de obra se recalculó a mano en Bash tres veces distintas, con
tres decisiones de margen distintas, porque no hay un solo lugar que la calcule.

## 1. Lo que ya coincide con un patrón probado (no tocar la idea, sí consolidarla)

| Patrón de la industria | Dónde ya existe en este repo | Fuente |
|---|---|---|
| **Reglas como datos, no como código** (business rules engine): la lógica vive en una tabla/JSON que el código lee, no en `if/else` repetidos | `servicios.json` — título, redacción y palabras clave por tipo de servicio, con `generar.py` negándose a correr si alguien intenta escribir un título a mano | Ver "Decision Engine vs Rules Engine" — GoRules, Nected |
| **Costeo por actividad (Activity-Based Costing)**: separar el costo en los generadores reales (material, mano de obra, fijos) y repartir los fijos por un criterio de uso (m², piezas), no por partes iguales | `herramientas/precio.py` — exactamente esto: material real + mano de obra + fijos distribuidos por peso de costo directo | MRPeasy, "Standard vs Activity-Based Costing" |
| **Cutting stock / bin packing**: búsqueda multi-estrategia para minimizar desperdicio de material en rollo | `herramientas/laminado.py` — 18 combinaciones de orientación/orden/ajuste, con verificación geométrica propia | Problema de investigación de operaciones clásico, ya bien resuelto acá |
| **Human-in-the-loop con evidencia antes de comprometerse**: el sistema arma una propuesta, la muestra, y solo avanza con aprobación explícita | El flujo completo (`flujo-completo.md`) + esta sesión misma: vista previa PNG antes de cualquier PDF | StackAI, "Human-in-the-Loop AI Agents" |
| **Reglas endurecidas que la IA no puede saltarse** (tendencia CPQ 2026: la IA propone, el código bloquea) | Las validaciones duras de `generar.py`: sin ítems en S/0, sin cantidad 0, sin subtotal negativo — no son sugerencias, cortan la generación | Everstage, "CPQ Architecture 2026" |

**Conclusión de esta sección**: la arquitectura de fondo es correcta. El problema no es "qué
patrón usar", es que solo la mitad del sistema sigue el patrón que ya se demostró que funciona.

## 2. La brecha real: reglas de precio en prosa, no en datos

`criterios-actuales.md` tiene la fórmula de mano de obra (personas × tarifa × 2 por amanecida),
el rango de margen (60–80%), y el piso mínimo — todo en texto. Un rules engine de verdad
(GoRules, Nected, o simplemente un JSON propio) las tendría como **datos versionados y
validables**, igual que `servicios.json` ya hace con el título.

**Costo de no tenerlo así, medido esta semana**: en la cotización de Santa Anita, la mano de obra
se calculó 2 veces con supuestos distintos (S/600 con tarifa S/100, luego S/700 dado
directamente), y el margen se propuso en 70% sin que hubiera un criterio objetivo detrás — solo
"punto medio del rango". Eso no es un error puntual, es la consecuencia directa de que la regla
vive en prosa: cada vez que hace falta, se re-interpreta.

### Recomendación 1 (impacto alto): mover las reglas de precio a `criterios.json`

Estructura sugerida, análoga a `servicios.json`:

```json
{
  "mano_obra": {
    "lima": {"personas_default": {"carretillas": 2, "balanzas": 3}, "tarifas": [100, 200]},
    "provincia": {"criterio": "personal local cotiza aparte, o pasajes+viáticos desde Lima"}
  },
  "margen": {"rango": [0.60, 0.80], "referencia_default": 0.70},
  "piso_minimo": {"carretillas": 250}
}
```

No reemplaza el juicio comercial (`criterios-actuales.md` ya es clarísimo: el margen nunca se
aplica automático) — pero si la tarifa y el rango están en datos, el cálculo deja de rehacerse
distinto cada vez, y un futuro `costeo.py` puede leerlo igual que `generar.py` lee `servicios.json`.

### Recomendación 2 (impacto alto): un `costeo.py` genérico, no cálculos sueltos en Bash

Esta sesión calculó costo→margen→precio con `python3 -c "..."` al vuelo, tres veces, para
Santa Anita. `herramientas/precio.py` ya resuelve esto para laminado — pero está atado a la
lógica de rollos. Hace falta la misma idea, general: dado un costo y un margen, devolver el
precio redondeado, sin reescribir la fórmula cada vez. Diez líneas, pero evita que cada
cotización nueva sea "cocinar el cálculo de nuevo".

### Recomendación 3 (impacto medio): decision table para el margen sugerido

En vez de proponer siempre 70% (punto medio), una tabla chica: tipo de cliente (cadena grande /
independiente) × monto estimado → margen sugerido. Con solo 5 cotizaciones reales ya se vio un
patrón (Ica Panamericana, precio más bajo, ganó; HB rechazó dos veces un precio alto) — no hace
falta un modelo predictivo, una tabla de 3-4 filas ya sería mejor que "punto medio del rango".

### Recomendación 4 (impacto medio): cerrar el "evidence pack" de cada cotización

El patrón HITL bien hecho archiva junto: la propuesta, el razonamiento, quién aprobó, cuándo.
Hoy `cotizaciones-emitidas/` guarda la imagen final, pero no el JSON de costeo que la generó ni
el desglose (material/mano de obra/margen). Sin eso, reconstruir "cuánto costó" (como se hizo
con Ica Panamericana) depende de inferir por fecha — ya pasó, ya se resolvió una vez, va a volver
a pasar. Guardar el JSON de costeo junto a la imagen archivada cierra esto de raíz.

### Recomendación 5 (impacto bajo, no urgente): vínculo factura↔cotización

Ya señalado en `balanzas-industriales/casuistica-balanzas.md` — se resuelve solo si la
Recomendación 4 se implementa (el JSON archivado ya tendría el N° de cotización explícito).

## 3. Lo que NO hace falta

- **No hace falta un motor de reglas de terceros** (Drools, GoRules, etc.) — la escala de este
  negocio (una persona, decenas de cotizaciones al mes) no lo justifica. Un JSON propio + un
  script que lo lee, como ya se hace, es suficiente y más barato de mantener.
- **No hace falta IA para sugerir precios de forma predictiva todavía** — con 5 cotizaciones de
  balanza no hay data para entrenar nada; una decision table simple (Recomendación 3) da el
  mismo valor sin el riesgo de una caja negra.
- **No hace falta cambiar el bin-packing de `laminado.py`** — ya es la solución correcta al
  problema real (cutting stock), no una improvisación a mejorar.

## Plan sugerido, en orden

1. `criterios.json` con mano de obra + margen + piso mínimo (Recomendación 1) — desbloquea todo
   lo demás.
2. `herramientas/costeo.py` genérico que lo lea (Recomendación 2).
3. Archivar el JSON de costeo junto a la imagen en `cotizaciones-emitidas/` (Recomendación 4).
4. Decision table de margen sugerido, cuando haya 8–10 cotizaciones más para basarla en algo real
   (Recomendación 3) — esta es la única que conviene esperar, por la misma razón que el mes de
   calibración de mano de obra: no inventar el criterio, esperar la evidencia.

## Fuentes

- [CPQ Architecture: Structure, Models & Best Practices for 2026 — Everstage](https://www.everstage.com/cpq/cpq-architecture)
- [Decision Engine: What It Is and When You Need One — GoRules](https://gorules.io/solutions/decision-engine)
- [Decision Engine vs Rules Engine — Nected](https://www.nected.ai/us/blog-us/decision-engine-vs-rules-engine)
- [Hardcoded Business Rules vs Business Rules Engine — Higson](https://www.higson.io/blog/the-hidden-costs-of-hardcoded-business-rules--and-why-a-business-rules-engine-is-the-smarter-choice)
- [Activity Based Costing: What is ABC and Who is it for? — MRPeasy](https://www.mrpeasy.com/blog/activity-based-costing/)
- [Standard Costing vs Activity-Based Costing — Vintti](https://www.vintti.com/blog/standard-costing-vs-activity-based-costing)
- [Human-in-the-Loop AI Agents: How to Design Approval Workflows — StackAI](https://www.stackai.com/insights/human-in-the-loop-ai-agents-how-to-design-approval-workflows-for-safe-and-scalable-automation)
- [Human-in-the-Loop Approval Framework — Agentic Patterns](https://www.agentic-patterns.com/patterns/human-in-loop-approval-framework/)
