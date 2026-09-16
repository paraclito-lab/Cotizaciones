# Sistema de cotizaciones — en construcción

Repositorio privado, separado de la web pública (`webmunay`), donde se deja por escrito, en
lenguaje claro, las reglas reales con las que se cotiza en LF Munay Perú — antes de
convertirlas en un bot. La idea: que la lógica se pueda revisar, corregir y versionar como
cualquier otro cambio de código, en vez de vivir solo en una conversación de chat.

**Estado**: las reglas, el catálogo y el formato están decididos, y la generación de la
cotización ya está automatizada — ver `plantilla/generar.py` y la skill `cotizar`. El registro
de costos reales se lleva en un Google Sheet aparte y se llena a mano.

## Mapa del repositorio

| Carpeta / archivo | Qué es |
|---|---|
| `criterios-actuales.md` | Las reglas de negocio decididas (mano de obra por localidad, márgenes, checklist, numeración, flujo de aprobación, cómo se interactúa por Telegram). Es el documento que más se actualiza. |
| `catalogo.md` | **Única** fuente de precios de repuestos. Si un precio no está aquí, no es oficial. |
| `servicios.json` | **Única** fuente de los tipos de servicio: qué título lleva cada uno, cómo se redacta su fila, en qué categoría del registro cae y qué palabras lo reconocen. Lo lee el generador. |
| `casuistica.md` | Bitácora de casos nuevos o dudas que no encajan en las reglas actuales. Se agrega, no se borra. |
| `auditoria-2026-09-14.md` | Revisión completa de todo lo construido: vacíos, contradicciones, cuellos de botella y defectos detectados, con el orden sugerido para resolverlos. Leer antes de programar nada. |
| `flujo-completo.md` | El diagrama (mermaid) de punta a punta del proceso, desde la solicitud hasta el registro del costo real. |
| `analisis/` | Por qué se tomó cada decisión: qué tenían de malo los Excel originales y qué reveló la hoja de trabajo real de la balanza de Tarapoto. |
| `ejemplos-reales/` | Cotizaciones reales ya entregadas a clientes, estructuradas, usadas como referencia de formato y precios. |
| `branding/` | Logo y fondo decorativo de la marca. |
| `herramientas/` | Cálculos de apoyo. Hoy: `laminado.py`, que determina cuántos rollos de lámina se necesitan para un conjunto de piezas (no es una división por m²: depende de cómo encajan en el ancho del rollo). |
| `plantilla/` | Cómo se arma el PDF/PNG de cada cotización: una sola imagen real de encabezado (`headers/base.jpg`) + N° y título superpuestos como texto, la plantilla HTML y el generador `generar.py`. |
| `.claude/skills/cotizar/` | La skill que hace todo el proceso: se describe el trabajo en lenguaje natural y devuelve la vista previa y el PDF. |

## Cómo se usa

Cuando algo no está claro en una cotización real, dos caminos:

1. Si bloquea la cotización actual → se pregunta directo (en el chat con Claude o entre
   el equipo).
2. Si es una casuística nueva que no bloquea pero vale la pena registrar para el futuro →
   se anota en `casuistica.md`, y en algún momento se revisa en conjunto para decidir si
   cambia una regla en `criterios-actuales.md`.

