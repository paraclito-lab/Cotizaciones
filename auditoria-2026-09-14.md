# Auditoría integral del sistema de cotizaciones — 14/09/2026

Revisión completa de todo lo construido hasta ahora (reglas, catálogo, ejemplos reales,
plantilla, flujo, registro de costos) contra el objetivo declarado: **cotizar rápido, siempre
con el mismo formato, sin errores de precio, y sabiendo después si cada trabajo ganó o perdió
dinero**.

Cada hallazgo tiene: qué está mal o falta, por qué importa, y qué hacer. Los hallazgos que ya
se resolvieron llevan una nota ✅ al final; el diagnóstico original se deja escrito igual, para
que quede el registro de qué estaba mal y por qué.

---

## Resumen ejecutivo

Lo que está bien y no hay que tocar: la arquitectura de la plantilla (imagen real + texto
superpuesto), la separación repo privado / web pública, el catálogo como fuente única, la
bitácora de casuística, y la decisión de que el margen nunca se aplique automático.

El hallazgo central: **la fórmula de precio documentada no reproduce ninguna cotización
real** (A1). No se resolvió inventando una fórmula mejor, sino cambiando el enfoque: el precio
actual es de referencia, y la fórmula se va a **deducir de un mes de datos reales** que arranca
el 15/09/2026. El registro de costos se rediseñó para capturar exactamente lo que ese análisis
va a necesitar.

Conteo: 21 hallazgos — 3 bloqueantes, 6 vacíos, 5 contradicciones, 4 defectos del registro, 3
oportunidades. **8 ya resueltos o reencuadrados** (A1, A3, B2, D1, D2, D3, D4, y parte de C5);
13 abiertos.

---

> **Estado al 14/09/2026 (noche)**: los hallazgos **A1, A3, B2 y D1–D4 ya fueron resueltos o
> reencuadrados** — ver las notas ✅ dentro de cada uno. El resto sigue abierto.

## A. BLOQUEANTES (impiden programar el cálculo)

### A1. La fórmula de mano de obra no llega ni a la mitad de los precios reales

`criterios-actuales.md` punto 2 define: `personas × tarifa (S/100 o S/200) × 2 (amanecida)`.
Con carretillas = 2 personas (punto 3), el máximo posible es **S/800 para todo el trabajo**.

Contra lo que de verdad se cobró:

| Cotización | Unidades | Fila 1 real | Fórmula da | Con margen 80% |
|---|---|---|---|---|
| Moyobamba N°100 | 4 carretillas | **S/2,600** (S/650 c/u) | S/800 | S/1,440 |
| Porongoche N°107 | 5 carretillas | **S/3,450** (S/690 c/u) | S/800 | S/1,440 |

La fórmula queda entre 2× y 2.4× por debajo incluso aplicando el margen máximo. Faltan dos
variables que nadie escribió:

1. **Cuántas amanecidas toma el trabajo.** La fórmula multiplica por 2 (el día de descanso),
   pero no dice cuántas jornadas son. 5 carretillas no se hacen en una noche: si son 2 o 3
   amanecidas, el número empieza a cerrar. **Sin este dato la fórmula no es computable.**
2. **Cuántas unidades hace un equipo por amanecida.** Es el dato que convierte "5 carretillas"
   en "N amanecidas". Hoy no existe en ningún documento.

También hay una ambigüedad de fondo: **¿S/100–200 por persona es el COSTO (lo que se le paga
al técnico) o el PRECIO (lo que se le cobra al cliente)?** El punto 4 dice que encima va un
margen de 60–80%, lo que sugiere que es costo — pero entonces el punto 4 y el punto 2 están
mezclando las dos cosas sin decirlo.

**✅ REENCUADRADO (14/09/2026)**: no se va a inventar una fórmula ni se va a resolver con una
sesión de preguntas. El precio actual es **un precio de referencia por experiencia**, y la
fórmula se va a **deducir de datos reales**: desde el 15/09/2026 corre un **mes de prueba**
registrando cada trabajo, y al cierre se analiza. Para que eso funcione, el registro se amplió
con las columnas **N° de personas**, **N° de amanecidas**, **cantidad de unidades**, más un
bloque de KPIs de calibración (unidades por amanecida, costo real por amanecida, precio
promedio por unidad). Sin esas columnas, el mes de datos no podría responder la pregunta.
Deja de ser un bloqueante y pasa a ser el objetivo del mes 1.

### A2. La fila 1 de carretillas incluye repuestos que no están en el catálogo

El texto real de la fila 1 es: *"Reparación y mantenimiento de 04 carretillas hidráulicas
(cambio de pasadores, orings, retenes de elevación, pines de expansión, retenes de bomba,
anillos de jebe, aceite hidráulico)"*.

