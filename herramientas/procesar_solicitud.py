#!/usr/bin/env python3
"""
Procesa las solicitudes que llegan desde la app del celular (Google Apps Script).

Cada solicitud es una carpeta solicitudes/<id>/ con:
    solicitud.json   {"id", "modo": "vista" | "emitir", "creado_por", "creado", "pedido": {...}}
    fotos/*.jpg      (opcional) las fotos que el pedido nombra con ruta relativa

El "pedido" es una de dos cosas:
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
import datetime, glob, json, os, re, shutil, sys, traceback

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path[:0] = [os.path.join(RAIZ, "plantilla"), os.path.join(RAIZ, "herramientas")]
import generar as g          # noqa: E402
import cotizar_trabajo as motor  # noqa: E402

SOLICITUDES = os.path.join(RAIZ, "solicitudes")
MODOS = ("vista", "emitir")


def siguiente_numero(anio):
    """El N° que sigue al más alto emitido en el año (NNNN-AAAA). Nunca reutiliza uno."""
    mayor = 0
    for p in glob.glob(os.path.join(g.ARCHIVO, f"*-{anio}.json")):
        m = re.fullmatch(r"(\d{3,5})-" + str(anio), os.path.basename(p)[:-5])
        if m:
            mayor = max(mayor, int(m.group(1)))
    if not mayor:
        raise motor.Problema(f"no hay ninguna cotización de {anio} archivada para continuar la "
                             "numeración: indicar el N° en el pedido")
    return f"{mayor + 1}-{anio}"


def fila_registro(cot, servicio, sub, igv, total):
    """Los valores de la fila del registro, como números (no texto) para que sumen en Sheets."""
    primero = g.items_cotizados(cot)[0]
    return {
        "numero": cot["numero"], "fecha": cot["fecha"],
        "fecha_iso": datetime.date.today().isoformat(), "cliente": cot["cliente"],
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
        hoy = datetime.date.today()

        if "trabajo" in pedido:
            cot, _ = motor.armar(pedido, borrador=(modo == "vista"), hoy=hoy)
        else:
            cot = json.loads(json.dumps(pedido))
            cot.setdefault("fecha", motor.fecha_larga(hoy))

        if modo == "emitir":
            cot["numero"] = pedido.get("numero") or siguiente_numero(hoy.year)
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
        res.update(errores=errores, alertas=alertas, avisos=avisos)
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
            res["registro"] = fila_registro(cot, servicio, sub, igv, total)
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
