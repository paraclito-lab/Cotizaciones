# Auditoría del sistema de IA — tokens, costos y lógica (17/09/2026)

Tercera auditoría del repo, distinta de las dos anteriores en su objeto: `auditoria-2026-09-14.md`
revisó las **reglas de negocio**; `auditoria-laminado.md` revisó **un cálculo**. Esta revisa el
**sistema de IA que los ejecuta**: qué cuesta operarlo, qué se puede medir de él, y dónde la
automatización falla en silencio.

Todos los números de costo salen de medir el log real de la sesión
(`~/.claude/projects/-home-user-webmunay/e6e7a7ea…jsonl`, 46 MB, 3,953 entradas, del 13/09 al
17/09/2026) con las tarifas oficiales vigentes por millón de tokens. Los casos borde se probaron
ejecutando el generador, no leyendo el código.

**Nota sobre la medición**: las cifras son una foto tomada al iniciar esta auditoría (US$195.04).
La sesión sigue corriendo, así que el número se mueve: producir esta auditoría costó US$5.88 más,
cerrando en US$200.92 — medido con `herramientas/costo_sesion.py`, que quedó en el repo justamente
para que esto se pueda volver a medir sin rehacer el análisis.

**Nota sobre alcance**: el plan original de esta auditoría pedía una muestra de 10-20 cotizaciones
y métricas por tipo de prompt. Eso no existe: hay **una** cotización generada de punta a punta y
**una** sesión de conversación. Las celdas que no se pudieron medir se marcan `sin medir (n=1)` en
vez de rellenarse con un promedio inventado — el mismo criterio que se aplicó a la fórmula de mano
de obra.

---

## 1. Resumen ejecutivo

El sistema **no tiene un problema de costo de operación**: generar una cotización cuesta centavos.
Tiene un problema de **costo de construcción**, y ese ya se pagó: US$195.04 en 4 días, de los cuales
**88.9% no fue generar nada, sino releer y reescribir contexto** (US$104.03 en lectura de caché +
US$69.29 en escritura) contra apenas US$21.70 de salida real. El caché ya evitó US$901.63 (82.2% de
ahorro sobre US$1,096.66 sin caché), así que la palanca restante no es el caché sino **el tamaño y
la continuidad de las sesiones**: 32 turnos de arranque en frío concentran US$55.71 (28.6% del
total) porque cada reanudación tras una pausa larga reescribe ~400K tokens de historia a precio
doble. Un turno al final de la sesión costó **10.2x** lo que costaba al inicio.

Riesgo crítico, y es de cumplimiento, no de costo: **hay nombres de contacto de clientes reales
commiteados y pusheados a GitHub**, en contra de una regla que el propio sistema tiene escrita
(`.claude/skills/cotizar/SKILL.md`, líneas 18-21). Además, la validación automática prometida en
`criterios-actuales.md` punto 9 paso 2 **está implementada a medias**: se probaron cuatro casos
borde y los cuatro pasaron o fallaron mal, incluyendo una cotización de **S/0.00 que se genera sin
una sola alerta** y otra con **subtotal e IGV negativos** cuya alerta reporta el problema
equivocado.

Prioridad: primero el cumplimiento (horas), después las validaciones que dejan salir documentos
inválidos (un día), y solo al final la optimización de costo — que en operación normal significa
ahorrar dólares al mes, no cientos.

---

## 2. Mapa de prompts

El sistema no es un pipeline de prompts discretos: es una skill (`cotizar`, 145 líneas) que se
dispara en conversación libre y orquesta scripts de Python. Los "tipos de prompt" son en realidad
**fases de la skill**, y solo una ruta completa se ha ejecutado de verdad.

