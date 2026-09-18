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
| Rueda de carga | 40.00 | **Confirmado** (14/09/2026) | Precio de venta vigente. Corrige el S/65 que aparece en Moyobamba y Porongoche — ese S/65 fue un error o un ajuste de conveniencia puntual, no el precio real. |
| Resorte de retorno de brazo | 55.00 | **Confirmado** (14/09/2026) | Coincide con Moyobamba |
| Rueda direccional / rueda giratoria o delantera (mismo ítem, nombre unificado) | 80.00 | **Confirmado** (14/09/2026) | Precio de venta vigente. Corrige el S/95 de Moyobamba y Porongoche. |
| Protector soporte de pistón | 29.00 | Por validar | Moyobamba |
| Trapecio y ejes de rueda de carga | 300.00 | Por validar | Moyobamba |
| Eje de brazo | 55.00 | Por validar | Moyobamba |
| Suministro y regulación de cadena y varilla de retorno | 190.00 | Por validar | Moyobamba |
| Brazo (suministro) | 320.00 | Por validar | Moyobamba |
| Enderezado de chasis y reforzamiento con soldadura | 100.00 | Por validar | Moyobamba |
| Desarmado y engrase total de chasis (por unidad) | 10.00 | Por validar | Moyobamba |
| Alineamiento de barra de tiro | 50.00 | Por validar | Moyobamba |

## Repuestos — Balanzas

### Costo de compra por componente (proveedor Gufra Perú)

Del chat con el proveedor, ver el análisis completo en
`balanzas-industriales/analisis-proveedor-gufra.md` (18/09/2026) — ahí está cada nota técnica de
compatibilidad y las fuentes. Estos son **costos de compra**, no precio de venta — hay que
aplicarles margen antes de cotizar. Precios vigentes a abril–junio 2026; el proveedor ya avisó
un ajuste el 17/04/2026, confirmar antes de usar en una cotización nueva.

| Componente | Marca / modelo | Costo de compra | Estado | Fecha |
|---|---|---|---|---|
| Kit de celdas (4 unid. + patas + espaciadores) | Mavin NB2, 1T o 2T | S/212.40 (US$180+IGV) | Por validar | 16/04/2026 |
| Caja sumadora, hasta 4 celdas, inox | Mavin SS4 | S/59.00 (US$50+IGV) | Por validar | 16/04/2026 |
| Kit de celdas (4 unid.), acero | KELI SQB "original" | US$520 | Por validar — no aclara si incluye patas/espaciadores como el kit Mavin | 03/03/2026 |
| Indicador de peso, comercial, sin impresión | E-Accura SB51 | S/887.95 (US$215+IGV) | Por validar | 09/04/2026 |
| Indicador de peso, industrial, plástico ABS | T-Scale BW | US$259.60 (US$220+IGV) | Por validar | 16/04/2026 |
| Indicador de peso, industrial, acero inoxidable | T-Scale BWS | US$342.20 (US$290+IGV) | Por validar | 16/04/2026 |
| Base móvil para indicador T-Scale | — | US$39 | Por validar | 23/06/2026 |

**No usar** la cifra "S/631.8" que aparece una vez en el chat para un kit Mavin NB2 — no cuadra
con el resto de precios del mismo kit y no está claro qué incluía (ver el análisis completo).

### Referencia de paquete completo (precio de venta, de cotizaciones reales)

Las 4 cotizaciones reales analizadas en `balanzas-industriales/casuistica-balanzas.md`
(18/09/2026) cotizan el mantenimiento como paquete, no por componente:

| Paquete (marca / alcance) | Precio de venta (S/) | Estado | Fuente |
|---|---|---|---|
| Marvin 1T — celdas + caja sumatoria, sin indicador | 5,785.00 | Por validar | N° 3032-2026 (Ica Panamericana — la única aprobada) |
| Marvin 1T — celdas (04) + caja sumatoria + cableado, sin indicador | 7,690.00 | Por validar | N° 8202-2026 (Tottus Olivos — rechazada) |
| KELI 1T — kit celdas + patas + caja sumatoria 4 canales + cable 6m, sin indicador | 8,520.00 | Por validar | N° 6112/7171-2026 (Tarapoto/Moyobamba — rechazadas) |
| Indicador de peso T-Scale BW (suministro, aparte) | 1,350.00 | Por validar | N° 6112/7171-2026 |

Comparando: el paquete de venta de Marvin sin indicador (S/5,785) contra el costo de compra de
celdas + caja Mavin (S/212.40 + S/59.00 = S/271.40) deja un margen amplio que incluye mano de
obra, cableado y ganancia — pero no se puede separar cuánto de eso es cada cosa sin el dato de
horas/personas de esa cotización puntual (ver punto 2 de `criterios-actuales.md`).

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
