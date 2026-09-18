# Bitácora de casuística — balanzas industriales

Versión especializada de `casuistica.md` (raíz), solo para casos, dudas y excepciones propias
de balanzas. No se borra nada, solo se agrega. Un caso que resulta ser un problema del sistema
completo (no solo de balanzas) se anota en el `casuistica.md` general, no aquí — si hay duda,
se referencia en ambos en vez de duplicar el contenido completo.

## Plantilla para cada caso nuevo

```
### [Fecha] — [Título corto del caso]

- **Contexto**: ¿qué cotización o trabajo lo originó?
- **Qué pasó / qué no encajaba en las reglas actuales**:
- **Cómo se resolvió esta vez**:
- **¿Debería ser una regla permanente?** (sí / no / a evaluar)
```

## Casos registrados

### 18/09/2026 — Comparación de las 4 primeras cotizaciones reales: por qué solo se aprobó una

- **Contexto**: se subieron 4 cotizaciones reales de balanza a `cotizaciones-reales/`
  (8202-2026, 3032-2026, 6112-2026, 7171-2026). Solo una fue aprobada por el cliente: la
  **3032-2026 (HB Precio Uno, Ica Panamericana, S/5,785 subtotal)**.

- **Los 4 casos, lado a lado**:

  | N° | Fecha | Cliente / Local | Marca de equipo | Alcance | Subtotal | ¿Aprobada? |
  |---|---|---|---|---|---|---|
  | 8202-2026 | 21/08/2026 | Tottus, Olivos | Marvin (celdas NB21T, caja SS4) | Mantenimiento completo, **4 celdas** explícitas, sin indicador aparte | S/7,690.00 | No |
  | **3032-2026** | 03/03/2026 | **HB Precio Uno, Ica Panamericana** | **Marvin** (celdas NB2-1T, caja SS4) | Mismo mantenimiento, celdas **sin cantidad explícita**, sin indicador aparte | **S/5,785.00** | **Sí** |
  | 6112-2026 | 11/06/2026 | HB, Tarapoto | KELI (kit celdas SQB-AA 1T + patas SQB-SS 1T + caja 4 canales) | Mantenimiento + kit KELI completo + indicador T-Scale BW aparte | S/9,870.00 | No |
  | 7171-2026 | 17/07/2026 | HB Precio Uno, Moyobamba | KELI (idéntico al 6112) | Idéntico al 6112, mismas 2 filas | S/9,870.00 | No |

- **Qué explica la aprobación — en orden de peso**:

  1. **Precio, el factor más visible**: S/5,785 es el subtotal más bajo de los 4, por buen
     margen (33% menos que el siguiente más barato). El mismo cliente (HB) rechazó dos
     cotizaciones a S/9,870 y aprobó una a S/5,785 — evidencia directa de sensibilidad al
     precio en este cliente específico.
  2. **Marca del equipo, la causa probable detrás del precio**: las dos cotizaciones caras
     (6112, 7171) usan **KELI** (kit de celdas + patas + caja de 4 canales, todo como
     suministro nuevo). Las dos baratas (8202, 3032) usan **Marvin** (celdas + caja
     sumatoria, sin mencionar patas de apoyo como ítem aparte). Marvin sale más barato que
     KELI en este conjunto — o KELI trae más piezas nuevas (el kit de patas de apoyo no
     aparece en las cotizaciones Marvin).
  3. **Alcance menor**: la aprobada (3032) es la única de las 4 que **no** lleva un
     indicador de peso nuevo como línea aparte (T-Scale BW, S/1,350 en las KELI). Reemplazar
     menos piezas es coherente con costar menos.
  4. **Redacción menos específica**: 3032 dice "Cambio de celdas de carga Marvin NB2-1T" sin
     decir cuántas; 8202 sí especifica "04". Puede ser solo estilo de redacción, o puede
     significar que se cambiaron menos de 4 celdas — no hay forma de confirmarlo con el PDF
     solo.

- **Hallazgo aparte, no explica la aprobación pero es un defecto real**: las 4 cotizaciones
  tienen título distinto para el mismo tipo de trabajo — "MANTENIMIENTO DE BALANZAS" (8202),
  **"SERVICIOS GENERALES"** (3032, la aprobada — un título que no dice que es una balanza),
  "MANTENIMIENTO DE BALANZAS INDUSTRIALES" (6112) y "MANTENIMIENTO DE BALANZAS ELECTRONICAS"
  (7171). Es exactamente la incoherencia título↔contenido que `criterios-actuales.md` punto 8
  y `servicios.json` existen para prevenir — pero estas 4 son anteriores al sistema actual,
  así que no la rompieron: simplemente muestran por qué la regla hacía falta. De aquí en
  adelante, `servicios.json` ya fuerza un solo título ("Mantenimiento de balanzas") para todas.

- **Lo que NO se puede saber con estos 4 PDFs**: el costo real de cada repuesto por separado
  (celda individual, caja sumatoria sola) — los 4 cotizan el mantenimiento como paquete, nunca
  desglosado por pieza. No se puede armar `catalogo.md` de repuestos de balanza con esto solo;
  hace falta el costo de compra real, no el precio de venta empaquetado.

- **¿Debería ser una regla permanente?** A evaluar con más casos. Con 4 cotizaciones (2 pares
  casi idénticos) es una señal, no todavía un patrón confirmado. Vale la pena, en la próxima
  cotización real, anotar explícitamente la marca del equipo y si el cliente pidió mejorar el
  precio antes de aprobar — hoy esos dos datos no quedan en ningún lado del registro.
