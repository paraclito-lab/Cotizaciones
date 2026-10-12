#!/usr/bin/env python3
"""
Cotización de laminado de seguridad desde la lista de piezas, con el método de COT-2026-001.

El laminado no se cobra por unidad ni por m² parejo (casuistica.md, 16/09/2026): la lámina se
compra por rollo y el costo depende de cómo encajan las piezas en su ancho. Por eso:

  1. Cada pieza va al rollo estándar (1.52 m) si su lado menor, con sangría, entra; si no, al
     especial (1.82 m). Si tampoco entra ahí, necesita empalme y se cotiza aparte.
  2. `laminado.py` acomoda cada grupo en bandas y da los metros a comprar (con merma).
  3. El material de cada grupo sale de catalogo.md (sección "Lámina de seguridad — rollos").
  4. El precio total lo da quien cotiza (sin IGV): el sistema no aplica margen por su cuenta.
     Se reparte entre los grupos según lo que pesa su material, y dentro de cada grupo según el
     área de cada pieza. Así cada grupo tiene su propio S/ por m² y una pieza grande paga más.
  5. Los precios unitarios se redondean al sol y el redondeo se corrige en las piezas sueltas
     para que el subtotal sea exactamente el precio dado.

Sin precio total sale la propuesta técnica (precios "Pendiente") con el cálculo de rollos en la
nota interna.

pedido = {"trabajo": "laminado-seguridad", "cliente", "local", "atencion"?,
          "piezas": [{"zona", "tipo": "ventana"|"espejo"|"vidrio", "ancho", "alto", "cant"}],
          "precio_total"?: número sin IGV, "certificado"?: bool, "condiciones"?: [...]}
"""
import math, os, re, sys
from decimal import Decimal, ROUND_HALF_UP

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path[:0] = [AQUI]
import laminado as lam              # noqa: E402
import cotizar_trabajo as motor     # noqa: E402

SECCION = "## Lámina de seguridad"
SANGRIA = lam.SANGRIA
MERMA = lam.MERMA
TIPOS = {"ventana": "ventanas", "espejo": "espejos", "vidrio": "vidrios", "mampara": "mamparas"}
MEDIDA_MAX = 6.0     # metros: más que esto es casi seguro un error de tipeo (cm en vez de m)


def rollos_del_catalogo():
    """[{ancho, largo, precio_rollo, precio_metro, tramo}] ordenados del más angosto al más ancho."""
    filas, dentro = [], False
    for linea in open(os.path.join(RAIZ, "catalogo.md"), encoding="utf-8"):
        if linea.startswith("## "):
            dentro = linea.startswith(SECCION)
        if not dentro or not linea.startswith("|"):
            continue
        c = [x.strip() for x in linea.strip().strip("|").split("|")]
        try:
            ancho = float(c[0])
        except ValueError:
            continue
        tramo = re.search(r"(\d+(?:\.\d+)?)\s*m", c[4]) if "tramo" in c[4] else None
        filas.append({"ancho": ancho, "largo": float(c[1]), "precio_rollo": float(c[2]),
                      "precio_metro": float(c[3]) if c[3] else None,
                      "tramo": float(tramo.group(1)) if tramo else None, "estado": c[5]})
    if not filas:
        raise motor.Problema("catalogo.md no tiene la tabla de rollos de lámina de seguridad")
    return sorted(filas, key=lambda r: r["ancho"])


def costo_material(rollo, calculo):
    """Lo que cuesta comprar lo que pide el grupo: rollos completos, o por tramos si conviene."""
    completo = calculo["rollos"] * rollo["precio_rollo"]
    if rollo["precio_metro"] and rollo["tramo"]:
        metros = math.ceil(calculo["largo_con_merma"] / rollo["tramo"]) * rollo["tramo"]
        por_tramos = metros * rollo["precio_metro"]
        if por_tramos < completo:
            return por_tramos, f"{metros:g} m a S/{rollo['precio_metro']:,.2f}"
    rollos = calculo["rollos"]
    return completo, f"{rollos} rollo{'s' if rollos > 1 else ''} de {rollo['largo']:g} m a S/{rollo['precio_rollo']:,.2f}"