| Fase | Propósito | Inputs | Outputs | Tokens medidos |
|---|---|---|---|---|
| Identificación de tipo | Elegir tipo+título+redacción a la vez (regla de coherencia) | Descripción libre del trabajo | `tipo` + `subtipo` de `servicios.json` | sin medir (n=1) |
| Confirmación | Devolver lo entendido y esperar OK antes de gastar | Datos extraídos | Resumen en lenguaje natural | sin medir (n=1) |
| Numeración | Asignar `COT-AAAA-NNN` sin duplicar correlativo | Último N° usado (del registro) | N° nuevo | sin medir (n=1) |
| Cálculo de material | Rollos necesarios por bin-packing | Medidas de piezas | Rollos, largo, mapa de cortes | ~12 turnos (COT-2026-001) |
| Cálculo de precio | Costo → precio unitario por zona | Costos reales + margen | Tabla de precios | ~8 turnos (COT-2026-001) |
| Generación | PNG + PDF + fila de registro | JSON de cotización | PDF/PNG + alertas | 3 turnos |
| Registro | Fila para el Google Sheet | Cotización aprobada | Línea de texto | 1 turno |

**Variables dinámicas** que el sistema maneja hoy: `numero`, `tipo`, `subtipo`, `cliente`, `local`,
`atencion`, `fecha`, `resumen`, `items[]` (`cant`, `descripcion`, `precio_unit`, `fotos[]`,
`separador`/`texto`), `nota`. El IGV (0.18) y el `precio_recibido: "subtotal"` viven en
`servicios.json`, no en el prompt — correcto.

**Variables que el plan de auditoría asumía y no existen**: descuentos por volumen (no hay campo ni
regla; el criterio de bajar margen por cantidad está escrito en prosa pero no implementado), RUC del
cliente (la plantilla no tiene el campo — solo lleva el RUC propio en el encabezado), y condiciones
comerciales (validez de la oferta, plazo de entrega, forma de pago: **ninguna aparece en el PDF**).

**Consistencia del formato de salida**: buena y por construcción. El título sale de `tipo` y el
generador se niega a correr si el JSON trae `titulo` a mano; un `generales` sin `subtipo` tampoco
corre. Eso cierra dos clases de error de raíz y es lo mejor diseñado del sistema.

---

## 3. Casos borde — probados, no deducidos

Se ejecutó el generador con cuatro entradas defectuosas. **Los cuatro resultados son defectos.**

| Caso | Qué debería pasar | Qué pasa de verdad | Gravedad |
|---|---|---|---|
| `cant: 0` | Bloquear: una cotización de S/0 no se envía | **Genera el PDF con Sub Total S/0.00 y cero alertas** | Alta |
| `subtipo` con typo (`laminado_de_seguridad_MAL`) | Rechazar: no está en `subtipos_sugeridos` | **Se acepta en silencio** | Alta |
| Ítem sin `precio_unit` | Decir qué ítem le falta el precio | **`KeyError: 'precio_unit'`**, traceback crudo | Media |
| `precio_unit: -800` | Bloquear: subtotal e IGV negativos | **Genera con Sub Total S/-800.00 e IGV S/-144.00**, y la alerta dice *"ítem 1 tiene precio 0"* — reporta el problema equivocado | Alta |

El del subtipo es el más grave de los cuatro por una razón que no es obvia: el umbral de promoción
(3 cotizaciones del mismo subtipo) **depende de poder contarlos**. `tipo_de()` verifica que el
subtipo *exista*, nunca que sea *válido*. Un typo crea una categoría fantasma de una sola
cotización, que es exactamente el error que la regla de promoción se escribió para prevenir. La
regla se cumple en el papel y se rompe en el código.

**Validación automática prometida vs. implementada** (`criterios-actuales.md` punto 9, paso 2):

| Check prometido | Estado real |
|---|---|
| Ningún ítem en S/0 | Implementado, pero con el mensaje equivocado para precios negativos |
| IGV correcto | No es un check: el código lo calcula, así que no puede discrepar. Si `servicios.json` tuviera mal el 0.18, nada lo detecta |
| Margen dentro de rango | **No implementado, y no es implementable hoy**: `generar.py` nunca recibe el costo, solo el precio. No tiene con qué comparar |
| Checklist de preguntas resuelto | **No implementado** |

