# Catálogo de precios — fuente única de verdad

Reemplaza toda referencia anterior a `Sistema_Cotizaciones_MunayPeru.xlsx` (ese archivo era
del primer intento, en el repo `webmunay`, y **queda descontinuado** — ver nota al final).
Esta tabla es el único lugar donde se busca el precio de un repuesto. No se repite en ningún
otro documento; los demás archivos deben enlazar aquí, no copiar valores.

**Qué es la columna "Precio"**: es el **precio de venta al cliente** (lo que aparece en la
cotización), no el costo de compra. El costo de compra de cada repuesto todavía no está
registrado en ninguna parte — es una columna pendiente de agregar, y hasta que exista no se
puede saber el margen real repuesto por repuesto (solo el margen global del trabajo, vía el
registro de costos).

**Estado**: `Confirmado` = validado explícitamente. `Por validar` = viene de una sola
cotización real (Moyobamba u otra) pero nadie lo ha confirmado a propósito todavía — úsese con
precaución hasta confirmar.

## Repuestos — Carretillas (precio fijo, no cambia por localidad — ver criterios-actuales.md punto 1)

| Repuesto | Precio (S/) | Estado | Fuente |
|---|---|---|---|
| Rueda de carga | 40.00 | **Confirmado** (14/09/2026) | Precio de venta vigente. Corrige el S/65 que aparece en Moyobamba y Porongoche — ese S/65 fue un error o un ajuste de conveniencia puntual, no el precio real. **Ojo: en 9196-2026 (TT Pucallpa, 20/09) se cobró S/60** — sin decidir si el catálogo cambia (hallazgos-abiertos.md, Q2). |
| Resorte de retorno de brazo | 55.00 | **Confirmado** (14/09/2026) | Coincide con Moyobamba |
| Rueda direccional / rueda giratoria o delantera (mismo ítem, nombre unificado) | 80.00 | **Confirmado** (14/09/2026) | Precio de venta vigente. Corrige el S/95 de Moyobamba y Porongoche. **Ojo: en 9196-2026 (TT Pucallpa, 20/09) se cobró S/95** — sin decidir si el catálogo cambia (Q2). |
| Protector soporte de pistón / tapa protector de resorte | 29.00 | Por validar | Moyobamba. "Tapa (protector) de resorte" es el mismo repuesto: así se pidió en 9197-2026 y 10082-2026. |
| Trapecio y ejes de rueda de carga | 300.00 | Por validar | Moyobamba |
| Eje de brazo | 55.00 | Por validar | Moyobamba |
| Bocina de eje (por par) | 18.00 | Validado | Fijado el 08/10/2026. Antes: 10082-2026 (TT Calle 7) salió a S/15, Tarapoto S/15, Excel histórico S/30. |
| Suministro y regulación de cadena y varilla de retorno | 190.00 | Por validar | Moyobamba |
| Brazo (suministro) | 320.00 | Por validar | Moyobamba |
| Enderezado de chasis y reforzamiento con soldadura | 100.00 | Por validar | Moyobamba |
| Desarmado y engrase total de chasis (por unidad) | 10.00 | Por validar | Moyobamba |
| Alineamiento de barra de tiro | 50.00 | Por validar | Moyobamba |
| Reparación de botella hidráulica (kit de retenes + o-rings de cilindro) | 38.00 | **Confirmado** (20/09/2026) | Dado el 20/09 en la preparación de TT Pucallpa; **la cotización emitida (9196-2026) salió finalmente a S/50** — sin decidir cuál vale (Q2). |

## Repuestos — Balanzas

### Costo de compra por componente (proveedor Gufra Perú)

Fuente: 15 documentos reales del proveedor (proformas + 1 factura + 1 guía de remisión) en
`balanzas-industriales/proveedor-gufra/`, extraídos en
`balanzas-industriales/analisis-proveedor-gufra.md` (18/09/2026) — ahí está cada nota técnica
de compatibilidad. Estos son **costos de compra**, no precio de venta — hay que aplicarles
margen antes de cotizar. Varios precios subieron entre marzo y junio 2026 (el proveedor avisó
un ajuste el 17/04/2026) — se muestra la fecha de cada uno; usar el más reciente salvo que se
confirme vigencia.

**Corrección (18/09/2026): la cifra "S/631.8" SÍ es correcta** — la auditoría anterior la había
marcado como "no usar" por no cuadrar con una proforma en dólares. Ahora hay una **factura real
pagada** (F001-72, 27/03/2026) que la confirma: es el precio en soles al tipo de cambio que
aplicó el proveedor ese día (≈S/3.51 por US$1). Ver el detalle en el análisis completo.

