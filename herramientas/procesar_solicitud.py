#!/usr/bin/env python3
"""
Procesa las solicitudes que llegan desde la app del celular (Google Apps Script).

Cada solicitud es una carpeta solicitudes/<id>/ con:
    solicitud.json   {"id", "modo": "vista" | "emitir", "creado_por", "creado", "pedido": {...}}
    fotos/*.jpg      (opcional) las fotos que el pedido nombra con ruta relativa

El "pedido" es una de dos cosas:
  - laminado de seguridad (trabajo "laminado-seguridad"): piezas y precio total, se arma con
    herramientas/cotizar_laminado.py (rollos y reparto como en COT-2026-001)
  - un pedido de ficha (trae "trabajo"): se arma con herramientas/cotizar_trabajo.py
  - una cotización directa (trae "items" y "tipo"): va tal cual a plantilla/generar.py

Modo "vista": genera la imagen con N° PENDIENTE; no gasta número ni archiva.
Modo "emitir": toma el N° que sigue (o el que traiga el pedido), genera el PDF con su nombre
de entrega y archiva imagen + JSON en cotizaciones-emitidas/, igual que --final.

El resultado queda en solicitudes/<id>/salida/ con resultado.json, que la app lee para mostrar
la vista previa, guardar el PDF en Drive y escribir la fila del registro. Una solicitud que ya
tiene resultado.json no se vuelve a procesar.

Uso:
    python3 herramientas/procesar_solicitud.py              (todas las pendientes)
    python3 herramientas/procesar_solicitud.py <carpeta>    (una sola)
"""
import datetime, glob, json, os, re, shutil, sys, traceback, zoneinfo

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(RAIZ, "plantilla"), os.path.join(RAIZ, "herramientas")]
import generar as g          # noqa: E402
import cotizar_trabajo as motor  # noqa: E402
import cotizar_laminado as laminado  # noqa: E402

SOLICITUDES = os.path.join(RAIZ, "solicitudes")
MODOS = ("vista", "emitir")
LIMA = zoneinfo.ZoneInfo("America/Lima")


def hoy_lima():
    """La fecha en Lima. El motor corre en GitHub con hora UTC: desde las 7 p. m. de Lima ya
    sería el día siguiente, en la fecha impresa y en el N°."""
    return datetime.datetime.now(LIMA).date()


def siguiente_numero(dia):
    """N° del día: mes + día (dos dígitos) + cuántas van ese día, y el año.
    12/10/2026 → 10121-2026 la primera, 10122-2026 la segunda; 5/09/2026 → 9051-2026.
    Así salen los N° reales (9053 el 5/09, 9127 el 12/09, 10082 y 10083 el 8/10). Cuenta las
    archivadas de ese día y sigue a la mayor: nunca reutiliza uno, aunque haya un hueco."""
    prefijo = f"{dia.month}{dia.day:02d}"
    usados = []
    for p in glob.glob(os.path.join(g.ARCHIVO, f"{prefijo}*-{dia.year}.json")):
        m = re.fullmatch(prefijo + r"(\d)-" + str(dia.year), os.path.basename(p)[:-5])
        if m:
            usados.append(int(m.group(1)))
    n = max(usados, default=0) + 1
    if n > 9:
        raise motor.Problema(f"ya hay 9 cotizaciones emitidas el {dia:%d/%m/%Y}: indicar el N° "
                             "en el pedido")
    return f"{prefijo}{n}-{dia.year}"


def fila_registro(cot, servicio, sub, igv, total, hoy):
    """Los valores de la fila del registro, como números (no texto) para que sumen en Sheets."""
    primero = g.items_cotizados(cot)[0]
    return {
        "numero": cot["numero"], "fecha": cot["fecha"],
        "fecha_iso": hoy.isoformat(), "cliente": cot["cliente"],
        "local": cot.get("local", ""), "tipo": servicio["categoria_registro"],
        "subtipo": cot.get("subtipo", ""),
        "descripcion": g.recortar(cot.get("resumen") or primero["descripcion"]),
        "unidades": g.unidades_de(cot), "subtotal": float(sub), "igv": float(igv),
        "total": float(total),
        "costo_estimado": float(cot["costo_estimado"]) if "costo_estimado" in cot else None,
        "subtotal_calculado": (float(cot["subtotal_calculado"])
                               if "subtotal_calculado" in cot else None),
        "nota_interna": " ".join(cot.get("nota_interna", "").split()),
    }


