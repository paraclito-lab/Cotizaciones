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
