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

## Instalación (una vez, desde una computadora, con la cuenta del negocio)

1. Entrar a **script.google.com** con la cuenta del negocio → **Nuevo proyecto**. Nombre:
   `Cotizaciones Munay`.
2. Borrar el contenido de `Código.gs` y pegar el de `Code.gs`.
3. **+ → HTML**, nombre exacto `Index` (sin `.html`), y pegar el contenido de `Index.html`.
4. **Configuración del proyecto** (engranaje):
   - Zona horaria: **(GMT-05:00) Lima**.
   - **Propiedades del script → Agregar propiedad**: `GITHUB_TOKEN` = el token de GitHub.
     El token no se escribe en ningún otro lugar.
5. Volver al editor, elegir la función **probarConexion** y **Ejecutar**. Google pide permisos
   (Drive, Hojas de cálculo, conexión a servicios externos): aceptar. Si aparece "Google no
   verificó esta app", entrar a *Configuración avanzada → Ir a Cotizaciones Munay*: la app es
   de la misma cuenta. El registro de ejecución debe terminar en **Todo conectado.**
6. **Implementar → Nueva implementación → Aplicación web**:
   - Ejecutar como: **Yo**
   - Quién tiene acceso: **Solo yo**
   - Copiar la URL de la aplicación web.
7. En el celular, con la cuenta del negocio abierta en Chrome: abrir la URL → menú ⋮ →
   **Agregar a la pantalla principal**.

## Cambiar el código después

Pegar el archivo nuevo → **Implementar → Administrar implementaciones → editar (lápiz) →
Versión: Nueva versión → Implementar**. La URL no cambia.

## Seguridad

- El token vive solo en las propiedades del script. Si se pierde un celular o alguien deja de
  cotizar, se borra el token en GitHub y se crea otro.
- Publicada como "Solo yo", solo la cuenta del negocio puede abrirla. Dar acceso a otro
  correo necesita un ajuste: con cuentas Gmail personales, Google no le dice a la app quién
  la abre si se ejecuta como el dueño. Pedirlo antes de cambiar el acceso.
- Las fotos se achican y se vuelven a codificar en el celular: eso borra los metadatos de
  ubicación del archivo. Lo que está **dibujado** en la foto (sello con dirección, mapa) no se
  borra: recortarlo antes de subirla.
