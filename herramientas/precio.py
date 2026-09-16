#!/usr/bin/env python3
"""
Del costo al precio unitario por zona.

Responde la pregunta que no resolvía `laminado.py`: cuánto se cobra. Toma los costos
reales (rollos, mano de obra, retiro, logística), les aplica el margen, y reparte el
total entre las zonas **según lo que cada zona pesa en el costo**, no según su área.

Por qué no se divide todo entre los m²: el costo no es proporcional al área. Un espejo
de 0.30 x 1.22 toma casi el mismo tiempo que uno de 0.97 x 0.96 —llegar, limpiar,
posicionar, aplicar, recortar— y solo cambia el material, que es la parte chica. Dividir
entre m² cobra de menos las piezas chicas y de más las grandes.

Uso:
    python3 herramientas/precio.py trabajo.json
"""
import json, math, os, sys, importlib.util

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "laminado", os.path.join(RAIZ, "herramientas", "laminado.py"))
lam = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(lam)


def consumo_por_zona(r):
    """Cuánto rollo consume cada zona, repartiendo cada banda entre sus piezas."""
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


def costear(trabajo):
    c = trabajo["costos"]
    r = lam.calcular(trabajo["piezas"],
                     trabajo.get("ancho_rollo", lam.ANCHO_ROLLO),
                     trabajo.get("largo_rollo", lam.LARGO_ROLLO),
                     trabajo.get("sangria", lam.SANGRIA),
                     trabajo.get("merma", lam.MERMA))
    if r["imposibles"]:
        raise SystemExit(
            f"{len(r['imposibles'])} pieza(s) no entran en un rollo de "
            f"{r['ancho_rollo']} m. Van en una cotización aparte, con su propio rollo.\n" +
            "\n".join(f"  - {p['zona']}: {p['w_real']} x {p['h_real']} m"
                      for p in r["imposibles"]))

    zonas = consumo_por_zona(r)
    rollo_total = sum(z["rollo"] for z in zonas.values())

    # Costo directo de cada zona
    for z in zonas.values():
        z["c_material"] = c["precio_rollo"] * r["rollos"] * (z["rollo"] / rollo_total)
        z["c_instalacion"] = c["mo_fijo_pieza"] * z["piezas"] + c["mo_por_m2"] * z["area"]
        z["c_retiro"] = c["retiro_fijo_pieza"] * z["piezas"] + c["retiro_por_m2"] * z["area"]
        z["c_directo"] = z["c_material"] + z["c_instalacion"] + z["c_retiro"]

    # Los fijos del trabajo (movilidad, certificado) se reparten según el peso de cada zona
    fijos = c.get("logistica", 0) + c.get("certificado", 0)
    directo_total = sum(z["c_directo"] for z in zonas.values())
    for z in zonas.values():
        z["c_fijos"] = fijos * (z["c_directo"] / directo_total)
        z["costo"] = z["c_directo"] + z["c_fijos"]

    # Precio: costo + margen, y el unitario se redondea a un número comercial
    margen = trabajo["margen"]
    paso = trabajo.get("redondeo_unitario", 10)
    for z in zonas.values():
        precio = z["costo"] * (1 + margen)
        z["unitario_exacto"] = precio / z["piezas"]
        z["unitario"] = math.ceil(z["unitario_exacto"] / paso) * paso
        z["importe"] = z["unitario"] * z["piezas"]

    return r, zonas, fijos, margen, paso


def informe(trabajo):
    r, zonas, fijos, margen, paso = costear(trabajo)
    c = trabajo["costos"]
    orden = sorted(zonas.items(), key=lambda kv: -kv[1]["importe"])

    costo_total = sum(z["costo"] for z in zonas.values())
    importe = sum(z["importe"] for z in zonas.values())

    inst = sum(z["c_instalacion"] for z in zonas.values())
    ret = sum(z["c_retiro"] for z in zonas.values())

    def linea(etiqueta, monto):
        print(f"  {etiqueta:<46} S/{monto:>10,.2f}")

    print("COSTO DEL TRABAJO")
    linea(f"Material: {r['rollos']} rollo(s) x S/{c['precio_rollo']:,.2f}",
          c["precio_rollo"] * r["rollos"])
    linea(f"Instalación (S/{c['mo_fijo_pieza']}/pieza + S/{c['mo_por_m2']}/m²)", inst)
    linea(f"Retiro del laminado viejo (S/{c['retiro_fijo_pieza']}/pieza + "
          f"S/{c['retiro_por_m2']}/m²)", ret)
    linea("Logística + certificado", fijos)
    print(f"  {'-' * 60}")
    linea("COSTO TOTAL", costo_total)
    linea(f"Margen {margen:.0%}", costo_total * margen)
    linea("PRECIO (antes de redondear)", costo_total * (1 + margen))
    print()

    print(f"PRECIO POR ZONA   (unitario redondeado hacia arriba a S/{paso})")
    print(f"  {'Zona':<24}{'Cant':>5}{'Costo u.':>10}{'P.unit':>9}{'Importe':>11}{'Margen':>8}")
    for nombre, z in orden:
        m = (z["unitario"] - z["costo"] / z["piezas"]) / (z["costo"] / z["piezas"])
        print(f"  {nombre:<24}{z['piezas']:>5}{z['costo'] / z['piezas']:>10,.0f}"
              f"{z['unitario']:>9,.0f}{z['importe']:>11,.0f}{m:>7.0%}")
    igv = importe * 0.18
    print(f"  {'-' * 65}")
    print(f"  {'SUB TOTAL':<24}{'':>5}{'':>10}{'':>9}{importe:>11,.2f}")
    print(f"  {'IGV 18%':<24}{'':>5}{'':>10}{'':>9}{igv:>11,.2f}")
    print(f"  {'TOTAL':<24}{'':>5}{'':>10}{'':>9}{importe + igv:>11,.2f}")

    real = (importe - costo_total) / costo_total
    print(f"\n  Margen real sobre el costo, ya con el redondeo: {real:.1%}")
    if abs(real - margen) > 0.05:
        print(f"  ⚠ El redondeo movió el margen más de 5 puntos. Revisar el paso de "
              f"redondeo o el margen.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    informe(json.load(open(sys.argv[1], encoding="utf-8")))
