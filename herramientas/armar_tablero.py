#!/usr/bin/env python3
"""
Arma la pestaña "Tablero" del registro (Google Sheet): las decisiones sobre gastos y servicios.

Como el registro, la hoja no se versiona; se versiona lo que la reconstruye. Todo número del
tablero es una fórmula sobre las pestañas Cotizaciones y Gastos: si alguien corrige una fila, el
tablero cambia solo. Las únicas celdas para escribir son las amarillas (mes a analizar y días de
alerta) y las tablas fijas de categorías, tipos, motivos y etapas.

De dónde salen las secciones (modelos revisados el 12/10/2026):
  - Tendencia mensual y gasto por categoría con SUMIFS y gráfico: el patrón de las plantillas de
    gastos de Google Sheets (spreadsheetpoint.com, thebricks.com).
  - Rentabilidad por tipo de servicio y por cliente, ticket promedio, costo por servicio:
    KPIs de empresas de servicio técnico (fieldproxy.ai, inetsoft.com).
  - % ganadas, antigüedad de las cotizaciones y motivos de pérdida: tableros de cotización
    (Infor CPQ: win/loss, aging); etapas 0-7, 8-14, 15-30 y 31+ días de ymeadows.com,
    "When Quotes Go Cold".

Uso:
    python3 herramientas/armar_tablero.py valores            # 2D para update_formulas (A1)
    python3 herramientas/armar_tablero.py formato <sheetId>  # requests de update_spreadsheet
"""
import json, os, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

COT = "Cotizaciones"
# Rangos abiertos: el registro crece hacia abajo y los gastos también.
C_NUM, C_FECHA, C_CLIENTE, C_LOCAL, C_TIPO = (f"{COT}!${c}$3:${c}" for c in "ABCDE")
C_SUB, C_ESTADO, C_MOTIVO = (f"{COT}!${c}$3:${c}" for c in "ILM")
G_FECHA, G_CAT, G_MONTO, G_COMP, G_CLIENTE, G_ACTIVO = (f"Gastos!${c}$2:${c}" for c in "ABCDEG")

CATEGORIAS = ["Repuestos y materiales", "Mano de obra", "Pasajes y viáticos",
              "Transporte y combustible", "Consumibles", "SCTR y EPP", "Herramientas", "Otros"]
MOTIVOS = ["Precio alto", "Plazo", "Otro proveedor", "Sin presupuesto", "No respondió", "Otro"]
ETAPAS = [(0, "Reciente"), (8, "Llamar"), (15, "Fría"), (31, "Dormida")]
FILAS_SEGUIMIENTO = 20
FILAS_CLIENTES = 25
FILAS_ACTIVOS = 15
ANCHO = 11                       # A:K
MES, FIN, DIAS = "$B$4", "$D$4", "$F$4"
INICIO_ANIO, FIN_ANIO = f"DATE(YEAR({MES}),1,1)", f"DATE(YEAR({MES}),12,31)"


def tipos_de_servicio():
    """Los tipos del registro salen de servicios.json, la misma fuente que la hoja Cotizaciones."""
    tipos = json.load(open(os.path.join(RAIZ, "servicios.json"), encoding="utf-8"))["tipos"]
    vistos = []
    for t in tipos.values():
        if t["categoria_registro"] not in vistos:
            vistos.append(t["categoria_registro"])
    return vistos


def en_mes(rango_fecha, desde=MES, hasta=FIN):
    return f'{rango_fecha},">="&{desde},{rango_fecha},"<="&{hasta}'


