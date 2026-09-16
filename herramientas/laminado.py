#!/usr/bin/env python3
"""
Calcula cuántos rollos de lámina se necesitan para un conjunto de piezas.

La lámina NO se compra por metro cuadrado: viene en rollos de ancho fijo (1.50 m por
defecto) y largo fijo (25 m). El cálculo considera además el error humano al cortar: una
merma configurable, un aviso para las bandas sin holgura, y un orden de corte que arranca
por las piezas grandes mientras el rollo está entero. Por eso el desperdicio no depende del área total sino de
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
MERMA = 0.10            # proporción de material que se pierde por cortes arruinados
HOLGURA_MINIMA = 0.05   # menos de esto libre a lo ancho es una banda riesgosa con cutter


def expandir(grupos, sangria):
    """Convierte los grupos del JSON en piezas sueltas, ya con sangría incluida."""
    piezas = []
    for g in grupos:
        for _ in range(g.get("cant", 1)):
            piezas.append({
                "zona": g["zona"],
                "ref": g.get("ref", ""),
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

    # Orden de corte dentro de cada rollo: primero las piezas más grandes, mientras el
    # rollo está entero. Si se arruina un corte grande al inicio, queda material para
    # rehacerlo; si se deja para el final y falla, hay que comprar un rollo por una pieza.
    for r in rollos:
        r["bandas"].sort(key=lambda b: -max(p["across"] * p["along"] for p in b["piezas"]))
    return rollos


def calcular(grupos, ancho_rollo=ANCHO_ROLLO, largo_rollo=LARGO_ROLLO, sangria=SANGRIA,
             merma=MERMA):
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

    # La merma es material que se pierde por cortes arruinados y hay que rehacer. No es la
    # sangría: la sangría son 2 cm que sí se pegan y se recortan al ras. Esto es la pieza
    # que se echó a perder y se corta de nuevo.
    import math
    largo_con_merma = mejor["largo"] * (1 + merma)
    rollos = max(len(lista_rollos), math.ceil(largo_con_merma / largo_rollo))

    # ¿Cuánta merma aguanta el plan antes de necesitar un rollo más?
    capacidad = len(lista_rollos) * largo_rollo
    merma_limite = (capacidad / mejor["largo"]) - 1 if mejor["largo"] else 0

    area_comprada = rollos * ancho_rollo * largo_rollo
    return {**mejor, "piezas": piezas, "rollos": rollos, "lista_rollos": lista_rollos,
            "merma": merma, "largo_con_merma": largo_con_merma,
            "merma_limite": merma_limite, "holgura_minima": HOLGURA_MINIMA,
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
    print(f"Largo de rollo consumido:  {r['largo']:.2f} m   (corte perfecto, sin errores)")
    print(f"  + merma por recortes:    {r['merma']:.0%}  ->  {r['largo_con_merma']:.2f} m")
    print(f"ROLLOS A COMPRAR:          {r['rollos']}")
    print(f"Área comprada:             {r['area_comprada']:.2f} m²")
    print(f"Aprovechamiento:           {r['aprovechamiento']:.1%}  "
          f"(desperdicio {1 - r['aprovechamiento']:.1%})")
    sobra = r["rollos"] * r["largo_rollo"] - r["largo_con_merma"]
    print(f"Margen que queda:          {sobra:.2f} m lineales")
    print(f"Merma que aguanta el plan: hasta {r['merma_limite']:.0%} "
          f"(más que eso obliga a comprar un rollo más)")

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
                ubicadas.append({"rollo": n, "zona": p["zona"], "ref": p.get("ref", ""),
                                 "x": x, "y": y,
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
    print(f"   █ = lámina pegada al vidrio    ░ = recorte que se bota")
    print(f"   ⚠ = menos de {r['holgura_minima'] * 100:.0f} cm libres a lo ancho: a pulso "
          f"con cutter no hay margen de error")
    print(f"   El orden de las bandas ES el orden de corte: primero las piezas grandes,")
    print(f"   mientras el rollo está entero y alcanza para rehacer una que salga mal.\n")

    for i, rollo in enumerate(r["lista_rollos"], start=1):
        usado = r["largo_rollo"] - rollo["libre"]
        print(f"  ROLLO {i}  —  {usado:.2f} m usados de {r['largo_rollo']:.0f} m "
              f"({rollo['libre']:.2f} m sobran)")

        # bandas idénticas se agrupan para que la lista sea legible en campo
        grupos = {}   # dict conserva el orden de inserción = orden de corte
        for b in rollo["bandas"]:
            firma = (round(b["alto"], 2),
                     tuple(((p["zona"] + (f" · {p['ref']}" if p.get("ref") else "")),
                            round(p["across"], 2)) for p in b["piezas"]))
            grupos[firma] = grupos.get(firma, 0) + 1

        # se listan en el orden en que se cortan, no por cantidad
        for (alto, piezas), veces in grupos.items():
            barra, usado_ancho = "", 0.0
            for j, (zona, across) in enumerate(piezas):
                n = max(1, round(across / r["ancho_rollo"] * cols))
                barra += ("|" if j else "") + "█" * n
                usado_ancho += across
            libre = r["ancho_rollo"] - usado_ancho
            barra += "░" * max(0, cols - len(barra.replace("|", "")))
            etiqueta = " + ".join(z for z, _ in piezas)
            riesgo = " ⚠" if libre < r["holgura_minima"] - 1e-9 else ""
            print(f"    x{veces:<3} {alto:>5.2f} m  {barra}  {etiqueta}"
                  f"  (libre {libre:.2f} m){riesgo}")
        print()

    riesgosas = []
    for b in r["bandas"]:
        libre = r["ancho_rollo"] - sum(p["across"] for p in b["piezas"])
        if libre < r["holgura_minima"] - 1e-9 and len(b["piezas"]) > 1:
            riesgosas.append((libre, " + ".join(p["zona"] for p in b["piezas"])))
    if riesgosas:
        print(f"  ⚠ BANDAS SIN HOLGURA — revisar antes de cortar")
        for libre, etiqueta in sorted(riesgosas):
            print(f"      {etiqueta}: solo {libre * 100:.0f} cm libres entre piezas.")
        print(f"      Encajan en el papel, pero a pulso con cutter un desvío de esa "
              f"magnitud\n      arruina las dos piezas. Conviene cortarlas en bandas "
              f"separadas.\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    datos = json.load(open(sys.argv[1], encoding="utf-8"))
    informe(calcular(datos["piezas"],
                     datos.get("ancho_rollo", ANCHO_ROLLO),
                     datos.get("largo_rollo", LARGO_ROLLO),
                     datos.get("sangria", SANGRIA),
                     datos.get("merma", MERMA)))
