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
