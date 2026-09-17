#!/usr/bin/env python3
"""
Cuánto costó una sesión de Claude Code, leído del log real.

Responde lo que ninguna otra herramienta del repo responde: qué cuesta operar el sistema.
Lee el JSONL que Claude Code deja en ~/.claude/projects/ y calcula el costo con las tarifas
oficiales por millón de tokens, separando las cuatro cosas que se cobran distinto: input sin
cachear, escritura de caché (2x con TTL de 1 hora), lectura de caché (0.1x) y output.

El hallazgo que justifica este script (ver auditoria-ia-2026-09-17.md): el 88.9% del gasto no
es generar respuestas, es releer y reescribir contexto. El KPI que más predice el costo no es
cuánto se escribe, es cuánto contexto arrastra cada turno.

Uso:
    python3 herramientas/costo_sesion.py ~/.claude/projects/<proyecto>/<sesion>.jsonl
    python3 herramientas/costo_sesion.py              # busca la sesión más reciente
"""
import collections, glob, json, os, statistics, sys

# Tarifas Anthropic (USD por millón de tokens de input/output).
# Caché: escritura 1.25x con TTL de 5 min, 2x con TTL de 1 hora; lectura 0.1x del input.
TARIFAS = {
    "claude-opus-5":   {"in": 5.0,  "out": 25.0},
    "claude-sonnet-5": {"in": 2.0,  "out": 10.0},
    "claude-haiku-4-5": {"in": 1.0, "out": 5.0},
}
UMBRAL_FRIO = 50_000     # por debajo de esto, el turno escribió caché en vez de leerlo


def leer(ruta):
    """Extrae un registro por turno de asistente, con su uso de tokens."""
    turnos = []
    for linea in open(ruta, encoding="utf-8"):
        try:
            e = json.loads(linea)
        except ValueError:
            continue
        if e.get("type") != "assistant":
            continue
        m = e.get("message") or {}
        u = m.get("usage")
        if not isinstance(u, dict):
            continue
        cc = u.get("cache_creation") or {}
        turnos.append({
            "modelo": m.get("model") or "?",
            "in": u.get("input_tokens", 0),
            "out": u.get("output_tokens", 0),
            "cw_1h": cc.get("ephemeral_1h_input_tokens", 0),
            "cw_5m": cc.get("ephemeral_5m_input_tokens", 0),
            "cr": u.get("cache_read_input_tokens", 0),
            "think": (u.get("output_tokens_details") or {}).get("thinking_tokens", 0),
            "fecha": (e.get("timestamp") or "")[:10],
            "herramientas": [b.get("name") for b in (m.get("content") or [])
                             if isinstance(b, dict) and b.get("type") == "tool_use"],
        })
    return turnos


def costo(t):
    """Costo de un turno, desglosado. Un modelo sin tarifa conocida cuenta como 0."""
    r = TARIFAS.get(t["modelo"])
    if not r:
        return dict.fromkeys(("in", "cw", "cr", "out"), 0.0)
    return {
        "in":  t["in"] * r["in"] / 1e6,
        "cw":  (t["cw_1h"] * r["in"] * 2 + t["cw_5m"] * r["in"] * 1.25) / 1e6,
        "cr":  t["cr"] * r["in"] * 0.1 / 1e6,
        "out": t["out"] * r["out"] / 1e6,
    }


def sin_cache(t):
    """Lo que habría costado sin caché: todo el prefijo a precio pleno de input."""
    r = TARIFAS.get(t["modelo"])
    if not r:
        return 0.0
    prefijo = t["in"] + t["cw_1h"] + t["cw_5m"] + t["cr"]
    return (prefijo * r["in"] + t["out"] * r["out"]) / 1e6


