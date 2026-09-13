# Sistema de cotizaciones — en construcción

Repositorio privado, separado de la web pública (`webmunay`), donde se deja por escrito, en
lenguaje claro, las reglas reales con las que se cotiza en LF Munay Perú — antes de
convertirlas en un bot. La idea: que la lógica se pueda revisar, corregir y versionar como
cualquier otro cambio de código, en vez de vivir solo en una conversación de chat.

**Nada de esto está automatizado todavía.** Es toda la etapa de diseño: reglas, catálogo,
formato del PDF/PNG y flujo de aprobación, ya decididos y listos para programarse.

## Mapa del repositorio

| Carpeta / archivo | Qué es |
|---|---|
| `criterios-actuales.md` | Las reglas de negocio decididas (mano de obra por localidad, márgenes, checklist, numeración, flujo de aprobación, cómo se interactúa por Telegram). Es el documento que más se actualiza. |
| `catalogo.md` | **Única** fuente de precios de repuestos. Si un precio no está aquí, no es oficial. |
| `casuistica.md` | Bitácora de casos nuevos o dudas que no encajan en las reglas actuales. Se agrega, no se borra. |
| `flujo-completo.md` | El diagrama (mermaid) de punta a punta del proceso, desde la solicitud hasta el registro del costo real. |
| `analisis/` | Por qué se tomó cada decisión: qué tenían de malo los Excel originales y qué reveló la hoja de trabajo real de la balanza de Tarapoto. |
| `ejemplos-reales/` | Cotizaciones reales ya entregadas a clientes, estructuradas, usadas como referencia de formato y precios. |
| `branding/` | Logo y fondo decorativo de la marca. |
| `plantilla/` | Cómo se arma el PDF/PNG de cada cotización (imágenes de encabezado por tipo de servicio + texto dinámico superpuesto) y las coordenadas exactas para agregar un tipo de servicio nuevo. |

## Cómo se usa

Cuando algo no está claro en una cotización real, dos caminos:

1. Si bloquea la cotización actual → se pregunta directo (en el chat con Claude o entre
   el equipo).
2. Si es una casuística nueva que no bloquea pero vale la pena registrar para el futuro →
   se anota en `casuistica.md`, y en algún momento se revisa en conjunto para decidir si
   cambia una regla en `criterios-actuales.md`.

## Dueño del proyecto

**alopez** es el dueño de LF Munay Perú y quien inició esta automatización desde el principio.
Las reglas de `criterios-actuales.md` que dicen "el equipo confirma/decide" se refieren a
alopez como responsable final.
