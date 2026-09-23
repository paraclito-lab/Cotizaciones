# Hallazgos abiertos — registro único

Última revisión: 23/09/2026.

**Qué es**: la lista de trabajo única de lo que está mal, falta o se contradice en el sistema.
Consolida los pendientes que seguían abiertos en las auditorías anteriores
(`auditoria-2026-09-14.md`, `auditoria-laminado.md`, `auditoria-ia-2026-09-17.md`,
`auditoria-arquitectura-2026-09-19.md` y `flujo-sistema-completo.md` §7). Esos documentos
quedan como historia; **los pendientes se siguen desde acá**. Cada hallazgo se verificó contra el
código o los archivos el 23/09/2026 (columna Evidencia). Un hallazgo se cierra marcándolo ✅ con
fecha y commit, no borrándolo.

**Por qué un registro y no una quinta auditoría**: en 9 días se produjeron 5 documentos de
diagnóstico. De las 4 recomendaciones de la auditoría de arquitectura se implementaron 0, y al
menos 12 hallazgos anteriores siguen abiertos (sección 7). El cuello de botella ya no es
detectar problemas: es cerrarlos. Una auditoría narrativa más habría sido un sexto documento con
recomendaciones repetidas, que es justamente el hallazgo D2 de `flujo-sistema-completo.md`.

## Estado (23/09/2026, noche)

| Estado | Hallazgos |
|---|---|
| ✅ Cerrado en `main` | **N01** (commit aee7eaa). **N02**: las fuentes de 9196 y 9197 quedaron en `cotizaciones-emitidas/` (4dbc40b); sus imágenes se generan con `--final` cuando se prueben los cambios de la rama. **R1**: este registro. |
| 🔧 Resuelto en la rama `mejora/biblioteca-trabajos`, **sin probar todavía** | N03 (corregido en el JSON archivado; falta regenerar el PDF) · N04 · N05 · N06 · N07 · N11 (los nombres; la regla sigue en Q3) · N12 · N14 (la alerta; el formato sigue en Q4) · N16 · N24 · N27 · N29 · N31 · N32 · N33 · R4 |
| 🟡 Parcial | N13 (el piso y la etiqueta de archivo ya se leen; `personal`, `patron_filas`, `sustento_base` y `acepta_fotos` no; la redacción por trabajo ahora vive en las fichas de `trabajos/`) · N17 (el costo fijo por visita está modelado en las fichas; falta como regla general en criterios) · N21 (el bloque de condiciones existe; el texto estándar depende de Q7) · N22 (checklist obligatorio en los trabajos que tienen ficha; los que se cotizan a mano siguen sin él) · N25 (anotado en la nota interna de 9196, y la ficha de carretillas lo avisa; sigue sin cotizarse) · N28 ("estoca" ya reconoce el trabajo; la descripción impresa no se cambió) |
| ⏳ Esperan una decisión (sección 8) o un dato externo | N08 (Q1) · N09, N10, N34 (Q2) · N15, R2 (Q5) · N18 · N19 · N20 (Q7 y el contador) · N23, R3 (Q4) · N26 · N30 |

**Por qué la rama no está probada**: en esta sesión el control de permisos bloqueó toda
ejecución de Python después de un intento de actualizar la dirección del repositorio remoto
(GitHub avisó que el repositorio cambió de nombre). Todo lo de la rama se revisó a mano y los
JSON se validaron con `jq`, pero nada pasa a `main` sin correr
`python3 herramientas/probar.py --render`. Hasta entonces, `main` sigue con el generador que ya
emitió 9196 y 9197.

## Objetivos contra los que se audita

| | Objetivo |
|---|---|
| O1 | Cotizar rápido, correcto y con presentación profesional |
| O2 | Ningún precio ni número inventado; cada precio con origen trazable |
| O3 | Nada confidencial llega al cliente |
| O4 | Deducir la fórmula de precio con datos reales (mes de prueba 15/09 → ~15/10) y hacer medible el ajuste final por experiencia |
| O5 | Medir % de cotizaciones ganadas, margen real y techo de precio por tipo de cliente |
| O6 | Depender menos de Claude: que lo mecánico corra solo |
| O7 | Agregar servicios, costeos y redacción sin romper lo que ya funciona |

