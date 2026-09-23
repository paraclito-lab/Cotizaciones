# Biblioteca de trabajos

Cada tipo de trabajo que se cotiza tiene una **ficha**: qué hay que preguntar antes de cotizar,
cuánto cuesta ir y cuánto cuesta cada unidad, cómo se describe al cliente y cuánto se cobró
las veces anteriores. Con la ficha, cotizar es llenar un pedido de pocas líneas. La primera vez
que aparece un trabajo cuesta pensarlo; desde la segunda, ya está resuelto.

## Agregar un trabajo nuevo

```bash
python3 herramientas/nuevo_trabajo.py
```

Hace 7 preguntas (nombre, familia, qué se cuenta, cómo se pone el precio, costos, checklist,
redacción) y guarda la ficha en `trabajos/<id>.json`. No hace falta saber JSON.

- Lo que todavía no se sabe se responde con **`?`**. Queda marcado como pendiente y **bloquea
  el precio** hasta completarlo: el sistema no inventa ese número.
- Al final revisa la ficha. Si tiene un problema, no la activa: la deja como
  `_borrador-<id>.json` y dice qué corregir.
- Desde el chat con Claude basta con pedir "agrega el trabajo …": la skill `cotizar` hace lo
  mismo.

## Cotizar con una ficha

Un pedido es un JSON corto. El de garruchas, por ejemplo:

```json
{
 "trabajo": "garruchas-coche-panaderia",
 "cliente": "SB PRECIO UNO",
 "local": "MARIATEGUI",
 "unidades": 3,
 "respuestas": {"horno": "si", "montaje": "soldada", "horario": "fuera"},
 "precio_unidad": 725
}
```

```bash
python3 herramientas/cotizar_trabajo.py pedido.json salida/
python3 plantilla/generar.py salida/<N°>.json salida/            # vista previa
python3 plantilla/generar.py salida/<N°>.json salida/ --final    # aprobada: PDF + archivo
```

El primer comando muestra, antes de escribir nada:

1. **El checklist**: cada pregunta con su respuesta, y los avisos que dispara (ej. "en
   provincia la mano de obra no tiene fórmula"). Si falta una respuesta, no sigue. Con
   `--borrador` sigue igual: lo que falta sale en la cotización como "alcance sujeto a
   confirmación de…" y el precio que dependa de eso queda pendiente.
2. **El costeo interno**, que no sale en la cotización: costos fijos por visita, costos por
   unidad y el costo total.
3. **El precio por unidad** al markup mínimo, sugerido y máximo de la ficha. **El precio no se
   pone solo**: lo pone quien cotiza, con `precio_unidad` en el pedido. Sin eso, la línea sale
   "Pendiente".
4. **Lo que ya se cobró por ese mismo trabajo**: las referencias de la ficha y todas las
   cotizaciones archivadas con `--final`. Cada cotización final se suma sola al historial.

El JSON que escribe lleva además `costo_estimado`, `subtotal_calculado` y una `nota_interna`
con el rastro de cada precio: de dónde salió, si difiere del catálogo, cuánto se ajustó sobre
el calculado. Nada de eso se imprime para el cliente.

## Qué cambia respecto de antes

| Antes | Ahora |
|---|---|
| Cada trabajo nuevo se costeaba de cero, en una hoja suelta | La ficha guarda el costeo; la segunda vez sale al instante |
| Las preguntas de especificación se hacían de memoria, a veces después de cotizar | Checklist obligatorio por trabajo: sin respuestas no se cotiza, o sale "sujeto a confirmación" |
| El precio final ajustado por experiencia no quedaba registrado | Queda el par calculado → final, y el historial lo muestra la próxima vez |
| Un precio distinto al catálogo no dejaba rastro | La nota interna lo anota sola: "Rueda de carga: S/60 dado directamente (catálogo: S/40)" |
| No existía el costo fijo por visita: los trabajos chicos se cotizaban a ojo | `costos_fijos`: lo que cuesta ir, igual para 3 unidades que para 15 |

## Cómo está hecha una ficha

Ver `garruchas-coche-panaderia.json` (el ejemplo más completo) y `_plantilla.json` (con la
explicación de cada campo). Lo esencial:

- **`modo_precio`**: `costo_mas_markup` si se sabe cuánto cuesta (el precio sale del costo), o
  `precio_referencia` si se cobra por experiencia (el precio lo trae cada pedido).
- **`preguntas`**: el checklist. Cada respuesta puede cambiar un costo, cambiar la redacción,
  agregar una condición o mostrar un aviso. Ejemplo real: si la garrucha va empernada en vez de
  soldada, aparece la pernería (sin monto todavía, así que bloquea el precio) y la redacción
  cambia a "montaje de las nuevas con pernería nueva".
- **`costos_fijos`** y **`costos_por_unidad`**: `null` = todavía no se sabe.
- **`redaccion`**: la línea que ve el cliente; `{unidades}` se reemplaza sola.
- **`referencias`**: precios reales cobrados antes de existir la ficha.

## Reglas

- **Los repuestos no tienen precio en la ficha**: se leen de `catalogo.md`, que sigue siendo la
  única fuente. La ficha solo dice en qué sección buscarlos (`seccion_catalogo`).
- **Si a un pedido le falta un costo, se agrega a la ficha, no al pedido.** El motor rechaza
  costos que la ficha no conoce, a propósito: así lo aprendido queda para la próxima vez.
- **Nada interno en el texto del cliente.** Ni la ficha ni el generador aceptan "catálogo",
  "piso mínimo", "markup", "por validar" y parecidos en lo que se imprime. Eso va en la nota
  interna.
- **Antes de subir cualquier cambio**: `python3 herramientas/probar.py`. Reproduce las
  cotizaciones reales ya emitidas; si un cambio mueve un céntimo de algo ya entregado, falla.

## Fichas actuales

| Ficha | Precio | De dónde salen los datos |
|---|---|---|
| `garruchas-coche-panaderia` | Costo + markup | Costeo real del 22/09/2026 (fijos S/450 + S/250 por coche) y los dos precios finales ajustados (S/2,170 y S/1,490) |
| `mantenimiento-carretillas` | Precio de referencia | Repuestos de `catalogo.md`; timón (S/40) y etiqueta (S/20) de 9197-2026; historial de 9196 y 9197 |

`ejemplos/` tiene los pedidos que reproducen 9196-2026, 9197-2026 y el borrador de garruchas:
sirven de modelo y de prueba.
