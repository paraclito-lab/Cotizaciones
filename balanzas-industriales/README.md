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

## Cuándo algo va acá y cuándo va al `casuistica.md` general

- **Acá**: algo que solo aplica a balanzas — un repuesto nuevo, una duda sobre nivelación,
  cómo se cotiza una plataforma que no encaja en el patrón de la sustento_base.
- **Al general**: algo que revela un problema del sistema completo (un bug del generador, una
  regla de negocio que aplica a todo tipo de servicio). Si hay duda, se anota en ambos con
  referencia cruzada, no se duplica el contenido completo.

## Próximo paso real

Subir la primera cotización real cerrada a `cotizaciones-reales/`. Con eso se puede empezar a
sacar: precio de repuestos frecuentes (celdas de carga, caja sumatoria, cable multiconductor),
si aplica un piso mínimo por unidad (hoy es `null` en `servicios.json`), y si el checklist de
preguntas pendientes (¿se pinta la estructura?, ¿cuántos trabajadores?) necesita ser propio de
balanzas o sigue compartido.
