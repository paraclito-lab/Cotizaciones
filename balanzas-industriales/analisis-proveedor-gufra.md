# Análisis: chat de WhatsApp con Gufra Perú (proveedor de componentes de balanza)

Fuente: conversación completa Feb–Jul 2026 entre LF Munay Perú y Gufra Perú (distribuidor de
celdas, cajas sumadoras, indicadores y plataformas). A diferencia de las 4 cotizaciones de
`cotizaciones-reales/` (que muestran el **precio de venta al cliente**, empaquetado), este chat
muestra el **costo de compra por componente individual** — es el dato que faltaba para poder
separar margen de material y margen de mano de obra.

**Vigencia de los precios**: el proveedor avisó el 17/04/2026 que "nuestros precios se han
actualizado" — los precios de este chat son de ese momento (feb–jul 2026), no un precio fijo.
Confirmar vigente antes de usar en una cotización nueva.

## Costo de compra por componente (confirmado en texto del chat)

| Componente | Marca / modelo | Detalle | Costo | Fecha | Confianza |
|---|---|---|---|---|---|
| Kit de celdas (4 unid. + 4 patas + 4 espaciadores) | Mavin NB2, 1T **o** 2T (mismo precio) | Acero niquelado | US$180 + IGV = **S/212.40** | 16/04/2026 (consistente con lo dicho el 03/03/2026) | Alta — repetido dos veces, mismo número |
| Caja sumadora, hasta 4 celdas | Mavin SS4 | Acero inoxidable | US$50 + IGV = **S/59.00** | 16/04/2026 | Alta |
| Kit de celdas (4 unid.) | KELI SQB "original" | Acero (no se aclaró si A o SS) | **US$520** (IGV no aclarado en el texto) | 03/03/2026 | Media — casi 3x el precio de Mavin, sin confirmar si incluye patas/espaciadores como el kit Mavin |
| Indicador de peso, uso comercial, sin impresión | E-Accura SB51 | Triple display LCD, teclado alfanumérico | US$215 + IGV ≈ **S/887.95** | 09/04/2026 | Alta |
| Indicador de peso, uso industrial | T-Scale BW | Carcasa plástico ABS | US$220 + IGV = **US$259.60** | 16/04/2026 | Alta (dato en dólares, no convertido a soles en el chat) |
| Indicador de peso, uso industrial | T-Scale BWS | Carcasa acero inoxidable | US$290 + IGV = **US$342.20** | 16/04/2026 | Alta (dato en dólares) |
| Base móvil para indicador T-Scale | — | Reemplazo de la base/perno de sujeción al tubo | **US$39** (IGV no aclarado) | 23/06/2026 | Media |
| Indicador de peso programable, montaje pared | Rice Lake 920i Panel Mount | Gama alta, tipo Mettler | US$3,750 + IGV | 26/05/2026 | Alta — **descartado por el cliente**: "muy caro, por ahora inviable" |

**Dato sin resolver, no usar sin confirmar**: el 16/04/2026 Andrés menciona *"KIT DE PESAJE: 4
CELDAS DE CARGA MAVIN NB2 1T, 4 PATAS DE APOYO, 4 ESPACIADORES S/ 631.8"* como referencia de una
compra anterior, en la misma conversación donde Gufra cotiza el mismo kit a S/212.40. Los dos
números no cuadran (S/631.8 es 3x más) y no hay forma de saber, solo con el texto, si S/631.8
incluía algo más (cableado, caja sumadora, instalación) o es un precio de otra fecha con otro
tipo de cambio. **No usar S/631.8 como costo de celdas sin confirmar qué incluía.**

## Lo que se pidió pero no tiene precio en texto (quedó solo en PDF adjunto)

Estos productos se cotizaron, pero el precio final está dentro de un PDF que el chat solo
referencia por nombre de archivo — no se puede leer desde el `.txt` de la conversación:

