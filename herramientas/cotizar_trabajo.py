#!/usr/bin/env python3
"""
Arma una cotización a partir de un PEDIDO corto y la FICHA del trabajo (trabajos/<id>.json).

Uso:
    python3 herramientas/cotizar_trabajo.py pedido.json [carpeta_salida] [--borrador]
    python3 herramientas/cotizar_trabajo.py --validar        (revisa todas las fichas)

Qué hace:
  1. Revisa que el pedido responda las preguntas de la ficha: es el checklist antes de
     cotizar. Si falta alguna, se detiene y la muestra. Con --borrador sigue igual: lo que no
     se respondió pasa a la cotización como "alcance sujeto a confirmación", y el precio que
     dependa de esas respuestas queda pendiente.
  2. Calcula el costo (costos fijos por visita + costos por unidad), propone el precio por
     unidad dentro del rango de markup de la ficha y muestra los precios reales que ya se
     cobraron por el mismo trabajo. El precio NUNCA se pone solo: se pone con "precio_unidad"
     en el pedido (criterios-actuales.md §4).
  3. Escribe el JSON de la cotización listo para plantilla/generar.py, con costo estimado,
     subtotal calculado y una nota interna que deja rastro del origen de cada precio.

Ver trabajos/README.md.
"""
import datetime, json, os, string, sys, unicodedata
from decimal import Decimal, ROUND_CEILING, ROUND_HALF_UP, InvalidOperation

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "plantilla"))
import generar  # noqa: E402  (una sola definición de términos internos, recorte y tipos)

TRABAJOS = os.path.join(RAIZ, "trabajos")
CATALOGO = os.path.join(RAIZ, "catalogo.md")
EMITIDAS = os.path.join(RAIZ, "cotizaciones-emitidas")
MODOS = ("costo_mas_markup", "precio_referencia")
# {cantidad} = "3 coches" o "1 coche": concuerda solo, a diferencia de {unidades} {unidad_plural}.
VARIABLES_FIJAS = ("unidades", "unidad", "unidad_plural", "cantidad", "cantidad_cotizada")
RESULTADOS = ("ganada", "perdida", "sin respuesta")
MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre")
CENTIMO = Decimal("0.01")
# Palabras con que abre un ítem que ya dice su acción; si no, se antepone "Suministro de".
ACCIONES = ("reparacion", "cambio", "suministro", "enderezado", "desarmado", "alineamiento",
            "mantenimiento", "regulacion", "instalacion")


class Problema(Exception):
    """Algo del pedido o de la ficha que hay que corregir, explicado para quien lo corrige."""


class FaltanRespuestas(Problema):
    def __init__(self, preguntas):
        super().__init__(f"faltan {len(preguntas)} respuesta(s) del checklist")
        self.preguntas = preguntas


# ---------------------------------------------------------------- utilidades

def d(v):
    return Decimal(str(v))


def soles(v):
    return f"S/{d(v).quantize(CENTIMO, rounding=ROUND_HALF_UP):,.2f}"


def pct(v):
    return f"{d(v) * 100:.0f}%"


def num(v):
    """Decimal → número para el JSON: entero si no tiene céntimos."""
    v = d(v).quantize(CENTIMO, rounding=ROUND_HALF_UP)
    return int(v) if v == v.to_integral_value() else float(v)


def normalizar(t):
    t = unicodedata.normalize("NFD", str(t).lower())
    return " ".join("".join(c for c in t if unicodedata.category(c) != "Mn").split())


def fecha_larga(dia):
    return f"{dia.day} de {MESES[dia.month - 1]} de {dia.year}"


def unir(partes):
    partes = list(partes)
    if len(partes) <= 1:
        return partes[0] if partes else "ninguno"
    return ", ".join(partes[:-1]) + " y " + partes[-1]


def componer(texto, detalle=""):
    texto = str(texto).strip().rstrip(". ")
    if str(detalle).strip():
        texto += " — " + str(detalle).strip().rstrip(". ")
    return texto + "."


def texto_repuesto(nombre):
    if normalizar(nombre).split(" ")[0] in ACCIONES:
        return nombre[0].upper() + nombre[1:]
    return "Suministro de " + nombre[0].lower() + nombre[1:]


def marcadores(texto):
    return {campo for _, campo, _, _ in string.Formatter().parse(texto) if campo}


# ---------------------------------------------------------------- catálogo

