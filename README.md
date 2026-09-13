# Sistema de cotizaciones — en construcción

Repositorio privado, separado de la web pública (`webmunay`), donde se deja por escrito, en
lenguaje claro, las reglas reales con las que Gera (LF Munay Perú) cotiza — antes de
convertirlas en un Excel o un bot. La idea: que la lógica se pueda revisar, corregir y
versionar como cualquier otro cambio de código, en vez de vivir solo en una conversación de
chat.

## Archivos de este repositorio

- **criterios-actuales.md** — la "foto" más reciente de las reglas de cotización ya
  confirmadas por Gera (personal por tipo de equipo, tarifas, márgenes, etc.). Se actualiza
  cada vez que se confirma o corrige un criterio.
- **casuistica.md** — bitácora de casos nuevos, excepciones y dudas que van apareciendo con
  el uso real (ej: un tipo de trabajo no contemplado, un cliente que pidió algo raro, un
  precio que no cuadró). No se borra nada, solo se agrega — sirve como historial de por qué
  el sistema cambió de una forma u otra.

## Cómo se usa

Cuando algo no está claro en una cotización real, dos caminos:

1. Si bloquea la cotización actual → se pregunta directo (en el chat con Claude o entre
   el equipo).
2. Si es una casuística nueva que no bloquea pero vale la pena registrar para el futuro →
   se anota en `casuistica.md` con la plantilla de abajo, y en algún momento se revisa en
   conjunto para decidir si cambia una regla en `criterios-actuales.md`.