def leer_piezas(pedido):
    piezas, errores = [], []
    for i, p in enumerate(pedido.get("piezas") or [], start=1):
        zona = " ".join(str(p.get("zona", "")).split())
        tipo = str(p.get("tipo", "ventana")).lower()
        try:
            ancho, alto, cant = float(p["ancho"]), float(p["alto"]), int(p.get("cant", 1))
        except (KeyError, TypeError, ValueError):
            errores.append(f"pieza {i}: falta el ancho, el alto o la cantidad")
            continue
        if not zona:
            errores.append(f"pieza {i}: falta la zona (ej.: Altillos, Baño hombres)")
        if tipo not in TIPOS:
            errores.append(f"pieza {i}: tipo '{tipo}' desconocido ({', '.join(TIPOS)})")
        if not (0 < ancho <= MEDIDA_MAX and 0 < alto <= MEDIDA_MAX):
            errores.append(f"pieza {i} ({zona}): {ancho} x {alto} no parece estar en metros")
        if cant < 1:
            errores.append(f"pieza {i} ({zona}): la cantidad tiene que ser 1 o más")
        piezas.append({"zona": zona, "tipo": tipo, "ancho": ancho, "alto": alto, "cant": cant})
    if not piezas and not errores:
        errores.append("agrega al menos una pieza con su zona y medidas")
    if errores:
        raise motor.Problema("; ".join(errores))
    return piezas


def texto_pieza(p, certificado):
    lamina = "laminado de seguridad certificado" if certificado else "laminado de seguridad"
    nombre = TIPOS[p["tipo"]] if p["cant"] > 1 else p["tipo"]
    cu = " c/u" if p["cant"] > 1 else ""
    return (f"Suministro e instalación de {lamina} — {p['zona']}: {nombre} de "
            f"{p['ancho']:.2f}m x {p['alto']:.2f}m{cu}.")