| Componente | Marca / modelo | Costo de compra | Fecha | Fuente |
|---|---|---|---|---|
| Kit de celdas (4 unid. + patas + espaciadores), 1T o 2T | Mavin NB2 | **S/631.80** (real, factura pagada) | 27/03/2026 | Factura F001-72 |
| Caja sumadora, hasta 4 celdas, inox | Mavin SS4 | **S/175.50** (real, factura pagada) | 27/03/2026 | Factura F001-72 |
| Caja sumadora, hasta 4 celdas, inox | Mavin SS4 | US$50 (repetido en 3 proformas distintas, precio estable) | 03/03 a 17/04/2026 | GP26-10, 102000237, 102000269 |
| Celda de carga suelta (sin patas), 2T, x4 unid. | Mavin NB2 | US$50 c/u = US$200 por 4 — **más cara que el kit completo con patas** (US$180); comprar el kit sale mejor | 17/04/2026 | 102600269 |
| Kit de celdas (4 unid.), 1T | KELI SQB-A (acero niquelado) | US$339 → subió a **US$420** | 27/03 → 11/06/2026 | 102000147 → 102600507 |
| Kit de celdas (4 unid.), 1T o 2T (mismo precio) | KELI SQB-SS (acero inoxidable) | **US$456** | 05/05/2026 | 102000237, 102000238 |
| Caja sumadora, hasta 4 celdas, inox, rectangular | KELI G08-4-S / G03-4-S | US$85 → subió a **US$95** | 27/03 → 11/06/2026 | 102000147/102000238 → 102600507 |
| Cable apantallado 6 hilos, 24 AWG | Hurricane | US$2/m (proforma) — **S/6/m real** (factura, 6m = S/36) | 27/03 y 11/06/2026 | F001-72, 102600507 |
| Pie de apoyo suelto, inox | KELI SQB-SS | US$40/unidad | 11/06/2026 | 102600507 |
| Indicador, uso comercial, sin impresión | E-Accura SB51 | S/887.95 (US$215+IGV) | 09/04/2026 | chat (sin proforma PDF) |
| Indicador, uso industrial, carcasa plástico | T-Scale BW | US$259.60 (US$220+IGV) | 16/04/2026 | chat (sin proforma PDF) |
| Indicador, uso industrial, carcasa acero inox | T-Scale BWS | US$342.20 (US$290+IGV) | 16/04/2026 | chat (sin proforma PDF) |
| Indicador, uso industrial, acero inox IP67, numérico | Handfree HC200 | **US$255** | 26/05/2026 | 102600426 |
| Indicador programable, gama alta | Rice Lake 920i Panel Mount | US$3,750+IGV — **descartado, "muy caro, inviable"** | 26/05/2026 | chat |
| Base móvil para indicador T-Scale | — | US$39 | 23/06/2026 | chat (sin proforma PDF) |
| Pesa patrón Clase M2, 20kg, **con calibración y certificado INACAL** | — | S/236.00 (S/200+IGV) | 27/03/2026 | 10260090 |
| Pesa patrón Clase M2, 50kg, solo suministro (sin calibración) | — | S/578.20 (S/490+IGV) | 11/04/2026 | 102000250 |

### Plataformas completas (con celdas y caja incluidas)

| Plataforma | Capacidad / medida | Incluye | Costo de compra | Fecha |
|---|---|---|---|---|
| Yaohua SCS1212-T7E | 300kg, 1.2×1.2m | Celdas KELI SQB-SS inox + caja + indicador LED | US$693 | 21/02/2026 |
| Yaohua SCS1212-T7 | 300kg, 1.2×1.2m | Celdas KELI SQB-SS inox + caja + indicador LCD | US$693 | 21/02/2026 |
| KELI SCS1515 | 3T, 1.5×1.5m, profundidad 10cm | Celdas KELI SQB-A + caja KELI inox — **sin indicador** | US$885 | 26/05/2026 |

Un dato real útil para sustento técnico: la plataforma KELI SCS1515 tiene **10cm de
profundidad** — relevante si la instalación es en foso.

### Referencia de paquete completo (precio de venta, de cotizaciones reales)

Las 4 cotizaciones reales analizadas en `balanzas-industriales/casuistica-balanzas.md`
(18/09/2026) cotizan el mantenimiento como paquete, no por componente:

| Paquete (marca / alcance) | Precio de venta (S/) | Estado | Fuente |
|---|---|---|---|
| Marvin 1T — celdas + caja sumatoria, sin indicador | 5,785.00 | Por validar | N° 3032-2026 (Ica Panamericana — la única aprobada) |
| Marvin 1T — celdas (04) + caja sumatoria + cableado, sin indicador | 7,690.00 | Por validar | N° 8202-2026 (Tottus Olivos — rechazada) |
| KELI 1T — kit celdas + patas + caja sumatoria 4 canales + cable 6m, sin indicador | 8,520.00 | Por validar | N° 6112/7171-2026 (Tarapoto/Moyobamba — rechazadas) |
| Indicador de peso T-Scale BW | 1,350.00 | Por validar | N° 6112/7171-2026. Suministro aparte del paquete |

Comparando: el paquete de venta de Marvin sin indicador (S/5,785) contra el costo de compra de
celdas + caja Mavin (S/212.40 + S/59.00 = S/271.40) deja un margen amplio que incluye mano de
obra, cableado y ganancia — pero no se puede separar cuánto de eso es cada cosa sin el dato de
horas/personas de esa cotización puntual (ver punto 2 de `criterios-actuales.md`).

## Lámina de seguridad — rollos (costo de compra)

La lámina se compra por rollo, no por m² (casuistica.md, 16/09/2026): el costo depende de cómo
encajan las piezas en el ancho del rollo. `herramientas/cotizar_laminado.py` lee esta tabla
para repartir el precio total entre las piezas, como se hizo en COT-2026-001.

| Ancho (m) | Largo (m) | Precio del rollo | Precio por metro | Se compra en | Estado | Fuente |
|---|---|---|---|---|---|---|
| 1.52 | 30 | 300.00 | | rollo completo | Por validar | Dato dado el 17/09/2026 (COT-2026-001) |
| 1.82 | 30 | 900.00 | 40.00 | tramos de 10 m | Por validar | Dato dado el 17/09/2026: rollo a S/900; se compraron 10 m por S/400 |

Las piezas cuyo lado menor (más 2 cm de sangría por lado) pasa de 1.52 m van al rollo de
1.82 m; si tampoco entran ahí, necesitan empalme y se cotizan aparte.

## Mano de obra — NO es un precio de catálogo fijo

El "mantenimiento de carretilla" no tiene un precio único: se calcula con la fórmula de
`criterios-actuales.md` punto 2 (personas × tarifa × 2 por amanecida ÷ cantidad de unidades),
con un **piso mínimo de S/250 por unidad** (punto 4). No poner un número fijo aquí para evitar
que alguien lo copie como si fuera un precio de catálogo.

## Pendiente

- **Agregar columna de costo de compra** por repuesto. Hoy solo está el precio de venta, así
  que no se puede calcular el margen de cada repuesto por separado.
- Confirmar (o corregir, como se hizo con la rueda de carga y la direccional) cada precio
  marcado "Por validar". **De los 11 ítems, 9 siguen sin confirmar.**
- Agregar los ítems que aparecen en cotizaciones reales y no están en esta tabla: **eje
  central (S/70)** y **soldadura de barra de tiro (S/100)**; y decidir si "soldadura de barra
  de tiro" (S/100) y "alineamiento de barra de tiro" (S/50) son dos trabajos distintos.
- Agregar precios de repuestos de **balanzas** por componente individual (celda de carga,
  caja sumatoria, indicador) — hoy solo hay precios de paquete completo, ver arriba.
- Agregar precios de repuestos de estructuras y motores cuando haya cotizaciones reales de
  esos tipos de servicio.

## Nota sobre el Excel anterior

`Sistema_Cotizaciones_MunayPeru.xlsx` (construido en el repo `webmunay`, antes de crear este
repo `cotizaciones`) tenía un catálogo de 38 ítems y una plantilla con fórmulas. Ese archivo
**no se trajo a este repo** y ya no es la fuente de verdad — quedó reemplazado por este
`catalogo.md` (para precios) y por `plantilla/` (para el diseño del PDF/PNG). Si en algún
momento se retoma ese Excel, hay que revisar sus precios contra esta tabla antes de reusarlo,
porque varios ya se sabe que estaban desactualizados (ver `analisis/tarapoto-excel.md` y
`ejemplos-reales/2026-08-moyobamba.md`).