def armar():
    filas, marcas = [], {"titulos": [], "encabezados": [], "dinero": [], "porcentaje": [],
                         "entero": [], "dias": [], "mes": [], "fecha": [], "nota": []}

    def fila(*celdas):
        filas.append(list(celdas) + [None] * (ANCHO - len(celdas)))
        return len(filas)            # número de fila (1-based)

    def titulo(texto):
        fila(None)
        n = fila(texto)
        marcas["titulos"].append(n)
        return n

    def encabezado(*textos):
        n = fila(*textos)
        marcas["encabezados"].append((n, len(textos)))
        return n

    fila("Tablero de decisiones")
    fila("Se actualiza solo con lo que entra a Cotizaciones y Gastos. "
         "Las celdas amarillas se pueden cambiar.")
    fila(None)
    fila("Mes a analizar", "=DATE(YEAR(TODAY()),MONTH(TODAY()),1)", "Fin del mes",
         f"=EOMONTH({MES},0)", "Alertar sin respuesta después de (días)", 7)
    marcas["mes"].append(("B", 4))
    marcas["fecha"].append(("D", 4))

    # 1. El mes en números ------------------------------------------------------------
    titulo("1. El mes en números")
    encabezado("Indicador", "Valor", "Cómo se lee")
    r = {}

    def kpi(clave, etiqueta, formula, lectura, tipo):
        n = fila(etiqueta, formula, lectura)
        r[clave] = n
        marcas[tipo].append(("B", n))

    kpi("emitidas", "Cotizaciones emitidas", f"=COUNTIFS({en_mes(C_FECHA)})",
        "Cuántas se enviaron en el mes.", "entero")
    kpi("cotizado", "Cotizado (S/, sin IGV)", f"=SUMIFS({C_SUB},{en_mes(C_FECHA)})",
        "Lo que se ofreció a los clientes.", "dinero")
    kpi("ganadas", "Ganadas", f'=COUNTIFS({en_mes(C_FECHA)},{C_ESTADO},"Ganado")',
        "Cotizaciones del mes marcadas Ganado en la hoja Cotizaciones.", "entero")
    kpi("perdidas", "Perdidas", f'=COUNTIFS({en_mes(C_FECHA)},{C_ESTADO},"Perdido")',
        "Marcadas Perdido. El motivo se ve en la sección 8.", "entero")
    kpi("pct", "% ganadas (de las que ya respondieron)",
        f'=IF(B{r["ganadas"]}+B{r["perdidas"]}=0,"",B{r["ganadas"]}/(B{r["ganadas"]}+B{r["perdidas"]}))',
        "Si baja, revisar precios y el seguimiento.", "porcentaje")
    kpi("ganado", "Ganado (S/, sin IGV)", f'=SUMIFS({C_SUB},{en_mes(C_FECHA)},{C_ESTADO},"Ganado")',
        "Trabajo aceptado por el cliente.", "dinero")
    kpi("gastado", "Gastado (S/, con IGV)", f"=SUMIFS({G_MONTO},{en_mes(G_FECHA)})",
        "Todo lo registrado en Gastos con fecha del mes.", "dinero")
    kpi("resultado", "Resultado aproximado (ganado − gastado)", f'=B{r["ganado"]}-B{r["gastado"]}',
        "Ganado va sin IGV y gastado con IGV: con facturas, el resultado real es algo mayor.",
        "dinero")
    kpi("ticket", "Ticket promedio cotizado (S/)",
        f'=IF(B{r["emitidas"]}=0,"",B{r["cotizado"]}/B{r["emitidas"]})',
        "Tamaño medio de cada cotización del mes.", "dinero")
    kpi("sincomp", "Gasto sin comprobante (S/)",
        f'=SUMIFS({G_MONTO},{en_mes(G_FECHA)},{G_COMP},"Sin comprobante")',
        "Gasto que no se puede sustentar con boleta o factura.", "dinero")
    kpi("pctsincomp", "% del gasto sin comprobante",
        f'=IF(B{r["gastado"]}=0,"",B{r["sincomp"]}/B{r["gastado"]})',
        "Mientras más bajo, mejor.", "porcentaje")
    kpi("alerta", "Sin respuesta pasado el plazo de alerta (todas las fechas)",
        f'=COUNTIFS({C_ESTADO},"Cotizado",{C_FECHA},"<="&TODAY()-{DIAS})'
        f'+COUNTIFS({C_ESTADO},"Enviado",{C_FECHA},"<="&TODAY()-{DIAS})',
        "Llamar a esos clientes: lista en la sección 2.", "entero")

    # 2. Seguimiento ------------------------------------------------------------------
    titulo("2. Seguimiento: cotizaciones sin respuesta (las más antiguas primero)")
    cab = encabezado("N°", "Fecha", "Cliente", "Local", "Subtotal (S/)", "Días", "Etapa")
    etapas_ini = cab + 1
    rango_etapas = f"$J${etapas_ini}:$K${etapas_ini + len(ETAPAS) - 1}"
    primera = cab + 1
    ultima = primera + FILAS_SEGUIMIENTO - 1
    b, f_ = f"B{primera}:B{ultima}", f"F{primera}:F{ultima}"
    fila(f'=IFERROR(ARRAY_CONSTRAIN(SORT(FILTER({{{C_NUM},{C_FECHA},{C_CLIENTE},'
         f'{C_LOCAL},{C_SUB}}},({C_ESTADO}="Cotizado")+({C_ESTADO}="Enviado")),2,TRUE),'
         f'{FILAS_SEGUIMIENTO},5),"Ninguna pendiente")', None, None, None, None,
         f'=ARRAYFORMULA(IF(ISNUMBER({b}),TODAY()-{b},""))',
         f'=ARRAYFORMULA(IF({f_}="","",VLOOKUP({f_},{rango_etapas},2,TRUE)))')
    for i in range(1, FILAS_SEGUIMIENTO):
        fila(None)
    for n in range(primera, ultima + 1):
        marcas["fecha"].append(("B", n))
        marcas["dinero"].append(("E", n))
        marcas["dias"].append(("F", n))
    # Tabla de etapas, al lado de la lista (J:K).
    filas[cab - 1][9:11] = ["Desde (días)", "Etapa"]
    marcas["encabezados"].append((cab, ("J", "K")))
    for i, (desde, etapa) in enumerate(ETAPAS):
        filas[etapas_ini - 1 + i][9:11] = [desde, etapa]
    marcas["nota"].append((f"J{cab}", "Fuente: etapas de antigüedad de una cotización según "
                           "ymeadows.com, \"When Quotes Go Cold\" (consultado el 12/10/2026). "
                           "Se pueden cambiar."))
    seguimiento = (primera, primera + FILAS_SEGUIMIENTO - 1)

    # 3. Últimos 6 meses --------------------------------------------------------------
    titulo("3. Últimos 6 meses")
    cab_meses = encabezado("Mes", "Cotizado (S/)", "Ganado (S/)", "Gastado (S/, con IGV)",
                           "Resultado (S/)")
    primera = cab_meses + 1
    for i in range(6):
        n = primera + i
        mes = f"=EDATE(A{n + 1},-1)" if i < 5 else f"={MES}"
        fila(mes,
             f'=SUMIFS({C_SUB},{en_mes(C_FECHA, f"$A{n}", f"EOMONTH($A{n},0)")})',
             f'=SUMIFS({C_SUB},{en_mes(C_FECHA, f"$A{n}", f"EOMONTH($A{n},0)")},{C_ESTADO},"Ganado")',
             f'=SUMIFS({G_MONTO},{en_mes(G_FECHA, f"$A{n}", f"EOMONTH($A{n},0)")})',
             f"=C{n}-D{n}")
        marcas["mes"].append(("A", n))
        for c in "BCDE":
            marcas["dinero"].append((c, n))
    meses = (cab_meses, primera + 5)

    # 4. Gastos por categoría ---------------------------------------------------------
    titulo("4. Gastos por categoría")
    cab_cat = encabezado("Categoría", "Mes elegido (S/)", "Año del mes elegido (S/)", "% del año")
    primera = cab_cat + 1
    total = primera + len(CATEGORIAS)
    for i, cat in enumerate(CATEGORIAS):
        n = primera + i
        fila(cat,
             f"=SUMIFS({G_MONTO},{G_CAT},$A{n},{en_mes(G_FECHA)})",
             f"=SUMIFS({G_MONTO},{G_CAT},$A{n},{en_mes(G_FECHA, INICIO_ANIO, FIN_ANIO)})",
             f'=IF($C${total}=0,"",C{n}/$C${total})')
        marcas["dinero"] += [("B", n), ("C", n)]
        marcas["porcentaje"].append(("D", n))
    fila("Total", f"=SUM(B{primera}:B{total - 1})", f"=SUM(C{primera}:C{total - 1})")
    marcas["dinero"] += [("B", total), ("C", total)]
    marcas["encabezados"].append((total, 3))
    categorias = (cab_cat, total - 1)

    # 5. Por tipo de servicio ---------------------------------------------------------
    titulo("5. Por tipo de servicio (todas las fechas)")
    cab_tipo = encabezado("Tipo", "Cotizaciones", "Ganadas", "Perdidas", "% ganadas",
                          "Cotizado (S/)", "Ganado (S/)", "Ticket promedio (S/)")
    primera = cab_tipo + 1
    tipos = tipos_de_servicio()
    for i, t in enumerate(tipos):
        n = primera + i
        fila(t,
             f"=COUNTIFS({C_TIPO},$A{n})",
             f'=COUNTIFS({C_TIPO},$A{n},{C_ESTADO},"Ganado")',
             f'=COUNTIFS({C_TIPO},$A{n},{C_ESTADO},"Perdido")',
             f'=IF(C{n}+D{n}=0,"",C{n}/(C{n}+D{n}))',
             f"=SUMIFS({C_SUB},{C_TIPO},$A{n})",
             f'=SUMIFS({C_SUB},{C_TIPO},$A{n},{C_ESTADO},"Ganado")',
             f'=IF(B{n}=0,"",F{n}/B{n})')
    total = primera + len(tipos)
    fila("Total", *(f"=SUM({c}{primera}:{c}{total - 1})" for c in "BCD"),
         f'=IF(C{total}+D{total}=0,"",C{total}/(C{total}+D{total}))',
         f"=SUM(F{primera}:F{total - 1})", f"=SUM(G{primera}:G{total - 1})",
         f'=IF(B{total}=0,"",F{total}/B{total})')
    for n in range(primera, total + 1):
        marcas["entero"] += [("B", n), ("C", n), ("D", n)]
        marcas["porcentaje"].append(("E", n))
        marcas["dinero"] += [("F", n), ("G", n), ("H", n)]
    marcas["encabezados"].append((total, 8))
    por_tipo = (cab_tipo, total - 1)

    # 6. Clientes ---------------------------------------------------------------------
    titulo("6. Clientes: cotizado, ganado y gastado (todas las fechas)")
    cab_cli = encabezado("Cliente", "Cotizaciones", "Cotizado (S/)", "Ganado (S/)",
                         "Gastado (S/, con IGV)", "Resultado (S/)")
    primera = cab_cli + 1
    ambos = f"{{{C_CLIENTE};{G_CLIENTE}}}"
    ultima = primera + FILAS_CLIENTES - 1
    a = f"A{primera}:A{ultima}"
    fila(f'=IFERROR(ARRAY_CONSTRAIN(SORT(UNIQUE(FILTER({ambos},{ambos}<>""))),{FILAS_CLIENTES},1),"")',
         f'=ARRAYFORMULA(IF({a}="","",COUNTIFS({C_CLIENTE},{a})))',
         # SUMIFS no se expande dentro de ARRAYFORMULA (devuelve un solo número); SUMIF sí.
         # Dos condiciones van como una clave unida: cliente & estado.
         f'=ARRAYFORMULA(IF({a}="","",SUMIF({C_CLIENTE},{a},{C_SUB})))',
         f'=ARRAYFORMULA(IF({a}="","",SUMIF({C_CLIENTE}&"|"&{C_ESTADO},{a}&"|Ganado",{C_SUB})))',
         f'=ARRAYFORMULA(IF({a}="","",SUMIF({G_CLIENTE},{a},{G_MONTO})))',
         f'=ARRAYFORMULA(IF({a}="","",D{primera}:D{ultima}-E{primera}:E{ultima}))')
    for i in range(1, FILAS_CLIENTES):
        fila(None)
    for n in range(primera, ultima + 1):
        marcas["entero"].append(("B", n))
        marcas["dinero"] += [("C", n), ("D", n), ("E", n), ("F", n)]

    # 7. Activos ----------------------------------------------------------------------
    titulo("7. Gastos por activo (año del mes elegido)")
    cab_act = encabezado("Activo", "Gastado (S/, con IGV)", "N° de gastos")
    primera = cab_act + 1
    ultima = primera + FILAS_ACTIVOS - 1
    a, anio = f"A{primera}:A{ultima}", en_mes(G_FECHA, INICIO_ANIO, FIN_ANIO)
    fila(f'=IFERROR(ARRAY_CONSTRAIN(SORT(UNIQUE(FILTER({G_ACTIVO},{G_ACTIVO}<>""))),{FILAS_ACTIVOS},1),"")',
         f'=ARRAYFORMULA(IF({a}="","",SUMIF({G_ACTIVO}&"|"&YEAR({G_FECHA}),{a}&"|"&YEAR({MES}),{G_MONTO})))',
         f'=ARRAYFORMULA(IF({a}="","",COUNTIFS({G_ACTIVO},{a},{anio})))')
    for i in range(1, FILAS_ACTIVOS):
        fila(None)
    for n in range(primera, ultima + 1):
        marcas["dinero"].append(("B", n))
        marcas["entero"].append(("C", n))

    # 8. Motivos de pérdida -----------------------------------------------------------
    titulo("8. Por qué se pierde (todas las fechas)")
    cab_mot = encabezado("Motivo", "Cotizaciones", "Monto (S/)")
    primera = cab_mot + 1
    for i, m in enumerate(MOTIVOS):
        n = primera + i
        fila(m, f"=COUNTIFS({C_MOTIVO},$A{n})", f"=SUMIFS({C_SUB},{C_MOTIVO},$A{n})")
        marcas["entero"].append(("B", n))
        marcas["dinero"].append(("C", n))

    graficos = {"meses": meses, "categorias": categorias, "por_tipo": por_tipo,
                "seguimiento": seguimiento}
    return filas, marcas, graficos