De cuatro validaciones que el flujo de aprobación da por hechas antes de mostrar una cotización, una
funciona, una es decorativa y dos no existen.

---

## 4. Seguridad y cumplimiento

**Hallazgo 1 — Datos de cliente en el repositorio (crítico).**
`.claude/skills/cotizar/SKILL.md` líneas 18-21 dicen, textualmente, que los nombres de contacto del
cliente van en la cotización pero **no en los archivos del repo**. Están en los archivos del repo:

- `herramientas/ejemplo-trabajo-cotizacion.json` línea 7 — nombre de contacto real, junto con razón
  social y local del cliente. Commiteado y **pusheado a GitHub** en 3 commits (`cbee6ac`, `abf2eaf`,
  `50b842b`).
- `ejemplos-reales/2026-08-moyobamba.md` línea 9 — otro nombre de contacto real.
- `.claude/skills/cotizar/SKILL.md` líneas 58 y 89 — el ejemplo de la propia skill muestra un nombre
  en el JSON, modelando la conducta que la skill prohíbe cuatro párrafos antes.

Que el repo sea privado lo mitiga, no lo resuelve: la regla no dice "no lo publiques", dice que no
vaya en los archivos. Y el historial de git conserva el dato aunque se borre del archivo hoy.

**Hallazgo 2 — Sin retención de lo entregado.** Los PDF y PNG se generan en `/tmp`, que muere con el
contenedor. Hoy **no existe copia de la única cotización emitida**: ni en el repo, ni en el Sheet
(que guarda montos, no el documento). Si el cliente reclama por lo cotizado, no hay documento que
mostrar. El único PDF archivado en el repo es una cotización de referencia de agosto.

**Hallazgo 3 — La trazabilidad completa está en un contenedor efímero.** Los 46 MB de log que hacen
posible esta auditoría viven en `~/.claude/projects/` dentro del contenedor, sin respaldo. Cuando el
contenedor se recicle, se va el registro de cómo se decidió cada precio. Esta auditoría no se podría
repetir.

**Hallazgo 4 — No hay umbral de validación humana por monto.** El flujo exige aprobación humana para
**todas** las cotizaciones, lo cual hoy está bien (volumen bajo, control máximo a propósito). Pero no
hay ningún tratamiento diferenciado por monto: una de S/500 y una de S/50,000 pasan por lo mismo. Al
automatizar el paso 4, el umbral por monto tiene que existir antes, no después.

**Lo que sí está bien**: el precio nunca se inventa (el catálogo es fuente única y la skill prohíbe
inventar), el margen no se aplica automático, y el bot no envía correos — el envío es humano por
decisión explícita. Esas tres cosas son las que evitan el daño grande.

---

## 5. Costos reales medidos

### Composición del gasto (sesión completa, 13-17/09/2026)

| Concepto | Costo | % |
|---|---|---|
| Lectura de caché (0.1x input) | US$104.03 | 53.3% |
| Escritura de caché (TTL 1h, 2x input) | US$69.29 | 35.5% |
| Output generado | US$21.70 | 11.1% |
| Input sin cachear | US$0.01 | 0.0% |
| **Total** | **US$195.04** | |
| Sin caché habría costado | US$1,096.66 | |
| **Ahorro ya logrado por caché** | **US$901.63** | **82.2%** |

**El 88.9% del gasto es mover contexto, no producir respuestas.** El contexto medio releído por
turno fue de **343,926 tokens**, sobre 1,233 turnos.

### Por modelo y por día

| Modelo | Turnos | % turnos | Costo | % costo |
|---|---|---|---|---|
| `claude-sonnet-5` | 970 | 79% | US$107.61 | 55% |
| `claude-opus-5` | 262 | 21% | US$87.42 | 45% |

Opus costó 2.5x por token: 21% de los turnos se llevaron 45% del gasto. Todo en Sonnet habría
costado US$142.58 (US$52.45 menos), pero parte del trabajo de criterio —el costeo, esta auditoría—
es donde Opus se justifica.

