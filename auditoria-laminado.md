# Auditoría del cálculo de laminado — 16/09/2026

Revisión crítica de `herramientas/laminado.py` y de las recomendaciones que se dieron con él,
usando como caso el pedido de Tottus Atocongo (63 piezas). Varios de los hallazgos son errores
del propio análisis, no del código.

---

## A. Lo que cambia el presupuesto

### A1. El 15.7% del trabajo no está costeado

| | |
|---|---|
| Área total del pedido | **71.94 m²** (63 piezas) |
| Área que el cálculo cubre | 60.68 m² (59 piezas) |
| **Área sin costear** | **11.26 m² — 15.7%** |

Los 4 espejos que no entran en el rollo de 1.50 m quedaron fuera del cálculo, y el titular
"3 rollos, 53.9% de aprovechamiento" se calcula **solo sobre las 59 piezas restantes**. Quien
cotice con ese número deja fuera una sexta parte del trabajo.

El informe los lista como advertencia, pero no impide seguir ni marca el resultado como
parcial. Debe hacerlo.

### A2. El empalme no es una opción en un trabajo certificado

Se planteó como decisión comercial —"un empalme se ve, hay que consultarlo con el cliente"—.
Es un error de criterio técnico. El asunto del correo es **"CAMBIO DE LAMINADO + CERTIFICADO"**:
una lámina de seguridad empalmada **no ofrece resistencia continua al impacto** y, en la
práctica, invalida la certificación (ANSI Z97.1 / EN 12600, que es lo que se suele exigir).

No es una pregunta para el cliente. Esas 4 piezas **requieren un rollo más ancho**, o no se
pueden certificar.

### A3. Se recomendaron anchos de rollo que no existen

La tabla comparativa incluía 2.03 m y 2.44 m, y sobre esa base se dijo "con 2.03 m usarías
2 rollos en vez de 3". Los anchos comerciales de lámina de seguridad son
**36" / 48" / 60" / 72"** = 0.91 / 1.22 / **1.52** / **1.83 m**. Por encima de 1.83 m no hay
presentación estándar.

La recomendación era inaplicable. El ancho real a evaluar es **1.83 m**, y con él entran las
4 piezas problemáticas (1.74 + 0.04 de sangría = 1.78 m ≤ 1.83 m).

| Estrategia | m² comprados | Piezas sin cubrir |
|---|---|---|
| Todo en 1.52 m | 112.5 | **4** |
| Todo en 1.83 m | 137.2 | 0 |
| 1.83 solo para los 4 espejos + 1.52 el resto (rollos completos) | 159.8 | 0 |
| Igual, pero comprando 6.64 m lineales de 1.83 | **124.7** | 0 |

**Pregunta que decide el costo: ¿el proveedor vende por metro lineal o solo rollo completo?**
Si vende por metro, la estrategia mixta es la más barata. Si solo vende rollos, conviene todo
en 1.83 m.

### A4. El retiro del laminado viejo no está en ningún lado

El pedido dice **cambio** de laminado: antes de instalar hay que **retirar** el existente. En
lámina vieja el film se vuelve quebradizo, sale en pedazos y deja el adhesivo pegado, que hay
que ablandar y raspar. En vidrios de 63 piezas ese trabajo es comparable al de instalación, a
veces mayor.

No está en el cálculo ni en la cotización de ejemplo. Es la omisión más cara del análisis.

### A5. La mano de obra no se calcula en absoluto

La herramienta resuelve el material y ahí se detiene. En laminado la mano de obra suele ser el
componente mayor, y no escala con los rollos sino con los m², la cantidad de piezas y la
dificultad de acceso. Los baños del pedido tienen griferías, dispensadores y bordes contra
mayólica (se ve en las fotos): no es vidrio plano y libre.

---

## B. Criterio técnico discutible

### B1. El giro libre de las piezas puede verse en el resultado

El algoritmo gira las piezas 90° cuando le conviene. Dos razones por las que eso no es gratis:

- La lámina sale enrollada y conserva la curvatura a lo largo del rollo; aplicarla con la
  curvatura cruzada complica el montaje.
- Algunas láminas presentan ligera variación de tono a lo ancho de la bobina. En un tramo
  visible y continuo —los **33 altillos**, uno al lado del otro— mezclar orientaciones puede
  hacerse notorio.