Lentes: `sistemas` · `automatización` · `ing. industrial` · `comunicación` (al cliente) ·
`contable` · `costeo` · `comercial`.

## 1. Urgente — hoy

| ID | Hallazgo | Evidencia | Acción |
|---|---|---|---|
| N01 | **El trabajo de esta semana no está guardado.** 5 archivos modificados sin commit: la corrección del marco, la regla de confidencialidad de `nota`, el modo `--sin-precios` y la casuística de garruchas. Si el contenedor se recicla, se pierden. `sistemas · O1` | `git status`: SKILL.md, casuistica.md, plantilla/README.md, cotizacion.html, generar.py | Commit + push. |
| N02 | **Los datos fuente de las cotizaciones emitidas viven en `/tmp`.** 9196-2026 y 9197-2026 existen solo como JSON temporal, y en el repo no queda ni su imagen. Si el cliente pide cambiar un ítem en dos semanas, hay que rehacerla de memoria. `sistemas · O1 O2` | `/tmp/pucallpa.json`, `/tmp/hb-panamericana.json`. `cotizaciones-emitidas/` tiene solo `COT-2026-001.jpg` | Guardar el JSON junto a la imagen en `cotizaciones-emitidas/`. Aplica la misma excepción de privacidad que ya cubre la imagen. |
| N03 | **Error ortográfico en un PDF final emitido**: 9197-2026 dice "tímón" (lo correcto es "timón"). `comunicación · O1` | `/tmp/hb-panamericana.json`, ítem 2 | Corregir y regenerar. Si ya se envió, corregirlo en la próxima versión. |

## 2. Esta semana — antes de que se pierda el mes de prueba

El mes de prueba cierra alrededor del 15/10. Estos cuatro hallazgos afectan justo los datos con
los que se va a deducir la fórmula: si no se corrigen ahora, el mes se cierra con datos que no
sirven.

| ID | Hallazgo | Evidencia | Acción |
|---|---|---|---|
| N04 | **"Cant. unidades" suma repuestos, no equipos.** Pucallpa quedó registrada con 33 unidades (10 traspaletas + 5 botellas + 16 ruedas + 2 direccionales) y HB con 29. Esa columna alimenta "precio por unidad" y "unidades por amanecida", que son **justo el bloque de calibración del mes de prueba**. El error va de 3.3x a 4.1x. `sistemas · costeo · O4` | `generar.py:357` suma el `cant` de todos los ítems. Pucallpa: S/6,400 ÷ 33 = S/193.94 por unidad (real: ÷ 10 = S/640.00). HB: S/2,318 ÷ 29 = S/79.93 (real: ÷ 7 = S/331.14) | Contar solo la fila de mantenimiento, o agregar un campo `unidades` explícito al JSON. Corregir a mano las filas que ya se pegaron. |
| N05 | **El ajuste final por experiencia no se puede medir.** El registro guarda solo el subtotal final, no el costo estimado ni el precio calculado antes del ajuste. Sin ese par (calculado, final) el criterio queda invisible y no se puede deducir. `costeo · O4` | `armar_registro.py:31-57`: la etapa 1 no tiene columna de costo ni de precio calculado | Agregar dos columnas a la etapa 1: `Costo estimado` y `Subtotal calculado`. "Ajuste %" sale por fórmula. |
| N06 | **Sesgo de supervivencia en los costos.** El costo real se llena al terminar el trabajo, y solo si se ganó. Las cotizaciones perdidas, que son las que más dicen sobre el precio, nunca tienen costo. Al cierre del mes, la fórmula saldría solo de los trabajos donde el precio ya funcionó. `contable · costeo · O4 O5` | `criterios-actuales.md` §6, momento 3: "solo si se ganó" | Resolver N05: así toda cotización tiene costo estimado desde el primer día, se gane o se pierda. |
| N07 | **El único campo de texto libre es el que ve el cliente.** Cualquier justificación interna (una excepción de precio, una duda sobre la identidad del cliente, el origen de un precio) solo se podía escribir en `nota`, que se imprime en el PDF. Es la causa raíz de las filtraciones de esta semana: 3 borradores llevaron referencias internas (a `catalogo.md`, al piso mínimo, a la identidad del cliente), y la regla escrita en la skill no lo impide. Además, al quitar esa nota, la excepción de HB (S/230, bajo el piso de S/250) quedó sin rastro en ninguna parte. `sistemas · comunicación · O3 O2` | `generar.py:150-151`: `nota` va directo al HTML y no existe otro campo | Crear un campo `nota_interna` que nunca se imprima y salga en la fila del registro. Además, un bloqueo por código: si `nota` contiene ".md", "catálogo", "piso", "margen" o "por validar", no se genera. |
| N08 | **No hay evidencia de que el registro se esté llenando.** Es un Google Sheet fuera del repo; `generar.py` imprime la fila, pero nada confirma que se pegue. Si está vacío, el mes de prueba no produce la fórmula, que es su único objetivo. `proceso · O4` | No hay acceso al Sheet desde el repo | Confirmar (Q1). |

