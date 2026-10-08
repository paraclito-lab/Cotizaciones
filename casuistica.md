# Bitácora de casuística — cotizaciones

Registro de casos nuevos, excepciones y anomalías que aparecen con el uso real del sistema de
cotización. No se borra nada, solo se agrega. Sirve para decidir, en conjunto, si algo debe
convertirse en una regla nueva dentro de `criterios-actuales.md`.

## Plantilla para cada caso nuevo

```
### [Fecha] — [Título corto del caso]

- **Contexto**: ¿qué cotización o trabajo lo originó?
- **Qué pasó / qué no encajaba en las reglas actuales**:
- **Cómo se resolvió esta vez**:
- **¿Debería ser una regla permanente?** (sí / no / a evaluar)
```

## Casos registrados

### 14/09/2026 — Título de servicio no coincidía con el contenido

- **Contexto**: prueba de la plantilla para demostrar que el título del encabezado ahora es
  texto editable (ver `plantilla/README.md`). Se cambió el título de "MANTENIMIENTO DE
  CARRETILLAS HIDRÁULICAS" a "MANTENIMIENTO DE BALANZAS" para probar.
- **Qué pasó**: el título cambió, pero la tabla de "sustento técnico" se dejó igual (contenido
  de repuestos de carretillas), quedando una cotización incoherente — título de balanza con
  contenido de carretilla.
- **Cómo se resolvió esta vez**: se rehizo el ejemplo con contenido real de balanza (tomado de
  `analisis/tarapoto-excel.md`), y se documentó la regla en `criterios-actuales.md` punto 8.
- **¿Debería ser una regla permanente?** Sí — ya se agregó como regla de coherencia
  título↔contenido en `criterios-actuales.md`.

### 14/09/2026 — El PDF salía en vertical y quedaba con media hoja en blanco

- **Contexto**: primera prueba del generador (`plantilla/generar.py`) con una cotización de 4
  ítems.
- **Qué pasó**: el PNG se veía bien, pero el PDF salía en A4 vertical con el contenido apenas
  ocupando el tercio superior de la hoja. Se veía como un documento mal armado.
- **Cómo se resolvió esta vez**: se revisó el PDF real ya entregado (Moyobamba N°100) y resultó
  medir 841.8 × 595.2 pts, es decir **A4 horizontal** — el formato vertical nunca fue el de la
  empresa. Se cambió el generador a apaisado y se le agregó un cálculo de escala que mide el
  alto real del contenido para llenar la hoja sin cortar.
- **¿Debería ser una regla permanente?** Sí — ya está en `plantilla/README.md`. Aprendizaje de
  fondo: **ante una duda de formato, medir el PDF real en vez de asumir el valor por defecto.**

### 14/09/2026 — La cotización no llenaba la hoja y el título se desbordaba

- **Contexto**: primeras pruebas del PDF apaisado, con 4 y con 12 ítems.
- **Qué pasó**: dos problemas encadenados. (1) La hoja tenía ancho fijo de 900px, pero su alto
  depende de cuánto texto tenga la cotización — con 12 ítems solo ocupaba el 77% del ancho de
  la página y quedaba una franja vacía al costado. (2) Al hacer el ancho variable, el N° y el
  título (que estaban en píxeles fijos) dejaron de escalar con la hoja y el título se salió de
  su zona del encabezado.
- **Cómo se resolvió esta vez**: el generador busca el ancho de hoja cuya proporción calce con
  la del A4 apaisado, y los textos del encabezado pasaron a medirse en `cqw` (porcentaje del
  ancho real de la hoja) en vez de píxeles. Además, si un título sigue sin entrar en una línea,
  se le reduce la letra hasta que entre y se avisa en las alertas.
- **¿Debería ser una regla permanente?** Sí — ya está en `plantilla/README.md`. De paso cierra
  el pendiente que había sobre qué hacer con títulos largos.

### 14/09/2026 — Se creó un tipo de servicio nuevo con un solo caso

- **Contexto**: primera cotización real del sistema (cambio de vidrio templado insulado en una
  vitrina refrigerada de autoconsumo, HB Precio Uno — Guardia Civil).
- **Qué pasó**: el trabajo no encajaba en carretillas ni balanzas, así que por regla debía
  entrar como "Servicios Generales". En vez de eso se creó en el momento una familia nueva
  ("vitrinas") con su propio título, basándose en un único caso. La regla que decía "no se
  subdivide más salvo que en el uso real se note que hace falta" se saltó en la primera
  oportunidad de aplicarla.
