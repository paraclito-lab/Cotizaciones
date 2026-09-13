# Plantilla técnica del PDF/PNG de cotización

Decisión de arquitectura (14/09/2026, revisada el mismo día) para que generar una cotización
sea rápido y siempre fiel a la marca real, sin depender de recrear el diseño a mano cada vez.

## El problema que esto resuelve

Intentar recrear el encabezado (logo, curvas decorativas, tipografías) con CSS desde cero
nunca calza exacto con el diseño real — se probó 3 veces (curvas gruesas inventadas, curvas
extraídas pálidas mal posicionadas, tipografía y jerarquía de títulos al revés) y cada versión
quedaba distinta al PDF real que ya usan. Recrear el diseño completo en HTML no es eficiente.

## La solución: una sola imagen base + todo lo variable como texto real superpuesto

Se usa **una única imagen real del encabezado** (`plantilla/headers/base.jpg`, tomada directo
de un PDF ya entregado, en alta resolución) con las dos zonas que cambian **vaciadas y
pintadas de blanco**, y encima se superponen como texto HTML real:

- El **N° de cotización** (cambia en cada cotización).
- El **título del servicio** ("MANTENIMIENTO DE CARRETILLAS HIDRÁULICAS", "MANTENIMIENTO DE
  BALANZAS", etc. — cambia según el tipo de trabajo).

Todo lo que nunca cambia (logo, "LF MUNAY PERÚ", RUC/dirección/cel/email, las curvas
decorativas, "COTIZACIÓN DE SERVICIOS") queda perfecto porque es literalmente la imagen real,
no una recreación.

**Por qué el título también quedó dinámico y no como una imagen por tipo de servicio**: la
primera versión guardaba una imagen distinta por cada tipo de servicio (con el título ya
"horneado" en la imagen). Funcionaba, pero cualquier ajuste de texto — corregir una palabra,
agregar un tipo de servicio nuevo — obligaba a rehacer todo el proceso de recorte otra vez.
Con el título como texto real, cambiarlo es editar una línea; **una sola imagen base sirve
para cualquier servicio**.

## Coordenadas calibradas (sobre `plantilla/headers/base.jpg`)

Como porcentaje del tamaño de la imagen (para que escale a cualquier ancho):

| Campo | left | top | width | height |
|---|---|---|---|---|
| N° de cotización (cápsula) | 70.49% | 32.14% | 17.75% | 25.41% |
| Título del servicio | 11.85% | 79.18% | 73.06% | 13.27% |

Estilos:
- **N°**: borde verde 2px (`#1f9e6e`), esquinas totalmente redondeadas, fondo blanco, texto
  verde oscuro (`#17795f`) en negrita ~15px, centrado.
- **Título**: fuente serif (Georgia / Times New Roman), negrita, ~30px, color verde oscuro
  (`#17795f`), centrado. Si un título es más largo que "MANTENIMIENTO DE CARRETILLAS
  HIDRÁULICAS" puede necesitar reducir el tamaño de fuente para no desbordar — pendiente de
  resolver cuando aparezca un caso así (ver `casuistica.md`).

## Cómo se genera una cotización nueva (resumen técnico)

1. Cargar `plantilla/headers/base.jpg` como fondo.
2. Superponer el N° (`COT-AAAA-NNN`) y el título del servicio en las coordenadas de arriba.
3. Completar el resto de la plantilla (cliente, local, atención, fecha, tabla de ítems,
   totales) como HTML normal.
4. Renderizar a PNG (vista previa) o PDF (entregable final) desde el mismo HTML.

## Fila con foto (tipo "resto de servicios") — construida y probada

Para motores/estructuras/pintado (ver `criterios-actuales.md` punto 8), la fila de ítem lleva
la descripción + hasta 3 fotos + precio. Probado con las 3 fotos reales del PDF de Angamos
(cambio de motor).

- Contenedor `.photo-row` (flex, `gap: 6px`) debajo del texto de la descripción.
- Cada foto: `90x90px`, `object-fit: cover` (así se "encuadra" sin importar la proporción
  original de la foto del celular), borde gris 1px, esquinas levemente redondeadas.
- La foto es **opcional** — si no llega ninguna, la fila queda solo con texto.
- Si llegan más de 3 fotos: sin resolver todavía (ver `casuistica.md`).

## Pendiente

- Si algún día se consigue el archivo fuente editable (AI/Figma/PSD) del diseño, se puede
  reemplazar este método por una plantilla 100% vectorial — pero mientras no exista, este
  método es el más eficiente y fiel disponible.
- Definir qué pasa si el título de un servicio nuevo no cabe en una sola línea con el tamaño
  de fuente actual.
- Definir qué pasa si llegan más de 3 fotos para un mismo ítem.