| Día | Turnos | Costo | US$/turno |
|---|---|---|---|
| 13/09 | 866 | US$84.78 | 0.098 |
| 14/09 | 57 | US$15.60 | 0.274 |
| 16/09 | 191 | US$69.44 | 0.364 |
| 17/09 | 119 | US$25.21 | 0.212 |

El costo por turno **subió 3.7x** entre el primer día y el tercero sin que el trabajo cambiara de
naturaleza: es la historia acumulada cobrándose en cada turno.

### El hallazgo que cambia la recomendación

| Contexto releído en el turno | Turnos | US$/turno | Total |
|---|---|---|---|
| 0-50K | 32 | **1.7409** | US$55.71 |
| 50-150K | 157 | 0.0845 | US$13.26 |
| 150-300K | 323 | 0.1042 | US$33.65 |
| 300-450K | 326 | 0.1228 | US$40.03 |
| 450K+ | 394 | 0.1330 | US$52.39 |

La primera fila parece un error y no lo es: son los **arranques en frío**. Un turno que lee poco
caché es un turno que tuvo que *escribir* todo el contexto a precio doble. **32 turnos concentran
28.6% del gasto total.** Cada pausa larga (una noche, los dos días entre el 14 y el 16) expira el
caché, y la siguiente pregunta —por trivial que sea— paga la reescritura de ~400K tokens de historia
que en su mayoría no tiene nada que ver con lo que se está preguntando.

Medido de punta a punta: **un turno al final de la sesión costó 10.2x lo que costaba al inicio**
(US$0.4113 vs US$0.0404).

### Outliers

68 turnos superan 2 desviaciones estándar en output (umbral 3,871 tokens; máximo 7,488). Suman
352,821 tokens y **US$27.33 — 14.0% del costo**. No son anomalías a corregir: son los turnos que
escribieron archivos grandes (`laminado.py`, `dibujar_rollos.py`, los documentos). Output caro pero
productivo. Los turnos verdaderamente caros no son estos, son los 32 arranques en frío.

Dato para descartar una optimización: el *thinking* fue 565,181 de 1,406,966 tokens de output (40%),
pero a precio de output son ~US$8.15, **4.2% del total**. Recortar razonamiento para ahorrar plata en
este sistema es cambiar calidad por nada.

### Proyección mensual — separando construir de operar

Mezclar estos dos números es el error que haría inútil la proyección:

- **Construir** (lo ya medido): US$195.04 por 4 días de desarrollo. Es un costo hundido, no recurrente.
- **Operar** una cotización en sesión limpia: ~12-15 turnos con contexto de 40-80K en Sonnet ≈
  **US$0.50-0.80 por cotización**.
- **Operar** la misma cotización dentro de una sesión de 400K arrastrada: los mismos turnos cuestan
  **3-4x más**, solo por el contexto que arrastra.

| Escenario mensual | Supuesto | Costo |
|---|---|---|
| 20 cotizaciones, sesión limpia cada una | 20 × US$0.65 | ~US$13/mes |
| 20 cotizaciones, sesiones arrastradas | 20 × US$2.20 | ~US$44/mes |
| + desarrollo continuo (2 días/mes al ritmo medido) | | +US$50-90/mes |

**La operación del sistema es barata; el desarrollo es lo que cuesta.** Esto reordena todas las
prioridades: no vale la pena optimizar el prompt de cotización para ahorrar centavos. Vale la pena no
desarrollar dentro de sesiones de 4 días.

---

## 6. Recomendaciones priorizadas

### Impacto alto

