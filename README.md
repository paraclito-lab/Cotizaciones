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
| `trabajos/` | **Biblioteca de trabajos**: una ficha por trabajo con su checklist, sus costos (fijos por visita y por unidad), su redacción y lo que ya se cobró. Con la ficha, cotizar es llenar un pedido de pocas líneas; un trabajo nuevo se agrega con `herramientas/nuevo_trabajo.py`. Ver su README. |
| `servicios.json` | **Única** fuente de los tipos de servicio: qué título lleva cada uno, cómo se redacta su fila, en qué categoría del registro cae y qué palabras lo reconocen. Lo lee el generador. |
| `casuistica.md` | Bitácora de casos nuevos o dudas que no encajan en las reglas actuales. Se agrega, no se borra. |
| `hallazgos-abiertos.md` | **Lista de trabajo única** de lo que está mal, falta o se contradice, con evidencia verificada y prioridad. Reemplaza como lista de pendientes a las auditorías de abajo, que quedan como historia. Un hallazgo se cierra marcándolo, no borrándolo. |
| `auditoria-2026-09-14.md` | Revisión completa de todo lo construido: vacíos, contradicciones, cuellos de botella y defectos detectados, con el orden sugerido para resolverlos. Leer antes de programar nada. |
| `auditoria-ia-2026-09-17.md` | Auditoría del sistema de IA en sí: qué cuesta operarlo (medido del log real, no estimado), los casos borde que hoy dejan salir cotizaciones inválidas, los datos de cliente expuestos en el repo, y el tablero de KPI con los campos exactos del JSONL. |
| `auditoria-arquitectura-2026-09-19.md` | Qué patrones ya probados de la industria (rules engine, costeo ABC, cutting stock, aprobación humana) coinciden con lo que ya se construyó acá, y las 5 recomendaciones concretas para consolidar lo que hoy sigue repartido entre código y prosa. |
| `flujo-sistema-completo.md` | **Mapa del sistema como sistema**: diagrama maestro de las 8 fases, SIPOC por subproceso (entrada, salida, audiencia), clasificación de datos (maestro/transaccional/derivado), matriz de qué regla valida el código y cuál solo la prosa, y estado de automatización de cada paso. |
| `flujo-completo.md` | El diagrama (mermaid) de punta a punta del proceso de negocio, desde la solicitud hasta el registro del costo real. |
| `analisis/` | Por qué se tomó cada decisión: qué tenían de malo los Excel originales y qué reveló la hoja de trabajo real de la balanza de Tarapoto. |
| `ejemplos-reales/` | Cotizaciones reales ya entregadas a clientes, estructuradas, usadas como referencia de formato y precios. |
| `balanzas-industriales/` | Carpeta especializada solo para balanzas: cotizaciones reales cerradas (`cotizaciones-reales/`) y su propia bitácora de casuística (`casuistica-balanzas.md`). Existe porque balanzas es el tipo de servicio con menos data real hoy — ver el README de la carpeta. |
| `branding/` | Logo y fondo decorativo de la marca. |
| `herramientas/` | `cotizar_trabajo.py` (pedido + ficha → costeo, propuesta de precio y JSON de la cotización), `nuevo_trabajo.py` (agrega un trabajo respondiendo preguntas), `probar.py` (**pruebas de regresión**: correrlas antes de subir cualquier cambio), `armar_registro.py` (reconstruye el registro de costos), y los cálculos de apoyo: `laminado.py`, `dibujar_rollos.py`, `precio.py`, `costo_sesion.py`, `flujo-calculo.md`. |
| `plantilla/` | Cómo se arma el PDF/PNG de cada cotización: una sola imagen real de encabezado (`headers/base.jpg`) + N° y título superpuestos como texto, la plantilla HTML y el generador `generar.py`. |
| `.claude/skills/cotizar/` | La skill que hace todo el proceso: se describe el trabajo en lenguaje natural y devuelve la vista previa y el PDF. |

## Cómo se usa

Cuando algo no está claro en una cotización real, dos caminos:

1. Si bloquea la cotización actual → se pregunta directo (en el chat con Claude o entre
   el equipo).
2. Si es una casuística nueva que no bloquea pero vale la pena registrar para el futuro →
   se anota en `casuistica.md`, y en algún momento se revisa en conjunto para decidir si
   cambia una regla en `criterios-actuales.md`.

