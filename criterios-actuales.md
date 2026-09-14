# Criterios de cotización — confirmados en conversación

Última actualización: 14/09/2026. Este documento resume lo confirmado hasta ahora en
conversación; no es un sistema todavía, es la base de reglas sobre la que se va a construir.

## 1. Repuestos → precio constante

El precio de un repuesto (retenes, ruedas, resortes, ejes, etc.) **no cambia según la
localidad**. Es el mismo en Lima o en provincia. **La tabla de precios vive en `catalogo.md`**
(no aquí, y no en ningún Excel) — ese archivo es la única fuente de verdad, para no tener el
mismo precio escrito en dos lugares que se puedan desincronizar.

**Fuente de verdad ante conflicto de precio o nombre — DECIDIDO**: cuando dos cotizaciones
reales tengan un precio o nombre distinto para lo que parece ser el mismo repuesto, se toma
como punto de partida lo que aparece en la cotización de **Moyobamba (N° 100-2026)** por ser
la más reciente, pero **se valida siempre antes de darlo por definitivo** — ya pasó que un
precio de Moyobamba resultó incorrecto (ver `catalogo.md`, rueda de carga). Toda vista previa
es una oportunidad de corregir el catálogo, no solo de aprobar o rechazar la cotización.

**Personal para servicios que no son carretilla/balanza (estructuras, motores, pintado)**: no
hay dato confirmado todavía. Mientras tanto se usa como referencia el modelo de costeo de la
hoja "COTIZACION MOTOR" (ver `analisis/cchh-cot-excel.md`) — no para copiar un número de
personas, sino para la lógica de costo → ganancia → precio. Sigue pendiente de confirmar caso
por caso.

## 2. Mano de obra → depende de la localidad

- **Lima / local**: tarifa por persona de S/100 o S/200 por "amanecida".
  - **Una amanecida se cobra doble** (equivale a 2 días): el personal descansa el día
    posterior al trabajo y no puede tomar otro servicio, así que ese día también se paga.
  - Falta confirmar: qué decide si la amanecida es de S/100 o S/200 (¿dificultad del
    trabajo? ¿horas? ¿tipo de cliente?).
- **Provincia**:
  - Si hay personal en la zona, se le pide que inspeccione y cotice en campo — **el precio
    de su mano de obra lo decide el personal local**, no hay techo fijo desde Lima.
  - Si el costo de personal local sale muy alto, se evalúa enviar equipo desde Lima
    (implica sumar pasajes + viáticos + encomienda de repuestos).

## 3. Personal requerido según tipo de equipo

| Tipo de equipo   | N° de personas |
|---|---|
| Carretilla hidráulica | 2 |
| Balanza | 3 |
| Servicios Generales (estructuras, motores, eléctrico/electromecánico, pintado, etc.) | **por confirmar** |

## 4. Margen de ganancia

- Referencia de experiencia: **60% a 80%** sobre el costo.
- Se puede bajar el margen si es una cantidad grande de unidades (ej. muchas carretillas de
  un mismo cliente).
- El precio final suele **ajustarse a un número "redondo"** cercano (ej. S/2,490, S/2,980,
  múltiplos de S/500) — es una decisión comercial, no una fórmula automática.
- **Importante**: el margen sugerido NUNCA debe aplicarse automático — el sistema debe
  proponerlo y confirmarse/ajustarse antes de enviar.

**Naturaleza del precio hoy — DECIDIDO (14/09/2026)**: los precios de mano de obra que se
cobran hoy (del orden de S/650–690 por carretilla) son **precios de referencia por
experiencia**, no el resultado de una fórmula. No existe todavía una fórmula que los reproduzca
y no se va a inventar una: **se va a deducir con datos reales**. Desde el 15/09/2026 arranca un
**mes de prueba** en el que cada cotización y cada trabajo se registran con el detalle
necesario (personas, amanecidas, costo real) — al cierre del mes se analiza esa data y recién
ahí se define la fórmula, o se confirma que el precio de referencia estaba bien. Se revisa y se
mejora mes a mes.

