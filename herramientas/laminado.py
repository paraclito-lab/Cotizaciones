#!/usr/bin/env python3
"""
Calcula cuántos rollos de lámina se necesitan para un conjunto de piezas.

La lámina NO se compra por metro cuadrado: viene en rollos de ancho fijo (1.50 m por
defecto) y largo fijo (25 m). Por eso el desperdicio no depende del área total sino de
cómo encajan las piezas a lo ancho del rollo. Dos trabajos con los mismos m² pueden
necesitar distinta cantidad de rollos.

Método: corte por bandas (lo que se hace en la práctica con un rollo — se corta de lado a
lado). Las piezas se acomodan una al lado de la otra a lo ancho; cada banda consume, a lo
largo del rollo, lo que mide la pieza más alta de esa banda.

Uso:
    python3 herramientas/laminado.py piezas.json
"""
import json, sys

ANCHO_ROLLO = 1.50
LARGO_ROLLO = 25.0
SANGRIA = 0.02          # margen de corte que se agrega a cada lado de cada pieza


def expandir(grupos, sangria):
    """Convierte los grupos del JSON en piezas sueltas, ya con sangría incluida."""
    piezas = []
    for g in grupos:
        for _ in range(g.get("cant", 1)):
            piezas.append({
                "zona": g["zona"],
                "w": round(g["ancho"] + 2 * sangria, 4),
                "h": round(g["alto"] + 2 * sangria, 4),
                "w_real": g["ancho"], "h_real": g["alto"],
            })
    return piezas


def orientar(p, ancho_rollo, criterio):
    """Devuelve (across, along) o None si la pieza no entra en el ancho del rollo."""
    opciones = [(p["w"], p["h"]), (p["h"], p["w"])]
    validas = [(a, b) for a, b in opciones if a <= ancho_rollo + 1e-9]
    if not validas:
        return None
    if criterio == "angosta":       # ocupa poco ancho -> caben más al costado
        return min(validas, key=lambda o: o[0])
    if criterio == "corta":         # consume poco largo de rollo
        return min(validas, key=lambda o: o[1])
    return max(validas, key=lambda o: o[0])


def empacar(piezas, ancho_rollo, criterio, orden="along", ajuste="mejor"):
    """Acomoda por bandas. Devuelve (bandas, no-encajables).

    criterio: cómo se gira cada pieza (ver orientar).
    orden:    con qué se ordenan antes de acomodar.
    ajuste:   "primera" = primera banda donde entra; "mejor" = la que deja menos hueco.
    """
    orientadas, imposibles = [], []
    for p in piezas:
        o = orientar(p, ancho_rollo, criterio)
        if o is None:
            imposibles.append(p)
        else:
            orientadas.append({**p, "across": o[0], "along": o[1]})

    claves = {"along": lambda p: -p["along"],
              "across": lambda p: -p["across"],
              "area": lambda p: -(p["along"] * p["across"])}
    orientadas.sort(key=claves[orden])

    bandas = []
    for p in orientadas:
        candidatas = [b for b in bandas if b["libre"] >= p["across"] - 1e-9]
        if candidatas:
            b = (min(candidatas, key=lambda b: b["libre"] - p["across"])
                 if ajuste == "mejor" else candidatas[0])
            b["piezas"].append(p)
            b["libre"] -= p["across"]
            b["alto"] = max(b["alto"], p["along"])
        else:
            bandas.append({"piezas": [p], "libre": ancho_rollo - p["across"],
                           "alto": p["along"]})
    return bandas, imposibles


def asignar_rollos(bandas, largo_rollo):
    """Reparte las bandas en rollos. Una banda NO se puede partir entre dos rollos.

    Sumar los metros y dividir entre el largo del rollo subestima: si quedan 0.8 m de
    sobrante y la siguiente banda mide 1.0 m, esa banda arranca un rollo nuevo y esos
    0.8 m se pierden. Se acomodan de mayor a menor para desperdiciar menos punta.
    """
    rollos = []
    for b in sorted(bandas, key=lambda b: -b["alto"]):
        for r in rollos:
            if r["libre"] >= b["alto"] - 1e-9:
                r["bandas"].append(b)
                r["libre"] -= b["alto"]
                break
        else:
            rollos.append({"bandas": [b], "libre": largo_rollo - b["alto"]})
    return rollos


