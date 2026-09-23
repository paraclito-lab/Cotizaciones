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
- **Título**: fuente serif (Georgia / Times New Roman), negrita, color verde oscuro
  (`#17795f`), centrado.

**Los dos tamaños de letra se miden en `cqw`, no en px** (`1.67cqw` el N°, `3.33cqw` el
título — equivalen a 15px y 30px sobre una hoja de 900px). Así escalan solos cuando el ancho
de la hoja cambia. Además, si un título no entra en una línea, el generador le baja el tamaño
hasta que entre (con un piso del 60% para que no quede ilegible) y lo avisa en las alertas.

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
   referencia de Moyobamba mide 841.8 × 595.2 pts, o sea A4 apaisado).

   **El ancho de la hoja no es fijo: se calcula.** Con un ancho fijo de 900px, el alto depende
   de cuánto texto tenga la cotización, así que su proporción casi nunca coincidía con la del
   A4 y quedaba una franja vacía a un costado (con 12 ítems llegaba a desperdiciar el 23% del
   ancho). El generador hace una búsqueda binaria del ancho cuya proporción calce con la de la
   página, y recién ahí calcula la escala. Probado con 4 y con 12 ítems: una sola página,
   centrada y llena en ambos casos.

   Por debajo de 0.55 de escala ya sería ilegible, así que en ese caso pasa a una segunda
   página en vez de seguir achicando.

   **La cotización queda centrada en la hoja**, no pegada a una esquina. El sobrante de
   espacio (a los costados si la tabla es larga y angosta, arriba/abajo si es corta) se
   reparte mitad y mitad como margen. Antes se intentaba forzar el ancho de la hoja para
   que su proporción calzara exacto con la del A4, pero con pocas filas eso topaba un
   ancho mínimo y dejaba media hoja en blanco abajo — se reemplazó por este centrado
   directo, más simple y sin ese caso raro.
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

## Propuesta técnica: `--sin-precios`

Hay trabajos donde **la especificación es la que manda el precio**, y cotizar antes de fijarla
es cotizar a ciegas (caso que lo originó el 22/09/2026: cambio de garruchas de coches de
panadería — la misma garrucha va de S/18 a S/140 según diámetro, montaje, material,
capacidad y temperatura de trabajo). Para esos casos:

```bash
python3 plantilla/generar.py cotizacion.json salida/ --sin-precios
```

Sale el documento con el alcance completo y los totales en **"Por definir"** en gris cursiva,
para que el cliente valide la especificación antes de costear.

Reglas que hace cumplir el generador, a propósito:

- **Todos** los ítems tienen que ser `pendiente`. Si alguno trae precio, no genera: un
  documento con filas con importe y un Total que dice "Por definir" se contradice solo.
- Nunca muestra "S/ 0.00" en los totales. **Un total en cero se lee como gratis** — ese es el
  riesgo real de emitir un documento sin precios, y es la razón de que el modo exista en vez
  de simplemente desactivar la validación de subtotal.
- **No se puede combinar con `--archivar`**: no se archiva como cotización emitida algo que
  todavía no tiene precio.
- **No imprime la fila del registro de costos**: entraría con monto 0 y ensuciaría el ticket
  promedio y el margen.

## Marco interno simétrico

El borde negro de `.sheet` tiene que quedar a la misma distancia del contenido arriba y abajo
— si no, el marco se ve descuadrado y el contenido parece no estar centrado verticalmente
(pasó el 20/09/2026: `.body-pad` tenía `padding: 4px 34px 30px 34px`, con 30px de aire muerto
abajo y casi nada arriba, notorio sobre todo en cotizaciones cortas o sin `nota`).

El encabezado (`base.jpg`) ya trae de fábrica ~14px de aire debajo del título antes de su
borde inferior, así que el padding superior de `.body-pad` puede quedar chico (4px) y aun así
verse balanceado. **Si se toca el padding inferior de `.body-pad`, hay que mantenerlo cerca de
ese mismo total (~18px)** para que el marco no vuelva a quedar irregular. Revisar siempre
regenerando una cotización corta (1 ítem, sin nota) Y una larga (6+ ítems, con nota): son los
dos extremos donde la asimetría se nota más.

## Fila separadora dentro de la tabla

Para dividir un mismo pedido en dos bloques sin partirlo en dos archivos (ej. piezas que
necesitan un rollo de ancho distinto, mismo precio unitario, pero hay que dejarlo claro),
un ítem puede ser un separador en vez de una fila normal:

```json
{"separador": true, "texto": "Piezas con lado menor mayor a 1.50 m — requieren rollo especial"}
```

Sale como una fila que ocupa las 5 columnas, con fondo verde claro y el texto en
mayúsculas — no se numera, no cuenta para el subtotal, no lleva precio. Los ítems de
antes y después sí se numeran de corrido (ver `herramientas/ejemplo-trabajo.json`, que
tiene la estructura real de Atocongo con 16 ítems y un separador en la fila 13).

## Pendiente

- Si algún día se consigue el archivo fuente editable (AI/Figma/PSD) del diseño, se puede
  reemplazar este método por una plantilla 100% vectorial — pero mientras no exista, este
  método es el más eficiente y fiel disponible.
- Definir qué pasa si llegan más de 3 fotos para un mismo ítem.