| # | Acción | Ahorro / efecto |
|---|---|---|
| 1 | Sacar los nombres de contacto de los 3 archivos del repo y usar un placeholder en los ejemplos. Decidir aparte qué hacer con el historial de git | Cierra el incumplimiento crítico. Sin costo |
| 2 | Validar `cant >= 1`, `precio_unit > 0` (con mensaje correcto para negativos) y `subtotal > 0` en `generar.py`; corregir el mensaje que dice "precio 0" cuando es negativo | Impide emitir cotizaciones de S/0 y de subtotal negativo |
| 3 | Validar que `subtipo` pertenezca a `subtipos_sugeridos`; si no, rechazar y sugerir `otros` | Protege el conteo del que depende el umbral de promoción |
| 4 | Una sesión nueva por tarea: cotizar en sesión limpia, desarrollar en otra. No reanudar una sesión de 400K para una pregunta chica | ~US$55 de los US$195 medidos fueron arranques en frío de contexto irrelevante. En operación, 3-4x por cotización |
| 5 | Archivar cada PDF emitido en el repo (`cotizaciones-emitidas/COT-AAAA-NNN.pdf`) y no en `/tmp` | Hoy no existe copia de lo cotizado. Sin costo |

### Impacto medio

| # | Acción | Ahorro / efecto |
|---|---|---|
| 6 | Reservar Opus para criterio (costeo, auditoría, diseño) y usar Sonnet para lo mecánico (correr el generador, leer archivos, commitear) | US$52 de diferencia medida en esta sesión (27%) |
| 7 | Reemplazar el `KeyError` por un mensaje que nombre el ítem sin precio | Convierte un crash en una pregunta contestable |
| 8 | Respaldar el JSONL de sesión al repo (o a otro lado) antes de cerrar trabajo | Sin respaldo, la trazabilidad muere con el contenedor |
| 9 | Definir el umbral de monto que exigirá doble revisión **antes** de automatizar el paso 4 | Evita que el primer error automatizado sea el caro |
| 10 | Agregar validez de la oferta, plazo y forma de pago al PDF | Hoy se emite un compromiso de precio sin fecha de vencimiento |

### Impacto bajo

| # | Acción | Por qué es bajo |
|---|---|---|
| 11 | Agrupar llamadas de herramienta independientes en un solo mensaje | 639 llamadas en la sesión; ahorra turnos, pero el turno cuesta US$0.16 |
| 12 | No tocar el *thinking* ni el `effort` para ahorrar | Son 4.2% del costo. Recortarlo cambia calidad por nada |
| 13 | El TTL de caché (1h, a 2x) no es una palanca disponible | Lo fija el entorno, no el usuario. La palanca equivalente es no dejar sesiones gigantes en pausa |

---

## 7. Dashboard de KPI

Campos reales verificados en el JSONL de esta sesión. `u` = `message.usage` de las entradas con
`type: "assistant"`.

| KPI | Fórmula | Campo del JSONL | Viable |
|---|---|---|---|
| Cotizaciones/día | Contar cotizaciones emitidas por fecha | **No está en el JSONL** — sale del Google Sheet (columna N° + fecha) | Sí, pero fuera del log |
| Tokens por cotización | `Σ(u.input + u.cache_creation + u.cache_read + u.output)` entre el primer y último turno de la cotización | `u.input_tokens`, `u.cache_creation_input_tokens`, `u.cache_read_input_tokens`, `u.output_tokens` | Sí, si cada cotización corre en sesión propia (hoy no se puede separar) |
| Costo por cotización | `in×T_in + out×T_out + cw1h×T_in×2 + cw5m×T_in×1.25 + cr×T_in×0.1`, con `T` por `message.model` | + `u.cache_creation.ephemeral_1h_input_tokens` / `ephemeral_5m_input_tokens`, `message.model` | Sí |
| Tasa de error | Correcciones pedidas ÷ cotizaciones emitidas | **NO calculable desde el JSONL** | **No.** Un precio equivocado no deja rastro en el log. Sale del Sheet: una columna de "vueltas de corrección" que hoy no existe |
| Tiempo de respuesta | `assistant.timestamp − timestamp del user/tool_result anterior` | `timestamp` (ISO 8601) | Aproximado: no hay campo de duración, se deriva de timestamps consecutivos |
| Ahorro por caché | `1 − costo_real ÷ Σ((in+cw+cr)×T_in + out×T_out)` | los mismos campos de usage | Sí. Medido: 82.2% |
| Varianza de tokens | Desv. estándar de `u.output_tokens` por turno; outliers > media+2sd | `u.output_tokens` | Sí. Medido: media 1,141, sd 1,365, 68 outliers |
| **Contexto medio por turno** (añadido) | `media(u.cache_read_input_tokens)` | `u.cache_read_input_tokens` | Sí. **Es el KPI que más predice el costo** (343,926 medido) |
| **Costo de arranque en frío** (añadido) | `Σ costo` de turnos con `cache_read < 50K` | `u.cache_read_input_tokens`, `u.cache_creation_input_tokens` | Sí. 28.6% del gasto |