- **Cómo se resolvió esta vez**: el tipo `vitrinas` se mantiene, porque se confirmó como
  decisión deliberada y el título quedó acotado a "Mantenimiento de vitrinas comerciales". Pero
  se construyó el mecanismo que faltaba para que no vuelva a pasar:
  - Todo servicio nuevo entra como `generales` con un **subtipo obligatorio**; el generador se
    niega a correr sin él.
  - El subtipo se registra en el Google Sheet (columna nueva) y la hoja Resumen los cuenta.
  - **Umbral explícito: 3 cotizaciones del mismo subtipo** para siquiera evaluar un título
    propio, al cierre de mes y con los números a la vista.
- **¿Debería ser una regla permanente?** Sí — ya está en `servicios.json` (bloque `promocion`),
  en `criterios-actuales.md` punto 8 y en la skill. Aprendizaje de fondo: **una regla que
  depende del criterio del momento no es una regla; hace falta un umbral y un dato que lo
  mida.**

### 16/09/2026 — El laminado no se cobra por unidad ni por m²: se cobra por rollo

- **Contexto**: solicitud de Tottus Atocongo — cambio de laminado de seguridad + certificado,
  en 12 zonas, 63 piezas entre ventanas y espejos, con medidas enviadas por el cliente.
- **Qué pasó**: al armar la cotización con el sistema aparecieron tres imprecisiones. (1) El
  generador cobra por "unidad", pero un espejo de 0.30 m y una ventana de 2.12 m contaban
  igual. (2) Se agruparon en una sola fila piezas de tamaños distintos con un único precio
  unitario. (3) Al corregir a m², tampoco era correcto: **la lámina se compra en rollos de
  ancho fijo (1.50 m × 25 m)**, así que el costo no depende del área sino de cómo encajan las
  piezas en el ancho del rollo.
- **Cómo se resolvió esta vez**: se construyó `herramientas/laminado.py`, que acomoda las
  piezas por bandas y devuelve rollos a comprar, aprovechamiento, desperdicio por zona y plan
  de corte. Resultado en este trabajo: **3 rollos, 53.9% de aprovechamiento — 46% del material
  se desperdicia**, y la causa es estructural (los 33 altillos de 0.97 m solo permiten una
  pieza por ancho de rollo). Se verificó que no es culpa del algoritmo: 18 combinaciones de
  acomodo dan el mismo resultado.
- **Dos hallazgos que exigen decisión antes de cotizar**:
  1. **4 espejos no entran en un rollo de 1.50 m en ninguna orientación** (1.54×1.73,
     1.74×1.74, y dos de 1.60×1.74). Necesitan empalme o un rollo más ancho. Hay que
     confirmarlo con el cliente: un empalme se ve.
  2. **El ancho del rollo cambia el costo**. Con 2.03 m el mismo trabajo usa 2 rollos en vez
     de 3 y entran todas las piezas. Falta saber qué anchos maneja el proveedor y a qué
     precio.
- **¿Debería ser una regla permanente?** Sí. Queda documentado en `herramientas/README.md`.
  Aprendizaje de fondo: **antes de fijar la unidad de cobro de un servicio, hay que entender
  cómo se compra el material.** La unidad que le sirve al cliente (por zona) no es la misma
  que determina el costo (por rollo).

### 16/09/2026 — El cálculo de lámina no consideraba el error humano al cortar

- **Contexto**: revisión del cálculo de rollos para Tottus Atocongo, después de ver el mapa de
  corte rollo por rollo.
- **Qué pasó**: el cálculo asumía corte perfecto. Tres problemas distintos, todos por la misma
  causa — 59 piezas se cortan a pulso con cutter, no con una máquina:
  1. No había factor de merma: ninguna pieza arruinada, ningún recorte rehecho.
  2. El acomodo presentaba como acierto una banda que deja **2 cm libres** entre dos piezas
     (Bravo 3 + Non Food). En el papel encaja; en la práctica, un desvío de esa magnitud
     arruina las dos piezas a la vez.
  3. El orden de corte no consideraba el riesgo. Si la pieza más grande se corta al final y
     sale mal, hay que comprar un rollo entero para rehacer una sola pieza.