**El precio se entrega siempre SIN IGV — DECIDIDO (14/09/2026)**: cuando se indica un precio
para una cotización, es el **subtotal**. El IGV del 18% y el total los calcula el sistema
encima de ese número. No hay que aclararlo caso por caso: si se dice "2330", el subtotal es
S/2,330 y el total S/2,749.40.

**Precio mínimo — DECIDIDO (14/09/2026)**: el mantenimiento de carretillas hidráulicas tiene
un **piso de S/250 por unidad**, sin importar lo que dé la fórmula de mano de obra (personas ×
tarifa × 2 ÷ cantidad). Si la fórmula da menos de S/250 (por ejemplo, muchas unidades entre
pocos días de mano de obra), se cobra el mínimo de S/250 igual. Pendiente de confirmar si este
mismo concepto de "precio mínimo" aplica a otros tipos de servicio (balanzas, estructuras) o
es específico de carretillas.

## 5. Checklist de consideraciones antes de enviar

Idea vista en la hoja de cotización de una balanza en Tarapoto: antes de
cerrar una cotización, dejar una lista de preguntas/consideraciones pendientes por tipo de
servicio (ej. para una balanza: ¿se pinta la estructura?, ¿qué tipo de pintura?, ¿cuántos
trabajadores?, ¿cuál es el costo real del pasaje?). Enviar una cotización es un compromiso de
precio, así que no debería salir con preguntas sin resolver.

**Pendiente de decidir**: si el checklist es el mismo para todo tipo de servicio o si
cada categoría de servicio (carretillas, balanzas, Servicios Generales) tiene su propio set
de preguntas.

## 6. Seguimiento de costos reales — DECIDIDO (14/09/2026, ampliado)

Hasta ahora no había manera de comparar lo cotizado contra lo que realmente costó el trabajo —
por lo tanto no se sabía con certeza si una cotización específica ganó, perdió, o cobró justo.
Se armó un **registro** (Google Sheet, fuera de este repo — es dato operativo que cambia todo
el tiempo, no encaja en control de versiones) con una fila por cotización, llenada en 3
momentos:

1. **Al cotizar**: N°, fecha, cliente/local, tipo de servicio, descripción, **cantidad de
   unidades**, subtotal/IGV/total cotizado.
2. **Cuando el cliente responde**: Estado (Cotizado / Enviado / Ganado / Perdido / Sin
   respuesta) y, si se perdió, **el motivo** (precio alto, plazo, otro proveedor, etc.) — sin
   el motivo, el % de cotizaciones ganadas es un número que no dice qué hacer distinto.
3. **Al terminar el trabajo** (solo si se ganó): fecha, **cuántas personas fueron**, **cuántas
   amanecidas tomó**, y el costo real de repuestos, mano de obra y logística. El costo total,
   la ganancia, el margen, las unidades por amanecida y el precio por unidad **se calculan
   solos por fórmula** — nunca se escriben a mano.

**Personas y amanecidas son las dos casillas más importantes del archivo.** Son exactamente los
datos que hoy faltan para poder calcular un precio en vez de estimarlo (ver punto 4). Si quedan
vacías durante el mes de prueba, al cierre habrá datos de facturación pero no se podrá deducir
la fórmula, que es el objetivo del mes. La hoja "Resumen" incluye un contador de trabajos con
esas casillas sin llenar, justamente para que no pase desapercibido.

**La ganancia se calcula sobre el subtotal, no sobre el total.** El IGV no es ingreso de la
empresa: se cobra al cliente y se le entrega a SUNAT. Contarlo como ganancia la infla alrededor
de un 36%.

La hoja "Resumen" calcula solo: KPIs comerciales (total cotizado, % ganadas, facturado),
rentabilidad real por tipo de servicio (Carretillas / Balanzas / Servicios Generales), el
conteo de motivos de pérdida, y un bloque de **calibración de la fórmula de precio**: unidades
por amanecida, costo real de mano de obra por amanecida, y precio promedio por unidad. Ese
bloque es el que se lee al cierre del mes de prueba.