## 3. Contradicciones — dos fuentes dicen cosas distintas

| ID | Hallazgo | Evidencia | Acción |
|---|---|---|---|
| N09 | **El precio "Confirmado" del catálogo no es el que se cobra.** La cotización más reciente (9196-2026) salió con rueda de carga a S/60, direccional a S/95 y botella a S/50. El catálogo dice S/40, S/80 y S/38 "Confirmado", y la fila de la botella cita como fuente justamente "TT Pucallpa". Además, tres cotizaciones reales (Moyobamba, Porongoche y Pucallpa) cobran la rueda entre S/60 y S/65: el catálogo es el que está en minoría. Un catálogo que no coincide con lo emitido deja de consultarse. `costeo · O2` | `catalogo.md:22,24,33` vs 9196-2026 | Decidir (Q2). Como mínimo, corregir la fuente de la fila de la botella. |
| N10 | **Si Pucallpa se cobró más por ser provincia, la regla §1 está mal.** `criterios-actuales.md` §1 dice que el precio del repuesto "no cambia según la localidad". Pucallpa es provincia y se cobró más caro. O la regla es falsa o el catálogo está desactualizado; las dos cosas no pueden ser ciertas a la vez. `costeo · O2` | `criterios-actuales.md:8-9` | Q2. |
| N11 | **"Margen" en realidad significa markup, y el nombre engaña.** `criterios` §4 dice "60-80% sobre el costo", y la columna "Margen %" del registro calcula ganancia ÷ costo: las dos cosas son **markup**. En contabilidad, "margen" es ganancia ÷ venta. Un markup de 73% equivale a un margen de 42%, así que cualquier comparación contra referencias del rubro se lee mal. Además, los precios finales reales de garruchas quedaron en markup de 81% y 107%: el rango 60-80% no describe lo que se hace. `contable · costeo · O5` | `armar_registro.py:101`: `V/U` = ganancia ÷ costo | Renombrar la columna a "Markup % (sobre costo)" y agregar "Margen % (sobre venta)". Q3. |
| N12 | **El piso de S/250 no se hace cumplir.** Figura como "DECIDIDO" y está en `servicios.json`, pero ningún código lo lee: 9197-2026 salió a S/230 sin ningún aviso. `sistemas · O2` | `grep precio_minimo_unidad` en el código: 0 resultados | Alerta (no bloqueo) cuando el mantenimiento quede bajo el piso. Q6 decide si hay excepciones. |
| N13 | **6 de los 9 campos por tipo de `servicios.json` son decorativos.** Ningún código lee `precio_minimo_unidad`, `personal`, `palabras_clave`, `patron_filas`, `sustento_base` ni `acepta_fotos`. Parecen configuración, pero son prosa: dan una sensación de control que no existe, y N12 es la consecuencia. `sistemas · O7` | `grep` sobre `generar.py` y `herramientas/*.py`: 0 referencias a cada uno | Hacer cumplir los que son reglas (piso, fotos) y mover el resto a documentación. |
| N14 | **La numeración decidida no es la que se usa.** `criterios` §7, la skill y el generador dicen `COT-AAAA-NNN`, pero lo real es `8211-2026`, `9196-2026` y `9197-2026`. Resultado: **toda cotización real dispara la alerta de formato**, y toda carretilla dispara además la de "título largo". Dos alertas que salen el 100% de las veces acostumbran a ignorarlas, y entre ellas se pierde la que sí importa (un precio pendiente). `sistemas · O1` | `generar.py:320`; salida de 9196 y 9197 | Q4. Después, ajustar la regex y silenciar la alerta del título conocido. |
| N15 | **Telegram figura como "DECIDIDO" en criterios y como "descartado" en la skill.** Abierto desde el 14/09 (B5 de esa auditoría); el README todavía lo describe. `proceso · O7` | `criterios-actuales.md:224,236`; `SKILL.md:14`; `README.md:16` | Q5. |
| N16 | **La skill se contradice sola**: dice "Solo existen tres" tipos y, seis líneas más abajo, "Hoy son cuatro". `O7` | `SKILL.md:42,48` | Corregir. |