def leer_catalogo(seccion):
    """Filas de una sección de catalogo.md: {nombre: {"precio": Decimal, "estado": texto}}.

    catalogo.md sigue siendo la única fuente de precios de repuestos, escrita para personas.
    Esto solo la lee: el precio no se copia a ninguna ficha.
    """
    lineas = open(CATALOGO, encoding="utf-8").read().splitlines()
    inicio = next((i for i, l in enumerate(lineas) if l.startswith("## " + seccion)), None)
    if inicio is None:
        raise Problema(f"catalogo.md no tiene la sección '## {seccion}'")
    filas = {}
    for linea in lineas[inicio + 1:]:
        if linea.startswith("## "):
            break
        if not linea.startswith("|"):
            continue
        celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
        if len(celdas) < 3:
            continue
        try:
            precio = Decimal(celdas[1].replace(",", ""))
        except InvalidOperation:
            continue                      # encabezado o separador de la tabla
        filas[celdas[0]] = {"precio": precio, "estado": celdas[2].replace("*", "").strip()}
    return filas


def buscar_repuesto(nombre, catalogo):
    """Devuelve (nombre en el catálogo, datos) o None si no está. Acepta el comienzo del nombre
    ("Rueda direccional" encuentra "Rueda direccional / rueda giratoria…"), sin tildes."""
    n = normalizar(nombre)
    exactos = [k for k in catalogo if normalizar(k) == n]
    if exactos:
        return exactos[0], catalogo[exactos[0]]
    parecidos = [k for k in catalogo if normalizar(k).startswith(n)]
    if len(parecidos) > 1:
        raise Problema(f"'{nombre}' coincide con varios repuestos del catálogo: "
                       f"{unir(parecidos)}. Escribir el nombre más completo")
    return (parecidos[0], catalogo[parecidos[0]]) if parecidos else None


# ---------------------------------------------------------------- fichas

def listar_fichas():
    if not os.path.isdir(TRABAJOS):
        return []
    return sorted(f[:-5] for f in os.listdir(TRABAJOS)
                  if f.endswith(".json") and not f.startswith("_"))


def _revisar_costos(costos, donde, errores):
    if not isinstance(costos, dict):
        errores.append(f"{donde} tiene que ser un objeto {{concepto: monto}}")
        return
    for concepto, monto in costos.items():
        if monto is None:
            continue                      # "por confirmar": se permite, bloquea el precio
        if not isinstance(monto, (int, float)) or monto < 0:
            errores.append(f"{donde}: '{concepto}' tiene monto {monto!r}; va un número, o null "
                           "si todavía no se sabe")


