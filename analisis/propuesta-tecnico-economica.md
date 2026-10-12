# Propuesta técnico-económica — recomendación (pendiente de decidir)

Fecha: 08/10/2026. Estado: **recomendación, no construida**. Falta una decisión (ver al final).

## De dónde sale

El curso "Full Day IA" trae una receta de propuesta comercial (Proyecto 02, en el repo
`IA-FULL-HERRAMIENTAS`: `02-notas/2026-09-proyecto-02-propuesta-comercial.md`). No es un skill
instalable: son dos prompts a Claude que redactan un .docx de 6 páginas (portada, resumen
ejecutivo, diagnóstico, solución por fases, metodología, cronograma, **pricing con 3 paquetes**,
términos) y Gamma lo convierte en 10 slides.

Comparada con este sistema:

| | Receta del curso | Este sistema (`cotizar`) |
|---|---|---|
| Precio | Lo redacta la IA en el momento; la única defensa es "revisar precios" a mano | Sale de `catalogo.md` y de las fichas; el generador bloquea texto interno |
| Memoria | Ninguna: cada propuesta desde cero | Fichas, catálogo, `cotizaciones-emitidas/` |
| Trazabilidad | Sin N°, sin archivo, sin registro | N°, archivo, fila del registro, pruebas de regresión |
| Lo que aporta | Formato de venta: diagnóstico, alcance por fases, cronograma | Solo tabla técnica con precio |

Lo único que vale traer es **el formato**. El riesgo de la receta (3 paquetes con precio sin
tarifario: la IA inventa precios) es justo lo que este sistema ya resolvió.

## Recomendación

No crear una herramienta aparte (duplicaría catálogo, numeración y registro) ni una más
grande. Agregar al mismo generador un segundo formato de salida:

```
Pedido → ficha/checklist → costeo (catálogo) → [regla de decisión] → Cotización (PNG/PDF)
                                                                     ↘ Propuesta técnico-económica (PDF)
         → misma aprobación → mismo N° → mismo archivo → misma fila del registro
```

- **Regla de decisión escrita**, no criterio del momento: la propuesta sale solo si se cumple
  una condición (por tipo, cliente nuevo o monto). Lo demás sigue como cotización simple.
- **Los 3 paquetes pasan a ser 3 alcances** (p. ej. correctivo / correctivo + preventivo /
  completo con garantía), cada uno costeado desde la ficha y el catálogo. La IA redacta
  diagnóstico y alcance; el precio nunca.
- **Sin Gamma.** Si un cliente pide presentación, se arma desde el mismo JSON.

## PHVA

| | Hoy | Se agrega |
|---|---|---|
| Planificar | Fichas, checklist, criterios | Regla de cuándo sale propuesta y plantilla de alcances |
| Hacer | `generar.py`, `cotizar_trabajo.py` | Modo `--propuesta` en el mismo generador |
| Verificar | `probar.py`, aprobación, registro | Caso de regresión de propuesta y columna "formato" en el registro |
| Actuar | Casuística → criterios al cierre de mes | Si la propuesta no gana más que la cotización simple, se retira |

## Falta decidir

¿Qué dispara la propuesta en vez de la cotización simple? Tipo de servicio (balanzas,
estructuras), cliente nuevo, un monto mínimo, o una combinación.
