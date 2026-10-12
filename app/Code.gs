/**
 * App de cotizaciones LF Munay Perú (Google Apps Script).
 *
 * La app no calcula nada: arma el pedido, lo deja en el repositorio (solicitudes/<id>/) y
 * espera a que el motor de GitHub (herramientas/procesar_solicitud.py) responda. Así el
 * precio, el IGV, el número y el PDF salen siempre del mismo código y de sus pruebas.
 *
 * Configuración (una sola vez, ver app/README.md):
 *   Proyecto > Configuración > Propiedades del script:
 *     GITHUB_TOKEN  = el token fine-grained (solo el repositorio Cotizaciones, Contents: RW)
 *     CODIGOS       = códigos personales:  Ana:ana-4821,Luis:luis-9370
 * El token nunca va escrito en este archivo.
 */

const REPO = 'paraclito-lab/Cotizaciones';
const RAMA = 'main';
const REGISTRO_ID = '1bsj4PmGSDWN2S8Bb0x5ECIuDAaXtiyU3vVhiys2rb7k';
const CARPETA_PDF_ID = '17Kx_gtJesPAJL-EDT_2N5hkGR4FbcXr0';
const HOJA = 'Cotizaciones';
const FICHA_CARRETILLAS = 'trabajos/mantenimiento-carretillas.json';
const SECCION_CATALOGO = '## Repuestos — Carretillas';

function doGet() {
  return HtmlService.createHtmlOutputFromFile('Index')
    .setTitle('Cotizaciones Munay')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1, maximum-scale=1');
}

/** Primer código de la lista, solo para la prueba de conexión desde el editor. */
function codigoPrueba_() {
  const par = (PropertiesService.getScriptProperties().getProperty('CODIGOS') || '').split(',')[0] || '';
  return par.slice(par.indexOf(':') + 1).trim();
}

/** Correr una vez desde el editor: pide los permisos y revisa que todo esté conectado. */
function probarConexion() {
  const cat = catalogo(codigoPrueba_());
  Logger.log('Catálogo: %s repuestos, %s adicionales', cat.repuestos.length, cat.adicionales.length);
  Logger.log('Registro: %s', SpreadsheetApp.openById(REGISTRO_ID).getName());
  Logger.log('Carpeta de PDF: %s', DriveApp.getFolderById(CARPETA_PDF_ID).getName());
  Logger.log('Todo conectado.');
}

// ------------------------------------------------------------------ acceso

/**
 * Cada cotizador entra con su código personal. Se guardan en la propiedad CODIGOS del script,
 * separados por coma:  Ana:ana-4821,Luis:luis-9370   (nombre:código, mínimo 6 caracteres).
 * Para dar de baja a alguien se borra su par y se guarda. Devuelve el nombre.
 */
function verificarCodigo_(codigo) {
  const cache = CacheService.getScriptCache();
  const fallos = Number(cache.get('fallos') || 0);
  if (fallos >= 8) throw new Error('Demasiados intentos fallidos. Esperar 10 minutos.');
  const lista = (PropertiesService.getScriptProperties().getProperty('CODIGOS') || '')
    .split(',').map(function (par) { return par.trim(); }).filter(String);
  for (let i = 0; i < lista.length; i++) {
    const corte = lista[i].indexOf(':');
    if (corte < 1) continue;
    const clave = lista[i].slice(corte + 1).trim();
    if (clave.length >= 6 && String(codigo || '').trim() === clave) {
      return lista[i].slice(0, corte).trim();
    }
  }
  cache.put('fallos', String(fallos + 1), 600);
  throw new Error('Código incorrecto.');
}

/** La pantalla de entrada llama a esta función: devuelve el nombre si el código es válido. */
function validar(codigo) {
  return verificarCodigo_(codigo);
}

// ------------------------------------------------------------------ GitHub