## 4. Vacíos — falta algo que el negocio necesita

| ID | Hallazgo | Evidencia | Acción |
|---|---|---|---|
| N17 | **No hay costo fijo por visita.** El costeo real de garruchas lo muestra: mano de obra + transporte + consumibles + SCTR = S/450 fijos, lo mismo para 3 coches que para 15. El sistema solo sabe costear por unidad, así que los trabajos chicos se cotizan a ojo. `costeo · ing. industrial · O4` | Costeo de garruchas (22/09); `criterios` §4 tiene pendiente desde el 14/09 si el piso aplica a otros tipos | Formalizarlo en `criterios-actuales.md`. |
| N18 | **La mano de obra se trata como costo en un lugar y como precio en otro.** En el costeo de garruchas es costo (el markup va encima). En `criterios` §4, el piso de S/250, que es un precio, se compara contra la fórmula de mano de obra. Abierto desde el 14/09 (A1 y A3). `costeo · O4` | `criterios-actuales.md:71-76` | Definirlo y dejarlo escrito: la fórmula da costo y el piso es de precio. |
| N19 | **Los costos no indican si llevan IGV.** El registro pide "Costo repuestos" sin aclararlo, y el catálogo mezcla en la misma columna montos con IGV ("US$215+IGV") y sin IGV (proformas en US$). Con factura, el IGV de la compra es crédito fiscal y el costo real es el neto, así que mezclarlos infla algunos costos un 18%. `contable · O4` | `catalogo.md:54-70`; `armar_registro.py:49` | Regla: todo costo se registra sin IGV. Agregarlo como columna o nota en el registro. |
| N20 | **La detracción no aparece en ninguna parte.** El mantenimiento y la reparación de bienes muebles están sujetos al SPOT. En las dos últimas cotizaciones serían del orden de S/906 (9196) y S/328 (9197), que no llegan a la cuenta corriente sino a la de detracciones del Banco de la Nación. La cotización no lo menciona y el costeo no lo considera en el flujo de caja. `contable` | `grep -i "detracci\|SPOT"` en todo el repo: 0 resultados | **Confirmar la tasa y el umbral vigentes con el contador** (referencia usual: 12% sobre operaciones mayores a S/700). Agregar la leyenda en las condiciones. |
| N21 | **Faltan las condiciones comerciales.** La plantilla solo trae la validez: no dice forma de pago, plazo de ejecución, garantía, ni qué incluye y qué no. Las cadenas pagan a 30-90 días; si la cotización no lo dice, rigen las condiciones del cliente, y la empresa financia repuestos y mano de obra sin que ese costo financiero esté en ningún cálculo. `comunicación · contable · O1` | `cotizacion.html`: 0 menciones de pago, plazo o garantía | Bloque fijo de "Condiciones" en la plantilla. Q7 define el contenido. |
| N22 | **El checklist previo al envío sigue sin escribirse** (abierto desde el 14/09, C4). Esta semana todas las cotizaciones necesitaron el mismo tipo de preguntas, hechas a mano: Lima o provincia (HB), alcance real (Pucallpa: montacargas), especificación (garruchas: temperatura, montaje). `ing. industrial · O1` | `criterios-actuales.md` §5: "pendiente de decidir" | Un checklist por tipo, en `servicios.json` para que el código pueda leerlo. |
| N23 | **Nadie custodia el correlativo** (abierto desde el 14/09, C2). "Continúa la numeración anterior" funcionó porque el número anterior estaba en esta conversación. Con varios cotizadores y rangos propios (`criterios` §7), el siguiente número puede chocar con otro. `sistemas · O2` | `criterios-actuales.md:129-131` | Q4. |
| N24 | **Los pasos del momento de aprobación son manuales y se saltan.** Renombrar el PDF ("N° 9196-2026 CARRETILLAS TT PUCALLPA MUNAY.pdf"), archivar con `--archivar` y pegar la fila del registro: los tres se hicieron a mano o no se hicieron. De 3 PDFs finales reales, ninguno quedó archivado. `automatización · O6` | `cotizaciones-emitidas/` tiene 1 archivo; el renombrado se hizo con `cp` | Un modo `--final` que exija N° real y cero pendientes, nombre el PDF según la convención, archive imagen + JSON e imprima la fila. |
| N25 | **Quedó sin seguimiento una oportunidad más grande que lo cotizado.** El montacargas y los 3 apiladores de Pucallpa salieron de la cotización "para cotizarse aparte", y no quedaron anotados en ningún lado. El PDF de HB también se llamaba "APILADOR Y STOCKAS". Son dos clientes pidiendo equipos que el sistema no sabe cotizar. `comercial` | `casuistica.md` no los menciona | Anotarlo en la casuística como línea de servicio pedida y no atendida. |
| N26 | **Lo mecánico todavía no corre fuera de este entorno.** `generar.py` no depende de Claude, pero sí de Chromium en `/opt/pw-browsers`, que solo existe aquí. Para automatizar en Google, lo que bloquea es el render, no la IA. `automatización · O6` | `generar.py:176` | Tenerlo en cuenta al decidir la migración. |

