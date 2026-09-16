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
SERVICIOS = json.load(open(os.path.join(RAIZ, "servicios.json"), encoding="utf-8"))
IGV = SERVICIOS["igv"]
MAX_FOTOS = 3


def tipo_de(cot):
    """El tipo de servicio determina el título. No se puede escribir un título a mano.

    Esto cierra por construcción el error de coherencia título/contenido: antes el título y
    la tabla eran dos campos independientes y se podía mandar un título de balanza con
    contenido de carretilla (ver casuistica.md, 14/09/2026).
    """
    if "titulo" in cot:
        raise SystemExit(
            "El JSON trae 'titulo'. El título no se escribe: sale del 'tipo'.\n"
            "Tipos válidos: " + ", ".join(SERVICIOS["tipos"]))
    t = cot.get("tipo")
    if t not in SERVICIOS["tipos"]:
        raise SystemExit(
            f"Falta 'tipo' o no es válido: {t!r}.\n"
            "Tipos válidos: " + ", ".join(SERVICIOS["tipos"]))
    servicio = SERVICIOS["tipos"][t]
    if servicio.get("subtipo_obligatorio") and not cot.get("subtipo"):
        raise SystemExit(
            "Falta 'subtipo'. Todo servicio nuevo entra como 'generales' con una etiqueta\n"
            "corta y estable (espejos, mamparas, laminado-seguridad, acrilicos, motores...).\n"
            "Es lo que permite contar después si merece tipo propio — ver 'promocion' en\n"
            "servicios.json. No se crea un tipo nuevo en medio de una cotización.")
    return servicio


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
    servicio = tipo_de(cot)
    filas, subtotal, n = [], 0.0, 0
    for it in cot["items"]:
        if it.get("separador"):
            # Fila que solo divide visualmente el bloque siguiente (ej. piezas que
            # necesitan un rollo de ancho distinto). No numera, no suma, no lleva precio.
            filas.append(
                f'        <tr class="separador"><td colspan="5">{esc(it["texto"])}</td></tr>'
            )
            continue
        n += 1
        i = n
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
        "TITULO": esc(servicio["titulo"]).upper(),
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

        achicado = encajar_titulo(pg)
        pg.locator(".sheet").screenshot(path=base_salida + ".png")

        # El ancho de la hoja queda fijo (900px, el diseño base); la escala se calcula para
        # que quepa entera en la página, y el sobrante de espacio —horizontal o vertical,
        # según cuál lado tenga holgura— se reparte MITAD Y MITAD como margen, para que la
        # cotización quede centrada en la hoja en vez de pegada arriba/a la izquierda.
        disp_w = (A4_ANCHO_MM - 2 * MARGEN_MM) * PX_POR_MM
        disp_h = (A4_ALTO_MM - 2 * MARGEN_MM) * PX_POR_MM
        caja = pg.locator(".sheet").bounding_box()
        escala = min(disp_w / caja["width"], disp_h / caja["height"], ESCALA_MAX)
        escala = max(escala, ESCALA_MIN)     # más abajo sería ilegible: mejor una 2da página

        sobra_w_mm = max(0, disp_w - caja["width"] * escala) / PX_POR_MM
        sobra_h_mm = max(0, disp_h - caja["height"] * escala) / PX_POR_MM
        m_x = f"{MARGEN_MM + sobra_w_mm / 2:.2f}mm"
        m_y = f"{MARGEN_MM + sobra_h_mm / 2:.2f}mm"

        pg.pdf(path=base_salida + ".pdf", format="A4", landscape=True, print_background=True,
               scale=round(escala, 3),
               margin={"top": m_y, "bottom": m_y, "left": m_x, "right": m_x})
        nav.close()
    return base_salida + ".png", base_salida + ".pdf", achicado


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cot = json.load(open(sys.argv[1], encoding="utf-8"))
    servicio = tipo_de(cot)
    salida = sys.argv[2] if len(sys.argv) > 2 else "."
    os.makedirs(salida, exist_ok=True)

    html, sub, igv, total = construir_html(cot)

    # Validación automática (criterios-actuales.md punto 9, paso 2)
    alertas = []
    for i, it in enumerate((x for x in cot["items"] if not x.get("separador")), start=1):
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
    print(f"IGV {IGV:.0%}    S/ {money(igv)}")
    print(f"Total      S/ {money(total)}")
    print(f"\nVista previa: {png}\nEntregable:   {pdf}")

    # Fila lista para pegar en el registro de costos (Momento 1)
    unidades = sum(it.get("cant", 1) for it in cot["items"] if not it.get("separador"))
    primer_item = next(x for x in cot["items"] if not x.get("separador"))
    print("\nFila para el registro:")
    print(" | ".join([
        cot["numero"], cot["fecha"], cot["cliente"], cot.get("local", ""),
        servicio["categoria_registro"], cot.get("subtipo", ""),
        cot.get("resumen", primer_item["descripcion"])[:60],
        str(unidades), money(sub), money(igv), money(total),
    ]))
    if alertas:
        print("\nREVISAR ANTES DE ENVIAR:")
        for a in alertas:
            print("  - " + a)


if __name__ == "__main__":
    main()