def validar_ficha(ficha, id_esperado=None):
    """Lista de errores de una ficha. Vacía = la ficha se puede usar."""
    errores = []
    for clave in ("id", "nombre", "tipo", "unidad", "unidad_plural", "modo_precio", "redaccion"):
        if not ficha.get(clave):
            errores.append(f"falta '{clave}'")
    if errores:
        return errores
    if id_esperado and ficha["id"] != id_esperado:
        errores.append(f"'id' es '{ficha['id']}' pero el archivo se llama '{id_esperado}.json'")
    tipos = generar.SERVICIOS["tipos"]
    if ficha["tipo"] not in tipos:
        errores.append(f"tipo '{ficha['tipo']}' no existe en servicios.json ({', '.join(tipos)})")
    elif tipos[ficha["tipo"]].get("subtipo_obligatorio") and \
            ficha.get("subtipo") not in generar.SERVICIOS["subtipos_sugeridos"]:
        errores.append(f"el tipo '{ficha['tipo']}' exige 'subtipo' de la lista: "
                       f"{', '.join(generar.SERVICIOS['subtipos_sugeridos'])}")
    if ficha["modo_precio"] not in MODOS:
        errores.append(f"modo_precio '{ficha['modo_precio']}' no existe ({' o '.join(MODOS)})")

    _revisar_costos(ficha.get("costos_fijos", {}), "costos_fijos", errores)
    _revisar_costos(ficha.get("costos_por_unidad", {}), "costos_por_unidad", errores)
    if ficha["modo_precio"] == "costo_mas_markup":
        mk = ficha.get("markup", {})
        if not all(isinstance(mk.get(k), (int, float)) for k in ("minimo", "maximo")):
            errores.append("costo_mas_markup necesita markup {minimo, maximo} (0.6 = 60% sobre el costo)")
        elif not 0 <= mk["minimo"] <= mk["maximo"]:
            errores.append("markup: el mínimo tiene que ser ≥ 0 y ≤ al máximo")
        if not ficha.get("costos_fijos") and not ficha.get("costos_por_unidad"):
            errores.append("costo_mas_markup sin ningún costo: no hay de dónde calcular")

    variables = ficha.get("variables", {})
    faltantes = marcadores(ficha["redaccion"]) - set(VARIABLES_FIJAS) - set(variables)
    if faltantes:
        nombres = ", ".join("{" + nombre + "}" for nombre in sorted(faltantes))
        errores.append(f"la redacción usa {nombres} sin valor por defecto en 'variables'")

    ids = set()
    for p in ficha.get("preguntas", []):
        pid = p.get("id", "?")
        if pid in ids:
            errores.append(f"pregunta '{pid}' repetida")
        ids.add(pid)
        if not p.get("pregunta") or not p.get("opciones"):
            errores.append(f"pregunta '{pid}' necesita 'pregunta' y 'opciones'")
            continue
        for valor, efecto in p["opciones"].items():
            donde = f"pregunta '{pid}', opción '{valor}'"
            if not isinstance(efecto, dict) or not efecto.get("texto"):
                errores.append(f"{donde}: necesita 'texto'")
                continue
            _revisar_costos(efecto.get("costos_fijos", {}), f"{donde} costos_fijos", errores)
            _revisar_costos(efecto.get("costos_por_unidad", {}), f"{donde} costos_por_unidad", errores)
            nuevas = set(efecto.get("variables", {})) - set(variables)
            if nuevas:
                errores.append(f"{donde}: cambia variables que la ficha no define "
                               f"({', '.join(sorted(nuevas))})")

    for aid, ad in ficha.get("adicionales", {}).items():
        if not ad.get("descripcion") or not isinstance(ad.get("precio_ref"), (int, float)):
            errores.append(f"adicional '{aid}' necesita 'descripcion' y 'precio_ref'")
    if ficha.get("seccion_catalogo"):
        try:
            leer_catalogo(ficha["seccion_catalogo"])
        except Problema as e:
            errores.append(str(e))
    for r in ficha.get("referencias", []):
        if not isinstance(r.get("precio_final"), (int, float)) or not r.get("unidades"):
            errores.append("cada referencia necesita 'precio_final' y 'unidades'")
        if r.get("resultado") not in (None, *RESULTADOS):
            errores.append(f"resultado '{r['resultado']}' no vale: {', '.join(RESULTADOS)}")

    # Lo que termina impreso para el cliente no puede llevar texto interno (hallazgos N07).
    impresos = [ficha["redaccion"], *ficha.get("condiciones", []), *variables.values(),
                *(ad.get("descripcion", "") for ad in ficha.get("adicionales", {}).values())]
    for p in ficha.get("preguntas", []):
        for efecto in p.get("opciones", {}).values():
            if isinstance(efecto, dict):
                impresos += [*efecto.get("condiciones", []), *efecto.get("variables", {}).values()]
    for texto in impresos:
        hallados = [t for t in generar.TERMINOS_INTERNOS if t in str(texto).lower()]
        if hallados:
            errores.append(f"texto que ve el cliente con términos internos ({', '.join(hallados)}): "
                           f"{generar.recortar(texto, 50)}")
    return errores


def cargar_ficha(trabajo_id):
    ruta = os.path.join(TRABAJOS, f"{trabajo_id}.json")
    if not trabajo_id or not os.path.exists(ruta):
        raise Problema(f"no existe la ficha '{trabajo_id}'. Fichas: "
                       f"{', '.join(listar_fichas()) or 'ninguna'}. Para un trabajo nuevo: "
                       "python3 herramientas/nuevo_trabajo.py")
    ficha = json.load(open(ruta, encoding="utf-8"))
    errores = validar_ficha(ficha, trabajo_id)
    if errores:
        raise Problema(f"la ficha '{trabajo_id}' tiene errores:\n" +
                       "\n".join("  - " + e for e in errores))
    return ficha