O sea, **la fila 1 no es solo mano de obra: es mano de obra + un kit de consumibles**. Ese kit
(pasadores, orings, retenes, pines, anillos, aceite) **no aparece en `catalogo.md`**, que solo
tiene los 11 repuestos que se cotizan por separado.

Consecuencia: la línea que más factura de todas (S/2,600 y S/3,450 en los dos ejemplos) es
justamente la única cuyo costo real no se puede calcular. No se sabe su margen verdadero.

**Acción**: agregar a `catalogo.md` una sección "kit de mantenimiento por carretilla" con el
costo de cada consumible, aunque sea aproximado. Es el dato que falta para saber si el negocio
principal deja lo que se cree que deja.

### A3. El piso de S/250 por unidad está calibrado contra la fórmula equivocada

El punto 4 fija un mínimo de S/250 por carretilla "sin importar lo que dé la fórmula". Pero
los precios reales son S/650 y S/690 por unidad — **2.6× el piso**. Un piso que está 2.6× por
debajo de todo lo que se cobra en la práctica nunca se va a activar, y si alguna vez se activa
va a producir una cotización muy por debajo de lo normal sin que nadie lo note.

**✅ REENCUADRADO**: queda como está durante el mes de prueba. El KPI "precio promedio por
unidad" del Resumen va a mostrar el piso real, y con ese dato se ajusta al cierre del mes en
vez de adivinarlo ahora.

---

## B. CONTRADICCIONES (dos documentos dicen cosas distintas)

### B1. "Moyobamba es la más reciente" — es la más antigua

`criterios-actuales.md` punto 1 dice que ante conflicto de precios se toma Moyobamba N°100
"por ser la más reciente". Las fechas reales:

| Cotización | Fecha |
|---|---|
| Moyobamba N°100 | **28 de agosto** ← la más antigua |
| Porongoche N°107 | 2 de septiembre |
| Comas N°9053 | 5 de septiembre |
| Angamos N°9127 | 12 de septiembre |

La regla se justifica con un hecho falso. El criterio puede seguir siendo válido (Moyobamba es
la más completa y la de formato elegido), pero hay que reescribir el porqué.

### B2. Rueda de carga: S/40 "confirmado" contra dos cotizaciones reales que dicen S/65

`catalogo.md` marca rueda de carga en **S/40 Confirmado**, "corrige el S/65 de Moyobamba". Pero
Porongoche —posterior a Moyobamba— **también cobró S/65**, y por 20 unidades (S/1,300).

Entonces: o las dos cotizaciones reales están mal, o **S/40 es el costo de compra y S/65 el
precio de venta**, y el catálogo está mezclando ambos conceptos en la misma columna. La segunda
explicación es mucho más probable (S/65 / S/40 = 62% de margen, exactamente dentro del rango
60–80% del punto 4).

Si es así, es un error grave de diseño: **`catalogo.md` no dice si su columna "Precio" es lo
que cuesta o lo que se cobra.** Toda cotización generada con esa tabla cobraría el costo sin
margen.

**✅ RESUELTO (14/09/2026)**: la columna de `catalogo.md` es **precio de venta al cliente**, y
así quedó declarado en el propio archivo. Precios confirmados: **rueda de carga S/40** (el S/65
de los dos PDFs fue un error o un ajuste de conveniencia puntual) y **rueda direccional S/80**
(corrige el S/95). Queda pendiente agregar la columna de **costo de compra**, que hoy no existe
en ninguna parte — sin ella no se puede calcular el margen repuesto por repuesto, solo el
margen global del trabajo vía el registro.

### B3. El README describe la arquitectura vieja de la plantilla