- **Cómo se resolvió esta vez**: se agregaron las tres cosas a `herramientas/laminado.py` —
  merma configurable (10% por defecto, con el informe mostrando el largo con y sin merma),
  aviso ⚠ para toda banda con menos de 5 cm de holgura, y orden de corte de la pieza más
  grande a la más chica dentro de cada rollo. Escenarios corridos sobre Atocongo: **ni al 10%
  ni al 15% de merma se pasa de 3 rollos**; el punto de quiebre está en **18.8%**, porque el
  tercer rollo queda medio vacío y da 11.87 m de colchón.
- **Lo que NO se hizo, a propósito**: se descartó bajar la sangría de 2 cm a 1 cm para meter
  dos espejos de gerencia en una misma banda. Con cutter a mano, menos margen es menos
  tolerancia al error — se ahorran centímetros a cambio de arriesgar piezas enteras. Quedó
  escrito en `herramientas/README.md` para que no se reintente.
- **¿Debería ser una regla permanente?** Sí. Aprendizaje de fondo: **un cálculo de materiales
  que asume ejecución perfecta subestima siempre.** Y cuando el optimizador encuentra un encaje
  muy justo, eso no es una virtud del plan: es un riesgo que hay que señalar.

### 16/09/2026 — El rollo especial (4 piezas) necesitaba su propio cálculo de precio

- **Contexto**: cotización de Tottus Atocongo. Se decidió separar las 4 piezas que no
  entran en el rollo estándar (1.52 m) en una cotización aparte, con su propio rollo de
  1.83 m — ver auditoría del cálculo de laminado.
- **Qué pasó**: `precio.py` solo sabía costear un ancho de rollo por trabajo. Con dos
  anchos, dos filas de la cotización (Baño hombres, Baños mujeres) tenían piezas
  repartidas entre los dos grupos y no había forma de calcular el costo conjunto.
- **Cómo se resolvió esta vez**: `precio.py` pasa a recibir una lista de `grupos` (uno por
  ancho de rollo), calcula cada uno por separado con `laminado.py` y junta las zonas de
  todos en una sola tabla de precios. Se agregó además una **política de carga** por
  grupo (`completo` o `proporcional`) para decidir si un rollo poco aprovechado (el
  especial quedó en 29%) se factura entero o solo lo que se consume.
- **Vacío detectado de paso**: no había forma de validar que el cálculo estuviera listo
  *antes* de tener los costos reales. Se agregó un modo donde `precio.py` corre con
  `costos` en `null`, no calcula precios pero sí confirma que la estructura (rollos,
  zonas, m²) está completa — documentado en `herramientas/flujo-calculo.md`.
- **¿Debería ser una regla permanente?** Sí. Aprendizaje de fondo: **cuando un trabajo se
  divide en dos cotizaciones por una razón técnica (el material), el cálculo de precio
  tiene que poder recombinarlas** — el cliente ve dos documentos, pero el costo real
  (mano de obra, logística) no se duplica, se reparte una sola vez entre las dos.

### 16/09/2026 — El PDF no quedaba centrado y una cotización dividida en dos archivos molestaba

- **Contexto**: cotización de Tottus Atocongo dividida en dos PDF (rollo estándar / rollo
  especial), y revisión visual de ambos.
- **Qué pasó**: dos problemas.
  1. El PDF corto (4 filas) quedaba con el contenido pegado arriba y medio folio en blanco
     abajo — el mecanismo que forzaba el ancho de la hoja a calzar la proporción del A4
     topaba un ancho mínimo con pocas filas y no lograba llenar la altura.
  2. Repartir un mismo pedido en dos archivos separados, aunque técnicamente correcto (dos
     materiales distintos), resultó incómodo de manejar: se pidió un solo archivo.
- **Cómo se resolvió esta vez**: se cambió el mecanismo de ajuste — ya no se fuerza el
  ancho de la hoja, se calcula la escala que hace caber el contenido en la página y el
  sobrante (horizontal o vertical, el que sobre) se reparte mitad y mitad como margen, así
  la cotización queda centrada sin importar cuántas filas tenga. Y se agregó un ítem de
  tipo **separador**: una fila que divide visualmente un bloque dentro de la misma tabla,
  sin numerar ni sumar, para casos como "estas piezas necesitan otro material" sin partir
  el documento en dos.
