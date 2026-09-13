# Análisis: CCHH_COT-1.xlsx (Excel histórico de cotizaciones)

Archivo que Gera usaba antes de este sistema para cotizar. Analizado el 13/09/2026.

## Qué contenía

23 hojas dentro de un mismo libro, casi todas llamadas genéricamente "Hoja2 (N)" — cada una es
una cotización distinta hecha copiando la hoja anterior y sobrescribiendo los datos. Una hoja,
**"COTIZACION MOTOR"**, es distinta a las demás: además de la tabla de cotización al cliente,
tiene un desglose completo de costo real, ganancia y precio final — la única hoja del archivo
con ese nivel de detalle.

## Problemas encontrados

- **Sin catálogo único de precios**: cada hoja repite manualmente el precio de cada repuesto;
  no hay una tabla central, así que el mismo repuesto podía tener precios distintos en hojas
  distintas sin que fuera intencional (dificulta saber si es una decisión o un error de tipeo).
- **Formatos de celda mezclados**: algunas hojas tienen el precio como número (`250`), otras
  como texto (`" S/ 50,00 "`) — esto rompe cualquier fórmula o suma automática entre hojas.
- **Celdas con error `#REF!`**: dos hojas (burletes de exhibidoras, ruedas de coches de
  panadería) tenían referencias rotas en celdas sueltas, fuera del cálculo del total pero
  señal de fórmulas que se rompieron en algún momento y nadie corrigió.
- **Sin registro histórico consultable**: no había manera de sumar "cuánto se cotizó este año"
  o sacar un ticket promedio sin abrir las 23 hojas una por una.
- **Sin trazabilidad de costos**: excepto la hoja "COTIZACION MOTOR", ninguna otra registra el
  costo real de la empresa (repuestos, mano de obra, viáticos) — solo el precio final al
  cliente. No hay manera de saber si una cotización pasada ganó o perdió dinero.

## Qué se rescató

- **38 repuestos y servicios** con su precio, deduplicados y organizados por categoría →
  quedaron en `Sistema_Cotizaciones_MunayPeru.xlsx` (hoja Catálogo_Items). Nota: varios de
  estos precios luego se detectaron desactualizados frente a las cotizaciones reales de
  septiembre 2026 (ver `tarapoto-excel.md` y `ejemplos-reales/`) — el catálogo prioriza ahora
  la fuente más reciente (Moyobamba, ver `criterios-actuales.md` punto 1).
- **19 cotizaciones históricas** (fecha, resumen, subtotal, IGV, total) migradas a una sola
  tabla → hoja Histórico_Cotizaciones del mismo Excel. KPIs calculados: total facturado
  histórico S/70,275.84, ticket promedio S/3,698.73, 63% de los trabajos en exterior.
- **El modelo de costeo de "COTIZACION MOTOR"** (costo real → margen → precio final) se usó
  como base para diseñar la hoja Costos_Operativos y el análisis interno de margen de la
  Plantilla_Cotización.

## Decisión pendiente que generó

El precio de "mantenimiento de carretilla" variaba de S/50 a S/650 por unidad en este archivo
sin ningún criterio visible — esto fue lo que llevó a preguntarle a Gera por qué, y la
respuesta (mano de obra depende de localidad, no es un precio fijo) está documentada en
`criterios-actuales.md` punto 2.