# ------------------------------------------------------------------ formato

VERDE = {"red": 0.11764706, "green": 0.47843137, "blue": 0.30980393}   # el del registro
AMARILLO = {"red": 1, "green": 0.96078, "blue": 0.61569}
GRIS = {"red": 0.93725, "green": 0.93725, "blue": 0.93725}
BLANCO = {"red": 1, "green": 1, "blue": 1}


def col(letra):
    return ord(letra) - ord("A")


def celda(sheet, letra, fila, hasta=None):
    c = col(letra)
    return {"sheetId": sheet, "startRowIndex": fila - 1, "endRowIndex": fila,
            "startColumnIndex": c, "endColumnIndex": (col(hasta) if hasta else c) + 1}


def repetir(rango, formato, campos):
    return {"repeatCell": {"range": rango, "cell": {"userEnteredFormat": formato}, "fields": campos}}


def tramos(celdas):
    """[(B,5),(B,6),(B,7),(C,5)] -> [(B,5,7),(C,5,5)]: un formato por tramo, no por celda."""
    salida = []
    for letra, n in sorted(set(celdas)):
        if salida and salida[-1][0] == letra and salida[-1][2] == n - 1:
            salida[-1][2] = n
        else:
            salida.append([letra, n, n])
    return [tuple(t) for t in salida]