function gh_(metodo, ruta, cuerpo, crudo) {
  const token = PropertiesService.getScriptProperties().getProperty('GITHUB_TOKEN');
  if (!token) throw new Error('Falta GITHUB_TOKEN en las propiedades del script.');
  const opciones = {
    method: metodo,
    muteHttpExceptions: true,
    headers: {
      Authorization: 'Bearer ' + token,
      Accept: crudo ? 'application/vnd.github.raw' : 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28'
    }
  };
  if (cuerpo) {
    opciones.contentType = 'application/json';
    opciones.payload = JSON.stringify(cuerpo);
  }
  return UrlFetchApp.fetch('https://api.github.com/repos/' + REPO + '/' + ruta, opciones);
}

function ruta_(path) {
  return 'contents/' + path.split('/').map(encodeURIComponent).join('/');
}

/** Archivo del repositorio, o null si todavía no existe. */
function leer_(path) {
  const r = gh_('get', ruta_(path) + '?ref=' + RAMA, null, true);
  if (r.getResponseCode() === 404) return null;
  if (r.getResponseCode() !== 200) {
    throw new Error('GitHub respondió ' + r.getResponseCode() + ' al leer ' + path);
  }
  return r;
}

function subir_(path, base64, mensaje) {
  for (let i = 0; i < 4; i++) {
    const r = gh_('put', ruta_(path), { message: mensaje, content: base64, branch: RAMA });
    const c = r.getResponseCode();
    if (c === 200 || c === 201) return;
    if (c !== 409 && c !== 502 && c !== 503) {
      throw new Error('GitHub respondió ' + c + ': ' + r.getContentText().slice(0, 300));
    }
    Utilities.sleep(1500 * (i + 1));   // el motor estaba guardando al mismo tiempo
  }
  throw new Error('GitHub no aceptó el archivo después de varios intentos: ' + path);
}

// ------------------------------------------------------------------ datos para el formulario

/** Repuestos de carretillas (catalogo.md) y adicionales de la ficha, para autocompletar. */
function catalogo(codigo) {
  verificarCodigo_(codigo);
  const cache = CacheService.getScriptCache();
  const guardado = cache.get('catalogo');
  if (guardado) return JSON.parse(guardado);

  const lineas = leer_('catalogo.md').getContentText('UTF-8').split('\n');
  const repuestos = [];
  let dentro = false;
  lineas.forEach(function (l) {
    if (l.indexOf('## ') === 0) dentro = l.indexOf(SECCION_CATALOGO) === 0;
    if (!dentro || l.indexOf('|') !== 0) return;
    const c = l.replace(/^\||\|$/g, '').split('|').map(function (s) { return s.trim(); });
    const precio = Number((c[1] || '').replace(/,/g, ''));
    if (c.length >= 3 && c[1] !== '' && !isNaN(precio)) {
      repuestos.push({ nombre: c[0], precio: precio });
    }
  });
  const ficha = JSON.parse(leer_(FICHA_CARRETILLAS).getContentText('UTF-8'));
  const adicionales = Object.keys(ficha.adicionales || {}).map(function (id) {
    const a = ficha.adicionales[id];
    return { id: id, nombre: a.descripcion, precio: a.precio_ref };
  });
  const res = { repuestos: repuestos, adicionales: adicionales,
                piso: (ficha.precio_referencia || {}).piso || null };
  cache.put('catalogo', JSON.stringify(res), 3600);
  return res;
}

// ------------------------------------------------------------------ solicitudes

/**
 * datos = {grupo, modo: 'vista'|'emitir', pedido, fotos: [{nombre, base64}]}
 * Las fotos se suben una vez por grupo (solicitudes/<grupo>/fotos/) y cada versión del
 * pedido las nombra con ruta relativa. La solicitud se sube al final: es la que activa el motor.
 */
