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
| Otros (estructuras metálicas, motores AC, planchado/pintado, etc.) | **por confirmar** |

## 4. Margen de ganancia

- Referencia de experiencia: **60% a 80%** sobre el costo.
- Se puede bajar el margen si es una cantidad grande de unidades (ej. muchas carretillas de
  un mismo cliente).
- El precio final suele **ajustarse a un número "redondo"** cercano (ej. S/2,490, S/2,980,
  múltiplos de S/500) — es una decisión comercial, no una fórmula automática.
- **Importante**: el margen sugerido NUNCA debe aplicarse automático — el sistema debe
  proponerlo y alopez (dueño) lo confirma o ajusta antes de enviar.

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

**Pendiente de decidir con alopez**: si el checklist es el mismo para todo tipo de servicio o si
cada categoría de servicio (carretillas, balanzas, estructuras, motores) tiene su propio set
de preguntas.

## 6. Seguimiento de costos reales (aún no existe)

Hoy no hay manera de comparar lo cotizado contra lo que realmente costó el trabajo — por lo
tanto no se sabe con certeza si una cotización específica ganó, perdió, o cobró justo.

Idea a desarrollar: por cada cotización, además del monto cotizado, registrar después del
trabajo:
- Costo real de repuestos usados.
- Días/personas reales de mano de obra.
- Gastos de campo reales (pasajes, viáticos, encomienda).
- Margen real obtenido vs. margen cotizado.

Esto permitiría, con el tiempo, tener un costo de referencia más preciso por tipo de servicio
y localidad (en vez de solo el precio cotizado que hay hoy en `catalogo.md`), y detectar
cuando una cotización se está subestimando.

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

La redacción de la tabla de ítems varía según tipo de servicio, y así se mantiene (no se
fuerza un único formato de fila):
- **Carretillas**: una fila de "mantenimiento" (mano de obra, por cantidad de unidades) +
  filas separadas por cada repuesto suministrado.
- **Balanzas**: redacción propia (más técnica: calibración, nivelación, alineamiento, etc.).
- **Resto de servicios** (estructuras, motores, pintado electrostático, etc.): una fila con
  foto del equipo/trabajo + descripción + precio final.

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

**Pendiente de decidir con alopez**: después de cuánto tiempo / cuántas cotizaciones sin
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
