# Flujo completo del proceso de cotización

Diagrama de referencia de punta a punta: desde que llega la solicitud hasta que el correo sale
y se retroalimenta el sistema con el costo real. Cada bloque corresponde a una regla ya
decidida en `criterios-actuales.md`.

```mermaid
flowchart TD
    A[Solicitud de cotización] --> B[Recolectar datos:\ntipo de equipo, cantidad,\nlocal/cliente, ubicación]
    B --> C{Checklist del tipo\nde servicio resuelto?}
    C -->|No| C1[Bloquea: preguntas pendientes\nej. pintura, N° trabajadores,\ncosto real de pasaje]
    C1 -.resolver.-> C
    C -->|Sí| D[Buscar repuestos en\ncatalogo.md — precio fijo,\nno cambia por zona]

    D --> E{Ubicación}
    E -->|Lima / Local| F["Mano de obra = personas x tarifa\n(S/100 o S/200) x 2\n(amanecida = doble día)"]
    E -->|Provincia| G{Hay personal\nen la zona?}
    G -->|Sí| H[Personal local cotiza\nsu propia mano de obra]
    G -->|No / muy caro| I[Evaluar enviar equipo desde Lima\n+ pasajes + viáticos + encomienda]

    F --> J[Costo total =\nmano de obra + repuestos + logística]
    H --> J
    I --> J

    J --> K["Margen sugerido 60-80%\n(NO automático)"]
    K --> L[Ajustar a número redondo\nej. 2490, 2980]
    L --> M[Generar cotización\ndesde plantilla HTML\nN° COT-AAAA-NNN]

    M --> N{Validación automática:\nsin ítems S/0, IGV correcto,\nmargen en rango, checklist ok}
    N -->|Falla algo| M
    N -->|OK| O[Renderizar PNG\nde vista previa]

    O --> P[Enviar preview por Telegram\nal especialista]
    P --> Q{Especialista revisa}
    Q -->|Pide corrección| M
    Q -->|Aprueba: 'envíalo'| R[Renderizar PDF final\ncon el mismo template]

    R --> S["Marcar 'Lista para enviar'\n(el bot NO envía el correo)"]
    S --> T[Notificar a responsable\npara enviar desde Gmail]
    T --> U[Registrar en Histórico:\nquién pidió, correcciones,\nquién aprobó, cuándo se envió]

    U --> V{Después del trabajo:\n¿se registró costo real?}
    V -->|No| V1[Pendiente: seguimiento de\ncosto real vs. cotizado]
    V -->|Sí| W[Comparar margen real\nvs. margen cotizado]
    W --> X[Alimenta catalogo.md\ny criterios para la\npróxima cotización]

    V1 -.anotar caso.-> Y[casuistica.md]
    Q -->|Caso raro / duda nueva| Y
```

## Formato de la vista previa (paso "Renderizar PNG") — decidido

**Imagen PNG**, no PDF ni texto plano, enviada como foto en Telegram. Razón: una imagen se ve
inline al instante en el chat (sin tocar ni descargar nada), y sí muestra el diseño real
(logo, colores, tabla) — a diferencia del texto plano. Un PDF sí muestra el formato, pero en
Telegram llega como documento que hay que abrir aparte, un paso extra en cada revisión.

Para no duplicar trabajo ni arriesgar que la vista previa y el PDF final se vean distintos: se
arma **una sola plantilla HTML** por tipo de servicio, hecha de la imagen real del encabezado
(logo, marca, curvas, título del servicio) + el N° de cotización superpuesto como texto real
(ver `plantilla/README.md` para el detalle técnico y por qué no se recreó el diseño desde
cero). Esa misma plantilla se renderiza a PNG para la vista previa rápida, y a PDF solo cuando
ya está aprobada, para el envío real por correo.
