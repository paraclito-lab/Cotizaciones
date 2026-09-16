#!/usr/bin/env python3
"""
Dibuja, a escala, cómo queda cortado cada rollo — una imagen por rollo físico.

Es la versión visual del mapa de texto de `laminado.py`. Sirve para llevar a campo: cada
pieza aparece en su posición real, con su zona, su medida, y el orden de corte (las bandas
se numeran de la más grande a la más chica — ver `asignar_rollos` en laminado.py).

Uso:
    python3 herramientas/dibujar_rollos.py trabajo.json carpeta_salida/
    python3 herramientas/dibujar_rollos.py piezas.json carpeta_salida/   (un solo ancho)
"""
import json, os, sys, importlib.util
from PIL import Image, ImageDraw, ImageFont

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "laminado", os.path.join(RAIZ, "herramientas", "laminado.py"))
lam = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(lam)

FUENTE_DIR = "/usr/share/fonts/truetype/dejavu"
F_TXT = ImageFont.truetype(f"{FUENTE_DIR}/DejaVuSans.ttf", 15)
F_TXT_CHICA = ImageFont.truetype(f"{FUENTE_DIR}/DejaVuSans.ttf", 12)
F_TITULO = ImageFont.truetype(f"{FUENTE_DIR}/DejaVuSans-Bold.ttf", 20)

PX_POR_M = 130          # escala del dibujo
MARGEN = 60              # px alrededor del rollo, para reglas y título
VERDE = (31, 158, 110)
VERDE_OSC = (23, 121, 95)
GRIS_SOBRA = (225, 225, 225)
ROJO = (200, 40, 40)


def envolver(d, texto, fuente, max_w):
    """Parte un texto en líneas que quepan en max_w px, palabra por palabra."""
    palabras, lineas, actual = texto.split(), [], ""
    for w in palabras:
        prueba = (actual + " " + w).strip()
        if not actual or d.textbbox((0, 0), prueba, font=fuente)[2] <= max_w:
            actual = prueba
        else:
            lineas.append(actual); actual = w
    if actual:
        lineas.append(actual)
    return lineas


def armar_bloque(d, partes, fuente, max_w):
    """Envuelve cada parte (zona, ref, medida) y las junta en una sola lista de líneas."""
    lineas = []
    for parte in partes:
        lineas += envolver(d, parte, fuente, max_w)
    alto_linea = fuente.size + 3
    ancho = max((d.textbbox((0, 0), l, font=fuente)[2] for l in lineas), default=0)
    return lineas, ancho, len(lineas) * alto_linea, alto_linea


def escribir_en_pieza(im, cx, cy, ancho_px, alto_px, partes):
    """Escribe zona + ref + medida centrados en la pieza, partiendo líneas largas.

    Con piezas angostas (ej. Ingreso 211, 0.30 m de across) el texto no entra ni envuelto.
    Ahí se rota 90°, aprovechando que esas piezas angostas suelen ser altas en la banda.
    Si tampoco entra rotado, se muestra solo la medida — mejor eso que texto ilegible
    superpuesto con la pieza vecina.
    """
    d = ImageDraw.Draw(im)

    lineas, ancho, alto, alto_linea = armar_bloque(d, partes, F_TXT_CHICA, ancho_px)
    if ancho <= ancho_px and alto <= alto_px:
        for j, l in enumerate(lineas):
            d.text((cx, cy + (j - (len(lineas) - 1) / 2) * alto_linea), l,
                   font=F_TXT_CHICA, fill=(40, 40, 40), anchor="mm")
        return

    lineas_r, ancho_r, alto_r, alto_linea_r = armar_bloque(d, partes, F_TXT_CHICA, alto_px)
    if ancho_r <= alto_px and alto_r <= ancho_px:
        tmp = Image.new("RGBA", (max(ancho_r, 1), max(alto_r, 1)), (0, 0, 0, 0))
        dt = ImageDraw.Draw(tmp)
        for j, l in enumerate(lineas_r):
            dt.text((ancho_r / 2, (j + 0.5) * alto_linea_r), l, font=F_TXT_CHICA,
                    fill=(40, 40, 40, 255), anchor="mm")
        girado = tmp.rotate(90, expand=True)
        im.paste(girado, (int(cx - girado.width / 2), int(cy - girado.height / 2)), girado)
        return

    # Última opción: solo la medida (siempre la última parte), sin envolver.
    medida = partes[-1]
    if d.textbbox((0, 0), medida, font=F_TXT_CHICA)[2] <= ancho_px:
        d.text((cx, cy), medida, font=F_TXT_CHICA, fill=(40, 40, 40), anchor="mm")