def techo(referencias):
    """(precio por unidad más alto que se ganó, más bajo que se perdió), o None.

    Es la señal del techo de precio: si se ganó a S/5,785 y se perdió desde S/7,690, el
    techo está en algún punto de ese tramo (hallazgos-abiertos.md, O5).
    """
    por_unidad = lambda r: d(r["precio_final"]) / d(r["unidades"])  # noqa: E731
    ganadas = [por_unidad(r) for r in referencias if r.get("resultado") == "ganada"]
    perdidas = [por_unidad(r) for r in referencias if r.get("resultado") == "perdida"]
    return (max(ganadas), min(perdidas)) if ganadas and perdidas else None


def historial(trabajo_id):
    """Lo que ya se cobró por este trabajo: las cotizaciones archivadas con el mismo 'trabajo'.
    Cada --final agrega una. Así el precio de experiencia queda a la vista al cotizar."""
    filas = []
    if not os.path.isdir(EMITIDAS):
        return filas
    for f in sorted(os.listdir(EMITIDAS)):
        if not f.endswith(".json"):
            continue
        c = json.load(open(os.path.join(EMITIDAS, f), encoding="utf-8"))
        if c.get("trabajo") != trabajo_id:
            continue
        primero = generar.items_cotizados(c)[0]
        filas.append({"numero": c["numero"], "fecha": c["fecha"],
                      "cliente": c.get("cliente_corto") or c["cliente"],
                      "local": c.get("local", ""), "unidades": c.get("unidades"),
                      "precio_unidad": primero.get("precio_unit"),
                      "respuestas": c.get("respuestas", {})})
    return filas


# ---------------------------------------------------------------- armado