def entero(x):
    return int(Decimal(str(x)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


def repartir(piezas, total):
    """Precio unitario entero por pieza; el redondeo se corrige para que sume exactamente total."""
    for p in piezas:
        p["precio"] = entero(p["area"] * p["tarifa"])
    dif = total - sum(p["precio"] * p["cant"] for p in piezas)
    # Primero las piezas sueltas y grandes: un sol más o menos se nota menos ahí.
    for p in sorted(piezas, key=lambda x: (x["cant"], -x["area"])):
        while dif and abs(dif) >= p["cant"]:
            paso = 1 if dif > 0 else -1
            p["precio"] += paso
            dif -= paso * p["cant"]
    return dif


def armar(pedido, hoy):
    """Devuelve (cotización, resumen para quien cotiza). El resumen no va al PDF."""
    piezas = leer_piezas(pedido)
    rollos = rollos_del_catalogo()
    certificado = bool(pedido.get("certificado", True))

    # 1. Grupo de cada pieza: el rollo más angosto en que entra su lado menor.
    for p in piezas:
        menor = min(p["ancho"], p["alto"]) + 2 * SANGRIA
        p["rollo"] = next((r for r in rollos if menor <= r["ancho"]), None)
        p["area"] = p["ancho"] * p["alto"]
        if p["rollo"] is None:
            raise motor.Problema(
                f"{p['zona']}: {p['ancho']:.2f} x {p['alto']:.2f} m no entra ni en el rollo de "
                f"{rollos[-1]['ancho']:.2f} m: necesita empalme. Cotizarla aparte")

    # 2-3. Acomodo y material por grupo.
    grupos = []
    for r in rollos:
        suyas = [p for p in piezas if p["rollo"] is r]
        if not suyas:
            continue
        calc = lam.calcular([{"zona": p["zona"], "cant": p["cant"], "ancho": p["ancho"],
                              "alto": p["alto"]} for p in suyas],
                            r["ancho"], r["largo"], SANGRIA, MERMA)
        costo, compra = costo_material(r, calc)
        grupos.append({"rollo": r, "piezas": suyas, "calc": calc, "material": costo,
                       "compra": compra, "area": sum(p["area"] * p["cant"] for p in suyas)})
    material = sum(g["material"] for g in grupos)

    # Piezas que encajan en el papel con muy poco aire entre ellas: a pulso con cutter un
    # desvío de esa magnitud arruina las dos (casuística 16/09/2026).
    justas = []
    for g in grupos:
        c = g["calc"]
        for b in c["bandas"]:
            libre = c["ancho_rollo"] - sum(x["across"] for x in b["piezas"])
            if libre < c["holgura_minima"] - 1e-9 and len(b["piezas"]) > 1:
                justas.append(f"rollo {c['ancho_rollo']:.2f} m: "
                              + " + ".join(x["zona"] for x in b["piezas"])
                              + f" ({libre * 100:.0f} cm libres)")

    # 4-5. Reparto del precio dado.
    total = pedido.get("precio_total")
    total = entero(total) if total not in (None, "") else None
    if total is not None and total <= 0:
        raise motor.Problema("el precio total tiene que ser mayor que cero")
    resto = 0
    if total is not None:
        for g in grupos:
            precio_grupo = total * g["material"] / material
            g["tarifa"] = precio_grupo / g["area"]
            for p in g["piezas"]:
                p["tarifa"] = g["tarifa"]
        resto = repartir(piezas, total)

    # La cotización: el grupo estándar primero; el especial, bajo un separador.
    items = []
    for k, g in enumerate(grupos):
        if k:
            items.append({"separador": True,
                          "texto": f"Piezas de medida especial (no entran en el rollo de "
                                   f"{grupos[0]['rollo']['ancho']:.2f} m) — material de rollo distinto"})
        for p in g["piezas"]:
            it = {"cant": p["cant"], "descripcion": texto_pieza(p, certificado)}
            if total is None:
                it["pendiente"] = True
            else:
                it["precio_unit"] = p["precio"]
            items.append(it)

    n = sum(p["cant"] for p in piezas)
    m2 = sum(g["area"] for g in grupos)
    nota = f"{n} piezas, {m2:.2f} m² en total."
    if len(grupos) > 1:
        especiales = sum(p["cant"] for g in grupos[1:] for p in g["piezas"])
        ancho, estandar = grupos[1]["rollo"]["ancho"], grupos[0]["rollo"]["ancho"]
        nota += (f" La pieza de medida especial usa un rollo de {ancho:.2f} m porque no entra en "
                 f"el de {estandar:.2f} m." if especiales == 1 else
                 f" Las {especiales} piezas de medida especial usan un rollo de {ancho:.2f} m "
                 f"porque no entran en el de {estandar:.2f} m.")
    if certificado:
        nota += " Incluye emisión de certificado."

    internas = [f"Laminado de seguridad: {n} piezas, {m2:.2f} m²."]
    if justas:
        internas.append("Cortes justos (menos de 5 cm libres entre piezas): " + "; ".join(justas) + ".")
    for g in grupos:
        c = g["calc"]
        linea = (f"Rollo {g['rollo']['ancho']:.2f} m: {sum(p['cant'] for p in g['piezas'])} piezas, "
                 f"{g['area']:.2f} m², {c['largo_con_merma']:.2f} m con {MERMA:.0%} de merma, "
                 f"aprovechamiento {c['aprovechamiento']:.0%}; material {g['compra']} = "
                 f"S/{g['material']:,.2f} ({g['rollo']['estado'].lower()}).")
        if total is not None:
            linea += f" Precio: S/{g['tarifa']:,.2f} por m²."
        internas.append(linea)
    if total is not None:
        internas.append(f"Precio total dado: S/{total:,.2f} sin IGV; el material es "
                        f"{material / total:.0%} del precio. Mano de obra, movilidad e insumos "
                        "no están en el cálculo: revisarlos antes de emitir.")
        if resto:
            internas.append(f"Por redondeo al sol el subtotal difiere en S/{resto} del precio dado.")

    cot = {"tipo": "generales", "subtipo": "laminado-seguridad",
           "cliente": pedido.get("cliente", ""), "local": pedido.get("local", ""),
           "atencion": pedido.get("atencion", ""), "fecha": motor.fecha_larga(hoy),
           "resumen": ("Cambio de laminado de seguridad certificado" if certificado
                       else "Cambio de laminado de seguridad") + f" en {n} piezas",
           "unidades": n, "items": items, "nota": nota,
           "nota_interna": " ".join(internas),
           "etiqueta_archivo": pedido.get("etiqueta_archivo") or "LAMINADO"}
    for clave in ("cliente_corto", "condiciones"):
        if pedido.get(clave):
            cot[clave] = pedido[clave]
    resumen = ["Rollos: " + "; ".join(f"{g['rollo']['ancho']:.2f} m → {g['compra']} (S/{g['material']:,.2f})"
                                    for g in grupos)]
    if justas:
        resumen.append("⚠ Corte justo — " + "; ".join(justas) + ". A pulso con cutter un desvío así "
                       "arruina las dos piezas: cortarlas por separado o con más cuidado.")
    if total is not None:
        resumen.append("Precio por m²: " + "; ".join(f"rollo {g['rollo']['ancho']:.2f} m S/{g['tarifa']:,.2f}"
                                                    for g in grupos) +
                       f". El material es {material / total:.0%} del precio: revisar que cubra mano de obra y movilidad.")
    return cot, resumen
