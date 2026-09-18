# Análisis: proveedor Gufra Perú (chat de WhatsApp + 15 documentos PDF reales)

Fuente: conversación completa Feb–Jul 2026 entre LF Munay Perú y Gufra Perú (distribuidor de
celdas, cajas sumadoras, indicadores y plataformas), más 15 documentos que el proveedor mandó
por WhatsApp y ahora están en `proveedor-gufra/`: 12 proformas, 1 **factura real pagada**
(F001-72), 1 guía de remisión (T001-79) y fichas técnicas. A diferencia de las 4 cotizaciones de
`cotizaciones-reales/` (que muestran el **precio de venta al cliente**, empaquetado), esto
muestra el **costo de compra por componente individual** — el dato que faltaba para separar
margen de material y margen de mano de obra.

**Vigencia de los precios**: el proveedor avisó el 17/04/2026 que "nuestros precios se han
actualizado". Varios precios de este análisis SÍ cambiaron entre marzo y junio (ver la tabla de
KELI SQB-A y la caja G08-4-S) — no es un precio fijo. Confirmar vigente antes de usar en una
cotización nueva. Los números definitivos están en `catalogo.md`; esto es el detalle y el
porqué.

## El misterio del S/631.8 — resuelto con la factura real

La primera versión de este análisis (17/09/2026) marcó la cifra "S/631.8" de un kit Mavin NB2
como **"no usar sin confirmar"**, porque no cuadraba con una proforma que cotizaba el mismo kit
a US$180 (~S/212 al tipo de cambio que se asumió entonces). Con los 15 documentos subidos, la
duda se cierra:

- **Factura F001-72** (27/03/2026, pagada al 100% — no es una cotización, es lo que realmente se
  pagó) muestra el kit Mavin NB2 1T a **S/631.80**, la caja sumadora Mavin SS4 a **S/175.50**, y
  6 metros de cable a **S/36.00**. Total S/843.30 + IGV S/151.79 = **S/995.09**.
- La **proforma GP26-10** (03/03/2026, 24 días antes) había cotizado el mismo kit a **US$180** y
  la misma caja a **US$50**.
- **Los números cuadran**: S/631.80 ÷ US$180 = 3.51, y S/175.50 ÷ US$50 = 3.51 — el mismo tipo de
  cambio en los dos casos. La factura simplemente cobra en soles lo que la proforma cotizó en
  dólares, al tipo de cambio real del día de pago.

**Conclusión: S/631.80 es el costo de compra real y confirmado del kit Mavin NB2 1T — más
confiable que cualquier proforma, porque es dinero que ya se pagó.** La tabla de `catalogo.md`
ya quedó corregida con este número.

## Costo de compra por componente (de proformas y la factura real)

Ver la tabla completa y con fuentes en `catalogo.md`, sección "Repuestos — Balanzas". Resumen de
los hallazgos que no son obvios en una tabla:

- **El kit Mavin con patas sale más barato que comprar las celdas sueltas**: el kit completo (4
  celdas + patas + espaciadores) cuesta US$180, pero 4 celdas sueltas (sin patas) cuestan US$50
  c/u = US$200. Comprar el kit es la opción correcta salvo que ya se tengan patas de otro trabajo.
- **KELI SQB-A subió de precio**: US$339 (27/03/2026) → US$420 (11/06/2026), +24% en menos de 3
  meses. Coincide con el aviso del proveedor del 17/04.
- **KELI SQB-SS (acero inoxidable) cuesta igual en 1T y 2T**: US$456 en ambos casos — el precio
  no depende de la capacidad, solo del material.
- **La caja KELI también subió**: US$85 → US$95 entre marzo y junio.
- **La pesa patrón de 20kg incluye calibración y certificado INACAL** (S/236 con IGV); la de
  50kg es solo el suministro, sin calibración (S/578.20) — no son comparables directamente pese
  a que ambas dicen "Clase M2".

## Plataformas completas — nuevo, no estaba en el análisis anterior

Tres plataformas con precio real, celdas y caja ya incluidas:

- **Yaohua SCS1212-T7 / T7E** (300kg, 1.2×1.2m): US$693 cada una, con celdas KELI SQB-SS
  (inoxidable) y caja incluidas — la diferencia entre T7 y T7E es solo el indicador (LCD vs LED),
  mismo precio.
