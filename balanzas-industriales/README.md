# Balanzas industriales

Carpeta dedicada a **balanzas** (plataforma, industriales — no confundir con "Servicios
Generales"), separada del resto porque hoy es el tipo de servicio con menos data real del
repo: la forma del servicio está definida en `servicios.json`, pero el contenido económico
descansa en un solo caso sin cerrar (ver `analisis/tarapoto-excel.md`). El objetivo de esta
carpeta es que deje de ser así, con casos reales.

No reemplaza nada de lo que ya existe — sigue siendo cierto que:

- `servicios.json` es la única fuente del título, la redacción base y las palabras clave.
- `criterios-actuales.md` tiene las reglas generales (personal: 3 por trabajo, margen 60-80%,
  numeración, flujo de aprobación) — esas aplican a balanzas igual que a todo lo demás.
- `catalogo.md` sigue siendo donde debería vivir el precio de un repuesto en cuanto se
  confirme uno — no se duplica precio acá.

Lo que esta carpeta agrega es lo que faltaba: un lugar para juntar **casos reales de balanzas**
y sacar de ahí lo que hoy no existe (precios de repuestos, piso mínimo, checklist propio).

## Qué va en cada carpeta

| Carpeta / archivo | Qué es |
|---|---|
| `cotizaciones-reales/` | Cotizaciones de balanza ya cerradas (con precios confirmados, no borradores). Un archivo por cotización, con el mismo criterio que `ejemplos-reales/` en la raíz: sirven de referencia de formato y precio. |
| `casuistica-balanzas.md` | Bitácora de casos, dudas y excepciones específicas de balanzas — mismo formato que `casuistica.md` de la raíz, pero enfocada. Los hallazgos con impacto en TODO el sistema (no solo balanzas) siguen yendo al `casuistica.md` general. |
| `analisis-proveedor-gufra.md` | Extracción del chat con el proveedor Gufra Perú: costo de compra por componente (celdas, cajas sumadoras, indicadores), notas técnicas de compatibilidad, y qué precios quedaron solo en un PDF adjunto sin leer. Los números confirmados ya están en `catalogo.md`; esto es el porqué y el detalle. |

## Cuándo algo va acá y cuándo va al `casuistica.md` general

- **Acá**: algo que solo aplica a balanzas — un repuesto nuevo, una duda sobre nivelación,
  cómo se cotiza una plataforma que no encaja en el patrón de la sustento_base.
- **Al general**: algo que revela un problema del sistema completo (un bug del generador, una
  regla de negocio que aplica a todo tipo de servicio). Si hay duda, se anota en ambos con
  referencia cruzada, no se duplica el contenido completo.

## Próximo paso real

✅ Ya hay 4 cotizaciones reales cerradas (analizadas en `casuistica-balanzas.md`) y el costo de
compra de los componentes más usados (Mavin NB2, caja Mavin SS4, indicadores E-Accura y
T-Scale — ver `catalogo.md` y `analisis-proveedor-gufra.md`).

Lo que sigue pendiente: si aplica un piso mínimo por unidad (hoy es `null` en `servicios.json`),
y si el checklist de preguntas pendientes (¿se pinta la estructura?, ¿cuántos trabajadores?)
necesita ser propio de balanzas o sigue compartido. También confirmar el costo de compra del
kit KELI (solo hay un dato suelto de US$520 sin desglosar) y leer los PDF de proformas que
quedaron sin transcribir (ver "Lo que se pidió pero no tiene precio en texto" en
`analisis-proveedor-gufra.md`).
