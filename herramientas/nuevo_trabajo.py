#!/usr/bin/env python3
"""
Agrega un trabajo nuevo a la biblioteca respondiendo preguntas. No hace falta saber JSON:
al final revisa la ficha, la guarda en trabajos/<id>.json y muestra el pedido para cotizarla.

Uso:
    python3 herramientas/nuevo_trabajo.py

Lo que no se sabe todavía (un costo, un precio) se responde con "?": queda marcado como
pendiente y el sistema no inventa ese número — bloquea el precio hasta que se complete.
"""
import copy, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cotizar_trabajo as motor  # noqa: E402

SERVICIOS = motor.generar.SERVICIOS
PLANTILLA = os.path.join(motor.TRABAJOS, "_plantilla.json")


def preguntar(texto, defecto=None, opciones=None):
    sufijo = f" [{defecto}]" if defecto not in (None, "") else ""
    while True:
        r = input(f"{texto}{sufijo}: ").strip()
        if not r and defecto is not None:
            r = str(defecto)
        if not r:
            print("  (hace falta una respuesta)")
        elif opciones and r not in opciones:
            print(f"  (opciones: {', '.join(opciones)})")
        else:
            return r


def numero(texto, defecto=None, permite_vacio=False):
    """Un número; '?' devuelve None si se permite (= todavía no se sabe)."""
    while True:
        r = preguntar(texto, defecto).replace("S/", "").replace(",", "").strip()
        if r == "?" and permite_vacio:
            return None
        try:
            return float(r)
        except ValueError:
            print("  (va un número" + (", o ? si todavía no se sabe)" if permite_vacio else ")"))


def lista(texto):
    print(texto + "  (una por línea; línea vacía para terminar)")
    items = []
    while True:
        r = input("  > ").strip()
        if not r:
            return items
        items.append(r)


def costos(texto):
    print(texto)
    print("  Una por línea:  concepto = monto   (? si todavía no se sabe; línea vacía para terminar)")
    res = {}
    while True:
        r = input("  > ").strip()
        if not r:
            return res
        if "=" not in r:
            print("  (formato: concepto = monto)")
            continue
        concepto, monto = (x.strip() for x in r.split("=", 1))
        monto = monto.replace("S/", "").replace(",", "").strip()
        if monto == "?":
            res[concepto] = None
            continue
        try:
            res[concepto] = float(monto)
        except ValueError:
            print("  (el monto va como número, o ?)")


def identificador(texto):
    return re.sub(r"[^a-z0-9]+", "-", motor.normalizar(texto)).strip("-")[:40].strip("-")


def plural(palabra):
    if not palabra or palabra[-1].isdigit():
        return palabra
    return palabra + ("s" if palabra[-1] in "aeiouáéíóú" else "es")