Debería poder fijarse la orientación por zona, y el informe debería advertir cuando piezas de
la misma zona quedan giradas de forma distinta.

### B2. La merma como porcentaje del largo no refleja cómo se arruina el material

Arruinar una pieza cuesta **la banda de esa pieza**, no un porcentaje del total. Echar a perder
un altillo cuesta 1.00 m de rollo; echar a perder la banda de 2.16 m cuesta el doble. Un
modelo más fiel sería una probabilidad de error por pieza, ponderada por su tamaño.

Además, 10% es probablemente bajo para este pedido: 63 piezas, baños con obstáculos, ambiente
de supermercado en operación.

### B3. Falta la pérdida fija por rollo

Los primeros y últimos centímetros de un rollo suelen ser inservibles —punta maltratada,
deformación del núcleo, polvo—. Son del orden de 0.30 a 0.50 m **por rollo**, y es una pérdida
fija, no proporcional. Con 3 rollos son ~1.2 m que nadie está contando.

### B4. Los retazos se cuentan como basura, y no siempre lo son

El 46% de "desperdicio" incluye 33 tiras de 0.49 × 1.00 m —unos 16 m²— que en un taller real
se guardan para piezas chicas. Tratarlas como pérdida total **sobreestima el costo** de este
trabajo y **subestima** el valor del inventario que queda. Debería reportarse aparte:
recorte inutilizable vs. retazo aprovechable.

### B5. Las medidas del cliente se están tomando como verdad

Tres problemas:

1. **Nunca se corta con medidas de terceros.** Se cotiza con ellas, se re-mide en sitio antes
   de cortar. Debe quedar escrito como condición de la cotización.
2. **¿Midieron el vidrio o el vano?** La lámina va sobre el vidrio, que es menor que la
   abertura del marco. Si midieron el marco, sobra material; si midieron el vidrio visible, la
   sangría de 2 cm es la correcta. No está verificado.
3. **El espejo de 1.74 × 1.74 m, exactamente cuadrado, es sospechoso.** Y es justo la pieza que
   obliga a comprar un rollo de 1.83 m. Conviene confirmarla antes de decidir la compra.

---

## C. Defectos del código

### C1. El conteo de rollos con merma repite el error ya corregido

```python
rollos = max(len(lista_rollos), math.ceil(largo_con_merma / largo_rollo))
```

La segunda mitad divide el largo total entre el largo del rollo — exactamente lo que se
corrigió para el caso base, porque **una banda no se puede partir entre dos rollos**. El
material de reposición también se corta en bandas.

### C2. `p not in mejor["imposibles"]` compara diccionarios por valor

Funciona hoy por casualidad, es O(n²) y se rompe en silencio si dos piezas distintas quedan
con el mismo contenido. Debería compararse por identidad o marcarse con una bandera.

### C3. El aprovechamiento mezcla dos universos

`area_vidrio` excluye las piezas imposibles, pero `area_comprada` sí incluye los rollos extra
por merma. El porcentaje resultante no responde una pregunta limpia.

---

## D. Lo que está bien y conviene conservar

- **El modelo de bandas** corresponde a cómo se corta de verdad un rollo. Un acomodo tipo
  tetris daría mejor número y un plan que nadie puede ejecutar con cúter.
- **La verificación geométrica**, y sobre todo que se haya probado rompiéndola a propósito.
- **No partir bandas entre rollos** (en el cálculo base).
- **El orden de corte por riesgo** y **el aviso de bandas sin holgura**: los dos son criterio
  de taller, no de planilla.
- **La decisión de no bajar la sangría** a cambio de encajes más ajustados.

---

## Qué hacer antes de usar este cálculo para cotizar

1. Confirmar con el proveedor: **anchos disponibles** del film certificado y si **vende por
   metro lineal**. Decide entre 124.7 y 159.8 m² de compra.
2. Verificar la medida del espejo de 1.74 × 1.74 m.
3. Costear el **retiro del laminado existente** — probablemente la partida más grande.
4. Costear la **mano de obra** de instalación por m² y por dificultad de acceso.
5. Dejar por escrito en la cotización que **las medidas se confirman en sitio** antes de
   cortar.
6. Corregir en la herramienta: cobertura parcial como error y no como aviso, pérdida fija por
   rollo, separación entre recorte y retazo aprovechable, y el conteo de rollos con merma.