def formato(sheet):
    filas, marcas, g = armar()
    total = len(filas)
    req = [repetir({"sheetId": sheet, "startRowIndex": 0, "endRowIndex": total,
                    "startColumnIndex": 0, "endColumnIndex": ANCHO},
                   {"textFormat": {"fontFamily": "Arial", "fontSize": 10}, "verticalAlignment": "MIDDLE"},
                   "userEnteredFormat.textFormat.fontFamily,userEnteredFormat.textFormat.fontSize,"
                   "userEnteredFormat.verticalAlignment"),
           repetir(celda(sheet, "A", 1), {"textFormat": {"bold": True, "fontSize": 16,
                   "foregroundColorStyle": {"rgbColor": VERDE}}},
                   "userEnteredFormat.textFormat.bold,userEnteredFormat.textFormat.fontSize,"
                   "userEnteredFormat.textFormat.foregroundColorStyle"),
           repetir(celda(sheet, "A", 2), {"textFormat": {"italic": True}},
                   "userEnteredFormat.textFormat.italic"),
           repetir(celda(sheet, "A", 4, "E"), {"textFormat": {"bold": True}},
                   "userEnteredFormat.textFormat.bold")]
    for letra in "BF":
        req.append(repetir(celda(sheet, letra, 4), {"backgroundColorStyle": {"rgbColor": AMARILLO},
                           "horizontalAlignment": "CENTER", "textFormat": {"bold": True}},
                           "userEnteredFormat.backgroundColorStyle,"
                           "userEnteredFormat.horizontalAlignment,userEnteredFormat.textFormat.bold"))
    for n in marcas["titulos"]:
        req.append(repetir(celda(sheet, "A", n), {"textFormat": {"bold": True, "fontSize": 12,
                           "foregroundColorStyle": {"rgbColor": VERDE}}},
                           "userEnteredFormat.textFormat.bold,userEnteredFormat.textFormat.fontSize,"
                           "userEnteredFormat.textFormat.foregroundColorStyle"))
    for n, ancho in marcas["encabezados"]:
        desde, hasta = ancho if isinstance(ancho, tuple) else ("A", chr(ord("A") + ancho - 1))
        es_total = filas[n - 1][0] == "Total"
        fmt = ({"backgroundColorStyle": {"rgbColor": GRIS}, "textFormat": {"bold": True}} if es_total else
               {"backgroundColorStyle": {"rgbColor": VERDE}, "horizontalAlignment": "CENTER",
                "wrapStrategy": "WRAP", "textFormat": {"bold": True,
                "foregroundColorStyle": {"rgbColor": BLANCO}}})
        campos = ("userEnteredFormat.backgroundColorStyle,userEnteredFormat.textFormat.bold" if es_total else
                  "userEnteredFormat.backgroundColorStyle,userEnteredFormat.horizontalAlignment,"
                  "userEnteredFormat.wrapStrategy,userEnteredFormat.textFormat.bold,"
                  "userEnteredFormat.textFormat.foregroundColorStyle")
        req.append(repetir(celda(sheet, desde, n, hasta), fmt, campos))
    patrones = {"dinero": '"S/ "#,##0.00;-"S/ "#,##0.00;"-"', "porcentaje": '0.0%;-0.0%;"-"',
                "entero": '0;-0;"-"', "dias": "0", "mes": "mmmm yyyy", "fecha": "dd/mm/yyyy"}
    tipos = {"dinero": "NUMBER", "porcentaje": "PERCENT", "entero": "NUMBER", "dias": "NUMBER", "mes": "DATE",
             "fecha": "DATE"}
    for clave, patron in patrones.items():
        for letra, desde, hasta in tramos(marcas[clave]):
            rng = celda(sheet, letra, desde)
            rng["endRowIndex"] = hasta
            req.append(repetir(rng, {"numberFormat": {"type": tipos[clave], "pattern": patron}},
                               "userEnteredFormat.numberFormat"))
    for ref, texto in marcas["nota"]:
        letra, n = ref[0], int(ref[1:])
        req.append({"updateCells": {"rows": [{"values": [{"note": texto}]}], "fields": "note",
                                    "start": {"sheetId": sheet, "rowIndex": n - 1,
                                              "columnIndex": col(letra)}}})
    anchos = {"A": 330, "B": 120, "C": 150, "D": 150, "E": 150, "F": 110, "G": 110, "H": 130,
              "I": 30, "J": 100, "K": 100}
    for letra, px in anchos.items():
        req.append({"updateDimensionProperties": {"range": {"sheetId": sheet, "dimension": "COLUMNS",
                    "startIndex": col(letra), "endIndex": col(letra) + 1},
                    "properties": {"pixelSize": px}, "fields": "pixelSize"}})
    req.append({"updateSheetProperties": {"properties": {"sheetId": sheet, "gridProperties":
                {"frozenRowCount": 4}}, "fields": "gridProperties.frozenRowCount"}})
    req += graficos_(sheet, g)
    return req


