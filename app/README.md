# App de cotizaciones (celular)

Formulario web que vive en la cuenta de Google del negocio. No calcula nada: deja el pedido en
`solicitudes/<id>/` de este repositorio, el motor de GitHub
(`.github/workflows/solicitudes.yml` → `herramientas/procesar_solicitud.py`) genera la vista
previa o la cotización emitida, y la app la muestra. Al emitir, guarda el PDF en Drive
(`MUNAY - Cotizaciones/PDF emitidos`) y escribe la fila en el registro.

| Archivo | Qué es |
|---|---|
| `Code.gs` | Servidor: conversa con GitHub, Drive y el registro |
| `Index.html` | Pantalla del celular: formulario, vista previa, emitir, registrar gasto |

## Registrar gasto

Segunda pestaña de la app. Se usa en el momento en que se gasta, con el mismo código personal.

- **Obligatorio:** fecha, monto pagado y categoría (la lista está en `CATEGORIAS_GASTO`, al
  inicio de `Code.gs`).
- **A qué corresponde:** activo (equipo), cliente, local o una descripción; basta con uno. No
  lleva N° de cotización.
- **Opcional:** tipo de comprobante y su foto. Con **factura**, la columna "Costo sin IGV" guarda
  el monto ÷ 1.18 (el IGV es crédito fiscal); con boleta o sin comprobante, el monto completo.

No pasa por GitHub: escribe directo en la hoja **Gastos** del registro (la crea sola la primera
vez) y guarda la foto en la carpeta **Comprobantes de gastos**, junto a `PDF emitidos` (si a la
cuenta de la app solo se le compartió `PDF emitidos`, la crea dentro de esa). Los
gastos son dato financiero y no se versionan en el repositorio. Cada gasto lleva un ID que
genera el celular: si se corta la conexión y se vuelve a tocar "Guardar", no se duplica. La
columna "Registrado por" sale del código personal.

Si alguien está en esta pestaña cuando llega una vista previa que pidió, la app no lo saca del
gasto: la pestaña **Cotizar** muestra un punto amarillo hasta que vuelva a ella.

Después de publicar esta versión, correr **probarConexion** una vez: crea la hoja y la carpeta,
y pide el permiso nuevo si hiciera falta.

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

No usar **Nueva implementación** para actualizar: crea otra URL, y si se archiva la anterior,
los accesos guardados en los celulares dejan de abrir.

## Si la app no abre

| Lo que aparece | Causa | Qué hacer |
|---|---|---|
| Página de Drive: *No se pudo abrir el archivo en este momento* | La URL es de una implementación archivada, o tiene `/u/0/`, `/u/1/` (varias cuentas de Google abiertas en el navegador) | **Administrar implementaciones** → la implementación **activa** → copiar su URL con el botón. Debe ser `https://script.google.com/macros/s/…/exec`, sin `/u/N/`. Probarla en una ventana de incógnito. En el celular, borrar el acceso viejo de la pantalla principal y crearlo con la URL nueva |
| *No se encontró el archivo HTML llamado Index* | La versión implementada es anterior al archivo `Index` | Revisar que el archivo se llame `Index` (sin `.html`) y publicar **Nueva versión** de la misma implementación |
| Pide iniciar sesión en Google | La implementación no tiene acceso **Cualquier persona** | Editar la implementación activa → Quién tiene acceso: **Cualquier persona** |
| *Código incorrecto* | El código no está en `CODIGOS`, o tiene espacios | Revisar la propiedad del script |
| *Demasiados intentos fallidos* | 8 códigos incorrectos seguidos en ese celular | Esperar 10 minutos, o en el editor: **desbloquear → Ejecutar** |

## Seguridad

- El token y los códigos viven solo en las propiedades del script. Para dar de baja a un
  cotizador se borra su par de `CODIGOS`; si se pierde un celular se cambia su código. Si se
  sospecha del token, se borra en GitHub y se crea otro.
- Con "Cualquier persona", la URL abre la pantalla de entrada, pero **no se puede ver ni hacer
  nada sin código**: el catálogo, las solicitudes y los resultados lo piden en cada llamada.
- Tras 8 códigos incorrectos seguidos se bloquea **ese celular** 10 minutos (los demás siguen
  entrando); acertar el código reinicia la cuenta. Si entre todos los celulares suman 30 fallos,
  se bloquea la entrada para todos 10 minutos. Los tres números están al inicio de `Code.gs`
  (`INTENTOS`, `INTENTOS_TOTAL`, `BLOQUEO_MIN`). Para desbloquear antes: en el editor, función
  **desbloquear → Ejecutar** (no hace falta publicar nada).
- Cada solicitud guarda quién la hizo (`creado_por`).
- La cuenta de servicio solo ve lo que se le comparte (la carpeta y el registro). El token da
  acceso únicamente al repositorio Cotizaciones.
- Las fotos se achican y se vuelven a codificar en el celular: eso borra los metadatos de
  ubicación del archivo. Lo que está **dibujado** en la foto (sello con dirección, mapa) no se
  borra: recortarlo antes de subirla.
