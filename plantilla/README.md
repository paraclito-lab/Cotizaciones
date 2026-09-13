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

## Archivos de esta carpeta

| Archivo | Qué es |
|---|---|
| `headers/base.jpg` | La imagen real del encabezado, con las dos zonas variables vaciadas. |
| `cotizacion.html` | La plantilla con marcadores `{{...}}`. **Acá se edita el diseño.** |
| `generar.py` | El generador: recibe un JSON y produce el PNG y el PDF. |

## Cómo se genera una cotización nueva

```bash
PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 plantilla/generar.py cotizacion.json salida/
```

El JSON lleva `numero`, `titulo`, `cliente`, `local`, `atencion`, `fecha`, la lista de `items`
(`cant`, `descripcion`, `precio_unit`, y `fotos` opcional) y una `nota` opcional. El script:

1. Incrusta `headers/base.jpg` y superpone el N° y el título en las coordenadas de arriba.
2. Arma la tabla, **calcula subtotal, IGV 18% y total** (nunca se escriben a mano).
3. Achica y encuadra las fotos a 90×90 (máximo 3 por ítem).
4. Renderiza **PNG** (vista previa, se ve al instante en el celular) y **PDF** desde el mismo
   HTML — así no pueden verse distintos.

   El PDF va en **A4 horizontal**, igual que las cotizaciones reales ya entregadas (el PDF de
   referencia de Moyobamba mide 841.8 × 595.2 pts, o sea A4 apaisado). La escala **se calcula
   sola** a partir del alto real del contenido: una cotización corta llena el ancho de la
   hoja, y una larga se achica lo justo para entrar en una sola página. Probado con 4 y con
   12 ítems: una página en ambos casos. Por debajo de 0.55 de escala ya sería ilegible, así
   que en ese caso pasa a una segunda página en vez de seguir achicando.
5. Imprime alertas de la validación automática (`criterios-actuales.md` punto 9, paso 2):
   ítems en S/0, N° que no cumple `COT-AAAA-NNN`, más de 3 fotos.

Todo esto está envuelto en la skill `cotizar` (ver `.claude/skills/cotizar/SKILL.md`), que es
la forma normal de usarlo: se describe el trabajo en lenguaje natural y ella se encarga del
resto.

## Fila con foto (tipo "Servicios Generales") — construida y probada

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
