# Bitácora de casuística — cotizaciones

Registro de casos nuevos, excepciones y anomalías que aparecen con el uso real del sistema de
cotización. No se borra nada, solo se agrega. Sirve para decidir, en conjunto, si algo debe
convertirse en una regla nueva dentro de `criterios-actuales.md`.

## Plantilla para cada caso nuevo

```
### [Fecha] — [Título corto del caso]

- **Contexto**: ¿qué cotización o trabajo lo originó?
- **Qué pasó / qué no encajaba en las reglas actuales**:
- **Cómo se resolvió esta vez**:
- **¿Debería ser una regla permanente?** (sí / no / a evaluar)
```

## Casos registrados

### 14/09/2026 — Título de servicio no coincidía con el contenido

- **Contexto**: prueba de la plantilla para demostrar que el título del encabezado ahora es
  texto editable (ver `plantilla/README.md`). Se cambió el título de "MANTENIMIENTO DE
  CARRETILLAS HIDRÁULICAS" a "MANTENIMIENTO DE BALANZAS" para probar.
- **Qué pasó**: el título cambió, pero la tabla de "sustento técnico" se dejó igual (contenido
  de repuestos de carretillas), quedando una cotización incoherente — título de balanza con
  contenido de carretilla.
- **Cómo se resolvió esta vez**: se rehizo el ejemplo con contenido real de balanza (tomado de
  `analisis/tarapoto-excel.md`), y se documentó la regla en `criterios-actuales.md` punto 8.
- **¿Debería ser una regla permanente?** Sí — ya se agregó como regla de coherencia
  título↔contenido en `criterios-actuales.md`.

### 14/09/2026 — El PDF salía en vertical y quedaba con media hoja en blanco

- **Contexto**: primera prueba del generador (`plantilla/generar.py`) con una cotización de 4
  ítems.
- **Qué pasó**: el PNG se veía bien, pero el PDF salía en A4 vertical con el contenido apenas
  ocupando el tercio superior de la hoja. Se veía como un documento mal armado.
- **Cómo se resolvió esta vez**: se revisó el PDF real ya entregado (Moyobamba N°100) y resultó
  medir 841.8 × 595.2 pts, es decir **A4 horizontal** — el formato vertical nunca fue el de la
  empresa. Se cambió el generador a apaisado y se le agregó un cálculo de escala que mide el
  alto real del contenido para llenar la hoja sin cortar.
- **¿Debería ser una regla permanente?** Sí — ya está en `plantilla/README.md`. Aprendizaje de
  fondo: **ante una duda de formato, medir el PDF real en vez de asumir el valor por defecto.**