- **¿Debería ser una regla permanente?** Sí — ambas quedaron en `plantilla/README.md`.
  Aprendizaje de fondo: **dos documentos correctos por separado pueden ser peor solución
  que uno solo bien estructurado** — la división técnica (rollo estándar vs especial) no
  tenía por qué convertirse en una división del entregable.

### 16/09/2026 — El texto de las piezas angostas se superponía en el dibujo de corte

- **Contexto**: primera versión de `herramientas/dibujar_rollos.py` (imágenes de corte por
  rollo, pedidas para llevar a campo en vez del mapa de texto), corrida sobre el caso real
  de Atocongo.
- **Qué pasó**: dos intentos fallidos antes del bueno.
  1. Con texto siempre horizontal sin envolver, el nombre de zonas angostas (Ingreso 211,
     0.30 m; Baño gerencia hombres, 0.75 m) se salía de su pieza y quedaba escrito encima de
     la vecina — ilegible.
  2. El primer arreglo (rotar si no entra) fue demasiado estricto: exigía que el texto
     cupiera en una sola línea sin envolver, así que pieza normales como "Comedor
     empleados" (0.95 m, texto largo) tampoco pasaban la prueba y **se quedaban sin
     ninguna etiqueta** — peor que el problema original.
- **Cómo se resolvió esta vez**: el texto primero se envuelve en varias líneas (como en
  cualquier documento), y solo si ni envuelto entra se rota 90°; si tampoco entra rotado,
  se deja solo la medida. Se verificó visualmente que las piezas normales (Comedor,
  Altillos) muestran su nombre completo en dos líneas, y las angostas (Ingreso 211) salen
  rotadas sin invadir a la vecina.
- **¿Debería ser una regla permanente?** Sí — documentado en `herramientas/README.md`.
  Aprendizaje de fondo: **un arreglo que evita un error visible no sirve si crea uno peor
  (texto faltante) en el camino** — hay que probar el caso común, no solo el caso que
  originó el arreglo.

### 20/09/2026 — Un pedido mezclaba carretillas con montacargas y apiladores

- **Contexto**: TT Pucallpa — 10 traspaletas, 1 montacargas a combustión y 3 apiladores en el
  mismo pedido.