Campos útiles adicionales ya presentes: `effort` / `perTurnEffort` (medium en 1,133 turnos, high en
99), `u.output_tokens_details.thinking_tokens`, `u.service_tier`, `requestId`, `sessionId`,
`gitBranch`, y el nombre de cada herramienta en `message.content[].name` donde
`type == "tool_use"`.

**Los dos KPI de calidad (cotizaciones/día y tasa de error) no salen del log.** Cualquier tablero que
los muestre desde el JSONL estaría inventando. Su fuente es el registro de costos, y la columna de
correcciones hay que agregarla.

El script que produjo todos los números de esta auditoría se puede dejar como
`herramientas/costo_sesion.py` para no rehacerlo cada mes.

---

## 8. Plan 30-60-90

Sin responsables asignados: la regla de redacción del repo no atribuye acciones a personas ni a
roles. Las acciones se enuncian como hechos a ejecutar.

### Primeros 30 días — cumplimiento y validaciones

Objetivos medibles:
1. **Cero datos de contacto de cliente en archivos del repo** (hoy: 3 archivos).
2. **Cero cotizaciones emitidas con subtotal ≤ 0 o subtipo inválido** (hoy: ambas posibles y sin alerta).
3. **100% de cotizaciones emitidas con PDF archivado** (hoy: 0%).

Acciones: (a) limpiar los 3 archivos y usar placeholders en los ejemplos de la skill; (b) agregar
las cuatro validaciones del punto 6 a `generar.py`; (c) validar `subtipo` contra
`subtipos_sugeridos`; (d) crear `cotizaciones-emitidas/` y generar ahí, no en `/tmp`; (e) agregar al
Sheet la columna de vueltas de corrección, que es la única fuente posible del KPI de calidad.

Revisión: al cerrar el mes de prueba ya previsto, junto con la calibración de la fórmula de mano de
obra. No se necesita un ciclo aparte.

### Días 30-60 — medición

Objetivos:
1. **Costo por cotización medido, no estimado**, con al menos 5 cotizaciones en sesiones separadas.
2. **Reducir el contexto medio por turno por debajo de 150K** (hoy 343,926) trabajando en sesiones
   por tarea.
3. **Umbral de monto para doble revisión, decidido y escrito** antes de automatizar cualquier paso.

Acciones: (a) dejar `costo_sesion.py` en el repo y correrlo al cierre de cada semana; (b) una sesión
por cotización, sin excepción, para que el costo sea atribuible; (c) respaldar el JSONL antes de que
el contenedor se recicle; (d) agregar validez de oferta, plazo y forma de pago al PDF.

### Días 60-90 — eficiencia, solo si los datos la justifican

Objetivos:
1. **Reducir 30% el costo por cotización** respecto a la medición de los días 30-60.
2. **3 o más cotizaciones del mismo subtipo** para evaluar la primera promoción a tipo propio con
   evidencia real.

Acciones: (a) Sonnet para lo mecánico, Opus para criterio, midiendo si la calidad aguanta; (b)
agrupar llamadas de herramienta; (c) evaluar la promoción de `laminado-seguridad` si llegó al
umbral; (d) recién acá, considerar automatizar el paso de aprobación, con el umbral de monto ya
definido.

**Lo que este plan deliberadamente no propone**: optimizar prompts para ahorrar tokens. A US$0.65 por
cotización, el trabajo de optimizar cuesta más que todo lo que ahorraría en un año.
