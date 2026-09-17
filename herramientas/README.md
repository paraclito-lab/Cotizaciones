# Herramientas de cálculo

Scripts de apoyo para cotizar. No generan documentos: calculan el dato que después se usa
para poner un precio.

## `laminado.py` — cuántos rollos de lámina se necesitan

**El problema que resuelve**: la lámina de seguridad no se compra por metro cuadrado. Viene
en **rollos de ancho fijo** (1.50 m es el más común) y largo fijo (25 m). Entonces el costo no
sale de dividir el área total: sale de **cómo encajan las piezas en el ancho del rollo**.

Dos trabajos con los mismos m² pueden necesitar distinta cantidad de rollos. Ejemplo real
(Tottus Atocongo, 63 piezas): 60.68 m² de vidrio consumieron 3 rollos = 112.50 m² de lámina.
**El 46% se fue a la basura**, y no por mal corte — por la geometría de las piezas.

### Cómo se usa

```bash
python3 herramientas/laminado.py piezas.json
```

El JSON lleva el ancho y largo del rollo, la sangría de corte, y la lista de piezas por zona:

```json
{
  "ancho_rollo": 1.50,
  "largo_rollo": 25.0,
  "sangria": 0.02,
  "merma": 0.10,
  "piezas": [
    {"zona": "Altillos", "cant": 33, "ancho": 0.97, "alto": 0.96}
  ]
}
```

### Qué devuelve

1. **Piezas que no entran en el ancho del rollo** — necesitan empalme o un rollo más ancho.
   Es lo primero que hay que revisar: un espejo de 1.74 × 1.74 m **no entra** en un rollo de
   1.50 m en ninguna de sus dos orientaciones.
2. **Rollos a comprar** y metros lineales consumidos.
3. **Aprovechamiento** — qué porcentaje de la lámina comprada termina pegada al vidrio.
4. **Desperdicio por zona** — dónde se está yendo el material. Casi siempre hay una o dos
   zonas que se comen el desperdicio.
5. **Mapa de cada rollo** — cómo queda cargado rollo por rollo, con una barra que muestra a
   escala cuánto del ancho se aprovecha y cuánto se bota. Es lo que se imprime y se lleva a
   campo.

### Las piezas nunca van pegadas — hay espacio real de corte

Además de la sangría (el margen que se pega y se recorta al ras de cada pieza), existe
`espacio_corte` (**1 cm por defecto**): la separación real que debe quedar entre una pieza
y la de al lado, y entre una banda y la siguiente. No es lo mismo — la sangría es parte de
la pieza, el espacio de corte es el hueco que hace falta para pasar el cutter sin tocar la
pieza vecina.

Este espacio **consume material de verdad**: se resta al acomodar (una pieza necesita su
ancho más el espacio antes de ella para entrar en una banda) y al asignar bandas a rollos.
Con 59 + 4 piezas en el caso de Atocongo, agregar 1 cm entre cada corte subió el largo
consumido de 63.13 a 63.68 m — no cambia cuántos rollos hacen falta, pero si el trabajo
fuera más ajustado sí podría.

En el dibujo (`dibujar_rollos.py`) ese centímetro real es casi invisible a la escala del
plano (menos de 2 px), así que se dibuja con un **mínimo de 5 px** para que el corte se
vea — la medida real (la que importa para comprar) sigue siendo la del texto, no la del
dibujo.

### El error humano sí está considerado

Cortar 59 piezas a pulso con cutter no sale perfecto. El script lo toma en cuenta de tres
maneras, todas separadas de la sangría:

**1. Merma configurable.** `"merma": 0.10` en el JSON suma 10% al largo consumido antes de
redondear a rollos. El informe muestra las dos cifras — largo con corte perfecto y largo con
merma — para ver cuánto pesa el supuesto y poder discutirlo.

**2. Aviso de bandas sin holgura.** Toda banda que deje menos de 5 cm libres a lo ancho sale
marcada con ⚠ en el mapa, y se repite al final con su explicación. Encajar dos piezas dejando
2 cm no es un acierto del acomodo: es una trampa. A pulso, un desvío de esa magnitud arruina
las **dos** piezas. En el caso de Atocongo la banda de Bravo 3 + Non Food (0.02 m libres) sale
marcada.

**3. Orden de corte por riesgo.** Dentro de cada rollo, las bandas se ordenan de la pieza más
grande a la más chica, y ese orden **es** el orden físico de corte. La razón: si se arruina un
corte grande al inicio, el rollo todavía está entero y alcanza para rehacerlo; si esa misma
pieza se deja para el final y falla, hay que comprar un rollo completo por una sola pieza.

## `dibujar_rollos.py` — una imagen por rollo, para llevar a campo

Es la versión visual del mapa de texto: dibuja cada rollo a escala, con cada pieza en su
posición real, su zona, medida y el orden de corte (las bandas se numeran igual que en el
mapa — la más grande primero).

```bash
python3 herramientas/dibujar_rollos.py trabajo.json carpeta_salida/
```

