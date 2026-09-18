# Borrador — cotización TT Santa Anita

Estado: **incompleto, no generar PDF todavía.** Faltan dos datos que no dependen del costeo:
si Santa Anita es Lima o provincia (cambia la fórmula de mano de obra) y el precio de la
plataforma metálica (pendiente por diseño, ver abajo). Este archivo es el borrador de trabajo,
no una cotización cerrada — no va en `cotizaciones-reales/` hasta que se apruebe.

## Estructura de costos — Ítem 1 (mantenimiento de celdas, caja e indicador)

Material: marca Mavin, caja sumatoria de acero (inoxidable, modelo SS4), indicador T-Scale BW.
Fuente de cada precio: `catalogo.md` sección Balanzas, con respaldo en factura real y proformas
de `proveedor-gufra/` (ver `analisis-proveedor-gufra.md`).

| Concepto | Costo | Fuente |
|---|---|---|
| Kit celdas Mavin NB2 (4 unid. + patas + espaciadores) | S/631.80 | Factura F001-72 (real, pagada) |
| Caja sumadora Mavin SS4 (acero inoxidable) | S/175.50 | Factura F001-72 (real, pagada) |
| Indicador T-Scale BW | ≈S/911.19 (US$259.60 × 3.51) | Proforma Gufra, 16/04/2026 — **confirmar tipo de cambio vigente antes de cerrar** |
| Cable apantallado 6 hilos | Según metraje real (ref. S/6/m, factura) | A medir en campo |
| **Material, subtotal estimado (sin cable)** | **≈S/1,718.49** | |
| Mano de obra | **Pendiente** | Depende de si Santa Anita es Lima o provincia (`criterios-actuales.md` punto 2) |
| Logística | Pendiente | Depende de lo anterior |
| Margen (60–80% de referencia) | Pendiente | Se aplica sobre costo total, no solo material |
| **Precio de venta, ítem 1** | **Pendiente** | |

### Sustento técnico propuesto — ítem 1

> SERVICIO: Mantenimiento de balanza plataforma, calibración, nivelación, alineamiento de
> plataforma, cambio de celdas de carga Marvin NB2, cambio de caja sumatoria Marvin modelo SS4
> (acero inoxidable), suministro e instalación de indicador de peso T-Scale BW.

Sigue el mismo patrón de redacción que las cotizaciones reales aprobadas/rechazadas (3032,
8202) — no se inventa un formato nuevo.

## Ítem 2 — nuevo, agregado a pedido (18/09/2026)

> Cambio de plataforma metálica a nivel de piso con sistema brazo cadena a nivel del piso.

| Concepto | Costo |
|---|---|
| Precio | **PENDIENTE** |

Este ítem es estructural (fabricación/cambio de la plataforma metálica y su sistema de
brazo-cadena empotrado a nivel de piso) — no es un componente electrónico de pesaje, así que no
tiene precio en los datos del proveedor Gufra (que cubre celdas, cajas e indicadores, no
fabricación de plataformas a medida). Necesita cotización aparte, probablemente con un
metalmecánico o directamente con Gufra si ofrece plataformas a medida — no está en el catálogo
de plataformas completas conocido (Yaohua, KELI SCS1515), que son plataformas estándar de
fábrica, no "a nivel de piso con sistema brazo-cadena" (eso suena a una instalación empotrada
específica del sitio, no un producto de catálogo).

## Pendientes para poder generar el PDF

1. **Lima o provincia** — Santa Anita es un distrito de Lima; sigue sin confirmarse si el
   comentario de "precios de provincia" aplicaba a este trabajo o a otro.
2. **Precio del ítem 2** (plataforma metálica) — pendiente por diseño/cotización aparte.
3. **Confirmar tipo de cambio vigente** para el indicador T-Scale BW (cotizado en dólares).
4. **Mano de obra y margen** — dependen del punto 1.
5. **Cliente, local, atención, fecha, N° de cotización** — correlativo `COT-AAAA-NNN`, sin
   inventar el siguiente número (ver `.claude/skills/cotizar/SKILL.md`, paso 3).