def armar_ficha():
    print("Trabajo nuevo para la biblioteca. Enter acepta lo que está entre corchetes.\n")
    nombre = preguntar("1. ¿Cómo se llama el trabajo? (ej: Cambio de garruchas de coches de panadería)")
    fid = identificador(preguntar("   Identificador corto", identificador(nombre)))
    ruta = os.path.join(motor.TRABAJOS, f"{fid}.json")
    if os.path.exists(ruta) and preguntar(f"   Ya existe trabajos/{fid}.json. ¿Reemplazarla?",
                                          "no", ["si", "no"]) != "si":
        raise SystemExit("No se tocó nada.")

    tipos = list(SERVICIOS["tipos"])
    tipo = preguntar(f"\n2. Familia ({' / '.join(tipos)}). Lo que no calza en las otras es "
                     "generales", "generales", tipos)
    ficha = {"id": fid, "nombre": nombre, "tipo": tipo}
    if SERVICIOS["tipos"][tipo].get("subtipo_obligatorio"):
        subtipos = SERVICIOS["subtipos_sugeridos"]
        ficha["subtipo"] = preguntar(f"   Subtipo ({' / '.join(subtipos)})", "otros", subtipos)
    ficha["etiqueta_archivo"] = preguntar(
        "   Palabra para el nombre del PDF", SERVICIOS["tipos"][tipo].get("etiqueta_archivo", "")).upper()

    unidad = preguntar("\n3. ¿Qué se cuenta? En singular (coche, carretilla, balanza, m2, servicio)")
    ficha["unidad"] = unidad
    ficha["unidad_plural"] = preguntar("   En plural", plural(unidad))
    ficha["palabras_clave"] = [p.strip() for p in preguntar(
        "   Palabras con que piden este trabajo, separadas por coma", nombre.lower()).split(",")
        if p.strip()]

    print("\n4. ¿Cómo se pone el precio?")
    print("   1) Sé cuánto me cuesta: el precio sale del costo + markup")
    print("   2) Se cobra por experiencia: el precio se pone en cada pedido")
    if preguntar("   Opción", "1", ["1", "2"]) == "1":
        ficha["modo_precio"] = "costo_mas_markup"
        ficha["costos_fijos"] = costos("\n   Costos FIJOS por visita (lo que cuesta ir, sin "
                                       "importar la cantidad): mano de obra, transporte, SCTR…")
        ficha["costos_por_unidad"] = costos(f"\n   Costos POR {unidad.upper()} (lo que se "
                                            "multiplica por la cantidad): material, repuesto…")
        minimo = numero("   Markup mínimo sobre el costo, en %", 60)
        maximo = numero("   Markup máximo sobre el costo, en %", 80)
        ficha["markup"] = {"minimo": round(minimo / 100, 4), "maximo": round(maximo / 100, 4)}
        ficha["redondeo"] = 5
    else:
        ficha["modo_precio"] = "precio_referencia"
        piso = numero("   Precio mínimo por unidad (? si no hay)", "?", permite_vacio=True)
        ficha["precio_referencia"] = {"piso": piso} if piso is not None else {}

    print("\n5. Checklist: ¿qué hay que saber antes de cotizar? (lo que cambia el precio o el alcance)")
    preguntas = []
    if preguntar("   ¿Incluir las de siempre (Lima o provincia, y horario)?", "si", ["si", "no"]) == "si":
        preguntas = copy.deepcopy(json.load(open(PLANTILLA, encoding="utf-8"))["preguntas"])
    for texto in lista("   Otras preguntas"):
        base = identificador(texto)[:30].strip("-") or "pregunta"
        pid, n = base, 2
        while pid in {p["id"] for p in preguntas}:
            pid, n = f"{base}-{n}", n + 1
        respuestas = [o.strip() for o in preguntar(
            f"     Respuestas posibles para «{texto}», separadas por coma", "si, no").split(",")
            if o.strip()]
        preguntas.append({"id": pid, "pregunta": texto,
                          "opciones": {identificador(o) or o: {"texto": o[0].upper() + o[1:] + "."}
                                       for o in respuestas}})
    ficha["preguntas"] = preguntas

    print("\n6. ¿Cómo se describe en la cotización? {unidades} se reemplaza por la cantidad.")
    print(f"   Ej: Suministro e instalación de … — {{unidades}} {ficha['unidad_plural']}.")
    ficha["redaccion"] = preguntar("   Texto", f"{nombre} — {{unidades}} {ficha['unidad_plural']}.")
    ficha["variables"] = {}
    for marcador in sorted(motor.marcadores(ficha["redaccion"]) - set(motor.VARIABLES_FIJAS)):
        ficha["variables"][marcador] = preguntar(f"   ¿Qué va en {{{marcador}}} por defecto?")

    ficha["condiciones"] = lista("\n7. Condiciones que van siempre en la cotización (retiro de "
                                 "lo cambiado, exclusiones…)")
    ficha["referencias"] = []
    return ficha, ruta


def main():
    try:
        ficha, ruta = armar_ficha()
    except (EOFError, KeyboardInterrupt):
        raise SystemExit("\nSe cortó la entrada: no se guardó nada.")

    errores = motor.validar_ficha(ficha, ficha["id"])
    if errores:
        borrador = os.path.join(motor.TRABAJOS, f"_borrador-{ficha['id']}.json")
        with open(borrador, "w", encoding="utf-8") as f:
            json.dump(ficha, f, ensure_ascii=False, indent=1)
            f.write("\n")
        print("\nLa ficha tiene problemas y NO quedó activa:")
        for e in errores:
            print(f"  - {e}")
        raise SystemExit(f"Quedó como borrador en {borrador}: corregirlo y renombrarlo a "
                         f"{ficha['id']}.json")

    os.makedirs(motor.TRABAJOS, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(ficha, f, ensure_ascii=False, indent=1)
        f.write("\n")
    sin_monto = [c for c, m in {**ficha.get("costos_fijos", {}),
                                **ficha.get("costos_por_unidad", {})}.items() if m is None]
    print(f"\n✓ Ficha guardada: {ruta}")
    if sin_monto:
        print(f"  Sin monto todavía (bloquean el precio hasta completarlos): {', '.join(sin_monto)}")
    ejemplo = {"trabajo": ficha["id"], "cliente": "CLIENTE", "local": "LOCAL", "unidades": 1,
               "respuestas": {p["id"]: next(iter(p["opciones"])) for p in ficha["preguntas"]}}
    print("\nPara cotizarlo, un pedido así (guardarlo como pedido.json y cambiar los datos):")
    print(json.dumps(ejemplo, ensure_ascii=False, indent=1))
    print("\n  python3 herramientas/cotizar_trabajo.py pedido.json salida/")


if __name__ == "__main__":
    main()
