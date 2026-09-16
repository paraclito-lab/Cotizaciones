#!/usr/bin/env python3
"""
Del costo al precio unitario por zona — soporta varios rollos (anchos distintos).

Responde la pregunta que no resolvía `laminado.py`: cuánto se cobra. Toma los costos
reales, aplica el margen, y reparte el total entre las zonas según lo que cada zona pesa
en el costo real, no según su área (ver herramientas/README.md, sección "por qué NO se
divide entre m²").

Un trabajo puede necesitar más de un ancho de rollo (ej. la mayoría de piezas en 1.52 m,
4 piezas grandes que solo entran en 1.83 m). Cada ancho es un "grupo": se calcula su propio
acomodo de bandas, y luego todas las zonas de todos los grupos se juntan en una sola tabla
de precios.

Uso:
    python3 herramientas/precio.py trabajo.json
"""
import json, math, os, sys, importlib.util

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "laminado", os.path.join(RAIZ, "herramientas", "laminado.py"))
lam = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(lam)


def consumo_por_zona(r):
    """Cuánto rollo consume cada zona dentro de UN grupo, repartiendo cada banda."""
    zonas = {}
    for b in r["bandas"]:
        consumo = b["alto"] * r["ancho_rollo"]
        ancho_usado = sum(p["across"] for p in b["piezas"])
        for p in b["piezas"]:
            z = zonas.setdefault(p["zona"], {"piezas": 0, "area": 0.0, "rollo": 0.0})
            z["piezas"] += 1
            z["area"] += p["w_real"] * p["h_real"]
            z["rollo"] += consumo * (p["across"] / ancho_usado)
    return zonas


def costear_grupo(grupo, costos):
    """Calcula el acomodo y el costo directo (material) de un grupo (un ancho de rollo)."""
    r = lam.calcular(grupo["piezas"],
                     grupo.get("ancho_rollo", lam.ANCHO_ROLLO),
                     grupo.get("largo_rollo", lam.LARGO_ROLLO),
                     grupo.get("sangria", lam.SANGRIA),
                     grupo.get("merma", lam.MERMA))
    if r["imposibles"]:
        raise SystemExit(
            f"Grupo '{grupo.get('nombre', '?')}': {len(r['imposibles'])} pieza(s) no entran "
            f"en un rollo de {r['ancho_rollo']} m. Necesitan otro grupo con rollo más ancho.\n" +
            "\n".join(f"  - {p['zona']}: {p['w_real']} x {p['h_real']} m"
                      for p in r["imposibles"]))

    precio_rollo = grupo.get("precio_rollo")
    if precio_rollo is None:
        precio_rollo = costos.get("precio_rollo")  # compatibilidad: un solo precio para todos

    zonas = consumo_por_zona(r)
    rollo_total = sum(z["rollo"] for z in zonas.values()) or 1.0

    # Cuánto del rollo comprado se factura a este trabajo:
    #   "completo"     -> se cobran los rollos enteros, aunque sobre material (sobra = activo)
    #   "proporcional" -> solo se cobra lo que de verdad se consume; el resto no se factura
    #                     aquí (queda como inventario para otro servicio, sin costo hundido)
    carga = grupo.get("carga", "completo")
    capacidad = r["rollos"] * r["largo_rollo"]
    material_total = precio_rollo * r["rollos"] if precio_rollo is not None else None
    if material_total is not None and carga == "proporcional":
        material_facturado = material_total * (r["largo_con_merma"] / capacidad)
        material_no_facturado = material_total - material_facturado
    else:
        material_facturado = material_total
        material_no_facturado = 0.0

    for z in zonas.values():
        z["c_material"] = (material_facturado * (z["rollo"] / rollo_total)
                            if material_facturado is not None else None)

    return r, zonas, {
        "nombre": grupo.get("nombre", f"{grupo.get('ancho_rollo')} m"),
        "ancho_rollo": r["ancho_rollo"], "rollos": r["rollos"],
        "largo_con_merma": r["largo_con_merma"], "capacidad": capacidad,
        "carga": carga, "precio_rollo": precio_rollo,
        "material_total": material_total, "material_facturado": material_facturado,
        "material_no_facturado": material_no_facturado,
    }


