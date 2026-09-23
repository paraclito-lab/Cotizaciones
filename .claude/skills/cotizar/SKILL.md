---
name: cotizar
description: Genera una cotización completa de LF Munay Perú (vista previa PNG + PDF final) a partir de una descripción en lenguaje natural del trabajo. Úsala SIEMPRE que se pida cotizar, armar una cotización, hacer un presupuesto o preparar una propuesta de precio para un cliente — por ejemplo "cotiza 5 carretillas en Tottus San Miguel, cambié 10 ruedas de carga", "arma la cotización del cambio de motor de Angamos", "hazme el presupuesto de la balanza de Tarapoto", o cuando se manden fotos de un trabajo junto con un precio. Cubre: identificar el tipo de servicio, buscar precios en el catálogo, calcular subtotal/IGV/total, asignar el N° correlativo, renderizar el PNG de vista previa, esperar aprobación, generar el PDF y entregar la fila lista para el registro de costos. NO uses esta skill para subir fotos a la web pública (para eso está fotos-trabajos) ni para analizar la data del registro al cierre de mes.
---

# Cotizar — LF Munay Perú

## Qué hace esta skill

Convierte una descripción suelta de un trabajo ("5 carretillas en Tottus San Miguel, cambié
10 ruedas de carga") en la cotización con el formato real de la empresa: PNG para revisar en
el celular y PDF para enviar por correo.

Es el reemplazo del bot de Telegram que se diseñó y se descartó: mismo flujo, sin servidor.

## Regla de redacción que aplica a TODO lo que produzcas

Ningún documento, cotización, commit, nota o mensaje generado aquí menciona a una persona ni a
un rol interno. Las reglas se enuncian como hechos del negocio, nunca atribuidas a alguien.
Esto incluye los nombres de contacto del cliente dentro del repositorio (en la cotización sí
van, porque es el documento que recibe el cliente; en los archivos del repo, no).

**Única excepción, explícita:** `cotizaciones-emitidas/` guarda la imagen de cada cotización ya
enviada, y esa imagen lleva el nombre del cliente porque es copia fiel de lo que el cliente
recibió. Es la excepción que confirma la regla: ahí va porque es el documento del cliente, no
un archivo de trabajo. En todo lo demás —ejemplos, JSON de prueba, documentación— va un
placeholder. Si esta excepción no estuviera escrita, el archivo rompería la regla en silencio.

## Antes de generar: leer siempre

1. `criterios-actuales.md` — las reglas vigentes. **Puede haber cambiado desde la última vez.**
2. `catalogo.md` — la ÚNICA fuente de precios. Si un repuesto no está ahí, no inventar el
   precio: preguntar. Los precios marcados "Por validar" se usan, pero se avisa que no están
   confirmados.
3. Si el tipo es `balanzas`, además leer `balanzas-industriales/` — tiene su propia bitácora de
   casuística (`casuistica-balanzas.md`) y las cotizaciones reales cerradas de
   `cotizaciones-reales/`, que hoy son la única referencia de precio real de este tipo (el
   catálogo general no tiene repuestos de balanza todavía).

## Paso 0 — ¿El trabajo ya tiene ficha?

Antes que nada, buscar en `trabajos/` una ficha cuyo `nombre` o `palabras_clave` coincida con
lo pedido (hoy: `garruchas-coche-panaderia`, `mantenimiento-carretillas`). **Si existe, se
cotiza con la ficha** (ver `trabajos/README.md`):

1. Armar el pedido: cliente, local, unidades y las **respuestas del checklist** de la ficha.
   Las que no se sepan se preguntan en lenguaje natural, junto con su "por qué importa".
2. `python3 herramientas/cotizar_trabajo.py pedido.json salida/` (con `--borrador` si el
   cliente quiere ver el alcance antes de tener todas las respuestas).
3. Mostrar el costeo, la propuesta de precio y **lo que ya se cobró antes por ese trabajo**, y
   esperar el precio. **El precio no se pone solo**: va en `precio_unidad` del pedido.
4. Con el JSON que escribe el motor se sigue en el Paso 4 (generar).

**Si no existe ficha**, se cotiza a mano como hasta ahora (pasos 1 a 7). Al terminar, si el
trabajo puede volver a pedirse, **ofrecer crear su ficha** con lo aprendido
(`python3 herramientas/nuevo_trabajo.py`, o escribirla siguiendo `trabajos/_plantilla.json`) y
validarla con `python3 herramientas/cotizar_trabajo.py --validar`. Así la segunda vez ya no se
piensa desde cero. Un costo que falta en la ficha se agrega a la ficha, no al pedido.

## Paso 1 — Identificar el tipo de servicio

**El tipo elige el título Y el contenido a la vez** — nunca se llenan por separado (regla de
coherencia, `criterios-actuales.md` punto 8).

Los tipos, sus títulos, sus palabras clave y el patrón de redacción de la fila están en
**`servicios.json`** — leerlo, no asumirlos de memoria ni copiarlos acá.

Hoy son cuatro: `carretillas`, `balanzas`, `vitrinas`, `generales`.

**Lo que no encaja en los tres primeros es `generales`. Siempre, sin consultar y sin
excepciones.** No se crea un tipo nuevo en medio de una cotización — ya se falló en esto una
vez (ver `casuistica.md`). Un servicio `generales` exige además un **`subtipo`** de la lista
`subtipos_sugeridos` de `servicios.json`; el generador se niega a correr sin él.

Si en la conversación parece que un trabajo merece familia propia, **no se le da**: se cotiza
como `generales` con su subtipo, y se menciona que el conteo del registro lo va a decidir al
cierre de mes (umbral: 3 cotizaciones del mismo subtipo). Si no hay subtipo que calce, se usa
`otros` y se anota el caso en `casuistica.md`.

**El título nunca repite el sustento técnico**: el título dice la familia, la fila dice el
trabajo. En la fila, abrir con "Suministro e instalación de..." cuando el material lo pone la
empresa.

## Paso 2 — Confirmar antes de generar

Hay dinero de por medio: nunca generar sin devolver un resumen de lo entendido y esperar el OK.

> "Entendí: 5 carretillas en Tottus San Miguel, con su contacto de atención, 10 ruedas de carga
> (S/40 c/u) y 4 direccionales (S/80 c/u). Mantenimiento a S/650 por unidad. ¿Correcto?"

Preguntar en lenguaje natural solo lo que realmente falte (cliente, local, atención, cantidad,
precio). No pedir todo de golpe como un formulario.

**El precio que se indica es siempre el subtotal, SIN IGV.** No preguntarlo cada vez: el IGV
del 18% y el total se calculan encima.

## Paso 3 — Numeración

El formato en uso real es `NNNN-AAAA` (8211-2026, 9196-2026, 9197-2026). `COT-AAAA-NNN`
quedó decidido en `criterios-actuales.md` §7 pero nunca se adoptó; cuál queda está pendiente
(`hallazgos-abiertos.md`, Q4). El generador acepta los dos. Para el siguiente número, preguntar
cuál fue el último usado. Si no se sabe, preguntar — **nunca inventar un número**: un
correlativo duplicado rompe la trazabilidad. Mientras no haya número, `PENDIENTE-AAAA`.

## Paso 4 — Generar

Armar un JSON y correr el generador:

```bash
PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 plantilla/generar.py cotizacion.json salida/
```

Formato del JSON:

```json
{
  "numero": "0000-2026",
  "tipo": "carretillas",
  "cliente": "TOTTUS",
  "cliente_corto": "TT",
  "local": "San Miguel",
  "atencion": "NOMBRE DE CONTACTO",
  "fecha": "15 de septiembre de 2026",
  "unidades": 5,
  "items": [
    {"cant": 5, "descripcion": "Reparación y mantenimiento de 5 carretillas hidráulicas: cambio de pasadores, orings, retenes de elevación, pines de expansión, retenes de bomba, anillos de jebe, aceite hidráulico.", "precio_unit": 650.00},
    {"cant": 10, "descripcion": "Suministro de rueda de carga.", "precio_unit": 40.00}
  ],
  "condiciones": ["El trabajo se ejecuta fuera del horario de atención al público."],
  "nota": "Opcional, la ve el cliente.",
  "nota_interna": "Por qué se cobró lo que se cobró. NUNCA se imprime."
}
```

**Lo que ve el cliente y lo que no.** `nota`, `condiciones` y las descripciones se imprimen
tal cual. `nota_interna` no se imprime nunca: ahí va todo razonamiento de precio (excepción al
piso, precio distinto al catálogo, origen de un número). El generador **se niega a generar** si
en lo impreso aparece "catálogo", ".md", "piso mínimo", "markup", "por validar", "ganancia" o
parecidos — pasó tres veces en una semana antes de que existiera este bloqueo.

- `unidades`: cuántos **equipos** se atienden (10 carretillas), no la suma de repuestos. Es lo
  que el registro divide para "precio por unidad".
- `cliente_corto` (opcional): cómo va el cliente en el nombre del PDF ("TT" por TOTTUS).
- `condiciones` (opcional): lista de frases (horario, retiro de lo cambiado, exclusiones). Salen
  en su propio bloque bajo la validez, no mezcladas en la nota.

- `fotos`: lista de rutas de imagen dentro de un ítem (máximo 3, opcional, solo Servicios
  Generales). Se achican y encuadran solas; **no se rechaza una foto por borrosa u oscura**.
- `tipo` es obligatorio y **reemplaza al título**: el generador se niega a correr si el JSON
  trae un `titulo` escrito a mano.
- `resumen` (opcional): la descripción corta que va al registro de costos.
- El subtotal, el IGV y el total los calcula el script. No escribirlos a mano.
- La fecha va en texto largo en español ("15 de septiembre de 2026").

El script imprime los totales, las rutas del PNG y del PDF, **la fila ya armada para pegar en
el registro de costos**, las **alertas** ("REVISAR ANTES DE ENVIAR": precio pendiente, bajo el
piso, N° que no es real…) y aparte los **avisos** informativos. Las alertas se resuelven o se
explican antes de mostrar nada; los avisos no exigen hacer nada.

## Paso 4b — Cuando la especificación manda el precio: propuesta técnica sin precios

Hay trabajos donde el mismo ítem cambia de precio varias veces según su especificación (una
garrucha de coche de panadería va de S/18 a S/140 según diámetro, tipo de montaje, material
de rueda, capacidad de carga y temperatura de trabajo). Cotizar antes de fijar la
especificación es cotizar a ciegas, y si el precio se manda mal, la corrección la paga la
empresa.

En esos casos se emite la **propuesta técnica**: mismo documento, alcance completo, precios en
"Por definir".

```bash
python3 plantilla/generar.py cotizacion.json salida/ --sin-precios
```

Exige que **todos** los ítems sean `pendiente`, no muestra nunca "S/ 0.00" en los totales, no
se puede archivar y no genera fila de registro (ver `plantilla/README.md`). Al entregarla hay
que decir explícitamente que es para validar el alcance, **no** para aprobar.

## Paso 5 — Vista previa y aprobación

Mostrar el **PNG** (no el PDF: se ve al instante, sin abrir nada) y esperar. Tres respuestas
posibles:

- **Aprobado** → volver a correr el generador con **`--final`**. En un solo comando: exige el
  N° real y ningún precio pendiente, deja el PDF con su nombre de entrega ("N° 9196-2026
  CARRETILLAS TT PUCALLPA MUNAY.pdf") y archiva imagen + JSON en `cotizaciones-emitidas/`.
  Entregar ese PDF y pasar al paso 6. Antes de este modo, archivar dependía de acordarse de un
  parámetro, y de 3 cotizaciones finales reales no se archivó ninguna.
- **Corregir** → aplicar el cambio, regenerar, volver a mostrar. Sin límite de vueltas.
- **Rechazado** → no se genera PDF.

**El PDF se entrega, no se envía.** Nunca mandar un correo ni ofrecer hacerlo: el envío al
cliente lo hace una persona desde Gmail. La cotización queda en estado "lista para enviar".

## Paso 6 — Fila para el registro de costos

Al aprobar, entregar los datos listos para pegar en el Google Sheet. El generador imprime dos
líneas:

- Columnas A a K: `N° Cotización | Fecha | Cliente | Local | Tipo | Subtipo | Descripción breve | Unidades (equipos) | Subtotal | IGV | Total`
- Columnas del final (Z a AB): `Costo estimado | Subtotal calculado | Nota interna`. Se llenan
  en **todas** las cotizaciones, se ganen o se pierdan: sin eso no se mide cuánto se ajusta el
  precio por experiencia ni a qué markup se pierde. Si la cotización salió de una ficha, el
  motor ya las trae calculadas.

El registro se reconstruye con `herramientas/armar_registro.py` si se pierde el archivo (ya
pasó una vez). El archivo `.xlsx` no se versiona — es dato operativo; el script sí.

Recordar que **personas y amanecidas se llenan después**, cuando el trabajo termine — son los
datos con los que se va a deducir la fórmula de precio al cierre del mes de prueba.

## Paso 7 — Casuística

Si apareció algo que las reglas no cubrían (un servicio raro, un título que no entra en una
línea, más de 3 fotos, un repuesto sin precio), anotarlo en `casuistica.md` con la plantilla
que está ahí. No inventar una regla nueva sobre la marcha: registrar el caso y seguir.

## Precios: lo que nunca se hace

- No aplicar un margen automático. El markup (60–80% sobre el costo) se propone, se confirma,
  y el precio final suele redondearse a un número comercial. Ojo: markup no es margen — un
  markup de 73% es un margen de 42% sobre la venta.
- No inventar un precio que no esté en `catalogo.md`.
- Antes de subir un cambio al sistema (generador, motor, fichas): `python3
  herramientas/probar.py`. Reproduce las cotizaciones reales ya emitidas.
- No cambiar las coordenadas de la cápsula ni del título en `plantilla/cotizacion.html` sin
  recalibrarlas contra `plantilla/headers/base.jpg` (ver `plantilla/README.md`).
