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

// Gastos operativos: hoja del mismo registro y carpeta de comprobantes junto a "PDF emitidos".
const HOJA_GASTOS = 'Gastos';
const CARPETA_COMPROBANTES = 'Comprobantes de gastos';
const CATEGORIAS_GASTO = ['Repuestos y materiales', 'Mano de obra', 'Pasajes y viáticos',
  'Transporte y combustible', 'Consumibles', 'SCTR y EPP', 'Herramientas', 'Otros'];
const COMPROBANTES = ['Sin comprobante', 'Boleta', 'Factura', 'Otro'];
// El gasto se registra con IGV, tal cual se pagó (decidido 12/10/2026, criterios §13).
const COLUMNAS_GASTOS = ['Fecha', 'Categoría', 'Monto pagado con IGV (S/)', 'Comprobante',
  'Cliente', 'Local', 'Activo', 'Descripción', 'Foto del comprobante',
  'Registrado por', 'Registrado el', 'ID'];

// Bloqueo por códigos incorrectos. Se pueden cambiar; vale al publicar una versión nueva.
const INTENTOS = 8;          // seguidos en un mismo celular: bloquea ese celular
const INTENTOS_TOTAL = 30;   // entre todos los celulares: frena a quien pruebe códigos al azar
const BLOQUEO_MIN = 10;      // minutos que dura el bloqueo

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
  Logger.log('Hoja de gastos: %s', hojaGastos_().getName());
  Logger.log('Carpeta de comprobantes: %s', carpetaComprobantes_().getName());
  Logger.log('Todo conectado.');
}

// ------------------------------------------------------------------ acceso

/**
 * Cada cotizador entra con su código personal. Se guardan en la propiedad CODIGOS del script,
 * separados por coma:  Ana:ana-4821,Luis:luis-9370   (nombre:código, mínimo 6 caracteres).
 * Para dar de baja a alguien se borra su par y se guarda. Devuelve el nombre.
 * equipo: identificador al azar que cada celular guarda, para bloquear solo al que se equivoca.
 */
function verificarCodigo_(codigo, equipo) {
  const cache = CacheService.getScriptCache();
  const ronda = cache.get('ronda') || '0';
  const total = 'fallos-' + ronda;
  const propio = total + '-' + (/^[0-9a-z]{8,40}$/.test(equipo || '') ? equipo : 'sin-equipo');
  const fallos = Number(cache.get(propio) || 0);
  const fallosTotal = Number(cache.get(total) || 0);
  if (fallos >= INTENTOS || fallosTotal >= INTENTOS_TOTAL) {
    throw new Error('Demasiados intentos fallidos. Esperar ' + BLOQUEO_MIN + ' minutos.');
  }
  const lista = (PropertiesService.getScriptProperties().getProperty('CODIGOS') || '')
    .split(',').map(function (par) { return par.trim(); }).filter(String);
  for (let i = 0; i < lista.length; i++) {
    const corte = lista[i].indexOf(':');
    if (corte < 1) continue;
    const clave = lista[i].slice(corte + 1).trim();
    if (clave.length >= 6 && String(codigo || '').trim() === clave) {
      if (fallos) cache.remove(propio);
      return lista[i].slice(0, corte).trim();
    }
  }
  cache.put(propio, String(fallos + 1), BLOQUEO_MIN * 60);
  cache.put(total, String(fallosTotal + 1), BLOQUEO_MIN * 60);
  throw new Error('Código incorrecto.');
}

/** La pantalla de entrada llama a esta función: devuelve el nombre si el código es válido. */
function validar(codigo, equipo) {
  return verificarCodigo_(codigo, equipo);
}

