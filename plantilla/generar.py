#!/usr/bin/env python3
"""
Genera la vista previa (PNG) y el entregable (PDF) de una cotización.

Uso:
    python3 plantilla/generar.py cotizacion.json [carpeta_de_salida]

El JSON describe la cotización; el subtotal, IGV y total se calculan solos.
Ver plantilla/README.md para el formato y las reglas de negocio.
"""
import base64, io, json, os, re, sys, glob

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADER = os.path.join(RAIZ, "plantilla", "headers", "base.jpg")
TPL = os.path.join(RAIZ, "plantilla", "cotizacion.html")
IGV = 0.18
MAX_FOTOS = 3


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def money(v):
    return f"{v:,.2f}"


def data_uri(ruta, mime="image/jpeg"):
    with open(ruta, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def foto_uri(ruta, lado=180):
    """Achica y encuadra la foto en un cuadrado, sin exigir calidad (criterios punto 8)."""
    from PIL import Image
    im = Image.open(ruta).convert("RGB")
    w, h = im.size
    c = min(w, h)
    im = im.crop(((w - c) // 2, (h - c) // 2, (w + c) // 2, (h + c) // 2)).resize((lado, lado), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=82)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def construir_html(cot):
    filas, subtotal = [], 0.0
    for i, it in enumerate(cot["items"], start=1):
        cant = it.get("cant", 1)
        pu = float(it["precio_unit"])
        imp = cant * pu
        subtotal += imp

        fotos = it.get("fotos", [])[:MAX_FOTOS]
        bloque = ""
        if fotos:
            imgs = "".join(f'<img src="{foto_uri(f)}">' for f in fotos)
            bloque = f'\n        <div class="photo-row">{imgs}</div>'

        filas.append(
            f'        <tr><td class="num">{i}</td><td class="num">{cant}</td>'
            f'<td>{esc(it["descripcion"])}{bloque}</td>'
            f'<td class="money">S/ {money(pu)}</td>'
            f'<td class="money">S/ {money(imp)}</td></tr>'
        )

    igv = round(subtotal * IGV, 2)
    total = round(subtotal + igv, 2)

    nota = cot.get("nota", "").strip()
    nota_html = f'\n    <div class="footer-note">{esc(nota)}</div>' if nota else ""

    html = open(TPL, encoding="utf-8").read()
    for k, v in {
        "HEADER_SRC": data_uri(HEADER),
        "NUMERO": esc(cot["numero"]),
        "TITULO": esc(cot["titulo"]).upper(),
        "CLIENTE": esc(cot["cliente"]).upper(),
        "LOCAL": esc(cot.get("local", "")).upper(),
        "ATENCION": esc(cot.get("atencion", "")).upper(),
        "FECHA": esc(cot["fecha"]),
        "FILAS": "\n".join(filas),
        "SUBTOTAL": money(subtotal),
        "IGV": money(igv),
        "TOTAL": money(total),
        "NOTA": nota_html,
    }.items():
        html = html.replace("{{" + k + "}}", v)
    return html, subtotal, igv, total


def chromium():
    c = glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome")
    return c[0] if c else None


# El PDF va en A4 HORIZONTAL, igual que las cotizaciones reales ya entregadas
# (el PDF de referencia de Moyobamba mide 841.8 x 595.2 pts = A4 apaisado).
MARGEN_MM = 8
PX_POR_MM = 96 / 25.4
A4_ANCHO_MM, A4_ALTO_MM = 297, 210          # apaisado
ESCALA_MIN, ESCALA_MAX = 0.55, 1.30


def render(html, base_salida):
    from playwright.sync_api import sync_playwright
    ruta_html = base_salida + ".html"
    open(ruta_html, "w", encoding="utf-8").write(html)
    with sync_playwright() as p:
        nav = p.chromium.launch(executable_path=chromium(), args=["--no-sandbox"])
        pg = nav.new_page(viewport={"width": 940, "height": 1400}, device_scale_factor=2)
        pg.goto("file://" + ruta_html)
        pg.wait_for_timeout(400)
        pg.locator(".sheet").screenshot(path=base_salida + ".png")

        # Escala que llena la hoja sin dejar espacio muerto: se ajusta al ancho, y si la
        # cotización es larga se achica lo necesario para que entre en una sola página.
        caja = pg.locator(".sheet").bounding_box()
        disp_w = (A4_ANCHO_MM - 2 * MARGEN_MM) * PX_POR_MM
        disp_h = (A4_ALTO_MM - 2 * MARGEN_MM) * PX_POR_MM
        escala = min(disp_w / caja["width"], disp_h / caja["height"], ESCALA_MAX)
        escala = max(escala, ESCALA_MIN)     # más abajo sería ilegible: mejor una 2da página

        m = f"{MARGEN_MM}mm"
        pg.pdf(path=base_salida + ".pdf", format="A4", landscape=True, print_background=True,
               scale=round(escala, 3),
               margin={"top": m, "bottom": m, "left": m, "right": m})
        nav.close()
    return base_salida + ".png", base_salida + ".pdf"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cot = json.load(open(sys.argv[1], encoding="utf-8"))
    salida = sys.argv[2] if len(sys.argv) > 2 else "."
    os.makedirs(salida, exist_ok=True)

    html, sub, igv, total = construir_html(cot)

    # Validación automática (criterios-actuales.md punto 9, paso 2)
    alertas = []
    for i, it in enumerate(cot["items"], start=1):
        if float(it["precio_unit"]) <= 0:
            alertas.append(f"ítem {i} tiene precio 0")
        if len(it.get("fotos", [])) > MAX_FOTOS:
            alertas.append(f"ítem {i} trae más de {MAX_FOTOS} fotos; se usaron las primeras {MAX_FOTOS}")
    if not re.fullmatch(r"COT-\d{4}-\d{3}", cot["numero"]):
        alertas.append(f"el N° '{cot['numero']}' no sigue el formato COT-AAAA-NNN")

    base = os.path.join(salida, cot["numero"])
    png, pdf = render(html, base)

    print(f"Sub Total  S/ {money(sub)}")
    print(f"IGV 18%    S/ {money(igv)}")
    print(f"Total      S/ {money(total)}")
    print(f"\nVista previa: {png}\nEntregable:   {pdf}")
    if alertas:
        print("\nREVISAR ANTES DE ENVIAR:")
        for a in alertas:
            print("  - " + a)


if __name__ == "__main__":
    main()