def color_pieza(indice):
    """Paleta que se repite; el color no significa nada, solo separa piezas vecinas."""
    paleta = [(214, 234, 224), (203, 224, 240), (240, 224, 203),
              (233, 214, 234), (224, 240, 214), (240, 214, 214)]
    return paleta[indice % len(paleta)]


def dibujar_rollo(nombre_grupo, ancho_rollo, largo_rollo, rollo_idx, rollo, holgura_min):
    """Una imagen: lo usado a escala real + una franja de 'sobra' recortada.

    Dibujar el sobrante completo (puede ser 15-20 m en un rollo poco aprovechado) deja una
    imagen carguísima de espacio vacío. Se dibuja lo usado, más un tramo corto de sobra a
    escala real, y el resto se indica con una etiqueta — no hace falta verlo para cortar.
    """
    largo_usado = largo_rollo - rollo["libre"]
    franja_sobra = min(rollo["libre"], max(1.0, largo_usado * 0.15))
    largo_mostrado = largo_usado + franja_sobra
    resto_sin_dibujar = rollo["libre"] - franja_sobra

    alto_dibujo = int(ancho_rollo * PX_POR_M)
    ancho_dibujo = int(largo_mostrado * PX_POR_M)

    im = Image.new("RGB", (ancho_dibujo + 2 * MARGEN, alto_dibujo + MARGEN + 90), "white")
    d = ImageDraw.Draw(im)

    ox, oy = MARGEN, 70  # origen del rollo dentro del lienzo

    d.text((MARGEN, 15), f"Rollo {rollo_idx} — grupo '{nombre_grupo}'  "
           f"({ancho_rollo:.2f} m x {largo_rollo:.0f} m)", font=F_TITULO, fill=(30, 30, 30))
    d.text((MARGEN, 42), f"Usado: {largo_usado:.2f} m   Sobra: {rollo['libre']:.2f} m   "
           f"— el orden de las bandas ES el orden de corte", font=F_TXT_CHICA, fill=(90, 90, 90))

    # contorno de lo dibujado (usado + franja corta de sobra a escala real)
    d.rectangle([ox, oy, ox + ancho_dibujo, oy + alto_dibujo], outline=(60, 60, 60), width=2)
    if franja_sobra > 0.01:
        x0 = ox + int(largo_usado * PX_POR_M)
        d.rectangle([x0, oy, ox + ancho_dibujo, oy + alto_dibujo], fill=GRIS_SOBRA)
        etiqueta_sobra = "sobra" if resto_sin_dibujar <= 0.01 else f"sobra\n(+{resto_sin_dibujar:.1f} m más, no dibujado)"
        d.text(((x0 + ox + ancho_dibujo) / 2, oy + alto_dibujo / 2), etiqueta_sobra,
               font=F_TXT_CHICA, fill=(130, 130, 130), anchor="mm", align="center")
    if resto_sin_dibujar > 0.01:
        # corte en zigzag al final, para que quede claro que la imagen no llega hasta ahí
        d.line([ox + ancho_dibujo - 6, oy, ox + ancho_dibujo + 6, oy + alto_dibujo],
               fill=(60, 60, 60), width=2)

    x_cursor = 0.0
    for orden, b in enumerate(rollo["bandas"], start=1):
        bx0 = ox + int(x_cursor * PX_POR_M)
        bx1 = ox + int((x_cursor + b["alto"]) * PX_POR_M)
        y_cursor = 0.0
        for i, p in enumerate(b["piezas"]):
            py0 = oy + int(y_cursor * PX_POR_M)
            py1 = oy + int((y_cursor + p["across"]) * PX_POR_M)
            d.rectangle([bx0, py0, bx1, py1], fill=color_pieza(orden + i),
                        outline=(120, 120, 120), width=1)

            partes = [p["zona"]] + ([p["ref"]] if p.get("ref") else []) + \
                [f"{p['w_real']:.2f}x{p['h_real']:.2f}m"]
            cx, cy = (bx0 + bx1) / 2, (py0 + py1) / 2
            escribir_en_pieza(im, cx, cy, bx1 - bx0 - 4, py1 - py0 - 4, partes)
            y_cursor += p["across"]

        # holgura sin usar dentro de la banda
        libre = ancho_rollo - y_cursor
        if libre > 0.001:
            py0 = oy + int(y_cursor * PX_POR_M)
            d.rectangle([bx0, py0, bx1, oy + alto_dibujo], fill=GRIS_SOBRA,
                        outline=(150, 150, 150))
        arriesgada = libre < holgura_min - 1e-9 and len(b["piezas"]) > 1
        color_borde = ROJO if arriesgada else VERDE_OSC
        grosor = 3 if arriesgada else 2
        d.rectangle([bx0, oy, bx1, oy + alto_dibujo], outline=color_borde, width=grosor)

        # número de orden de corte, arriba de la banda
        d.text(((bx0 + bx1) / 2, oy - 10), str(orden), font=F_TXT, fill=VERDE_OSC, anchor="mm")
        if arriesgada:
            d.text(((bx0 + bx1) / 2, oy + alto_dibujo + 14), "⚠ sin holgura",
                   font=F_TXT_CHICA, fill=ROJO, anchor="mm")

        x_cursor += b["alto"]

    # regla de ancho a la izquierda
    d.text((10, oy + alto_dibujo / 2), f"{ancho_rollo:.2f} m", font=F_TXT_CHICA,
           fill=(90, 90, 90), anchor="mm")
    return im