**Pendiente**: el registro se llena a mano; escribirlo automáticamente desde el sistema queda
para después de que el proceso manual demuestre que funciona.

## 7. Numeración de cotización — DECIDIDO

`COT-AAAA-NNN` (correlativo anual, reinicia cada año). Reemplaza el desorden actual: en los
PDFs reales entregados se encontró N° 100 (28-ago), N° 107 (2-sep), N° 9053 (5-sep) y N° 9127
(12-sep) — sin relación con la fecha, porque cada cotizador usa su propio rango de números.
Con `COT-AAAA-NNN` hay un solo correlativo compartido, ordenable y sin choques.

## 8. Marca y formato del PDF final — DECIDIDO

Datos reales de la empresa (tomados de las cotizaciones ya entregadas a clientes):

- Razón social: **LF MUNAY PERÚ**
- RUC: 20605791124
- Dirección: Calle Los Álamos Mz L Lt 5 - Pachacamac
- Celular: 946 763 582
- Email: lfmunayperu@gmail.com
- Logo: círculo con degradado naranja/turquesa/negro formando una "M" (ya guardado en
  `branding/logo.png`).

Formato de PDF a usar de aquí en adelante: el visto en la cotización N° 100-2026 (Moyobamba,
HB Precio) — encabezado con logo, franjas turquesa/naranja, N° de cotización en una cápsula
verde, tabla con Sub Total resaltado en amarillo. Reemplaza al formato simple sin color (visto
en la cotización N° 107-2026, Porongoche) que queda descontinuado. La implementación técnica
de este formato (cómo se genera el PDF/PNG real) está en `plantilla/README.md`.

**Títulos del encabezado y tipos de servicio — DECIDIDO (14/09/2026)**

La relación **tipo de servicio → título del encabezado → redacción del sustento técnico →
categoría del registro** vive en un solo archivo: **`servicios.json`**. No se repite acá ni en
la skill ni en `plantilla/README.md`, porque ya pasó que el mismo dato escrito en tres lugares
se desincronizara (ver `auditoria-2026-09-14.md`, hallazgo B3).

Hoy son cuatro tipos: `carretillas`, `balanzas`, `vitrinas` y `generales`. Cada uno trae su
título fijo, las palabras clave que lo reconocen desde una descripción en lenguaje natural, el
patrón de redacción de la fila, el personal requerido y el precio mínimo si tiene.

Dos reglas que `plantilla/generar.py` **hace cumplir por código**, no solo por escrito:

- **El título no se escribe a mano.** Se pide el `tipo` y el título sale de ahí. Si un JSON
  trae un `titulo`, el generador se niega a correr. Así el error de coherencia
  título↔contenido (título de balanza con contenido de carretilla) ya no puede ocurrir.
- **El título nombra la familia; el sustento técnico dice el trabajo.** Si ambos dicen casi lo
  mismo, el título está mal elegido.

La redacción de la tabla de ítems varía según tipo de servicio, y así se mantiene (no se
fuerza un único formato de fila):
- **Carretillas**: una fila de "mantenimiento" (mano de obra, por cantidad de unidades) +
  filas separadas por cada repuesto suministrado.
- **Balanzas**: redacción propia (más técnica: calibración, nivelación, alineamiento, etc.).
- **Servicios Generales** (estructuras, motores, eléctrico/electromecánico, pintado
  electrostático, y cualquier servicio nuevo que todavía no tenga categoría propia): una fila
  con foto del equipo/trabajo (opcional) + descripción + precio final. Es a propósito un cajón
  amplio — no se subdivide más (ej. "Eléctrico" separado de "Estructuras") salvo que en el uso
  real se note que hace falta.

**Fotos en "sustento técnico" — DECIDIDO (14/09/2026)**: para el tipo "Servicios Generales",
la foto es **opcional** — si el técnico no manda ninguna, la cotización sale solo con texto,
no bloquea la generación. Si manda entre 1 y 3 fotos, se aceptan **tal cual, sin exigir
calidad** (no se rechaza una foto oscura o borrosa), y el sistema las achica y encuadra
automáticamente para que quepan en la fila de la tabla. Si manda más de 3, pendiente de
decidir qué hacer (¿se usan las primeras 3? ¿se pide elegir?) — no se ha dado el caso todavía,
se resuelve cuando aparezca (ver `casuistica.md`).

