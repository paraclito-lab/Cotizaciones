# App de cotizaciones (celular)

Formulario web que vive en la cuenta de Google del negocio. No calcula nada: deja el pedido en
`solicitudes/<id>/` de este repositorio, el motor de GitHub
(`.github/workflows/solicitudes.yml` → `herramientas/procesar_solicitud.py`) genera la vista
previa o la cotización emitida, y la app la muestra. Al emitir, guarda el PDF en Drive
(`MUNAY - Cotizaciones/PDF emitidos`) y escribe la fila en el registro.

| Archivo | Qué es |
|---|---|
| `Code.gs` | Servidor: conversa con GitHub, Drive y el registro |
| `Index.html` | Pantalla del celular: formulario, vista previa, emitir |

## Instalación (una vez, desde una computadora)

La app vive en una cuenta de Google **solo para el negocio** (no la cuenta oficial), que recibe
como Editor la carpeta `MUNAY - Cotizaciones` y el registro. Así la app no ve nada más del Drive
oficial y los cotizadores no necesitan ninguna clave de Google: entran con un código personal.

1. Con la cuenta de servicio: **script.google.com → Nuevo proyecto**, nombre `Cotizaciones Munay`.
2. `Código.gs`: borrar lo que hay y pegar `Code.gs`. **+ → HTML**, nombre `Index`, pegar
   `Index.html`. Guardar los dos (Ctrl + S).
3. **Configuración del proyecto**: zona horaria Lima, y en **Propiedades de secuencia de
   comandos** agregar dos:
   - `GITHUB_TOKEN` = el token fine-grained (solo Cotizaciones, Contents: Read and write).
   - `CODIGOS` = `Ana:ana-4821,Luis:luis-9370` (nombre:código, mínimo 6 caracteres, sin espacios).
4. Función **probarConexion → Ejecutar**, aceptar permisos (*Configuración avanzada → Ir a
   Cotizaciones Munay*). Debe terminar en **Todo conectado.**
5. **Implementar → Nueva implementación → Aplicación web**: Ejecutar como **Yo**; Quién tiene
   acceso **Cualquier persona**. Copiar la URL (`.../exec`).
6. En el celular, abrir la URL → **Agregar a la pantalla principal**. Entrar con el código.

## Cambiar el código después

Pegar el archivo nuevo → **Implementar → Administrar implementaciones → editar (lápiz) →
Versión: Nueva versión → Implementar**. La URL no cambia.

## Seguridad

- El token y los códigos viven solo en las propiedades del script. Para dar de baja a un
  cotizador se borra su par de `CODIGOS`; si se pierde un celular se cambia su código. Si se
  sospecha del token, se borra en GitHub y se crea otro.
- Con "Cualquier persona", la URL abre la pantalla de entrada, pero **no se puede ver ni hacer
  nada sin código**: el catálogo, las solicitudes y los resultados lo piden en cada llamada. Tras
  8 códigos incorrectos seguidos se bloquea durante 10 minutos.
- Cada solicitud guarda quién la hizo (`creado_por`).
- La cuenta de servicio solo ve lo que se le comparte (la carpeta y el registro). El token da
  acceso únicamente al repositorio Cotizaciones.
- Las fotos se achican y se vuelven a codificar en el celular: eso borra los metadatos de
  ubicación del archivo. Lo que está **dibujado** en la foto (sello con dirección, mapa) no se
  borra: recortarlo antes de subirla.