def calcular(grupos, ancho_rollo=ANCHO_ROLLO, largo_rollo=LARGO_ROLLO, sangria=SANGRIA):
    piezas = expandir(grupos, sangria)
    mejor = None
    for criterio in ("angosta", "corta", "ancha"):
        for orden in ("along", "across", "area"):
            for ajuste in ("mejor", "primera"):
                bandas, imposibles = empacar(piezas, ancho_rollo, criterio, orden, ajuste)
                largo = sum(b["alto"] for b in bandas)
                if mejor is None or largo < mejor["largo"]:
                    mejor = {"criterio": criterio, "orden": orden, "ajuste": ajuste,
                             "bandas": bandas, "imposibles": imposibles, "largo": largo}

    area_vidrio = sum(p["w_real"] * p["h_real"] for p in piezas
                      if p not in mejor["imposibles"])
    lista_rollos = asignar_rollos(mejor["bandas"], largo_rollo)
    rollos = len(lista_rollos)
    area_comprada = rollos * ancho_rollo * largo_rollo
    return {**mejor, "piezas": piezas, "rollos": rollos, "lista_rollos": lista_rollos,
            "area_vidrio": area_vidrio, "area_comprada": area_comprada,
            "aprovechamiento": area_vidrio / area_comprada if area_comprada else 0,
            "ancho_rollo": ancho_rollo, "largo_rollo": largo_rollo, "sangria": sangria}


def informe(r):
    print(f"Rollo: {r['ancho_rollo']} m de ancho x {r['largo_rollo']} m de largo "
          f"({r['ancho_rollo'] * r['largo_rollo']:.1f} m² por rollo)")
    print(f"Sangría de corte: {r['sangria'] * 100:.0f} cm por lado\n")

    if r["imposibles"]:
        print(f"⚠  {len(r['imposibles'])} PIEZA(S) NO ENTRAN EN EL ANCHO DEL ROLLO")
        print("   Necesitan empalme, o un rollo más ancho. No están incluidas en el cálculo:")
        for p in r["imposibles"]:
            print(f"     - {p['zona']}: {p['w_real']} x {p['h_real']} m")
        print()

    n = len(r["piezas"]) - len(r["imposibles"])
    print(f"Piezas que sí entran:      {n}")
    print(f"Área de vidrio a cubrir:   {r['area_vidrio']:.2f} m²")
    print(f"Bandas de corte:           {len(r['bandas'])}")
    print(f"Largo de rollo consumido:  {r['largo']:.2f} m")
    print(f"ROLLOS A COMPRAR:          {r['rollos']}")
    print(f"Área comprada:             {r['area_comprada']:.2f} m²")
    print(f"Aprovechamiento:           {r['aprovechamiento']:.1%}  "
          f"(desperdicio {1 - r['aprovechamiento']:.1%})")
    sobra = r["rollos"] * r["largo_rollo"] - r["largo"]
    print(f"Sobrante sin usar:         {sobra:.2f} m lineales")

    colocadas, errores = verificar(r)
    if errores:
        print(f"\n✗ ACOMODO INVÁLIDO — {len(errores)} problema(s):")
        for e in errores[:10]:
            print("    " + e)
    else:
        print(f"\n✓ Verificado: {colocadas} piezas colocadas, ninguna se monta sobre otra "
              f"y ninguna se sale del rollo.")
    mapa(r)

    # Dónde se va el desperdicio: cuánto rollo consume cada zona y cuánto de eso se bota
    print("\nDESPERDICIO POR ZONA (qué está costando el material)")
    print(f"  {'Zona':<24} {'Piezas':>6} {'Vidrio':>9} {'Rollo':>9} {'Aprov.':>7}")
    zonas = {}
    for b in r["bandas"]:
        consumo_banda = b["alto"] * r["ancho_rollo"]
        ancho_usado = sum(p["across"] for p in b["piezas"])
        for p in b["piezas"]:
            z = zonas.setdefault(p["zona"], {"n": 0, "vidrio": 0.0, "rollo": 0.0})
            z["n"] += 1
            z["vidrio"] += p["w_real"] * p["h_real"]
            # el consumo de la banda se reparte según el ancho que ocupa cada pieza
            z["rollo"] += consumo_banda * (p["across"] / ancho_usado)
    for nombre, z in sorted(zonas.items(), key=lambda kv: -(kv[1]["rollo"] - kv[1]["vidrio"])):
        print(f"  {nombre:<24} {z['n']:>6} {z['vidrio']:>8.2f}m² {z['rollo']:>8.2f}m² "
              f"{z['vidrio'] / z['rollo']:>6.0%}")


