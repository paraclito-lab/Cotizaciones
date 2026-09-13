# Plantilla técnica del PDF/PNG de cotización

Decisión de arquitectura (14/09/2026) para que generar una cotización sea rápido y siempre
fiel a la marca real, sin depender de recrear el diseño a mano cada vez.

## El problema que esto resuelve

Intentar recrear el encabezado (logo, curvas decorativas, tipografías) con CSS desde cero
nunca calza exacto con el diseño real — se probó 3 veces (curvas gruesas inventadas, curvas
extraídas pálidas mal posicionadas, tipografía y jerarquía de títulos al revés) y cada versión
quedaba distinta al PDF real que ya usan. Recrear el diseño completo en HTML no es eficiente.

## La solución: imagen real de fondo + texto dinámico superpuesto

En vez de recrear el diseño, se usa **la imagen real del encabezado** (tomada directo de un
PDF ya entregado, en alta resolución) como fondo fijo, y se superpone **solo el campo que
cambia en esa zona** (el N° de cotización) como texto HTML real, en la posición exacta medida
sobre la imagen original.

- Todo lo que NO cambia por tipo de servicio (logo, "LF MUNAY PERÚ", RUC/dirección/cel/email,
  las curvas decorativas, "COTIZACIÓN DE SERVICIOS") queda perfecto porque es literalmente la
  imagen real, no una recreación.
- Lo único dinámico en el encabezado es el **N° de cotización**, superpuesto en HTML/CSS en
  la posición calibrada (ver abajo), así que sigue siendo texto real y editable.
- El nombre del servicio ("MANTENIMIENTO DE CARRETILLAS HIDRÁULICAS", "MANTENIMIENTO DE
  BALANZAS", etc.) no cambia cotización por cotización, cambia por **tipo de servicio** — por
  eso no hace falta que sea dinámico por cada cotización, alcanza con tener **una imagen de
  encabezado distinta por cada tipo de servicio**.

## Cómo agregar un tipo de servicio nuevo

1. Tomar un PDF real ya entregado de ese tipo de servicio (o pedir uno).
2. Renderizarlo en alta resolución: `pdftoppm -r 400 -png archivo.pdf pagina`
3. Recortar la franja del encabezado completo (logo + marca + títulos), sin el cuerpo de la
   tabla.
4. Ubicar el recuadro verde del N° de cotización (buscando el color de borde ~RGB(30,170,120))
   y "vaciarlo" pintándolo de blanco.
5. Guardar como `plantilla/headers/<tipo-servicio>.jpg`.
6. Usar las mismas coordenadas de la cápsula (son iguales en todos los formatos que comparten
   la plantilla base, ver abajo) para superponer el N° dinámico.

## Coordenadas calibradas de la cápsula del N° (formato base, ej. Moyobamba-100)

Como porcentaje del tamaño de la imagen del encabezado (para que escale a cualquier ancho):

- `left: 70.49%`
- `top: 32.14%`
- `width: 17.75%`
- `height: 25.41%`

Estilo del texto superpuesto: borde verde 2px (`#1f9e6e`), esquinas totalmente redondeadas,
fondo blanco, texto verde oscuro (`#17795f`) en negrita, centrado.

## Pendiente

- Preparar el header de **Balanzas** (falta un PDF real limpio de ese tipo de servicio).
- Preparar headers para **estructuras/motores/pintado** si van a usar el mismo formato base.
- Si algún día se consigue el archivo fuente editable (AI/Figma/PSD) del diseño, se puede
  reemplazar este método por una plantilla 100% vectorial — pero mientras no exista, este
  método es el más eficiente y fiel disponible.
