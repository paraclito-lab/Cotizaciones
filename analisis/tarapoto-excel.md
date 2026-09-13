# Análisis: COTIZCION_TARAPOTO.xlsx

Archivo distinto a los demás: no es una cotización terminada, es una **hoja de trabajo
interna real** (mantenimiento de una balanza plataforma) que Gera no había limpiado antes de
guardarla. Por eso vale más que varias cotizaciones ya terminadas — muestra el proceso, no
solo el resultado. Analizado el 13/09/2026.

## Qué contenía

4 hojas. Tres son cotizaciones normales (rampa de acero inoxidable, protectores, balanza). La
cuarta, sin embargo, deja ver el costeo interno completo de la balanza:

- Una lista de insumos/repuestos con su costo, varios todavía en S/0 (celdas y de acero,
  cable multiconductor, caja sumatoria) — es decir, precios que Gera aún no había confirmado
  al momento de guardar el archivo.
- Una columna de **preguntas pendientes al cliente o a sí mismo**, escritas tal cual mientras
  pensaba: "¿cuál es el precio de la cadena de brazo?", "¿se va a pintar la estructura?",
  "¿qué tipo de pintura, epóxica o gloss?", "¿cuántos trabajadores realizarán el
  mantenimiento?", "buscar precio en bus de Lima a Cuzco".
- Una anotación de ubicación en dos formas distintas en la misma hoja: "LOCAL: COMAS" y,
  aparte, la necesidad de cotizar un pasaje a Cuzco — evidencia de que la logística cambia
  según dónde se hace el trabajo.
- El cálculo final: **costo S/340 + ganancia S/204 = precio S/544** — la ganancia aparece
  como un monto decidido, no como un porcentaje aplicado a una fórmula.
- Un posible identificador de cotización, `8201-MES-DIA-#`, sin significado documentado en
  ningún lado.

## Por qué fue más útil que un PDF terminado

Un PDF final solo muestra el precio que se decidió cobrar. Esta hoja muestra **cómo se llegó**
a ese precio: qué faltaba resolver, qué se le iba a preguntar al cliente, y que la ganancia no
sale de una fórmula fija sino de una decisión caso por caso.

## Decisiones que generó (ver `criterios-actuales.md`)

- Punto 4 (margen de ganancia): confirmado que es una decisión de experiencia (60-80%,
  ajustable), no un porcentaje automático — igual que en esta hoja.
- Punto 5 (checklist de consideraciones): la idea de dejar preguntas pendientes antes de
  cotizar, vista aquí de forma improvisada, se decidió formalizar por tipo de servicio.
- Punto 2 (mano de obra por localidad): el caso del pasaje a Cuzco confirmó que la logística
  cambia según dónde se hace el trabajo, antes de que Gera lo explicara directamente en el
  chat.
- Punto 7 (numeración): el código `8201-MES-DIA-#` visto acá fue el disparador para preguntar
  por la numeración y terminar definiendo `COT-AAAA-NNN`.