- Plataforma Yaohua T7 300kg (`102600150 LF MUNAY.pdf`, 21/02/2026)
- Plataforma Keli SCS acero al carbono 1.50×1.50m (`Plataforma Keli SCS...pdf`, 03/03/2026)
- Kit celdas + caja sumadora Keli Sensor 4 canales (`GP26-10 LF MUNAY.pdf`, 03/03/2026 — este es
  el que corresponde al trabajo de Tarapoto/Moyobamba, cotizaciones 6112/7171)
- Caja sumadora Keli Sensor G08-4-S rectangular (`KELI SENSOR G08-4-S...pdf`, 09/04/2026)
- Kit celdas SQB-A/SQB-SS actualizado, 1T y 2T (`102000237`, `102000238`, 05/05/2026)
- Plataforma SCS-1515 completa con celdas y caja Keli (`102600426 LF MUNAY.pdf`, 26/05/2026) —
  profundidad de plataforma: **10cm** (dato sí quedó en texto, útil si se instala en foso)
- Pesa patrón M2 de 50kg (`102000250 MUNAY.pdf`, 11/04/2026)
- Kit con cableado 6 hilos × 8m (`102600507 LF MUNAY.pdf`, 11/06/2026)

Si se necesita el precio de alguno de estos, hay que abrir el PDF puntual — no está en este
análisis.

## Notas técnicas reales, útiles para el sustento técnico de una cotización

- **Mavin solo fabrica en acero niquelado** (no tiene versión inoxidable). KELI sí tiene ambas:
  **SQB-A** = acero niquelado, **SQB-SS** = acero inoxidable (misma patita, compatibles entre
  sí, la diferencia es solo el material y la resistencia a la corrosión).
- **Las patitas de apoyo no son universales**: Mavin NB2 usa patita M16; Mavin NB3 usa M18. No
  son intercambiables entre modelos.
- **Riesgo real de incompatibilidad por rango de mV/V**: el indicador DIGI DI 620 (uno de los
  que Munay ha reemplazado) trabaja en rango 1–2 mV/V, pero las celdas Mavin y KELI estándar
  trabajan alrededor de 3 mV/V. Si se cambia SOLO la celda y se deja el indicador viejo, puede no
  calzar — hay que verificar el rango del indicador actual antes de cotizar el cambio de celdas
  solas.
- **Los indicadores T-Scale (BW/BWS) son multirrango**, de ±1 a ±3 mV/V — compatibles con
  cualquier celda Mavin, KELI o equivalente sin verificar antes. Es la opción segura cuando se
  reemplaza indicador Y celdas juntos.
- **E-Accura es para balanzas comerciales; T-Scale es para uso industrial** con más funciones —
  ambas son buenas marcas, la elección depende del uso, no de calidad.
- **Soldar asas o refuerzos en la plataforma altera el pesaje** — la calibración ajusta la
  lectura pero no corrige un problema mecánico de reparto de peso. Toda modificación estructural
  necesita recalibración después.
- **En provincia no se puede verificar en campo la compatibilidad de celdas antes de comprar**
  (26/05/2026: *"como es provincia, no podemos medir eso"*) — para un trabajo fuera de Lima, hay
  que preguntar al cliente el modelo e indicador actual ANTES de cotizar el repuesto, porque no
  hay forma de confirmarlo en sitio antes de la compra.

## Relación con la cotización pendiente (TT Santa Anita)

El comentario "los precios aumentan porque es en provincia" de la conversación de cotización no
tiene un caso equivalente exacto en este chat con Gufra — el único caso de provincia mencionado
acá es una plataforma distinta, sin cerrar. **Santa Anita es un distrito de Lima**, así que la
contradicción señalada sigue sin resolver: si el trabajo de Santa Anita es realmente en Lima, la
fórmula de mano de obra de `criterios-actuales.md` es la de Lima, no la de provincia — falta
confirmarlo.