Genera una imagen **por rollo físico** (no por grupo — si un grupo necesita 3 rollos, salen
3 imágenes). Cada una muestra:

- Las piezas a escala real, coloreadas solo para diferenciarlas de su vecina (el color no
  significa nada).
- El **orden de corte** numerado arriba de cada banda.
- Las bandas **sin holgura** (menos de 5 cm libres, ver `laminado.py`) marcadas en rojo con
  ⚠, igual que en el mapa de texto.
- El sobrante del rollo, recortado a una franja corta (no se dibuja completo si son varios
  metros vacíos — dejaría la imagen carguísima de espacio en blanco) con el resto indicado
  en texto: `+9.9 m más, no dibujado`.

### El texto se envuelve o se rota — nunca se deja superpuesto

Con piezas angostas (ej. Ingreso 211, 0.30 m) el nombre de la zona no entra en una línea
horizontal y se salía sobre la pieza vecina. Antes de escribir, se prueba: (1) el texto
envuelto en varias líneas, normal; (2) si tampoco entra, rotado 90° (las piezas angostas
suelen ser altas en su banda); (3) si ni así entra, se muestra solo la medida. Nunca se deja
un texto que invada la pieza de al lado.

### El acomodo se verifica solo, en cada corrida

Que las piezas no se monten unas sobre otras es una promesa del algoritmo, no un hecho. Por
eso el script le asigna a cada pieza su posición real (x, y) dentro de su rollo y comprueba,
pieza contra pieza, que **ninguna se solape con otra y ninguna se salga del rollo**. Si alguna
vez se cambia la forma de acomodar, el error aparece acá y no en el taller con la lámina ya
cortada.

La verificación se probó rompiéndola a propósito — metiendo una pieza de más en una banda
llena y poniendo una banda más larga que el rollo — y detectó ambos casos. Un verificador que
siempre dice que todo está bien no sirve de nada.

### Una banda no se puede partir entre dos rollos

El primer cálculo sumaba los metros de todas las bandas y dividía entre 25. Está mal: si a un
rollo le quedan 0.80 m y la siguiente banda mide 1.00 m, esa banda arranca un rollo nuevo y
esos 0.80 m se pierden. El script reparte las bandas en rollos de mayor a menor, sin partir
ninguna. En el caso de Atocongo el resultado no cambió (3 rollos en ambos métodos), pero en un
trabajo con bandas largas sí puede cambiar.

### Cómo acomoda las piezas

Corte por bandas, que es lo que se hace en la práctica con un rollo: se corta de lado a lado.
Las piezas se acomodan una al lado de otra a lo ancho, y cada banda consume, a lo largo del
rollo, lo que mide la pieza más alta de esa banda.

El script prueba **18 combinaciones** de criterio de giro, orden de acomodo y regla de encaje,
y se queda con la que menos rollo consume. Cada pieza puede ir girada 90° si eso ayuda.

### Antes de confiar en el resultado, revisar

- **¿La lámina se puede girar?** El script asume que sí. Si el material tiene dirección (por
  el patrón o el tipo de adhesivo), hay que desactivar el giro y el desperdicio sube.
- **La sangría** por defecto es 2 cm por lado, y son a propósito: se pega sobrado y se recorta
  al ras contra el marco. **No bajarla para hacer entrar una pieza más.** Con cutter a mano,
  menos margen es menos tolerancia al error: se ahorran centímetros a cambio de arriesgar
  piezas enteras, y una pieza arruinada cuesta muchísimo más que el recorte que se ahorró.
- **La merma** por defecto es 10%. Es otra cosa distinta de la sangría: la sangría sí se pega
  al vidrio, la merma es la pieza que se echó a perder y hay que cortar de nuevo. El informe
  muestra el largo con y sin merma, para que se vea cuánto pesa el supuesto.

### El ancho del rollo cambia todo — conviene preguntarle al proveedor qué anchos maneja

Mismo trabajo de Atocongo, variando solo el ancho:

| Ancho del rollo | Piezas que no entran | Rollos | m² comprados | Aprovechamiento |
|---|---|---|---|---|
| 1.22 m | 4 | 3 | 91.5 m² | 66% |
| **1.52 m** (el actual) | **4** | **3** | **114.0 m²** | **53%** |
| 1.83 m | 0 | 3 | 137.2 m² | 52% |
| 2.03 m | 0 | 2 | 101.5 m² | 71% |
| 2.44 m | 0 | 2 | 122.0 m² | 59% |

Lo importante no es el porcentaje sino **los m² comprados**, que es lo que se paga. Y como el
precio por rollo cambia según el ancho, la decisión final necesita el precio de cada
presentación — dato que todavía no está en `catalogo.md`.

### Cuánta merma aguanta un plan antes de costar un rollo más

El informe lo calcula solo. En Atocongo el plan consume 63.13 m y tres rollos dan 75 m, así
que **aguanta 11.87 m de recortes arruinados: hasta 18.8% de merma**. Escenarios corridos:

| Merma | Largo necesario | Rollos |
|---|---|---|
| 0% | 63.13 m | 3 |
| 10% | 69.44 m | 3 |
| 15% | 72.60 m | 3 |
| **19%** | **75.12 m** | **4** |

Ni al 10% ni al 15% se pasa de 3 rollos. Ese colchón existe solo porque el tercer rollo va
medio vacío; en un trabajo donde los rollos queden justos, una merma del 10% sí puede costar un
rollo entero.

## `flujo-calculo.md` — el mapa completo, para validar antes de cotizar

Diagrama y checklist de punta a punta: de las medidas del cliente al precio final,
pasando por `laminado.py` y `precio.py`. Incluye qué datos faltan (precio del rollo,
tarifas) y qué decisiones siguen abiertas (política de carga del rollo especial). Leer
esto antes de meter costos reales a un trabajo nuevo.

## `precio.py` — del costo al precio unitario por zona

Responde lo que `laminado.py` no resuelve: **cuánto se cobra**. Toma los costos reales, les
aplica el margen y reparte el total entre las zonas.

```bash
python3 herramientas/precio.py trabajo.json
```

### Un trabajo puede necesitar más de un ancho de rollo

Cuando algunas piezas no entran en el rollo estándar (ver `laminado.py`), el JSON de
`precio.py` no es una sola lista de piezas: es una lista de **`grupos`**, uno por ancho
de rollo. `precio.py` calcula el acomodo de cada grupo por separado y junta las zonas de
todos en una sola tabla de precios. Ver `herramientas/ejemplo-trabajo.json` y
`herramientas/flujo-calculo.md`.

Cada grupo puede tener su propia **política de carga**:

- `"completo"` — se factura el o los rollos enteros a las piezas de ese grupo, aunque
  sobre material. El sobrante queda como inventario para otro trabajo.
- `"proporcional"` — solo se factura lo que de verdad se consume (con su merma); el
  resto no se cobra a este cliente.

Si `precio.py` corre con `costos` en `null`, no calcula precios pero sí valida que la
estructura (rollos, zonas, m²) está lista — así se puede confirmar el cálculo un día
antes de tener los números finales.

### Por qué NO se divide el total entre los m²

El costo **no es proporcional al área**. Un espejo de 0.30 × 1.22 m toma casi el mismo tiempo
que uno de 0.97 × 0.96 —llegar, limpiar el vidrio, posicionar, aplicar, sacar burbujas,
recortar al ras— y lo único que cambia es el material, que es la parte chica del costo.

Repartiendo un mismo total de S/12,000 de las dos formas:

| Pieza | m² | Solo por m² | Fijo + m² | Diferencia |
|---|---|---|---|---|
| Altillo | 0.93 | S/224 | S/227 | +1% |
| **Espejo Ingreso 211** | 0.37 | **S/88** | **S/152** | **+73%** |
| **Espejo mujeres grande** | 3.03 | **S/729** | **S/505** | **−31%** |

Dividir entre m² **cobra de menos las piezas chicas** (pierdes plata) y **de más las grandes**
(te sacan de carrera). Por eso el modelo es `fijo por pieza + tarifa por m²`.

### Cómo reparte el costo

- **Material**: según el rollo que consume cada zona de verdad, incluyendo su desperdicio —
  no según su área. Sale del acomodo por bandas de `laminado.py`.
- **Instalación y retiro**: `fijo por pieza × piezas + tarifa por m² × área`.
- **Logística y certificado**: son fijos del trabajo; se reparten según cuánto pesa cada zona
  en el costo directo.
- **Margen**: se aplica sobre el costo total, y el precio unitario se **redondea hacia arriba**
  al múltiplo que se indique (S/10 por defecto), para que en la cotización aparezcan números
  comerciales y no resultados de división.

El informe muestra el **margen real después del redondeo** y avisa si se movió más de 5 puntos
respecto del margen pedido.

### Lo que NO se muestra al cliente

- **La tarifa por m²**. Si en la cotización aparece "S/241/m²", el cliente la usa para
  negociar y para compararte contra el vendedor de lámina. El valor está en la instalación
  certificada, no en revender film.
- **El desperdicio**. Va dentro del precio. Si se muestra como partida, el cliente pide que se
  absorba.

### Piezas que no entran: cotización aparte

Si alguna pieza no entra en el ancho del rollo, `precio.py` **se niega a calcular** y las
lista. Van en una cotización separada, con su propio rollo más ancho. Dos razones: usan otro
material, y si el cliente rechaza esas piezas no se cae el trabajo completo.

## Cómo entra esto en el precio

El cálculo de rollos da el **costo de material**. El precio al cliente sale de:

```
costo material (rollos × precio del rollo)
+ mano de obra (personas × amanecidas, ver criterios-actuales.md punto 2)
+ logística
= costo total  →  + margen  →  precio
```

La cotización al cliente se sigue presentando **por zona** (es como el cliente lo pidió y como
lo entiende), pero el número sale de los rollos, no de los m².