def armar(pedido, borrador=False, hoy=None):
    """Arma la cotización. Devuelve (cotizacion, info). No escribe ningún archivo."""
    hoy = hoy or datetime.date.today()
    ficha = cargar_ficha(pedido.get("trabajo", ""))
    unidades = pedido.get("unidades")
    if not isinstance(unidades, (int, float)) or unidades <= 0:
        raise Problema(f"falta 'unidades': cuántos {ficha['unidad_plural']} se atienden")
    for clave in ("cliente", "local"):
        if not str(pedido.get(clave, "")).strip():
            raise Problema(f"falta '{clave}'")

    # 1. Checklist
    preguntas = ficha.get("preguntas", [])
    respuestas = pedido.get("respuestas", {})
    ajenas = set(respuestas) - {p["id"] for p in preguntas}
    if ajenas:
        raise Problema(f"respuestas a preguntas que la ficha no tiene: {', '.join(sorted(ajenas))}. "
                       f"Preguntas: {', '.join(p['id'] for p in preguntas) or 'ninguna'}")
    efectos, faltan = [], []
    for p in preguntas:
        valor = respuestas.get(p["id"])
        if valor is None:
            faltan.append(p)
        elif valor not in p["opciones"]:
            raise Problema(f"'{valor}' no es una respuesta válida para '{p['id']}' "
                           f"({p['pregunta']}). Opciones: {', '.join(p['opciones'])}")
        else:
            efectos.append((p, valor, p["opciones"][valor]))
    if faltan and not borrador:
        raise FaltanRespuestas(faltan)
    avisos = [ef["aviso"] for _, _, ef in efectos if ef.get("aviso")]

    # La línea puede contar algo más chico que la unidad costeada: 3 coches se venden como
    # "12 ruedas", que al cliente le dice más que "3 juegos". El precio va por esa pieza.
    cp = ficha.get("cotizar_por")
    n_linea = unidades * cp["por_unidad"] if cp else unidades
    pieza = cp["nombre"] if cp else ficha["unidad"]
    piezas = cp["plural"] if cp else ficha["unidad_plural"]

    # 2. Variables de la redacción
    variables = {"unidades": num(unidades), "unidad": ficha["unidad"],
                 "unidad_plural": ficha["unidad_plural"],
                 "cantidad": f"{num(unidades)} {ficha['unidad'] if unidades == 1 else ficha['unidad_plural']}",
                 "cantidad_cotizada": f"{num(n_linea)} {pieza if n_linea == 1 else piezas}",
                 **ficha.get("variables", {})}
    for _, _, ef in efectos:
        variables.update(ef.get("variables", {}))
    ajenas = set(pedido.get("variables", {})) - set(ficha.get("variables", {}))
    if ajenas:
        raise Problema(f"el pedido define variables que la ficha no usa: {', '.join(sorted(ajenas))}. "
                       f"Existen: {', '.join(ficha.get('variables', {})) or 'ninguna'}")
    variables.update(pedido.get("variables", {}))

    # 3. Costo
    fijos = dict(ficha.get("costos_fijos", {}))
    por_unidad = dict(ficha.get("costos_por_unidad", {}))
    for _, _, ef in efectos:
        fijos.update(ef.get("costos_fijos", {}))
        por_unidad.update(ef.get("costos_por_unidad", {}))
    cambios = []
    for concepto, monto in pedido.get("costos", {}).items():
        destino = fijos if concepto in fijos else por_unidad if concepto in por_unidad else None
        if destino is None:
            raise Problema(f"el pedido cambia el costo '{concepto}', que la ficha no tiene. Si es "
                           "un costo real de este trabajo, se agrega a la ficha: así queda para la "
                           f"próxima vez. Costos de la ficha: {unir(list(fijos) + list(por_unidad))}")
        cambios.append((concepto, destino[concepto], monto))
        destino[concepto] = monto

    costo = propuesta = None
    incompleto = []
    if ficha["modo_precio"] == "costo_mas_markup":
        incompleto = [f"monto de '{c}'" for c, m in {**fijos, **por_unidad}.items() if m is None]
        incompleto += [f"respuesta a «{p['pregunta']}»" for p in faltan
                       if any(o.get("costos_fijos") or o.get("costos_por_unidad")
                              for o in p["opciones"].values())]
        if not incompleto:
            total_fijo = sum((d(m) for m in fijos.values()), Decimal("0"))
            total_unidad = sum((d(m) for m in por_unidad.values()), Decimal("0"))
            costo = total_fijo + total_unidad * d(unidades)
            mmin, mmax = d(ficha["markup"]["minimo"]), d(ficha["markup"]["maximo"])
            msug = (mmin + mmax) / 2
            paso = d(ficha.get("redondeo", 5))

            def precio_con(m):
                bruto = costo * (1 + m) / d(n_linea)
                return (bruto / paso).to_integral_value(rounding=ROUND_CEILING) * paso

            propuesta = {"minimo": (mmin, precio_con(mmin)), "sugerido": (msug, precio_con(msug)),
                         "maximo": (mmax, precio_con(mmax))}
    if "costo_estimado" in pedido:
        costo = d(pedido["costo_estimado"])

    # 4. Línea principal
    faltan_redaccion = marcadores(ficha["redaccion"]) - set(variables)
    if faltan_redaccion:
        raise Problema(f"la redacción necesita {', '.join(sorted(faltan_redaccion))}")
    principal = ficha["redaccion"].format_map(variables)
    if pedido.get("agregar"):
        principal = principal.rstrip() + " " + pedido["agregar"].strip()
    item1 = {"cant": num(n_linea), "descripcion": principal}
    precio_unidad = pedido.get("precio_unidad")
    if precio_unidad is not None:
        item1["precio_unit"] = num(precio_unidad)
    else:
        item1["pendiente"] = True
    items, trazas = [item1], []

    # 5. Líneas adicionales: repuestos (catálogo), adicionales (ficha) o libres
    catalogo = None
    for n, linea in enumerate(pedido.get("lineas", []), start=2):
        cant = linea.get("cant", 1)
        precio = d(linea["precio"]) if "precio" in linea else None
        if "repuesto" in linea:
            if not ficha.get("seccion_catalogo"):
                raise Problema(f"la línea {n} pide un repuesto, pero la ficha no dice en qué "
                               "sección de catalogo.md buscarlo ('seccion_catalogo')")
            catalogo = catalogo or leer_catalogo(ficha["seccion_catalogo"])
            nombre = linea["repuesto"]
            hallado = buscar_repuesto(nombre, catalogo)
            if hallado is None:
                if precio is None:
                    raise Problema(f"'{nombre}' no está en catalogo.md ({ficha['seccion_catalogo']}). "
                                   "El precio no se inventa: agregarlo al catálogo, o pasar "
                                   "'precio' en la línea (queda anotado como dado directamente)")
                trazas.append(f"{nombre}: {soles(precio)} dado directamente (no está en el catálogo).")
            else:
                _, datos = hallado
                if precio is not None and precio != datos["precio"]:
                    trazas.append(f"{nombre}: {soles(precio)} dado directamente "
                                  f"(catálogo: {soles(datos['precio'])}, {datos['estado']}).")
                else:
                    precio = datos["precio"]
                    validar_txt = ", POR VALIDAR" if "por validar" in datos["estado"].lower() else ""
                    trazas.append(f"{nombre}: {soles(precio)} de catálogo{validar_txt}.")
            texto = linea.get("descripcion") or texto_repuesto(nombre)
        elif "adicional" in linea:
            ad = ficha.get("adicionales", {}).get(linea["adicional"])
            if ad is None:
                raise Problema(f"el adicional '{linea['adicional']}' no está en la ficha. Existen: "
                               f"{', '.join(ficha.get('adicionales', {})) or 'ninguno'}")
            ref = d(ad["precio_ref"])
            if precio is not None and precio != ref:
                trazas.append(f"{ad['descripcion']}: {soles(precio)} dado directamente "
                              f"(referencia de la ficha: {soles(ref)}).")
            else:
                precio = ref
                trazas.append(f"{ad['descripcion']}: {soles(ref)}, referencia de la ficha"
                              f"{' (' + ad['fuente'] + ')' if ad.get('fuente') else ''}.")
            texto = linea.get("descripcion") or ad["descripcion"]
        elif linea.get("descripcion"):
            texto = linea["descripcion"]
            trazas.append(f"{generar.recortar(texto, 40)}: " +
                          (f"{soles(precio)} dado directamente." if precio is not None else "sin precio."))
        else:
            raise Problema(f"la línea {n} no dice qué es: usar 'repuesto', 'adicional' o 'descripcion'")
        item = {"cant": cant, "descripcion": componer(texto, linea.get("detalle", ""))}
        if precio is None:
            item["pendiente"] = True
        else:
            item["precio_unit"] = num(precio)
        items.append(item)

    # 6. Condiciones: las de la ficha, las de cada respuesta y las del pedido
    condiciones = list(ficha.get("condiciones", []))
    for _, _, ef in efectos:
        condiciones += ef.get("condiciones", [])
    condiciones += pedido.get("condiciones", [])
    por_confirmar = [p["etiqueta_cliente"] for p in faltan if p.get("etiqueta_cliente")]
    if por_confirmar:
        condiciones.insert(0, f"Alcance sujeto a confirmación de: {unir(por_confirmar)}.")

    # 7. Subtotal calculado: el que habría salido con el markup sugerido, para medir el ajuste
    otras = sum((d(it["precio_unit"]) * d(it["cant"]) for it in items[1:] if "precio_unit" in it),
                Decimal("0"))
    subtotal_calculado = propuesta["sugerido"][1] * d(n_linea) + otras if propuesta else None

    # 8. Nota interna: el rastro de cada precio (antes no quedaba en ninguna parte)
    nota = [f"Ficha {ficha['id']}."]
    if efectos:
        nota.append("Respuestas: " + "; ".join(f"{p['pregunta']} {ef['texto']}" for p, _, ef in efectos) + ".")
    if faltan:
        nota.append("Sin responder: " + "; ".join(p["pregunta"] for p in faltan) + ".")
    if incompleto:
        nota.append(f"Costo incompleto: falta {unir(incompleto)}.")
    elif costo is not None and "costo_estimado" not in pedido and ficha["modo_precio"] == "costo_mas_markup":
        nota.append(f"Costo estimado {soles(costo)} = fijos {soles(total_fijo)} + "
                    f"{soles(total_unidad)} × {num(unidades)} {ficha['unidad_plural']}.")
    elif "costo_estimado" in pedido:
        nota.append(f"Costo estimado dado en el pedido: {soles(costo)}.")
    for concepto, antes, ahora in cambios:
        nota.append(f"Costo cambiado para este pedido: {concepto} "
                    f"{soles(ahora) if ahora is not None else 'sin monto'} "
                    f"(ficha: {soles(antes) if antes is not None else 'sin monto'}).")
    if propuesta:
        (m0, p0), (ms, ps), (m1, p1) = propuesta["minimo"], propuesta["sugerido"], propuesta["maximo"]
        nota.append(f"Precio calculado a markup {pct(ms)}: {soles(ps)} por {pieza} "
                    f"(rango {pct(m0)}–{pct(m1)}: {soles(p0)} a {soles(p1)}).")
    if precio_unidad is not None:
        ajuste = f" ({d(precio_unidad) / propuesta['sugerido'][1] - 1:+.1%} sobre el calculado)" if propuesta else ""
        nota.append(f"Precio final dado: {soles(precio_unidad)} por {pieza}{ajuste}.")
    piso = ficha.get("precio_referencia", {}).get("piso")
    if piso and precio_unidad is not None and d(precio_unidad) < d(piso):
        nota.append(f"Bajo el piso de {soles(piso)} por {ficha['unidad']}.")
    nota += trazas
    if pedido.get("nota_interna"):
        nota.append(pedido["nota_interna"].strip())

    cot = {"numero": pedido.get("numero") or f"PENDIENTE-{hoy.year}",
           "tipo": ficha["tipo"]}
    if ficha.get("subtipo"):
        cot["subtipo"] = ficha["subtipo"]
    cot["cliente"] = pedido["cliente"]
    if pedido.get("cliente_corto"):
        cot["cliente_corto"] = pedido["cliente_corto"]
    cot.update({"local": pedido["local"], "atencion": pedido.get("atencion", ""),
                "fecha": pedido.get("fecha") or fecha_larga(hoy),
                "resumen": f"{ficha['nombre']} — {num(unidades)} {ficha['unidad_plural']}",
                "unidades": unidades, "trabajo": ficha["id"], "respuestas": respuestas})
    if ficha.get("etiqueta_archivo"):
        cot["etiqueta_archivo"] = ficha["etiqueta_archivo"]
    cot["items"] = items
    if condiciones:
        cot["condiciones"] = condiciones
    if pedido.get("nota"):
        cot["nota"] = pedido["nota"]
    if costo is not None:
        cot["costo_estimado"] = num(costo)
    if subtotal_calculado is not None:
        cot["subtotal_calculado"] = num(subtotal_calculado)
    cot["nota_interna"] = " ".join(nota)

    info = {"ficha": ficha, "efectos": efectos, "faltan": faltan, "avisos": avisos,
            "fijos": fijos, "por_unidad": por_unidad, "cambios": cambios, "costo": costo,
            "incompleto": incompleto, "propuesta": propuesta, "trazas": trazas,
            "historial": historial(ficha["id"]), "unidades": unidades,
            "n_linea": n_linea, "pieza": pieza}
    return cot, info


