#!/usr/bin/env python3
"""
Genera la vista previa (PNG) y el entregable (PDF) de una cotización.

Uso:
    python3 plantilla/generar.py cotizacion.json [carpeta_de_salida] [--sin-precios | --final]

El JSON describe la cotización; el subtotal, el IGV y el total se calculan solos.

  --sin-precios  Propuesta técnica: todos los ítems `pendiente` y los totales en "Por
                 definir". Para validar el alcance con el cliente antes de costear.
  --final        El paso de aprobación en un solo comando: exige el N° real y ningún precio
                 pendiente, deja el PDF con su nombre de entrega ("N° 9196-2026 CARRETILLAS
                 TT PUCALLPA MUNAY.pdf") y archiva imagen + JSON en cotizaciones-emitidas/
                 (reemplaza la copia anterior de ese N°).
  --archivar     Solo archiva, sin las exigencias de --final. Se mantiene por compatibilidad.

Ver plantilla/README.md para el formato y las reglas de negocio.
"""
import base64, glob, io, json, os, re, shutil, sys
from decimal import Decimal, ROUND_HALF_UP

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HEADER = os.path.join(RAIZ, "plantilla", "headers", "base.jpg")
TPL = os.path.join(RAIZ, "plantilla", "cotizacion.html")
SERVICIOS = json.load(open(os.path.join(RAIZ, "servicios.json"), encoding="utf-8"))
IGV = Decimal(str(SERVICIOS["igv"]))
VALIDEZ_DIAS = SERVICIOS["validez_dias"]
MAX_FOTOS = 3
CENTIMO = Decimal("0.01")
OPCIONES = {"--sin-precios", "--final", "--archivar"}

# El archivo de lo emitido se guarda como imagen comprimida, no como PDF: el PDF pesa el doble
# y el repositorio se llenaría. La imagen a tamaño 1x con JPEG queda legible y ~3x más liviana.
# Junto a la imagen va el JSON fuente: sin él, corregir un ítem semanas después obligaba a
# rehacer la cotización de memoria (hallazgos-abiertos.md, N02).
ARCHIVO = os.path.join(RAIZ, "cotizaciones-emitidas")
ARCHIVO_CALIDAD = 85

# La numeración que se usa en la práctica es NNNN-AAAA (8211-2026, 9196-2026). COT-AAAA-NNN
# quedó decidida pero nunca se adoptó (hallazgos N14, Q4). Se aceptan las dos: una alerta que
# sale en el 100% de las cotizaciones reales entrena a ignorar todas las alertas.
NUMERO_REAL = re.compile(r"COT-\d{4}-\d{3}|\d{3,5}-\d{4}")

# Texto que delata razonamiento interno de precios. Si aparece en algo que el cliente ve, no se
# genera: pasó tres veces en una semana con la `nota` (hallazgos N07), y la regla escrita en la
# skill no lo evitó. Lo interno va en `nota_interna`, que nunca se imprime.
TERMINOS_INTERNOS = (".md", "catalogo", "catálogo", "criterios-actuales", "piso mínimo",
                     "piso minimo", "por validar", "markup", "ganancia", "utilidad",
                     "costo de compra", "precio de venta")


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
    if servicio.get("subtipo_obligatorio"):
        sub = cot.get("subtipo")
        validos = SERVICIOS["subtipos_sugeridos"]
        if not sub:
            raise SystemExit(
                "Falta 'subtipo'. Todo servicio nuevo entra como 'generales' con una etiqueta\n"
                "corta y estable (espejos, mamparas, laminado-seguridad, acrilicos, motores...).\n"
                "Es lo que permite contar después si merece tipo propio — ver 'promocion' en\n"
                "servicios.json. No se crea un tipo nuevo en medio de una cotización.")
        # Un subtipo mal escrito pasaba en silencio y creaba una categoría fantasma de una
        # sola cotización — justo lo que el umbral de promoción (3 del mismo subtipo) existe
        # para evitar. Si no se puede contar, la regla no sirve.
        if sub not in validos:
            raise SystemExit(
                f"El subtipo {sub!r} no está en 'subtipos_sugeridos' de servicios.json.\n"
                f"Válidos: {', '.join(validos)}.\n"
                "Si de verdad no calza ninguno, se usa 'otros' y se anota el caso en\n"
                "casuistica.md. No se inventa un subtipo nuevo al vuelo: rompe el conteo\n"
                "del que depende la promoción a tipo propio.")
    return servicio


