# Catálogo de precios — fuente única de verdad

Reemplaza toda referencia anterior a `Sistema_Cotizaciones_MunayPeru.xlsx` (ese archivo era
del primer intento, en el repo `webmunay`, y **queda descontinuado** — ver nota al final).
Esta tabla es el único lugar donde se busca el precio de un repuesto. No se repite en ningún
otro documento; los demás archivos deben enlazar aquí, no copiar valores.

**Estado**: `Confirmado` = validado explícitamente en esta conversación. `Por validar` = viene
de una sola cotización real (Moyobamba u otra) pero nadie lo ha confirmado a propósito
todavía — úsese con precaución hasta confirmar.

## Repuestos (precio fijo, no cambia por localidad — ver criterios-actuales.md punto 1)

| Repuesto | Precio (S/) | Estado | Fuente |
|---|---|---|---|
| Rueda de carga | 40.00 | **Confirmado** (14/09/2026) | Corrige el S/65 de Moyobamba |
| Resorte de retorno de brazo | 55.00 | **Confirmado** (14/09/2026) | Coincide con Moyobamba |
| Rueda direccional / rueda giratoria o delantera (mismo ítem, nombre unificado) | 95.00 | Por validar | Moyobamba y Porongoche coinciden en el precio |
| Protector soporte de pistón | 29.00 | Por validar | Moyobamba |
| Trapecio y ejes de rueda de carga | 300.00 | Por validar | Moyobamba |
| Eje de brazo | 55.00 | Por validar | Moyobamba |
| Suministro y regulación de cadena y varilla de retorno | 190.00 | Por validar | Moyobamba |
| Brazo (suministro) | 320.00 | Por validar | Moyobamba |
| Enderezado de chasis y reforzamiento con soldadura | 100.00 | Por validar | Moyobamba |
| Desarmado y engrase total de chasis (por unidad) | 10.00 | Por validar | Moyobamba |
| Alineamiento de barra de tiro | 50.00 | Por validar | Moyobamba |

## Mano de obra — NO es un precio de catálogo fijo

El "mantenimiento de carretilla" no tiene un precio único: se calcula con la fórmula de
`criterios-actuales.md` punto 2 (personas × tarifa × 2 por amanecida ÷ cantidad de unidades),
con un **piso mínimo de S/250 por unidad** (punto 4). No poner un número fijo aquí para evitar
que alguien lo copie como si fuera un precio de catálogo.

## Pendiente

- Confirmar (o corregir, como se hizo con la rueda de carga) cada precio marcado "Por validar".
- Agregar precios de repuestos de balanzas, estructuras y motores cuando haya cotizaciones
  reales de esos tipos de servicio.

## Nota sobre el Excel anterior

`Sistema_Cotizaciones_MunayPeru.xlsx` (construido en el repo `webmunay`, antes de crear este
repo `cotizaciones`) tenía un catálogo de 38 ítems y una plantilla con fórmulas. Ese archivo
**no se trajo a este repo** y ya no es la fuente de verdad — quedó reemplazado por este
`catalogo.md` (para precios) y por `plantilla/` (para el diseño del PDF/PNG). Si en algún
momento se retoma ese Excel, hay que revisar sus precios contra esta tabla antes de reusarlo,
porque varios ya se sabe que estaban desactualizados (ver `analisis/tarapoto-excel.md` y
`ejemplos-reales/2026-08-moyobamba.md`).