`README.md` dice que `plantilla/` contiene *"imágenes de encabezado **por tipo de servicio**"*.
Eso quedó descartado el mismo día: ahora es **una sola `base.jpg`** con el título como texto
dinámico. Mismo residuo en `flujo-completo.md` ("una sola plantilla HTML **por tipo de
servicio**") y en `branding/README.md` ("las imágenes de `plantilla/headers/`", en plural).

Tres archivos apuntando a un diseño que ya no existe.

### B4. El registro de costos no figura en el mapa del repo ni en el diagrama

El punto 6 de criterios describe el registro (Google Sheet con 3 momentos y KPIs) como
DECIDIDO y construido. Pero:

- `README.md` no lo menciona en la tabla del mapa del repositorio.
- `flujo-completo.md` termina en "Registrar en Histórico" sin nombrarlo.
- **No hay en ningún lado el enlace al Sheet ni la ubicación del archivo.**

El entregable más operativo del proyecto no tiene dirección registrada. Si se pierde el chat
donde se entregó, se pierde.

### B5. Criterios punto 10 y el flujo asumen Telegram, que ya no es la dirección elegida

Todo el punto 10 y los pasos 3–4 del flujo están escritos asumiendo un bot de Telegram con
técnico, especialista y responsable como tres personas distintas. La conversación posterior
concluyó que con un solo usuario en celular eso es overhead innecesario. Los documentos no
reflejan ese cambio de rumbo.

---

## C. VACÍOS (falta información que el sistema necesita para funcionar)

### C1. No hay campo de validez de la cotización

Ninguna cotización real ni ningún documento dice **"esta oferta es válida por X días"**. Una
cotización es un compromiso de precio: sin fecha de vencimiento, un cliente puede aceptar en
marzo un precio calculado en septiembre, con los repuestos ya más caros. Es el vacío de mayor
riesgo comercial de todo el sistema, y se arregla con una línea de texto en la plantilla.

Faltan también, por el mismo motivo: **condiciones de pago**, **tiempo de ejecución** y
**garantía del trabajo**.

### C2. Nadie custodia el correlativo `COT-AAAA-NNN`

Se decidió el formato, pero no **dónde vive el último número usado**. Sin un lugar único, dos
cotizaciones seguidas pueden recibir el mismo número. Lo natural es que lo custodie el propio
registro (el número siguiente = contar filas del año), pero hay que decidirlo y escribirlo.

Además: los otros cotizadores siguen usando sus rangos propios (100, 107, 9053, 9127). Si este
sistema arranca con COT-2026-001 van a convivir **dos universos de numeración**. No está
resuelto quién más cotiza ni cómo se migra.

### C3. "Servicios Generales" —el cajón que más se va a usar— no tiene personal definido

El punto 3 deja **"por confirmar"** justo la categoría diseñada para absorber todo lo nuevo
(motores, eléctrico, estructuras, pintado). Es el tipo de servicio donde más falta la regla,
porque es el que no tiene precedente.

### C4. El checklist del punto 5 está descrito pero nunca escrito

El punto 5 dice que debe existir un checklist de preguntas antes de cerrar cada cotización, y
el flujo lo pone como **bloqueante** (`¿Checklist resuelto? No → bloquea`). Pero el checklist
**no existe**: no hay una sola pregunta escrita en ningún archivo. Un paso bloqueante sin
contenido es un paso que no se puede ejecutar.

### C5. Ítems reales que faltan en el catálogo

De las cotizaciones ya entregadas, no están en `catalogo.md`:

| Ítem | Precio visto | Dónde |
|---|---|---|
| Eje central | S/70 | Porongoche |
| Soldadura de barra de tiro | S/100 | Porongoche |

Y hay dos posibles duplicados sin unificar: *"soldadura de barra de tiro"* (S/100) vs
*"alineamiento de barra de tiro"* (S/50) — ¿son dos trabajos distintos o el mismo con nombre
distinto? Igual con *"rueda de carga"* vs *"rueda trasera"* (Porongoche las nombra juntas:
"ruedas de carga y/o traseras"), que el catálogo no unificó aunque sí unificó
direccional/giratoria/delantera.

### C6. La tasa de IGV nunca se escribió como regla

Los 4 ejemplos usan 18%, y el flujo dice "IGV correcto" — pero **en ningún documento dice que
la tasa es 18%**. Es el tipo de dato obvio que se olvida escribir y después nadie sabe de dónde
salió.

---

## D. DEFECTOS EN EL REGISTRO DE COSTOS

**✅ LOS CUATRO CORREGIDOS (14/09/2026)** — el archivo fue reconstruido: ganancia sobre
subtotal, fórmulas hasta la fila 500, instrucciones del LEEME con las columnas correctas, y
columna de motivo de pérdida con su conteo en el Resumen. Se agregaron además las columnas de
calibración (personas, amanecidas, unidades). Validado: 2,519 fórmulas, 0 errores. Se deja el
diagnóstico original abajo como registro de qué estaba mal.

### D1. La ganancia está inflada: cuenta el IGV como ingreso propio

`Ganancia real = Total cotizado − Costo real`, donde "Total cotizado" **incluye el IGV**. El
IGV no es ingreso de la empresa: se cobra y se le entrega a SUNAT. Con la fila de ejemplo del
propio archivo:

| | Como está | Como debería ser |
|---|---|---|
| Base | Total S/2,206.60 | Subtotal S/1,870.00 |
| Costo real | S/940.00 | S/940.00 |
| **Ganancia** | **S/1,266.60** | **S/930.00** |
| **Margen** | **57.4%** | **49.7%** |

**La ganancia aparece 36% más alta de lo real, en todas las filas y en todos los KPIs.** Es el
defecto más caro del proyecto: es exactamente el número que el registro existe para medir.
Arreglo: cambiar `I` (Total) por `G` (Subtotal) en las tres fórmulas y en los KPIs del Resumen.

### D2. Las fórmulas llegan hasta la fila 200, pero los KPIs suman hasta la 500

Una cotización cargada en la fila 250 **no va a mostrar ganancia ni margen** (esas celdas están
vacías, sin fórmula) y va a distorsionar los promedios del Resumen en silencio. Hay que
extender las fórmulas hasta 500, o mejor convertir el rango en tabla.

### D3. Las instrucciones de la hoja LEEME tienen las columnas corridas

Dice *"MOMENTO 1 — columnas A a J"* y *"MOMENTO 2 — columna K"*. Pero Estado (Momento 2) es la
columna **J**, y K es "Fecha respuesta". También dice *"MOMENTO 3 — columnas L a P"* cuando P ya
es una fórmula que no se toca (debería ser **L a O**). Alguien siguiendo las instrucciones al
pie de la letra escribiría encima de una fórmula.

### D4. No hay columna de "por qué se perdió"

El registro captura Perdido/Sin respuesta, pero no el motivo (precio alto, plazo, competencia,
el cliente desapareció). Sin eso, el % de cotizaciones ganadas es un número que no dice qué
hacer distinto.

---

## E. PROCESO Y OPORTUNIDADES

### E1. El flujo está diseñado para 3 personas y lo va a operar 1

Técnico que carga → especialista que revisa → responsable que envía. Con un solo operador, los
pasos 3 y 4 son autorevisión: aprobar tu propia cotización no agrega control, solo agrega
clics. **Recomendación**: colapsar el flujo a un solo rol ahora (generar → revisar → marcar
lista), dejando el diseño de 3 roles documentado como "cuando el equipo crezca". No borrarlo —
guardarlo.

### E2. La bitácora de casuística existe pero no se está usando

`casuistica.md` tiene **un solo caso**, mientras que hay al menos 3 dudas abiertas anotadas
sueltas dentro de `ejemplos-reales/` que nunca llegaron ahí:

- El título genérico "Mantenimiento de carretillas hidráulicas" usado en una cotización de
  cambio de motor (Angamos).
- El campo de cronograma *"en dos grupos de 10 bandejas, 6 días por grupo"* (Comas) — nunca se
  decidió si es un campo fijo de la plantilla.
- La duda de nombres de ruedas (Porongoche).

El mecanismo está bien diseñado; simplemente no se siguió. Hay que migrar esas 3 y cerrar las
que ya tienen respuesta.

### E3. Riesgo de privacidad no considerado: nombres de contactos de clientes

Existe una regla estricta de no nombrar a ninguna persona del lado propio. Pero
`ejemplos-reales/` contiene **nombres completos de personas de contacto de clientes** (4
personas). Es incoherente con el criterio adoptado, y son datos personales de terceros bajo la
Ley 29733. El repo es privado, así que no hay exposición hoy — pero conviene reemplazarlos por
"Atención: [contacto]" y quedarse solo con el dato estructural.

### E4. Oportunidad de mayor retorno: validar los 9 precios "Por validar"

`catalogo.md` tiene 11 ítems, de los cuales **9 están sin confirmar**. Es el 82% del catálogo
en estado dudoso. Una sola sesión corta repasando esa lista desbloquea la confiabilidad de todo
lo demás — y ya se demostró que vale la pena, porque al validar el primero (rueda de carga)
apareció una discrepancia.

### E5. Detalles menores de la plantilla

- **`base.jpg` es JPG**: formato con pérdida, para una imagen con texto y bordes finos. PNG
  daría bordes limpios y pesa parecido a esa resolución.
- **"hidraúlica" está mal escrito** en el PDF original (va "hidráulica") y se propagó a los
  documentos. Como el título ahora es texto dinámico y no parte de la imagen, **es el momento
  de corregirlo** — de aquí en adelante sale bien sin rehacer nada.
- **No está documentado cómo se recortó `base.jpg`** del PDF. Están las coordenadas del texto
  superpuesto, pero no las del recorte. Si hay que rehacerlo (cambia una dirección, un
  celular), toca redescubrir el proceso entero.

---

## Orden sugerido de ataque

1. **A1 + A2 + B2** — definir amanecidas por trabajo, costo del kit de consumibles, y separar
   costo de precio de venta en el catálogo. Sin esto no hay cálculo posible.
2. **D1** — corregir la ganancia del registro (cambiar Total por Subtotal). Es un arreglo de
   minutos sobre un número que hoy miente en un 36%.
3. **C1** — agregar validez de la oferta, condiciones de pago y plazo a la plantilla.
4. **E4 + C5** — validar los 9 precios dudosos y agregar los 2 ítems faltantes.
5. **C4** — escribir el checklist, que hoy es un paso bloqueante vacío.
6. **B3 + B4 + B5** — sincronizar README, flujo y branding con las decisiones ya tomadas.
7. El resto, a medida que aparezca en el uso real.