- **Qué pasó**: el título del documento es uno solo por tipo ("Mantenimiento de carretillas
  hidráulicas"); con montacargas adentro, el título no correspondía al contenido.
- **Cómo se resolvió**: la cotización 9196-2026 cubre solo las traspaletas; el montacargas y los
  apiladores quedaron para cotizarse aparte (anotado en su nota interna).
- **¿Regla permanente?** Sí — criterios-actuales.md punto 11.2, y pregunta obligatoria en la
  ficha de carretillas. Sigue pendiente cotizarlos: no hay ficha ni precios para esos equipos.

### 20/09/2026 — La nota de la cotización llevaba información interna

- **Contexto**: HB Precio Uno, Panamericana Urbana (9197-2026) y dos borradores de la misma semana.
- **Qué pasó**: la `nota` era el único campo de texto libre y se imprime al cliente. Ahí terminó
  el razonamiento de precios (catalogo.md, piso mínimo) y una duda sobre la identidad del cliente.
  Se detectó al revisar el PDF, antes de enviarlo.
- **Cómo se resolvió**: campo `nota_interna`, que nunca se imprime, y bloqueo por código si el
  texto impreso trae términos internos.
- **¿Regla permanente?** Sí — criterios-actuales.md punto 11.1. Aprendizaje de fondo: **una
  regla escrita no evita el error si el sistema no tiene otro lugar donde poner lo interno.**

### 22/09/2026 — El precio final no sale del cálculo: se ajusta por experiencia

- **Contexto**: costeo de garruchas para SB Precio Uno, Mariátegui (hoja con dos escenarios).
- **Qué pasó**: el cálculo daba S/1,990 y S/1,390; los precios finales fueron S/2,170 y S/1,490,
  ajustados por experiencia, sin fórmula. Además la hoja no sumaba el SCTR (S/50) al costo.
- **Cómo se resolvió**: la ficha de garruchas guarda los dos precios finales como referencia; el
  registro y el motor guardan el par calculado → final. Hipótesis a probar con más casos: el
  ajuste busca una utilidad en soles por visita (S/770 a S/970), no un porcentaje.
- **¿Regla permanente?** Sí — punto 11.8. Hacen falta 8 a 10 casos para distinguir hipótesis.

### 25/09/2026 — Cotizar por pieza en vez de por juego

- **Contexto**: garruchas, 3 coches × 4 ruedas.
- **Qué pasó**: "12 ruedas" se ve más completo para el cliente que "3 juegos".
- **Cómo se resolvió**: `cotizar_por` en la ficha: el costo sigue por coche, la línea cuenta
  ruedas y el precio va por rueda.
- **¿Regla permanente?** Sí — punto 11.10.

### 22/09/2026 — Cambio de garruchas de coches de panadería: sin subtipo que calce

- **Contexto**: cotización de SB Precio Uno, Mariátegui — cambio de garruchas a 3 coches de
  panadería (4 garruchas c/u, 12 unidades en total).
- **Qué pasó / qué no encajaba en las reglas actuales**: no es carretillas (son garruchas de
  coches de panadería, no ruedas de carretilla hidráulica), ni balanzas, ni vitrinas. Tampoco
  hay ningún subtipo de `subtipos_sugeridos` que calce (espejos, mamparas, laminado-seguridad,
  acrilicos, vitrales, motores, estructuras, pintado, electrico). Tampoco hay precio de
  referencia: ni en `catalogo.md` ni en el Excel histórico (esa celda, "ruedas de coches de
  panadería", tenía un error `#REF!` sin dato real recuperable — ver `analisis/cchh-cot-excel.md`).
- **Cómo se resolvió esta vez**: entra como `generales` con subtipo `otros`, como indica la
  regla cuando ninguno calza. El precio queda `pendiente` hasta que se confirme.
- **¿Debería ser una regla permanente?** A evaluar — si aparecen más trabajos de mobiliario de
  panadería (coches, bandejas, etc.), considerar un subtipo `mobiliario` o similar al llegar al
  umbral de 3 cotizaciones (ver `promocion` en `servicios.json`).

### 17/09/2026 — Las piezas se dibujaban pegadas, sin espacio para el cutter

- **Contexto**: revisión de las imágenes de corte con los rollos ya confirmados en 30 m.
- **Qué pasó**: el acomodo por bandas coloca las piezas una al lado de otra sin ningún
  hueco entre ellas — correcto para calcular cuánto material se necesita, pero en la
  práctica hace falta espacio para pasar el cutter entre dos piezas sin tocar la vecina.
- **Cómo se resolvió esta vez**: se agregó `espacio_corte` (1 cm por defecto) como
  parámetro real del cálculo — no solo del dibujo. Se resta en `empacar()` (a lo ancho,
  entre piezas de una misma banda) y en `asignar_rollos()` (a lo largo, entre bandas de un
  mismo rollo), y `ubicar()`/`verificar()` quedaron consistentes con esas posiciones. En el
  dibujo, como 1 cm da menos de 2 px a la escala del plano, se fuerza un mínimo de 5 px
  para que el corte se vea, dejando la medida real solo en el texto.
- **¿Debería ser una regla permanente?** Sí — documentado en `herramientas/README.md`.
  Aprendizaje de fondo: **una separación real entre piezas no es un detalle del dibujo, es
  parte del cálculo de material** — tratarla solo como estética habría subestimado el
  rollo en trabajos más ajustados que el de Atocongo.

### 08/10/2026 — Soldadura TIG en equipo de producción (10083-2026, Lince)

- **Contexto**: reparación y soldadura TIG de un equipo de producción de acero inoxidable, con
  precio único dado directamente y una foto del equipo.
- **Qué pasó / qué no encajaba en las reglas actuales**: no es carretillas, balanzas ni vitrinas,
  y ningún subtipo sugerido calza (`estructuras` es otra cosa). La foto venía con el sello de la
  app de cámara: dirección, mapa, brújula y hora quemados en la imagen.
- **Cómo se resolvió esta vez**: `generales` con subtipo `otros`. La foto se recortó al equipo
  antes de usarla, para que el documento no lleve la ubicación del cliente.
- **¿Debería ser una regla permanente?** El recorte, sí: toda foto con sello de ubicación se
  recorta antes de ir a una cotización. El subtipo, a evaluar: si se repiten trabajos de
  soldadura en equipos de cocina o producción, considerar un subtipo `soldadura` al llegar al
  umbral de 3.