function enviar(datos) {
  const usuario = verificarCodigo_(datos.codigo);
  if (['vista', 'emitir'].indexOf(datos.modo) < 0) throw new Error('Modo inválido.');
  if (!/^[0-9a-z-]{8,40}$/.test(datos.grupo || '')) throw new Error('Grupo inválido.');
  const sello = Utilities.formatDate(new Date(), 'America/Lima', 'HHmmss');
  const id = datos.grupo + (datos.modo === 'emitir' ? '-emitir-' : '-v') + sello;

  (datos.fotos || []).forEach(function (f) {
    if (!/^[0-9a-z-]+\.jpg$/.test(f.nombre)) throw new Error('Nombre de foto inválido.');
    subir_('solicitudes/' + datos.grupo + '/fotos/' + f.nombre, f.base64,
           'Foto de la solicitud ' + datos.grupo);
  });

  const solicitud = {
    id: id, grupo: datos.grupo, modo: datos.modo, creado_por: usuario,
    creado: new Date().toISOString(), pedido: datos.pedido
  };
  subir_('solicitudes/' + id + '/solicitud.json',
         Utilities.base64Encode(JSON.stringify(solicitud, null, 1), Utilities.Charset.UTF_8),
         (datos.modo === 'emitir' ? 'Emitir' : 'Vista previa') + ' desde la app (' + id + ')');
  return { id: id };
}

/** Lo que respondió el motor. Si la cotización se emitió, guarda el PDF y la fila (una vez). */
function consultar(id, codigo) {
  verificarCodigo_(codigo);
  if (!/^[0-9a-z-]{8,60}$/.test(id || '')) throw new Error('Solicitud inválida.');
  const r = leer_('solicitudes/' + id + '/salida/resultado.json');
  if (!r) return { estado: 'pendiente' };
  const res = JSON.parse(r.getContentText('UTF-8'));
  delete res.detalle;
  if (res.estado !== 'ok') return res;
  const png = leer_('solicitudes/' + id + '/salida/' + res.png);
  res.imagen = 'data:image/png;base64,' + Utilities.base64Encode(png.getContent());
  if (res.modo === 'emitir') res.entrega = registrar_(id, res);
  delete res.registro;
  return res;
}

function registrar_(id, res) {
  const props = PropertiesService.getScriptProperties();
  const clave = 'emitida_' + id;
  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const hecho = props.getProperty(clave);
    if (hecho) return JSON.parse(hecho);

    const pdf = leer_('solicitudes/' + id + '/salida/' + res.pdf);
    const archivo = DriveApp.getFolderById(CARPETA_PDF_ID)
      .createFile(pdf.getBlob().setName(res.pdf).setContentType('application/pdf'));

    const hoja = SpreadsheetApp.openById(REGISTRO_ID).getSheetByName(HOJA);
    const colA = hoja.getRange('A3:A' + hoja.getMaxRows()).getValues();
    const g = res.registro;
    let fila = -1;
    for (let i = 0; i < colA.length; i++) {
      if (String(colA[i][0]) === g.numero) { fila = i + 3; break; }     // ya registrada
      if (colA[i][0] === '' && fila < 0) { fila = i + 3; break; }
    }
    if (fila < 0) throw new Error('El registro no tiene filas libres: agregar filas con fórmulas.');
    const f = g.fecha_iso.split('-').map(Number);
    hoja.getRange(fila, 1, 1, 12).setValues([[
      g.numero, new Date(f[0], f[1] - 1, f[2]), g.cliente, g.local, g.tipo, g.subtipo,
      g.descripcion, g.unidades, g.subtotal, g.igv, g.total, 'Cotizado']]);
    hoja.getRange(fila, 26, 1, 3).setValues([[
      g.costo_estimado === null ? '' : g.costo_estimado,
      g.subtotal_calculado === null ? '' : g.subtotal_calculado,
      g.nota_interna]]);

    const entrega = { pdf: res.pdf, url: archivo.getUrl(), id: archivo.getId(), fila: fila };
    props.setProperty(clave, JSON.stringify(entrega));
    return entrega;
  } finally {
    lock.releaseLock();
  }
}