def rango(sheet, letra, desde, hasta):
    return {"sheetId": sheet, "startRowIndex": desde - 1, "endRowIndex": hasta,
            "startColumnIndex": col(letra), "endColumnIndex": col(letra) + 1}


def grafico(sheet, titulo_, tipo, dominio, series, ancla, pie=False):
    if pie:
        spec = {"title": titulo_, "pieChart": {"legendPosition": "RIGHT_LEGEND",
                "domain": {"sourceRange": {"sources": [dominio]}},
                "series": {"sourceRange": {"sources": [series[0]]}}}}
    else:
        spec = {"title": titulo_, "basicChart": {"chartType": tipo, "legendPosition": "BOTTOM_LEGEND",
                "headerCount": 1, "domains": [{"domain": {"sourceRange": {"sources": [dominio]}}}],
                "series": [{"series": {"sourceRange": {"sources": [s]}},
                            "targetAxis": "BOTTOM_AXIS" if tipo == "BAR" else "LEFT_AXIS"}
                           for s in series]}}
    return {"addChart": {"chart": {"spec": spec, "position": {"overlayPosition": {
            "anchorCell": {"sheetId": sheet, "rowIndex": ancla - 1, "columnIndex": col("J")},
            "widthPixels": 560, "heightPixels": 320}}}}}


def graficos_(sheet, g):
    m0, m1 = g["meses"]
    c0, c1 = g["categorias"]
    t0, t1 = g["por_tipo"]
    # Uno debajo del otro en J, desde la sección 3: cada gráfico ocupa unas 16 filas.
    return [
        grafico(sheet, "Cotizado, ganado y gastado por mes", "COLUMN", rango(sheet, "A", m0, m1),
                [rango(sheet, c, m0, m1) for c in "BCD"], m0),
        grafico(sheet, "Gastos por categoría (año)", "BAR", rango(sheet, "A", c0, c1),
                [rango(sheet, "C", c0, c1)], m0 + 17),
        grafico(sheet, "Cotizado por tipo de servicio", None, rango(sheet, "A", t0 + 1, t1),
                [rango(sheet, "F", t0 + 1, t1)], m0 + 34, pie=True),
    ]


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "formato":
        print(json.dumps(formato(int(sys.argv[2])), ensure_ascii=False))
    else:
        filas, _, _ = armar()
        print(json.dumps(filas, ensure_ascii=False))