## 5. Detalles — bajo impacto, rápidos de cerrar

| ID | Hallazgo | Evidencia | Acción |
|---|---|---|---|
| N27 | El IGV se redondea con `float`: en 3 de 7 casos de prueba difiere en 1 céntimo del redondeo contable (subtotal S/30.25 da S/5.44 en vez de S/5.45). Hasta hoy no afectó ninguna cotización emitida, porque todos los subtotales fueron enteros. `contable` | `generar.py:147` | Usar `Decimal` con `ROUND_HALF_UP`. |
| N28 | El cliente llama a sus equipos "ESTOCA" (sus propias etiquetas dicen "07 ESTOCA HIDRAULICA 2026") y la cotización dice "stockas". Quien aprueba compara contra su propio inventario. `comunicación` | Fotos del PDF de HB; `servicios.json` no incluye "estoca" | Usar el nombre del cliente y agregar "estoca" a las palabras clave. |
| N29 | Si "Atención" está vacío, se imprime la etiqueta sola. `comunicación` | 9197-2026; `cotizacion.html:107` | No imprimir la línea cuando esté vacía. |
| N30 | `atencion` se fuerza a mayúsculas (abierto desde el 19/09, B2). `comunicación` | `generar.py:160` | Decidir. |
| N31 | La descripción que va al registro se corta a 60 caracteres, a mitad de palabra: "…hidráulicas (stock". `sistemas` | `generar.py:363` | Cortar en una palabra completa, o no cortar. |
| N32 | `armar_registro.py` repite a mano los tipos y subtipos en vez de leerlos de `servicios.json`, que se declara "fuente única": agregar un subtipo no lo agrega al desplegable. `sistemas · O7` | `armar_registro.py:63-65` | Leer `servicios.json`. |
| N33 | Con `--sin-precios` salen alertas repetidas: una por cada ítem pendiente, más la general. Introducido esta semana. `sistemas` | Salida de SB Mariátegui | Suprimir las alertas por ítem en ese modo. |
| N34 | `criterios` §1 sigue diciendo que Moyobamba es "la más reciente", cuando es la más antigua (abierto desde el 14/09, B1). | `criterios-actuales.md:16` | Corregir. |