- **KELI SCS1515** (3T, 1.5×1.5m, profundidad 10cm): US$885, con celdas KELI SQB-A y caja KELI
  incluidas — **sin indicador**, hay que sumarlo aparte.

## Notas técnicas reales, útiles para el sustento técnico de una cotización

- **Mavin solo fabrica en acero niquelado** (no tiene versión inoxidable). KELI sí tiene ambas:
  **SQB-A** = acero niquelado, **SQB-SS** = acero inoxidable (misma patita, compatibles entre
  sí, la diferencia es solo el material, la resistencia a la corrosión, y el precio: SQB-SS
  cuesta más).
- **Las patitas de apoyo no son universales**: Mavin NB2 usa patita M16; Mavin NB3 usa M18. No
  son intercambiables entre modelos.
- **Riesgo real de incompatibilidad por rango de mV/V**: el indicador DIGI DI 620 (uno de los
  que Munay ha reemplazado) trabaja en rango 1–2 mV/V, pero las celdas Mavin y KELI estándar
  trabajan alrededor de 3 mV/V (las KELI SQB-SS específicamente: 2.0–3.0 mV/V, según su ficha
  técnica). Si se cambia SOLO la celda y se deja el indicador viejo, puede no calzar — hay que
  verificar el rango del indicador actual antes de cotizar el cambio de celdas solas.
- **Los indicadores T-Scale (BW/BWS) son multirrango**, de ±1 a ±3 mV/V — compatibles con
  cualquier celda Mavin, KELI o equivalente sin verificar antes. El **Handfree HC200** también es
  de gama industrial (acero inox IP67, soporta hasta 8 celdas de 350 ohms o 16 de 700 ohms) y es
  US$15 más barato que el T-Scale BW (US$255 vs US$259.60) — alternativa a considerar.
- **E-Accura es para balanzas comerciales; T-Scale y Handfree son para uso industrial** con más
  funciones — todas son buenas marcas, la elección depende del uso, no de calidad.
- **Soldar asas o refuerzos en la plataforma altera el pesaje** — la calibración ajusta la
  lectura pero no corrige un problema mecánico de reparto de peso. Toda modificación estructural
  necesita recalibración después.
- **En provincia no se puede verificar en campo la compatibilidad de celdas antes de comprar**
  (26/05/2026: *"como es provincia, no podemos medir eso"*) — para un trabajo fuera de Lima, hay
  que preguntar al cliente el modelo e indicador actual ANTES de cotizar el repuesto, porque no
  hay forma de confirmarlo en sitio antes de la compra.
- **Todas las celdas y cajas de este proveedor tienen certificación OIML Clase C3** e IP68
  (celdas) / IP65 (cajas) — dato útil para el sustento técnico si el cliente pregunta por
  certificaciones.

## Documentos ya subidos a `proveedor-gufra/` (15 archivos)

Todos revisados el 18/09/2026. Los que traen precio en texto plano (no solo en el PDF) ya están
en `catalogo.md`. Documentos de referencia técnica sin precio nuevo relevante: fichas técnicas de
Mavin NB2/NB2-1/SS4, KELI SQB, KELI G08-4-S, Yaohua T7E, guía de conexión de celdas, Rice Lake
920i (dos variantes), JADEVER JWP, Super SS — quedan como archivo de consulta si hace falta un
dato de instalación o especificación puntual, no se transcriben acá completos.

## Relación con la cotización pendiente (TT Santa Anita)

Sigue sin resolver: **Santa Anita es un distrito de Lima**, y el comentario "los precios
aumentan porque es en provincia" no tiene un caso equivalente exacto en este chat — el único
caso de provincia mencionado acá es una plataforma distinta, sin cerrar. Si el trabajo de Santa
Anita es realmente en Lima, la fórmula de mano de obra de `criterios-actuales.md` es la de Lima,
no la de provincia — falta confirmarlo antes de cotizar.

Con los datos de este análisis, la cotización de Santa Anita (Marvin + indicador T-Scale BW,
según lo ya conversado) ahora tiene costo de compra real y confirmado:
- Kit celdas Mavin NB2: S/631.80 (factura real)
- Caja sumadora Mavin SS4: S/175.50 (factura real)
- Indicador T-Scale BW: US$259.60 (~S/911 al tipo de cambio de la factura, a confirmar tipo de
  cambio vigente)
- **Total material estimado: ≈S/1,718**, antes de mano de obra, logística y margen.