def informe(turnos):
    if not turnos:
        raise SystemExit("La sesión no tiene turnos de asistente con datos de uso.")

    tot = collections.Counter()
    por_modelo = collections.defaultdict(collections.Counter)
    por_dia = collections.defaultdict(collections.Counter)
    herramientas = collections.Counter()

    for t in turnos:
        c = costo(t)
        for k, v in c.items():
            tot[k] += v
            por_modelo[t["modelo"]][k] += v
            por_dia[t["fecha"]][k] += v
        por_modelo[t["modelo"]]["turnos"] += 1
        por_dia[t["fecha"]]["turnos"] += 1
        herramientas.update(t["herramientas"])

    total = sum(tot[k] for k in ("in", "cw", "cr", "out"))
    bruto = sum(sin_cache(t) for t in turnos)

    print("=" * 66)
    print(f"COSTO DE LA SESIÓN — {len(turnos)} turnos de asistente")
    print("=" * 66)
    etiquetas = [("in", "Input sin cachear"), ("cw", "Escritura de caché"),
                 ("cr", "Lectura de caché"), ("out", "Output generado")]
    for k, etq in etiquetas:
        print(f"  {etq:<24} US${tot[k]:>8.2f}   {tot[k]/total*100:>5.1f}%")
    print(f"  {'TOTAL':<24} US${total:>8.2f}")
    mover = (tot["cr"] + tot["cw"]) / total * 100
    print(f"\n  Mover contexto (caché) = {mover:.1f}% del gasto; generar = {tot['out']/total*100:.1f}%")
    if bruto:
        print(f"  Sin caché habría costado US${bruto:.2f} — ahorro US${bruto-total:.2f} "
              f"({(bruto-total)/bruto*100:.1f}%)")

    print("\n--- por modelo ---")
    for mdl, c in sorted(por_modelo.items(), key=lambda kv: -sum(
            kv[1][k] for k in ("in", "cw", "cr", "out"))):
        s = sum(c[k] for k in ("in", "cw", "cr", "out"))
        print(f"  {mdl:<20} {int(c['turnos']):>5} turnos  US${s:>7.2f}  "
              f"({s/total*100:>4.1f}% del costo)")

    print("\n--- por día ---")
    for d in sorted(por_dia):
        c = por_dia[d]
        s = sum(c[k] for k in ("in", "cw", "cr", "out"))
        print(f"  {d}  {int(c['turnos']):>5} turnos  US${s:>7.2f}  "
              f"US${s/c['turnos']:.3f}/turno")

    ctx = [t["cr"] for t in turnos]
    outs = [t["out"] for t in turnos]
    print("\n--- lo que predice el costo ---")
    print(f"  Contexto medio releído por turno: {statistics.mean(ctx):,.0f} tokens")
    frios = [t for t in turnos if t["cr"] < UMBRAL_FRIO]
    if frios:
        cf = sum(sum(costo(t).values()) for t in frios)
        print(f"  Arranques en frío (<{UMBRAL_FRIO//1000}K de lectura): {len(frios)} turnos, "
              f"US${cf:.2f} ({cf/total*100:.1f}% del total)")
    if len(outs) > 1:
        lim = statistics.mean(outs) + 2 * statistics.pstdev(outs)
        alto = [t for t in turnos if t["out"] > lim]
        ca = sum(sum(costo(t).values()) for t in alto)
        print(f"  Outliers de output (>{lim:,.0f} tok): {len(alto)} turnos, "
              f"US${ca:.2f} ({ca/total*100:.1f}% del total)")
    think = sum(t["think"] for t in turnos)
    if sum(outs):
        print(f"  Thinking: {think:,} de {sum(outs):,} tokens de output "
              f"({think/sum(outs)*100:.0f}%)")

    if herramientas:
        print(f"\n--- herramientas ({sum(herramientas.values())} llamadas) ---")
        for n, k in herramientas.most_common(8):
            print(f"  {n}: {k}")


def mas_reciente():
    rutas = glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl"))
    if not rutas:
        raise SystemExit("No hay sesiones en ~/.claude/projects/. Pasa la ruta del JSONL.")
    return max(rutas, key=os.path.getmtime)


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else mas_reciente()
    print(f"Sesión: {ruta}\n")
    informe(leer(ruta))