## 6. Redundancias

| ID | Qué se repite | Dónde | Acción |
|---|---|---|---|
| R1 | 5 documentos de diagnóstico con pendientes solapados | Los 4 `auditoria-*.md` y `flujo-sistema-completo.md` §7 | Este registro los reemplaza como lista de trabajo. |
| R2 | 3 documentos de flujo (abierto desde el 19/09, D1) | `flujo-completo.md` (todavía con Telegram), `flujo-sistema-completo.md`, `herramientas/flujo-calculo.md` | Dejar uno. El candidato a retirar es `flujo-completo.md`. |
| R3 | La regla de numeración está en 3 lugares, y los 3 están desactualizados | criterios §7, SKILL paso 3, `generar.py:320` | Q4, y después dejarla en un solo lugar. |
| R4 | Tipos y subtipos en 2 lugares | `servicios.json` y `armar_registro.py` | Ver N32. |

## 7. Recomendaciones anteriores que no se implementaron

| Origen | Recomendación | Estado al 23/09 |
|---|---|---|
| Arquitectura 19/09, n.° 1 | Reglas de precio en `criterios.json` | No existe |
| Arquitectura 19/09, n.° 2 | `costeo.py` genérico | No existe; el costeo de garruchas se hizo en Excel |
| Arquitectura 19/09, n.° 3 | Tabla de decisión para el margen | No existe (y N11 muestra que primero hay que definir qué significa "margen") |
| Flujo 19/09, V6/B6 | Generador de la hoja de costos editable dentro del repo | No existe |
| Flujo 19/09, B5 | Validar `sustento_base` de vitrinas y generales | Abierto; N13 muestra además que el código ni lo usa |
| Flujo 19/09, B3/B4 | Cotización enviada sin archivar; COT-2026-002 huérfano | Empeoró: hay 3 PDFs finales sin archivar |
| 14/09, B1 · B5 · C2 · C4 | Moyobamba "más reciente" · Telegram · custodia del correlativo · checklist | Los cuatro siguen abiertos (N34, N15, N23, N22) |

## 8. Decisiones que no se pueden tomar desde el sistema

| ID | Pregunta | Destraba |
|---|---|---|
| Q1 | ¿Se está llenando el registro desde el 15/09? | N08 |
| Q2 | Los precios de Pucallpa (60/95/50): ¿actualizan el catálogo, son solo de ese trabajo, o son más altos por ser provincia? | N09, N10 |
| Q3 | "Margen 60-80%": ¿es sobre el costo (markup) o sobre la venta? | N11 |
| Q4 | Numeración real: formato, quién lleva el correlativo y qué rango usa cada cotizador | N14, N23, R3 |
| Q5 | Telegram: ¿se retoma o se retira de los criterios? | N15, R2 |
| Q6 | El piso de S/250: ¿admite excepciones? ¿Quién las autoriza y dónde quedan registradas? | N12 |
| Q7 | Condiciones comerciales estándar: forma de pago, plazo, garantía, leyenda de detracción | N20, N21 |

## 9. Lo que tienen en común

1. **Reglas escritas que ningún código hace cumplir** (N07, N12, N13, N14). Es la misma lección
   que la casuística dejó escrita el 14/09: "una regla que depende del criterio del momento no es
   una regla". Esta semana se volvió a comprobar tres veces: el piso se rompió sin aviso, la
   `nota` filtró información interna y la numeración decidida nunca se usó.
2. **Los pasos del momento de aprobación son manuales y se saltan siempre** (N02, N24). No es
   descuido: el momento de aprobar no dispara nada. Mientras archivar dependa de acordarse de un
   parámetro, no va a ocurrir.
3. **Los datos para el análisis se capturan con la unidad equivocada o sin el dato que les da
   sentido** (N04, N05, N06, N19). Los cuatro amenazan el mismo objetivo (O4) y tienen fecha
   límite: el cierre del mes de prueba.