def dibujar_grupo(nombre, r, carpeta):
    os.makedirs(carpeta, exist_ok=True)
    rutas = []
    for i, rollo in enumerate(r["lista_rollos"], start=1):
        im = dibujar_rollo(nombre, r["ancho_rollo"], r["largo_rollo"], i, rollo,
                           r["holgura_minima"])
        ruta = os.path.join(carpeta, f"rollo_{nombre}_{i}.png")
        im.save(ruta)
        rutas.append(ruta)
    return rutas


def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    datos = json.load(open(sys.argv[1], encoding="utf-8"))
    carpeta = sys.argv[2]

    grupos = datos["grupos"] if "grupos" in datos else [
        {"nombre": "rollo", "ancho_rollo": datos.get("ancho_rollo", lam.ANCHO_ROLLO),
         "largo_rollo": datos.get("largo_rollo", lam.LARGO_ROLLO),
         "sangria": datos.get("sangria", lam.SANGRIA), "merma": datos.get("merma", lam.MERMA),
         "piezas": datos["piezas"]}]

    todas = []
    for g in grupos:
        r = lam.calcular(g["piezas"], g.get("ancho_rollo", lam.ANCHO_ROLLO),
                         g.get("largo_rollo", lam.LARGO_ROLLO),
                         g.get("sangria", lam.SANGRIA), g.get("merma", lam.MERMA))
        colocadas, errores = lam.verificar(r)
        if errores:
            print(f"⚠ Grupo '{g.get('nombre')}': el acomodo no pasó la verificación, no se dibuja.")
            for e in errores[:5]:
                print("   -", e)
            continue
        rutas = dibujar_grupo(g.get("nombre", "rollo"), r, carpeta)
        todas += rutas
        print(f"Grupo '{g.get('nombre')}': {len(rutas)} imagen(es) -> " + ", ".join(rutas))
        if r["imposibles"]:
            print(f"   ({len(r['imposibles'])} pieza(s) no entraron y no están dibujadas)")

    print(f"\nTotal: {len(todas)} imágenes en {carpeta}")


if __name__ == "__main__":
    main()