# ---------------------------------------------------------------- informe

def imprimir_informe(cot, info):
    f = info["ficha"]
    u, plural, uno = info["unidades"], f["unidad_plural"], f["unidad"]
    print(f"══ {f['nombre']} — {num(u)} {plural} · {cot['cliente']} / {cot['local']} ══")

    if f.get("preguntas"):
        print("\nCHECKLIST ANTES DE COTIZAR")
        for p, _, ef in info["efectos"]:
            print(f"  ✓ {p['pregunta']}  →  {ef['texto']}")
        for p in info["faltan"]:
            print(f"  ✗ {p['pregunta']}  →  SIN RESPONDER ({' / '.join(p['opciones'])})")
        for a in info["avisos"]:
            print(f"  ! {a}")

    if f["modo_precio"] == "costo_mas_markup":
        print("\nCOSTEO INTERNO (no sale en la cotización)")
        for c, m in info["fijos"].items():
            print(f"  {c:<52} {soles(m) if m is not None else 'SIN MONTO':>12}   por visita")
        for c, m in info["por_unidad"].items():
            linea = f"{soles(m)} × {num(u)} = {soles(d(m) * d(u))}" if m is not None else "SIN MONTO"
            print(f"  {c:<52} {linea:>12}")
        if info["costo"] is not None:
            print(f"  {'COSTO ESTIMADO':<52} {soles(info['costo']):>12}")
        else:
            print(f"  Costo incompleto: falta {unir(info['incompleto'])}. Sin eso no hay precio que proponer.")
        if info["propuesta"]:
            pieza, n = info["pieza"], info["n_linea"]
            print(f"\nPRECIO POR {pieza.upper()} (markup sobre el costo; el precio lo pone una persona)")
            for clave in ("minimo", "sugerido", "maximo"):
                m, p = info["propuesta"][clave]
                marca = "   ← sugerido" if clave == "sugerido" else ""
                print(f"  {pct(m):>4}  {soles(p):>11} por {pieza} × {num(n)}  →  total "
                      f"{soles(p * d(n))}{marca}")
    else:
        piso = f.get("precio_referencia", {}).get("piso")
        print("\nPRECIO DE REFERENCIA (por experiencia, sin fórmula todavía)")
        if piso:
            print(f"  Piso: {soles(piso)} por {uno}")
        if f.get("precio_referencia", {}).get("nota"):
            print(f"  {f['precio_referencia']['nota']}")

    if f.get("referencias") or info["historial"]:
        print("\nLO QUE YA SE COBRÓ POR ESTE TRABAJO")
        for r in f.get("referencias", []):
            por_u = d(r["precio_final"]) / d(r["unidades"])
            mk = f", markup {pct(d(r['precio_final']) / d(r['costo']) - 1)}" if r.get("costo") else ""
            costo_txt = f"costo {soles(r['costo'])} → " if r.get("costo") else ""
            resultado = f" · {r['resultado'].upper()}" if r.get("resultado") else ""
            print(f"  {r.get('fecha', '')} · {r.get('fuente', '')} · {num(r['unidades'])} {plural} · "
                  f"{costo_txt}{soles(r['precio_final'])} ({soles(por_u)} por {uno}{mk}){resultado}")
            if r.get("nota"):
                print(f"      {r['nota']}")
        limite = techo(f.get("referencias", []))
        if limite:
            print(f"  → Techo visible: se ganó hasta {soles(limite[0])} por {uno} y se perdió desde "
                  f"{soles(limite[1])} (comparar alcances: no todas incluyen lo mismo).")
        for h in info["historial"]:
            resp = ", ".join(f"{k}: {v}" for k, v in h["respuestas"].items())
            precio = soles(h["precio_unidad"]) if h["precio_unidad"] is not None else "pendiente"
            print(f"  {h['numero']} · {h['cliente']} {h['local']} · {h['unidades']} {plural} a "
                  f"{precio} por {uno}{' · ' + resp if resp else ''}")

    print("\nLÍNEAS DE LA COTIZACIÓN")
    for i, it in enumerate(cot["items"], start=1):
        precio = f"{soles(it['precio_unit'])}" if "precio_unit" in it else "PENDIENTE"
        print(f"  {i}. {it['cant']} × {precio:>11}   {generar.recortar(it['descripcion'], 70)}")
    for t in info["trazas"]:
        print(f"      · {t}")
    for c in cot.get("condiciones", []):
        print(f"  Condición: {c}")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opciones = {a for a in sys.argv[1:] if a.startswith("--")}
    validas = {"--borrador", "--validar"}
    if opciones - validas:
        raise SystemExit("Opción desconocida: " + ", ".join(sorted(opciones - validas)))

    if "--validar" in opciones:
        con_error = 0
        for fid in listar_fichas():
            errores = validar_ficha(json.load(open(os.path.join(TRABAJOS, f"{fid}.json"),
                                                   encoding="utf-8")), fid)
            print(f"{'✓' if not errores else '✗'} {fid}")
            for e in errores:
                print(f"    - {e}")
            con_error += bool(errores)
        sys.exit(1 if con_error else 0)

    if not args:
        print(__doc__)
        sys.exit(1)
    pedido = json.load(open(args[0], encoding="utf-8"))
    salida = args[1] if len(args) > 1 else "."
    try:
        cot, info = armar(pedido, borrador="--borrador" in opciones)
    except FaltanRespuestas as e:
        print("FALTA RESPONDER ANTES DE COTIZAR:")
        for p in e.preguntas:
            print(f"  ✗ {p['pregunta']}  ({' / '.join(p['opciones'])})")
            if p.get("por_que"):
                print(f"      Por qué importa: {p['por_que']}")
        print("\nPoner las respuestas en \"respuestas\" del pedido, o correr con --borrador para "
              "emitir la propuesta con el alcance sujeto a confirmación.")
        sys.exit(2)
    except Problema as e:
        raise SystemExit(f"NO SE ARMA — {e}")

    imprimir_informe(cot, info)
    os.makedirs(salida, exist_ok=True)
    ruta = os.path.join(salida, f"{cot['numero']}.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(cot, f, ensure_ascii=False, indent=1)
        f.write("\n")

    con_precio = [it for it in cot["items"] if "precio_unit" in it]
    pendientes = [it for it in cot["items"] if it.get("pendiente")]
    if not con_precio:
        opcion = " --sin-precios"
    elif not pendientes and generar.NUMERO_REAL.fullmatch(cot["numero"]):
        opcion = "          (y --final cuando esté aprobada)"
    else:
        opcion = ""
    print(f"\n→ Cotización escrita en {ruta}")
    print(f"→ Siguiente paso: python3 plantilla/generar.py {ruta} {salida}{opcion}")


if __name__ == "__main__":
    main()