def sin_precio(pedido):
    """Un precio en 0 o vacío es "todavía no lo tengo", no un precio de S/ 0: la línea queda
    Pendiente, la vista previa sale y emitir sigue bloqueado hasta que haya precio."""
    for clave in ("precio_unidad", "precio_total"):
        if clave in pedido:
            try:
                vacio = float(pedido[clave]) <= 0
            except (TypeError, ValueError):
                vacio = pedido[clave] in ("", None)
            if vacio:
                del pedido[clave]


def procesar(carpeta):
    salida = os.path.join(carpeta, "salida")
    os.makedirs(salida, exist_ok=True)
    res = {"estado": "error", "errores": [], "alertas": [], "avisos": []}
    try:
        sol = json.load(open(os.path.join(carpeta, "solicitud.json"), encoding="utf-8"))
        modo = sol.get("modo")
        if modo not in MODOS:
            raise motor.Problema(f"modo '{modo}' desconocido: debe ser 'vista' o 'emitir'")
        res.update(id=sol.get("id", os.path.basename(carpeta)), modo=modo)
        pedido = sol["pedido"]
        sin_precio(pedido)
        hoy = hoy_lima()

        resumen = []
        if pedido.get("trabajo") == "laminado-seguridad":
            cot, resumen = laminado.armar(pedido, hoy)
        elif "trabajo" in pedido:
            cot, info = motor.armar(pedido, borrador=(modo == "vista"), hoy=hoy)
            resumen = list(info.get("avisos", []))   # lo que la ficha advierte a quien cotiza
            resumen += motor.referencias_para_vista(info)   # y lo que ya se cobró por este trabajo
            # Lo que la ficha no decide y quien cotiza sí: cómo se llama el archivo.
            for clave in ("etiqueta_archivo", "detalle_archivo"):
                if pedido.get(clave):
                    cot[clave] = pedido[clave]
        else:
            cot = json.loads(json.dumps(pedido))
            cot.setdefault("fecha", motor.fecha_larga(hoy))

        if modo == "emitir":
            cot["numero"] = pedido.get("numero") or siguiente_numero(hoy)
        else:
            cot["numero"] = f"PENDIENTE-{hoy.year}"

        g.resolver_fotos(cot, carpeta)
        servicio = g.tipo_de(cot)
        sub, igv, total = g.calcular(cot)
        items = g.items_cotizados(cot)
        sin_precios = modo == "vista" and all(it.get("pendiente") or "precio_unit" not in it
                                              for it in items)
        final = modo == "emitir"
        errores, alertas, avisos = g.validar(cot, servicio, sub, sin_precios, final, final)
        res.update(errores=errores, alertas=resumen + alertas, avisos=avisos)
        if errores:
            raise motor.Problema("hay que corregir el pedido antes de generar")

        html = g.construir_html(cot, servicio, sub, igv, total, sin_precios)
        base = os.path.join(salida, cot["numero"])
        png, pdf, achicado = g.render(html, base)
        os.remove(base + ".html") if os.path.exists(base + ".html") else None
        res.update(estado="ok", numero=cot["numero"], png=os.path.basename(png),
                   subtotal=float(sub), igv=float(igv), total=float(total),
                   sin_precios=sin_precios)
        if final:
            nombre = g.nombre_entrega(cot, servicio)
            shutil.copyfile(pdf, os.path.join(salida, nombre))
            os.remove(pdf)
            res["pdf"] = nombre
            res["archivado"] = [os.path.relpath(g.archivar(png, cot["numero"]), RAIZ),
                                os.path.relpath(g.archivar_json(cot), RAIZ)]
            res["registro"] = fila_registro(cot, servicio, sub, igv, total, hoy)
        else:
            res["pdf"] = os.path.basename(pdf)
    except motor.FaltanRespuestas as e:
        res["errores"].append(str(e))
        res["preguntas"] = e.preguntas
    except motor.Problema as e:
        if not res["errores"]:
            res["errores"].append(str(e))
    except Exception as e:  # el error se le muestra a quien cotiza; el detalle queda aquí
        res["errores"].append(f"error interno: {e}")
        res["detalle"] = traceback.format_exc()
    with open(os.path.join(salida, "resultado.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return res


def pendientes():
    return sorted(c for c in glob.glob(os.path.join(SOLICITUDES, "*"))
                  if os.path.isfile(os.path.join(c, "solicitud.json"))
                  and not os.path.isfile(os.path.join(c, "salida", "resultado.json")))


def main():
    carpetas = sys.argv[1:] or pendientes()
    for c in carpetas:
        r = procesar(os.path.abspath(c))
        print(f"{os.path.basename(c)}: {r['estado']} {r.get('numero', '')} "
              f"{'; '.join(r['errores'])}")


if __name__ == "__main__":
    main()