def esc(t):
    return (str(t).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def money(v):
    return f"{v:,.2f}"


def dinero(v):
    """Monto en Decimal con redondeo contable. Con float, el IGV de un subtotal de S/30.25
    salía S/5.44 en vez de S/5.45 (hallazgos N27)."""
    return Decimal(str(v)).quantize(CENTIMO, rounding=ROUND_HALF_UP)


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


def items_cotizados(cot):
    """Los ítems numerados, en orden (los separadores no cuentan)."""
    return [x for x in cot["items"] if not x.get("separador")]


def calcular(cot):
    """Subtotal, IGV y total. Separado del HTML para poder probarlo sin navegador."""
    subtotal = Decimal("0")
    for it in items_cotizados(cot):
        if it.get("pendiente") or "precio_unit" not in it:
            continue
        subtotal += dinero(Decimal(str(it.get("cant", 1))) * dinero(it["precio_unit"]))
    igv = dinero(subtotal * IGV)
    return subtotal, igv, subtotal + igv


def unidades_de(cot):
    """Cuántos equipos se atienden: es lo que el registro divide para "precio por unidad".

    Antes se sumaba la cantidad de TODOS los ítems, y Pucallpa se registraba con 33 unidades
    (10 traspaletas + 5 botellas + 16 ruedas + 2 direccionales) en vez de 10 — justo el dato
    con el que se calibra la fórmula en el mes de prueba (hallazgos N04). Va explícito en el
    JSON; si falta, se toma la cantidad del ítem 1, que en carretillas es el mantenimiento.
    """
    if "unidades" in cot:
        return cot["unidades"]
    return items_cotizados(cot)[0].get("cant", 1)


def recortar(texto, largo=60):
    """Acorta en una palabra completa, no a la mitad ("…hidráulicas (stock")."""
    texto = " ".join(str(texto).split())
    if len(texto) <= largo:
        return texto
    corte = texto[:largo + 1].rsplit(" ", 1)[0]
    return corte.rstrip(" ,;:(—-") + "…"


def textos_cliente(cot):
    """Todo el texto libre que termina impreso en el PDF."""
    yield "la nota", cot.get("nota", "")
    for c in cot.get("condiciones", []):
        yield "una condición", c
    n = 0
    for it in cot["items"]:
        if it.get("separador"):
            yield "un separador", it.get("texto", "")
        else:
            n += 1
            yield f"el ítem {n}", it.get("descripcion", "")


def validar(cot, servicio, sub, sin_precios=False, final=False, archivar_pedido=False):
    """Revisa la cotización antes de renderizar. Devuelve (errores, alertas, avisos).

    Los errores bloquean. Las alertas van en "REVISAR ANTES DE ENVIAR". Los avisos son
    información que no exige hacer nada — van aparte para que las alertas no se vuelvan ruido
    de fondo (hallazgos N14).
    """
    errores, alertas, avisos = [], [], []
    items = items_cotizados(cot)
    if not items:
        return ["la cotización no tiene ítems"], alertas, avisos

    if not isinstance(cot.get("condiciones", []), list):
        errores.append("'condiciones' tiene que ser una lista de frases, no un texto suelto")
        cot = dict(cot, condiciones=[])

    for i, it in enumerate(items, start=1):
        if not str(it.get("descripcion", "")).strip():
            errores.append(f"el ítem {i} no tiene 'descripcion'")
        cant = it.get("cant", 1)
        if cant < 1:
            errores.append(f"ítem {i} tiene cantidad {cant}: no se cotiza algo que no se entrega")
        if it.get("pendiente"):
            if "precio_unit" in it:
                errores.append(f"el ítem {i} trae 'pendiente' y 'precio_unit' a la vez: es "
                               "ambiguo. Si ya tiene precio, quitar 'pendiente'")
            elif not sin_precios:
                alertas.append(f"ítem {i} tiene precio PENDIENTE — confirmar antes de enviar")
        elif "precio_unit" not in it:
            errores.append(f"el ítem {i} no trae 'precio_unit' "
                           f"({recortar(it.get('descripcion', '(sin descripción)'))}). Si el "
                           "precio no está en catalogo.md no se inventa: se pregunta, o el "
                           "ítem se marca 'pendiente'")
        else:
            pu = dinero(it["precio_unit"])
            if pu < 0:
                errores.append(f"ítem {i} tiene precio negativo (S/ {money(pu)})")
            elif pu == 0:
                errores.append(f"ítem {i} tiene precio 0")
        if len(it.get("fotos", [])) > MAX_FOTOS:
            alertas.append(f"ítem {i} trae más de {MAX_FOTOS} fotos; se usan las primeras {MAX_FOTOS}")

    for donde, texto in textos_cliente(cot):
        hallados = [t for t in TERMINOS_INTERNOS if t in str(texto).lower()]
        if hallados:
            errores.append(f"{donde} tiene texto interno ({', '.join(hallados)}) y el cliente "
                           "lo vería impreso. Eso va en 'nota_interna', que no se imprime")

    if sin_precios:
        # Mezclar precios con "Por definir" en los totales daría un documento que se contradice:
        # filas con importe y un Total que dice que no hay total.
        if sub > 0:
            errores.append(f"--sin-precios pero hay ítems con precio (subtotal S/ {money(sub)}): "
                           "o se quitan esos precios, o se genera la cotización normal")
        if archivar_pedido:
            errores.append("--sin-precios no se archiva ni se emite como final: se archiva la "
                           "versión aprobada, con precios")
        alertas.append("documento SIN PRECIOS: es una propuesta técnica para validar el "
                       "alcance, NO una cotización para aprobar")
    elif sub <= 0:
        errores.append(f"el subtotal es S/ {money(sub)}: no se emite una cotización sin monto")

    # El piso vivía en servicios.json pero nada lo leía: 9197-2026 salió a S/230 sin ningún
    # aviso (hallazgos N12). Es alerta y no bloqueo porque puede haber excepciones autorizadas.
    piso = servicio.get("precio_minimo_unidad")
    primero = items[0]
    if piso and "precio_unit" in primero and not primero.get("pendiente"):
        pu = dinero(primero["precio_unit"])
        if pu < dinero(piso):
            alertas.append(f"ítem 1 (mantenimiento) a S/ {money(pu)} por unidad: bajo el piso de "
                           f"S/ {money(dinero(piso))}. Si es una excepción autorizada, dejar el "
                           "motivo en 'nota_interna'")

    numero = cot["numero"]
    if not NUMERO_REAL.fullmatch(numero):
        if final:
            errores.append(f"--final exige el N° real con que se envía; '{numero}' no lo es")
        else:
            alertas.append(f"el N° '{numero}' no es un correlativo real (NNNN-AAAA)")

    if final:
        pendientes = [str(i) for i, it in enumerate(items, start=1) if it.get("pendiente")]
        if pendientes:
            errores.append(f"--final con precio pendiente en el ítem {', '.join(pendientes)}: se "
                           "emite cuando todo tiene precio")

    if not sin_precios and "unidades" not in cot:
        avisos.append(f"sin 'unidades' en el JSON: el registro toma {unidades_de(cot)} (la "
                      "cantidad del ítem 1). Si el ítem 1 no cuenta equipos, agregar 'unidades'")
    return errores, alertas, avisos


def construir_html(cot, servicio, sub, igv, total, sin_precios=False):
    filas, n = [], 0
    for it in cot["items"]:
        if it.get("separador"):
            # Fila que solo divide visualmente el bloque siguiente (ej. piezas que
            # necesitan un rollo de ancho distinto). No numera, no suma, no lleva precio.
            filas.append(
                f'        <tr class="separador"><td colspan="5">{esc(it["texto"])}</td></tr>'
            )
            continue
        n += 1
        cant = it.get("cant", 1)
        fotos = it.get("fotos", [])[:MAX_FOTOS]
        bloque = ""
        if fotos:
            imgs = "".join(f'<img src="{foto_uri(f)}">' for f in fotos)
            bloque = f'\n        <div class="photo-row">{imgs}</div>'
        if it.get("pendiente"):
            # Ítem con sustento técnico ya definido pero sin precio todavía: fila normal,
            # numerada, que no suma al Sub Total hasta que tenga precio.
            precio = importe = '<td class="money pendiente">Pendiente</td>'
        else:
            pu = dinero(it["precio_unit"])
            precio = f'<td class="money">S/ {money(pu)}</td>'
            importe = f'<td class="money">S/ {money(dinero(Decimal(str(cant)) * pu))}</td>'
        filas.append(
            f'        <tr><td class="num">{n}</td><td class="num">{cant}</td>'
            f'<td>{esc(it["descripcion"])}{bloque}</td>{precio}{importe}</tr>'
        )

    atencion = cot.get("atencion", "").strip()
    fila_atencion = (f'<div><b>Atenci&oacute;n:</b> {esc(atencion).upper()}</div>'
                     if atencion else "")

    # Condiciones (alcance, horario, exclusiones) en su propio bloque, no mezcladas en la nota.
    condiciones = [c.strip() for c in cot.get("condiciones", []) if c.strip()]
    condiciones_html = ""
    if condiciones:
        lis = "".join(f"<li>{esc(c)}</li>" for c in condiciones)
        condiciones_html = f'\n    <div class="condiciones"><b>Condiciones:</b><ul>{lis}</ul></div>'

    nota = cot.get("nota", "").strip()
    nota_html = f'\n    <div class="footer-note">{esc(nota)}</div>' if nota else ""

    html = open(TPL, encoding="utf-8").read()
    for k, v in {
        "HEADER_SRC": data_uri(HEADER),
        "NUMERO": esc(cot["numero"]),
        "TITULO": esc(servicio["titulo"]).upper(),
        "CLIENTE": esc(cot["cliente"]).upper(),
        "LOCAL": esc(cot.get("local", "")).upper(),
        "FILA_ATENCION": fila_atencion,
        "FECHA": esc(cot["fecha"]),
        "FILAS": "\n".join(filas),
        "VALIDEZ": str(VALIDEZ_DIAS),
        # Un documento sin precios muestra "Por definir", nunca "S/ 0.00": un total en cero se
        # lee como gratis, y ese es justamente el riesgo de emitir la propuesta técnica.
        "SUBTOTAL": "Por definir" if sin_precios else f"S/ {money(sub)}",
        "IGV": "Por definir" if sin_precios else f"S/ {money(igv)}",
        "TOTAL": "Por definir" if sin_precios else f"S/ {money(total)}",
        "CLASE_TOTALES": "sin-precios" if sin_precios else "",
        "CONDICIONES": condiciones_html,
        "NOTA": nota_html,
    }.items():
        html = html.replace("{{" + k + "}}", v)
    sobrantes = re.findall(r"\{\{\w+\}\}", html)
    if sobrantes:
        raise SystemExit(f"La plantilla tiene marcadores que el generador no llena: {sobrantes}")
    return html


def nombre_entrega(cot, servicio):
    """'N° 9196-2026 CARRETILLAS TT PUCALLPA MUNAY.pdf': la convención con que se entrega.

    Antes el PDF se renombraba a mano después de cada cotización (hallazgos N24).
    """
    partes = [cot["numero"],
              cot.get("etiqueta_archivo") or servicio.get("etiqueta_archivo", ""),
              cot.get("cliente_corto") or cot["cliente"],
              cot.get("local", "")]
    nombre = " ".join(" ".join(str(p).split()).upper() for p in partes if str(p).strip())
    return "N° " + re.sub(r'[\\/:*?"<>|]', "-", nombre) + " MUNAY.pdf"


def fila_registro(cot, servicio, sub, igv, total):
    """Las dos líneas para pegar en el registro: columnas A-K y las columnas nuevas del final."""
    primero = items_cotizados(cot)[0]
    etapa1 = [cot["numero"], cot["fecha"], cot["cliente"], cot.get("local", ""),
              servicio["categoria_registro"], cot.get("subtipo", ""),
              recortar(cot.get("resumen") or primero["descripcion"]),
              str(unidades_de(cot)), money(sub), money(igv), money(total)]
    def monto(clave):
        return money(dinero(cot[clave])) if clave in cot else ""

    nuevas = [monto("costo_estimado"), monto("subtotal_calculado"),
              " ".join(cot.get("nota_interna", "").split())]
    return " | ".join(etapa1), (" | ".join(nuevas) if any(nuevas) else "")


def chromium():
    c = glob.glob("/opt/pw-browsers/chromium*/chrome-linux/chrome")
    return c[0] if c else None


# El PDF no es para imprimir en papel físico, es un archivo para pantalla — no tiene que
# calzar en un tamaño de hoja exacto. La página se arma del tamaño real del contenido más un
# margen fijo, y la orientación sale sola de la forma del contenido (más ancho que alto ->
# apaisada; más alto que ancho -> vertical). Antes se forzaba siempre A4 apaisado de 297x210mm
# fijo: cuando una cotización con muchas filas crecía en alto más que en ancho, el contenido se
# ajustaba por la altura y sobraba muchísimo margen vacío a los costados (ver casuistica.md).
# LADO_MAYOR_MM es solo una referencia de tamaño "más o menos A4", no un marco que llenar.
MARGEN_MM = 8
PX_POR_MM = 96 / 25.4
LADO_MAYOR_MM = 297
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
        # que su lado más largo (ancho o alto, según cuál domine) llegue a "más o menos A4".
        # La página del PDF se dimensiona EXACTO al contenido ya escalado + el margen fijo, así
        # que no queda holgura que repartir: el margen es el mismo en los 4 lados por
        # construcción, no por centrado después.
        caja = pg.locator(".sheet").bounding_box()
        lado_mayor_px = max(caja["width"], caja["height"])
        escala = (LADO_MAYOR_MM - 2 * MARGEN_MM) * PX_POR_MM / lado_mayor_px
        escala = min(escala, ESCALA_MAX)
        escala = max(escala, ESCALA_MIN)     # más abajo sería ilegible: mejor una 2da página

        ancho_mm = caja["width"] * escala / PX_POR_MM + 2 * MARGEN_MM
        alto_mm = caja["height"] * escala / PX_POR_MM + 2 * MARGEN_MM
        margen = f"{MARGEN_MM}mm"

        pg.pdf(path=base_salida + ".pdf", width=f"{ancho_mm:.2f}mm", height=f"{alto_mm:.2f}mm",
               print_background=True, scale=round(escala, 3),
               margin={"top": margen, "bottom": margen, "left": margen, "right": margen})
        nav.close()
    return base_salida + ".png", base_salida + ".pdf", achicado


def archivar(png, numero):
    """Guarda copia de lo emitido como imagen comprimida, no como PDF.

    El PDF de una cotización pesa ~334 KB y el PNG de vista previa ~675 KB (viene a 2x para
    que se vea nítido en pantalla). Bajado a 1x y en JPEG queda en ~220 KB: legible, y el
    repositorio no crece a saltos. Se guarda por N° de cotización, así que regenerar el mismo
    número reemplaza su copia — el archivo conserva la última versión de cada cotización.
    """
    from PIL import Image
    os.makedirs(ARCHIVO, exist_ok=True)
    im = Image.open(png).convert("RGB")
    w, h = im.size
    im = im.resize((w // 2, h // 2), Image.LANCZOS)
    destino = os.path.join(ARCHIVO, numero + ".jpg")
    im.save(destino, "JPEG", quality=ARCHIVO_CALIDAD, optimize=True)
    return destino


def archivar_json(cot):
    """Guarda el JSON fuente junto a la imagen: es lo que permite corregir después."""
    os.makedirs(ARCHIVO, exist_ok=True)
    destino = os.path.join(ARCHIVO, cot["numero"] + ".json")
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(cot, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return destino


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    opciones = {a for a in sys.argv[1:] if a.startswith("--")}
    if opciones - OPCIONES:
        raise SystemExit(f"Opción desconocida: {', '.join(sorted(opciones - OPCIONES))}. "
                         f"Válidas: {', '.join(sorted(OPCIONES))}")
    cot = json.load(open(args[0], encoding="utf-8"))
    servicio = tipo_de(cot)
    salida = args[1] if len(args) > 1 else "."
    os.makedirs(salida, exist_ok=True)

    # Propuesta técnica: el documento sale con el alcance definido y los precios todavía no.
    # Sirve para que el cliente valide la especificación antes de costear (en trabajos donde la
    # especificación es la que manda el precio, cotizar antes de fijarla es cotizar a ciegas).
    sin_precios = "--sin-precios" in opciones
    final = "--final" in opciones
    # El archivado NO es automático: se archiva la cotización aprobada. Cuando era automático,
    # cualquier prueba o regeneración de ejemplo pisaba la copia de la cotización real ya
    # enviada (pasó al implementarlo: el ejemplo con placeholder sobrescribió la real).
    archivar_pedido = final or "--archivar" in opciones

    sub, igv, total = calcular(cot)
    errores, alertas, avisos = validar(cot, servicio, sub, sin_precios, final, archivar_pedido)
    if errores:
        raise SystemExit("NO SE GENERA — hay que corregir esto primero:\n" +
                         "\n".join("  - " + e for e in errores))

    html = construir_html(cot, servicio, sub, igv, total, sin_precios)
    base = os.path.join(salida, cot["numero"])
    png, pdf, achicado = render(html, base)
    if achicado:
        avisos.append(f"título reducido a {achicado}px para que entre en una línea")

    entregable = pdf
    if final:
        entregable = os.path.join(salida, nombre_entrega(cot, servicio))
        shutil.copyfile(pdf, entregable)
    archivados = [archivar(png, cot["numero"]), archivar_json(cot)] if archivar_pedido else []

    if sin_precios:
        print("Sub Total  Por definir  (documento sin precios)")
        print(f"IGV {IGV:.0%}    Por definir")
        print("Total      Por definir")
    else:
        print(f"Sub Total  S/ {money(sub)}")
        print(f"IGV {IGV:.0%}    S/ {money(igv)}")
        print(f"Total      S/ {money(total)}")
    print(f"Validez    {VALIDEZ_DIAS} días")
    print(f"\nVista previa: {png}\nEntregable:   {entregable}")
    if archivados:
        print("Archivado:    " + "  +  ".join(archivados))
    else:
        print("Archivado:    no (usar --final cuando la cotización esté aprobada)")

    # Un documento sin precios no se registra: entraría con monto 0 y ensuciaría el ticket
    # promedio y el markup.
    if sin_precios:
        print("\nFila para el registro: no corresponde todavía — se registra cuando tenga precios.")
    else:
        etapa1, nuevas = fila_registro(cot, servicio, sub, igv, total)
        print("\nFila para el registro (columnas A a K):")
        print(etapa1)
        if nuevas:
            print("Columnas del final (Costo estimado | Subtotal calculado | Nota interna):")
            print(nuevas)
    if avisos:
        print("\nPara tu información:")
        for a in avisos:
            print("  - " + a)
    if alertas:
        print("\nREVISAR ANTES DE ENVIAR:")
        for a in alertas:
            print("  - " + a)


if __name__ == "__main__":
    main()
