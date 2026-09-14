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

## Antes de generar: leer siempre

1. `criterios-actuales.md` — las reglas vigentes. **Puede haber cambiado desde la última vez.**
2. `catalogo.md` — la ÚNICA fuente de precios. Si un repuesto no está ahí, no inventar el
   precio: preguntar. Los precios marcados "Por validar" se usan, pero se avisa que no están
   confirmados.

## Paso 1 — Identificar el tipo de servicio

Solo existen tres. **El tipo elige el título Y el contenido a la vez** — nunca se llenan por
separado (regla de coherencia, `criterios-actuales.md` punto 8):

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

> "Entendí: 5 carretillas en Tottus San Miguel, atención Carlos Ramos, 10 ruedas de carga
> (S/40 c/u) y 4 direccionales (S/80 c/u). Mantenimiento a S/650 por unidad. ¿Correcto?"

Preguntar en lenguaje natural solo lo que realmente falte (cliente, local, atención, cantidad,
precio). No pedir todo de golpe como un formulario.

**El precio que se indica es siempre el subtotal, SIN IGV.** No preguntarlo cada vez: el IGV
del 18% y el total se calculan encima.

## Paso 3 — Numeración

Formato `COT-AAAA-NNN`, correlativo anual. Para saber el siguiente número, preguntar cuál fue
el último usado (vive en el registro de costos, columna A). Si no se sabe, preguntar — **nunca
inventar un número**, porque un correlativo duplicado rompe la trazabilidad.

## Paso 4 — Generar

Armar un JSON y correr el generador:

```bash
PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 plantilla/generar.py cotizacion.json salida/
```

Formato del JSON:

```json
{
  "numero": "COT-2026-001",
  "tipo": "carretillas",
  "cliente": "Hipermercados Tottus S.A",
  "local": "San Miguel",
  "atencion": "Carlos Ramos",
  "fecha": "15 de septiembre de 2026",
  "items": [
    {"cant": 5, "descripcion": "Reparación y mantenimiento de 05 carretillas hidráulicas (cambio de pasadores, orings, retenes de elevación, pines de expansión, retenes de bomba, anillos de jebe, aceite hidráulico)", "precio_unit": 650.00},
    {"cant": 10, "descripcion": "Suministro de rueda de carga", "precio_unit": 40.00}
  ],
  "nota": "Opcional. Ej: El servicio se realiza en dos grupos de 10 bandejas (6 días por grupo)."
}
```

- `fotos`: lista de rutas de imagen dentro de un ítem (máximo 3, opcional, solo Servicios
  Generales). Se achican y encuadran solas; **no se rechaza una foto por borrosa u oscura**.
- `tipo` es obligatorio y **reemplaza al título**: el generador se niega a correr si el JSON
  trae un `titulo` escrito a mano.
- `resumen` (opcional): la descripción corta que va al registro de costos.
- El subtotal, el IGV y el total los calcula el script. No escribirlos a mano.
- La fecha va en texto largo en español ("15 de septiembre de 2026").

El script imprime los totales, las rutas del PNG y del PDF, **la fila ya armada para pegar en
el registro de costos**, y una lista de **alertas** (ítems en
S/0, N° con formato incorrecto, más de 3 fotos). Si hay alertas, resolverlas antes de mostrar
nada.

## Paso 5 — Vista previa y aprobación

Mostrar el **PNG** (no el PDF: se ve al instante, sin abrir nada) y esperar. Tres respuestas
posibles:

- **Aprobado** → entregar el PDF y pasar al paso 6.
- **Corregir** → aplicar el cambio, regenerar, volver a mostrar. Sin límite de vueltas.
- **Rechazado** → no se genera PDF.

**El PDF se entrega, no se envía.** Nunca mandar un correo ni ofrecer hacerlo: el envío al
cliente lo hace una persona desde Gmail. La cotización queda en estado "lista para enviar".

## Paso 6 — Fila para el registro de costos

Al aprobar, entregar los datos listos para pegar en el Google Sheet, en este orden:

`N° Cotización | Fecha cotización | Cliente | Local | Tipo de servicio | Descripción breve | Cant. unidades | Subtotal | IGV | Total`

Recordar que **personas y amanecidas se llenan después**, cuando el trabajo termine — son los
datos con los que se va a deducir la fórmula de precio al cierre del mes de prueba.

## Paso 7 — Casuística

Si apareció algo que las reglas no cubrían (un servicio raro, un título que no entra en una
línea, más de 3 fotos, un repuesto sin precio), anotarlo en `casuistica.md` con la plantilla
que está ahí. No inventar una regla nueva sobre la marcha: registrar el caso y seguir.

## Precios: lo que nunca se hace

- No aplicar un margen automático. El margen (60–80%) se propone, se confirma, y el precio
  final suele redondearse a un número comercial.
- No inventar un precio que no esté en `catalogo.md`.
- No cambiar las coordenadas de la cápsula ni del título en `plantilla/cotizacion.html` sin
  recalibrarlas contra `plantilla/headers/base.jpg` (ver `plantilla/README.md`).