**Regla de coherencia título↔contenido — DECIDIDO (14/09/2026)**: el título del servicio (el
texto grande superpuesto, ver `plantilla/README.md`) y el contenido de "sustento técnico" no
son piezas independientes — el tipo de servicio elige ambos a la vez. Un título de "Balanzas"
nunca debe ir con contenido de "Carretillas" (o viceversa). Se detectó este error en una
prueba (se cambió el título a balanza pero se dejó el contenido de carretillas) — al generar
una cotización, el tipo de servicio debe ser un solo dato que determina título + patrón de
contenido juntos, nunca dos campos que se llenan por separado.

## 9. Flujo de aprobación antes de enviar — DECIDIDO (primera versión)

Contexto: manejar automatización sobre datos de costos/ganancias/precios es nuevo para el
equipo, así que el flujo arranca con el máximo de control humano y se relaja con el tiempo,
no al revés.

1. **Generación** — el sistema arma la cotización (PDF + vista previa) desde la plantilla.
2. **Validación automática** — antes de mostrarla a nadie, se revisa: ningún ítem en S/0,
   IGV correcto, margen dentro de un rango razonable, checklist de preguntas pendientes (ver
   punto 5) resuelto. Si falta algo, no avanza al paso 3.
3. **Revisión humana por Telegram** — se manda la vista previa a un especialista; puede pedir
   correcciones (el sistema regenera y vuelve a mandar) o aprobar.
4. **Aprobación ≠ envío** — cuando el especialista dice "envíalo", la cotización queda
   marcada como **"Lista para enviar"**, y se notifica a la persona responsable para que sea
   ella quien mande el correo desde Gmail. El bot NO envía el correo directamente todavía.
5. **Registro trazable** — cada cotización guarda su historial completo: quién la pidió, qué
   correcciones tuvo, quién la aprobó, cuándo se marcó lista, cuándo se envió realmente.

**Pendiente de decidir**: después de cuánto tiempo / cuántas cotizaciones sin
corrección se evalúa automatizar el paso 4 (y probablemente solo para el tipo de servicio más
estandarizado — mantenimiento rutinario de carretillas — no para estructuras/motores).

## 10. Cómo se interactúa por Telegram — DECIDIDO

Se evaluaron 3 formas (formato de texto fijo, formulario/Mini App de Telegram, conversación
libre con IA) y se eligió la más simple e intuitiva:

- **Carga del técnico → conversación libre, sin formato fijo.** El técnico escribe como si le
  hablara a una persona (ej: "hice mantenimiento a 5 carretillas en Tottus San Miguel, cambié
  10 ruedas de carga, atendió Carlos Ramos"). El bot, con un modelo de lenguaje detrás,
  entiende el mensaje, arma los campos y **pregunta de vuelta en lenguaje natural** si falta
  algo (ubicación, dato del checklist, etc.) — igual que una conversación normal. Siempre
  confirma lo que entendió antes de generar el PNG ("Entendí: 5 carretillas, Tottus San
  Miguel... ¿correcto?"), porque hay dinero de por medio y un malentendido no debe colarse.
- **Aprobación del especialista → botones, no texto.** Debajo del PNG de vista previa,
  botones `[✅ Enviar]  [✏️ Corregir]  [❌ Rechazar]`. Tocar un botón es más simple y rápido
  que escribir "envíalo"; si toca "Corregir", ahí sí se abre a texto libre para decir qué
  cambiar.
- **Descartado por ahora**: un formulario / Mini App de Telegram (más estructurado pero menos
  natural y más trabajo de construcción) y un formato de texto con etiquetas fijas (obliga a
  recordar una sintaxis). Quedan como opción futura si la conversación libre resulta lenta o
  poco confiable en el uso real.