def costear(trabajo):
    c = trabajo["costos"]
    zonas_todas = {}
    grupos_info = []

    for grupo in trabajo["grupos"]:
        r, zonas, info = costear_grupo(grupo, c)
        grupos_info.append(info)
        for nombre, z in zonas.items():
            clave = f"{nombre} ({info['nombre']})" if len(trabajo["grupos"]) > 1 else nombre
            zonas_todas[clave] = z

    faltan_precio = [g["nombre"] for g in grupos_info if g["material_total"] is None]

    # Mano de obra: una sola tarifa que YA incluye retiro del material viejo (decisión del
    # 16/09/2026: no se separa, se cotiza junto). Ver herramientas/README.md.
    for z in zonas_todas.values():
        mo_fijo = c.get("mo_fijo_pieza")
        mo_m2 = c.get("mo_por_m2")
        z["c_instalacion"] = (mo_fijo * z["piezas"] + mo_m2 * z["area"]) \
            if mo_fijo is not None and mo_m2 is not None else None

    def suma_o_none(valores):
        if any(v is None for v in valores):
            return None
        return sum(valores)

    for z in zonas_todas.values():
        z["c_directo"] = suma_o_none([z["c_material"], z["c_instalacion"]])

    fijos = c.get("logistica"), c.get("certificado")
    fijos_total = suma_o_none(fijos)
    directos_conocidos = [z["c_directo"] for z in zonas_todas.values() if z["c_directo"] is not None]
    directo_total = sum(directos_conocidos) if directos_conocidos else None

    for z in zonas_todas.values():
        if fijos_total is not None and directo_total and z["c_directo"] is not None:
            z["c_fijos"] = fijos_total * (z["c_directo"] / directo_total)
            z["costo"] = z["c_directo"] + z["c_fijos"]
        else:
            z["c_fijos"] = None
            z["costo"] = None

    margen = trabajo["margen"]
    paso = trabajo.get("redondeo_unitario", 10)
    for z in zonas_todas.values():
        if z["costo"] is None:
            z["unitario"] = z["importe"] = None
            continue
        precio = z["costo"] * (1 + margen)
        z["unitario"] = math.ceil((precio / z["piezas"]) / paso) * paso
        z["importe"] = z["unitario"] * z["piezas"]

    return zonas_todas, grupos_info, fijos_total, margen, paso, faltan_precio


def informe(trabajo):
    zonas, grupos_info, fijos, margen, paso, faltan_precio = costear(trabajo)
    c = trabajo["costos"]

    print("=" * 70)
    print("PASO 1 — CÁLCULO DE ROLLOS (laminado.py, por grupo)")
    print("=" * 70)
    for g in grupos_info:
        print(f"\n  Grupo '{g['nombre']}'  (rollo de {g['ancho_rollo']} m de ancho)")
        print(f"    Rollos a comprar:        {g['rollos']}")
        print(f"    Consumido (con merma):   {g['largo_con_merma']:.2f} m "
              f"de {g['capacidad']:.0f} m comprados "
              f"({g['largo_con_merma']/g['capacidad']:.0%} aprovechado)")
        if g["material_total"] is None:
            print(f"    Precio del rollo:        ⚠ NO INGRESADO — no se puede costear")
        else:
            print(f"    Costo del material:      S/{g['material_total']:,.2f}  "
                  f"({g['rollos']} x S/{g['precio_rollo']:,.2f})")
            print(f"    Política de carga:       {g['carga']}"
                  + (f"  — se factura S/{g['material_facturado']:,.2f}, quedan "
                     f"S/{g['material_no_facturado']:,.2f} sin facturar (inventario)"
                     if g["carga"] == "proporcional" else " — se factura el rollo completo"))

    print("\n" + "=" * 70)
    print("PASO 2 — COSTO Y PRECIO POR ZONA (precio.py)")
    print("=" * 70)
    faltan_datos = []
    if c.get("mo_fijo_pieza") is None or c.get("mo_por_m2") is None:
        faltan_datos.append("tarifa de mano de obra (S/ por pieza + S/ por m², incluye retiro)")
    if c.get("logistica") is None:
        faltan_datos.append("logística")
    if c.get("certificado") is None:
        faltan_datos.append("certificado")
    if faltan_precio:
        faltan_datos.append(f"precio del rollo: {', '.join(faltan_precio)}")

    if faltan_datos:
        print("\n  ⚠ NO SE PUEDE CALCULAR EL PRECIO TODAVÍA. Faltan estos datos:")
        for f in faltan_datos:
            print(f"      - {f}")
        print("\n  Se muestra igual la estructura (zonas, piezas, m²) para validar que el")
        print("  cálculo de rollos y el reparto por zona están listos para recibir los costos.\n")

    print(f"  {'Zona':<38}{'Cant':>5}{'m²':>8}{'Costo u.':>10}{'P.unit':>9}{'Importe':>11}")
    orden = sorted(zonas.items(), key=lambda kv: -(kv[1]['importe'] or 0))
    importe_total = 0
    for nombre, z in orden:
        cu = f"{z['costo']/z['piezas']:,.0f}" if z["costo"] is not None else "  ?"
        pu = f"{z['unitario']:,.0f}" if z["unitario"] is not None else "  ?"
        imp = f"{z['importe']:,.0f}" if z["importe"] is not None else "  ?"
        if z["importe"]:
            importe_total += z["importe"]
        print(f"  {nombre:<38}{z['piezas']:>5}{z['area']:>7.2f}m{cu:>10}{pu:>9}{imp:>11}")

    if not faltan_datos:
        igv = importe_total * 0.18
        print(f"  {'-' * 75}")
        print(f"  {'SUB TOTAL':<38}{'':>5}{'':>8}{'':>10}{'':>9}{importe_total:>11,.2f}")
        print(f"  {'IGV 18%':<38}{'':>5}{'':>8}{'':>10}{'':>9}{igv:>11,.2f}")
        print(f"  {'TOTAL':<38}{'':>5}{'':>8}{'':>10}{'':>9}{importe_total + igv:>11,.2f}")
        costo_total = sum(z["costo"] for z in zonas.values())
        real = (importe_total - costo_total) / costo_total
        print(f"\n  Margen real sobre el costo, ya con el redondeo: {real:.1%}")
        if abs(real - margen) > 0.05:
            print(f"  ⚠ El redondeo movió el margen más de 5 puntos.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    informe(json.load(open(sys.argv[1], encoding="utf-8")))