def ubicar(r):
    """Le da a cada pieza su posición real (x, y) dentro de su rollo.

    x = distancia desde el borde del rollo, a lo ancho.
    y = distancia desde el inicio del rollo, a lo largo.
    Las bandas se apilan a lo largo; dentro de una banda las piezas van una al lado de otra.
    """
    ubicadas = []
    for n, rollo in enumerate(r["lista_rollos"], start=1):
        y = 0.0
        for b in rollo["bandas"]:
            x = 0.0
            for p in b["piezas"]:
                ubicadas.append({"rollo": n, "zona": p["zona"], "x": x, "y": y,
                                 "ancho": p["across"], "largo": p["along"]})
                x += p["across"]
            y += b["alto"]
    return ubicadas


def verificar(r):
    """Comprueba que ninguna pieza se monte sobre otra ni se salga del rollo.

    El acomodo por bandas no debería producir solapamientos, pero eso es una promesa del
    algoritmo. Esto lo mide sobre las coordenadas reales: si alguna vez se cambia la forma
    de acomodar, el error se ve acá y no en el taller con la lámina ya cortada.
    """
    u = ubicar(r)
    tol = 1e-9
    errores = []

    for p in u:
        if p["x"] < -tol or p["x"] + p["ancho"] > r["ancho_rollo"] + tol:
            errores.append(f"{p['zona']} se sale del ancho del rollo {p['rollo']}")
        if p["y"] < -tol or p["y"] + p["largo"] > r["largo_rollo"] + tol:
            errores.append(f"{p['zona']} se sale del largo del rollo {p['rollo']}")

    for i, a in enumerate(u):
        for b in u[i + 1:]:
            if a["rollo"] != b["rollo"]:
                continue
            solapa_x = min(a["x"] + a["ancho"], b["x"] + b["ancho"]) - max(a["x"], b["x"])
            solapa_y = min(a["y"] + a["largo"], b["y"] + b["largo"]) - max(a["y"], b["y"])
            if solapa_x > tol and solapa_y > tol:
                errores.append(f"{a['zona']} se monta sobre {b['zona']} en el rollo "
                               f"{a['rollo']} ({solapa_x:.3f} x {solapa_y:.3f} m)")

    colocadas = len(u)
    esperadas = len(r["piezas"]) - len(r["imposibles"])
    if colocadas != esperadas:
        errores.append(f"se colocaron {colocadas} piezas pero eran {esperadas}")
    return colocadas, errores


def mapa(r, cols=30):
    """Dibuja cómo queda cargado cada rollo. Cada línea es una banda de corte."""
    print(f"\nMAPA DE CADA ROLLO   (ancho = {r['ancho_rollo']} m = {cols} caracteres)")
    print(f"   █ = lámina pegada al vidrio    ░ = recorte que se bota\n")

    for i, rollo in enumerate(r["lista_rollos"], start=1):
        usado = r["largo_rollo"] - rollo["libre"]
        print(f"  ROLLO {i}  —  {usado:.2f} m usados de {r['largo_rollo']:.0f} m "
              f"({rollo['libre']:.2f} m sobran)")

        # bandas idénticas se agrupan para que la lista sea legible en campo
        grupos = {}
        for b in rollo["bandas"]:
            firma = (round(b["alto"], 2),
                     tuple((p["zona"], round(p["across"], 2)) for p in b["piezas"]))
            grupos[firma] = grupos.get(firma, 0) + 1

        for (alto, piezas), veces in sorted(grupos.items(), key=lambda kv: -kv[1]):
            barra, usado_ancho = "", 0.0
            for j, (zona, across) in enumerate(piezas):
                n = max(1, round(across / r["ancho_rollo"] * cols))
                barra += ("|" if j else "") + "█" * n
                usado_ancho += across
            libre = r["ancho_rollo"] - usado_ancho
            barra += "░" * max(0, cols - len(barra.replace("|", "")))
            etiqueta = " + ".join(z for z, _ in piezas)
            print(f"    x{veces:<3} {alto:>5.2f} m  {barra}  {etiqueta}"
                  f"  (libre {libre:.2f} m)")
        print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    datos = json.load(open(sys.argv[1], encoding="utf-8"))
    informe(calcular(datos["piezas"],
                     datos.get("ancho_rollo", ANCHO_ROLLO),
                     datos.get("largo_rollo", LARGO_ROLLO),
                     datos.get("sangria", SANGRIA)))