/** Correr desde el editor si alguien quedó bloqueado: borra los intentos fallidos de todos. */
function desbloquear() {
  CacheService.getScriptCache().put('ronda', String(Date.now()), 21600);
  Logger.log('Desbloqueado: ya se puede entrar.');
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

// ------------------------------------------------------------------ gastos operativos

/** Listas del formulario de gastos (viven aquí para que la pantalla no las repita). */
function opcionesGasto(codigo) {
  verificarCodigo_(codigo);
  return { categorias: CATEGORIAS_GASTO, comprobantes: COMPROBANTES };
}

/**
 * datos = {codigo, id, fecha: 'AAAA-MM-DD', monto, categoria, comprobante,
 *          cliente, local, activo, descripcion, foto: base64 jpg | null}
 * No pasa por GitHub: los gastos son dato financiero y no se versionan. Escribe directo en la
 * hoja "Gastos" del registro. El id lo genera el celular: si la conexión se corta y se reenvía,
 * no se duplica la fila.
 */
function registrarGasto(datos) {
  const usuario = verificarCodigo_(datos.codigo);
  const g = validarGasto_(datos);

  const lock = LockService.getScriptLock();
  lock.waitLock(30000);
  try {
    const hoja = hojaGastos_();
    const ultima = hoja.getLastRow();
    const col = COLUMNAS_GASTOS.length;
    if (ultima > 1) {
      const ids = hoja.getRange(2, col, ultima - 1, 1).getValues();
      for (let i = 0; i < ids.length; i++) {
        if (String(ids[i][0]) === g.id) return { fila: i + 2, repetido: true };
      }
    }
    let enlace = '';
    if (g.foto) {
      const nombre = g.fecha.replace(/-/g, '') + ' ' + g.categoria + ' S' + g.monto + ' ' + g.id + '.jpg';
      enlace = carpetaComprobantes_().createFile(
        Utilities.newBlob(Utilities.base64Decode(g.foto), 'image/jpeg', nombre)).getUrl();
    }
    const f = g.fecha.split('-').map(Number);
    hoja.appendRow([new Date(f[0], f[1] - 1, f[2]), g.categoria, g.monto, g.comprobante,
      texto_(g.cliente), texto_(g.local), texto_(g.activo), texto_(g.descripcion), enlace,
      usuario, new Date(), g.id]);
    return { fila: hoja.getLastRow(), repetido: false };
  } finally {
    lock.releaseLock();
  }
}

function validarGasto_(d) {
  const errores = [];
  const id = String(d.id || '');
  if (!/^[0-9a-z-]{8,40}$/.test(id)) errores.push('Identificador del gasto inválido.');

  const fecha = String(d.fecha || '');
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(fecha);
  const hoy = Utilities.formatDate(new Date(), 'America/Lima', 'yyyy-MM-dd');
  const dia = m ? new Date(Number(m[1]), Number(m[2]) - 1, Number(m[3])) : null;
  if (!dia || dia.getMonth() !== Number(m[2]) - 1 || dia.getDate() !== Number(m[3])) {
    errores.push('Falta la fecha.');
  } else if (fecha > hoy) {
    errores.push('La fecha no puede ser futura.');
  }

  const monto = Math.round(Number(d.monto) * 100) / 100;
  if (!(monto > 0) || monto > 1000000) errores.push('El monto tiene que ser mayor que cero.');

  const categoria = String(d.categoria || '');
  if (CATEGORIAS_GASTO.indexOf(categoria) < 0) errores.push('Elige una categoría.');

  const comprobante = String(d.comprobante || 'Sin comprobante');
  if (COMPROBANTES.indexOf(comprobante) < 0) errores.push('Tipo de comprobante inválido.');

  const campos = {};
  ['cliente', 'local', 'activo', 'descripcion'].forEach(function (k) {
    campos[k] = String(d[k] || '').trim().slice(0, k === 'descripcion' ? 500 : 120);
  });
  if (!campos.cliente && !campos.local && !campos.activo && !campos.descripcion) {
    errores.push('Indica a qué corresponde el gasto: activo, cliente, local o una descripción.');
  }

  const foto = d.foto ? String(d.foto) : null;
  if (foto && (foto.length > 4000000 || !/^[A-Za-z0-9+/=]+$/.test(foto))) {
    errores.push('La foto no es válida o es demasiado grande.');
  }
  if (errores.length) throw new Error(errores.join(' '));

  return Object.assign({ id: id, fecha: fecha, monto: monto, categoria: categoria,
                         comprobante: comprobante, foto: foto }, campos);
}

/** Texto libre a la hoja sin que se interprete como fórmula (=, +, -, @). */
function texto_(s) {
  return /^[=+\-@]/.test(s) ? "'" + s : s;
}

function hojaGastos_() {
  const libro = SpreadsheetApp.openById(REGISTRO_ID);
  let hoja = libro.getSheetByName(HOJA_GASTOS);
  if (hoja) return hoja;
  hoja = libro.insertSheet(HOJA_GASTOS);
  const col = COLUMNAS_GASTOS.length;
  hoja.getRange(1, 1, 1, col).setValues([COLUMNAS_GASTOS]).setFontWeight('bold')
    .setBackground('#1f9e6e').setFontColor('#ffffff');
  hoja.setFrozenRows(1);
  const columna = function (nombre) { return COLUMNAS_GASTOS.indexOf(nombre) + 1; };
  hoja.getRange(2, columna('Fecha'), hoja.getMaxRows() - 1, 1).setNumberFormat('dd/mm/yyyy');
  hoja.getRange(2, columna('Monto pagado con IGV (S/)'), hoja.getMaxRows() - 1, 1)
    .setNumberFormat('#,##0.00');
  hoja.getRange(2, columna('Registrado el'), hoja.getMaxRows() - 1, 1)
    .setNumberFormat('dd/mm/yyyy hh:mm');
  return hoja;
}

/**
 * Junto a "PDF emitidos" si la carpeta MUNAY - Cotizaciones está compartida entera; si solo se
 * compartió "PDF emitidos", la cuenta no ve la carpeta de arriba y va dentro de esa.
 */
function carpetaComprobantes_() {
  const pdf = DriveApp.getFolderById(CARPETA_PDF_ID);
  const padres = pdf.getParents();
  const padre = padres.hasNext() ? padres.next() : pdf;
  const hay = padre.getFoldersByName(CARPETA_COMPROBANTES);
  return hay.hasNext() ? hay.next() : padre.createFolder(CARPETA_COMPROBANTES);
}
