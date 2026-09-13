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
ANCHO_MIN, ANCHO_MAX = 700, 1500        # rango en el que se busca el ancho de la hoja


def ajustar_ancho(pg, ratio_objetivo):
    """Busca el ancho de hoja cuya proporción calce con la de la página.

    El alto de la cotización depende de cuánto texto tenga, así que con un ancho fijo la
    hoja casi nunca tiene la misma proporción que el A4 y queda una franja vacía a un lado.
    Ensanchar la hoja acorta las filas y sube la proporción; angostarla la baja. Con unas
    pocas pasadas de búsqueda binaria queda centrada y llenando la página.
    """
    lo, hi = ANCHO_MIN, ANCHO_MAX
    mejor, mejor_dif = None, None
    for _ in range(9):
        medio = (lo + hi) / 2
        pg.eval_on_selector(".sheet", "(el, w) => el.style.width = w + 'px'", medio)
        pg.wait_for_timeout(40)
        caja = pg.locator(".sheet").bounding_box()
        ratio = caja["width"] / caja["height"]
        dif = abs(ratio - ratio_objetivo)
        if mejor_dif is None or dif < mejor_dif:
            mejor, mejor_dif = medio, dif
        if ratio < ratio_objetivo:
            lo = medio          # muy angosta: queda alta, hay que ensancharla
        else:
            hi = medio
    pg.eval_on_selector(".sheet", "(el, w) => el.style.width = w + 'px'", mejor)
    pg.wait_for_timeout(60)


def encajar_titulo(pg):
    """Achica el título si no entra en una línea dentro de su zona del encabezado.

    Los títulos largos ("MANTENIMIENTO DE CARRETILLAS HIDRÁULICAS" ya es de los más largos)
    se salían de la cápsula del encabezado. En vez de dejarlo desbordar, se reduce el tamaño
    de letra hasta que entre, con un piso por debajo del cual ya sería ilegible.
    """
    return pg.evaluate("""() => {
        const el = document.querySelector('.title-overlay');
        if (!el) return null;
        const base = parseFloat(getComputedStyle(el).fontSize);
        let px = base;
        while (el.scrollWidth > el.clientWidth && px > base * 0.6) {
            px -= 0.5;
            el.style.fontSize = px + 'px';
        }
        return px < base ? Math.round(px * 10) / 10 : null;
    }""")


def render(html, base_salida):
    from playwright.sync_api import sync_playwright
    ruta_html = base_salida + ".html"
    open(ruta_html, "w", encoding="utf-8").write(html)
    with sync_playwright() as p:
        nav = p.chromium.launch(executable_path=chromium(), args=["--no-sandbox"])
        pg = nav.new_page(viewport={"width": 940, "height": 1400}, device_scale_factor=2)
        pg.goto("file://" + ruta_html)
        pg.wait_for_timeout(400)

        disp_w = (A4_ANCHO_MM - 2 * MARGEN_MM) * PX_POR_MM
        disp_h = (A4_ALTO_MM - 2 * MARGEN_MM) * PX_POR_MM

        # Primero se ajusta el ancho de la hoja a la proporción de la página, para que no
        # quede una franja vacía al costado ni abajo. Se hace ANTES del PNG, para que la
        # vista previa y el PDF sean exactamente el mismo documento.
        ajustar_ancho(pg, disp_w / disp_h)
        achicado = encajar_titulo(pg)
        pg.locator(".sheet").screenshot(path=base_salida + ".png")

        caja = pg.locator(".sheet").bounding_box()
        escala = min(disp_w / caja["width"], disp_h / caja["height"], ESCALA_MAX)
        escala = max(escala, ESCALA_MIN)     # más abajo sería ilegible: mejor una 2da página

        m = f"{MARGEN_MM}mm"
        pg.pdf(path=base_salida + ".pdf", format="A4", landscape=True, print_background=True,
               scale=round(escala, 3),
               margin={"top": m, "bottom": m, "left": m, "right": m})
        nav.close()
    return base_salida + ".png", base_salida + ".pdf", achicado


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
    png, pdf, achicado = render(html, base)
    if achicado:
        alertas.append(f"el título es largo: se redujo la letra a {achicado}px para que entrara")

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
