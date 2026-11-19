#!/usr/bin/env python3
import argparse
import json
import sys

FORMACIONES = {
    "4-3-3": {
        "DEL": 3,
        "MED": 3,
        "DEF": 4,
        "ARQ": 1,
    },
    "4-4-2": {
        "DEL": 2,
        "MED": 4,
        "DEF": 4,
        "ARQ": 1,
    },
    "3-5-2": {
        "DEL": 2,
        "MED": 5,
        "DEF": 3,
        "ARQ": 1,
    },
    "4-2-3-1": {
        "DEL": 4,
        "MED": 2,
        "DEF": 4,
        "ARQ": 1,
    },
    "5-3-2": {
        "DEL": 2,
        "MED": 3,
        "DEF": 5,
        "ARQ": 1,
    },
}

ROLES_POR_FORMACION = {
    "4-3-3": {
        "DEL": ["Extremo izquierdo (EI)", "Delantero centro (DC)", "Extremo derecho (ED)"],
        "MED": ["Interior izquierdo (LI)", "Volante central (MCD)", "Interior derecho (LD)"],
        "DEF": ["Lateral izquierdo (LI)", "Central izquierdo (DFC)", "Central derecho (DFC)", "Lateral derecho (LD)"],
        "ARQ": ["Arquero (ARQ)"],
    },
    "4-4-2": {
        "DEL": ["Delantero izquierdo (DI)", "Delantero derecho (DD)"],
        "MED": ["Volante izquierdo (MI)", "Mediocentro izquierdo (MC)", "Mediocentro derecho (MC)", "Volante derecho (MD)"],
        "DEF": ["Lateral izquierdo (LI)", "Central izquierdo (DFC)", "Central derecho (DFC)", "Lateral derecho (LD)"],
        "ARQ": ["Arquero (ARQ)"],
    },
    "3-5-2": {
        "DEL": ["Delantero izquierdo (DI)", "Delantero derecho (DD)"],
        "MED": ["Carrilero izquierdo (CI)", "Interior izquierdo (LI)", "Volante central (MCD)", "Interior derecho (LD)", "Carrilero derecho (CD)"],
        "DEF": ["Central izquierdo (DFC)", "Líbero / Central (DFC)", "Central derecho (DFC)"],
        "ARQ": ["Arquero (ARQ)"],
    },
    "4-2-3-1": {
        "DEL": [
            "Mediapunta izquierdo (MI)",
            "Enganche / Mediapunta central (MCO)",
            "Mediapunta derecho (MD)",
            "Delantero centro / 9 (DC)",
        ],
        "MED": ["Doble pivote izquierdo (MCD)", "Doble pivote derecho (MCD)"],
        "DEF": ["Lateral izquierdo (LI)", "Central izquierdo (DFC)", "Central derecho (DFC)", "Lateral derecho (LD)"],
        "ARQ": ["Arquero (ARQ)"],
    },
    "5-3-2": {
        "DEL": ["Delantero izquierdo (DI)", "Delantero derecho (DD)"],
        "MED": ["Interior izquierdo (LI)", "Volante central (MCD)", "Interior derecho (LD)"],
        "DEF": [
            "Carrilero izquierdo (CI)",
            "Central izquierdo (DFC)",
            "Central medio (DFC)",
            "Central derecho (DFC)",
            "Carrilero derecho (CD)",
        ],
        "ARQ": ["Arquero (ARQ)"],
    },
}

# Posiciones horizontales (0.0 = banda izquierda, 1.0 = banda derecha) y profundidad
# extra para que se note el dibujo táctico en cada esquema.
MAPA_VISUAL = {
    "4-3-3": {
        "DEL": [(0.16, 1), (0.50, 0), (0.84, 1)],
        "MED": [(0.22, 0), (0.50, 1), (0.78, 0)],
        "DEF": [(0.14, 1), (0.38, 0), (0.62, 0), (0.86, 1)],
        "ARQ": [(0.50, 0)],
    },
    "4-4-2": {
        "DEL": [(0.34, 0), (0.66, 0)],
        "MED": [(0.14, 0), (0.38, 1), (0.62, 1), (0.86, 0)],
        "DEF": [(0.14, 1), (0.38, 0), (0.62, 0), (0.86, 1)],
        "ARQ": [(0.50, 0)],
    },
    "3-5-2": {
        "DEL": [(0.35, 0), (0.65, 0)],
        "MED": [(0.12, 0), (0.32, 1), (0.50, 2), (0.68, 1), (0.88, 0)],
        "DEF": [(0.24, 0), (0.50, 1), (0.76, 0)],
        "ARQ": [(0.50, 0)],
    },
    "4-2-3-1": {
        # Los primeros 3 en DEL son los mediapuntas y el 4to es el 9 más adelantado.
        "DEL": [(0.20, 1), (0.50, 1), (0.80, 1), (0.50, 0)],
        "MED": [(0.36, 0), (0.64, 0)],
        "DEF": [(0.14, 1), (0.38, 0), (0.62, 0), (0.86, 1)],
        "ARQ": [(0.50, 0)],
    },
    "5-3-2": {
        "DEL": [(0.35, 0), (0.65, 0)],
        "MED": [(0.24, 0), (0.50, 1), (0.76, 0)],
        "DEF": [(0.12, 0), (0.32, 1), (0.50, 2), (0.68, 1), (0.88, 0)],
        "ARQ": [(0.50, 0)],
    },
}


def repartir_linea(jugadores, cantidad):
    """Toma `cantidad` jugadores y devuelve una lista."""
    tomados = jugadores[:cantidad]
    del jugadores[:cantidad]
    while len(tomados) < cantidad:
        tomados.append("Vacante")
    return tomados


def obtener_roles_linea(formacion, codigo_linea, cantidad):
    """Devuelve nombres descriptivos para cada puesto de la línea."""
    roles = ROLES_POR_FORMACION.get(formacion, {}).get(codigo_linea)
    if roles and len(roles) == cantidad:
        return roles
    return [f"Puesto {i + 1} ({codigo_linea})" for i in range(cantidad)]


def guardar_json(equipo, formacion, jugadores):
    """Guarda la alineación completa en un archivo JSON."""
    nombre_sugerido = f"{equipo.strip().lower().replace(' ', '_')}_{formacion}.json"
    ruta = input(f"Nombre del archivo [{nombre_sugerido}]: ").strip()
    if not ruta:
        ruta = nombre_sugerido
    if not ruta.endswith(".json"):
        ruta += ".json"

    datos = {
        "equipo": equipo,
        "formacion": formacion,
        "jugadores": jugadores,
    }
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print(f"Alineación guardada en '{ruta}'.")


def modo_interactivo(equipo_inicial=None, formacion_inicial=None):
    """Pide equipo, formación, titulares, suplentes y opción de guardar en JSON."""
    print("\n=== MODO INTERACTIVO: ARMADOR DE ALINEACIÓN ===\n")

    if equipo_inicial:
        equipo = equipo_inicial
    else:
        entrada_equipo = input("Nombre del equipo [Mi Equipo]: ").strip()
        equipo = entrada_equipo if entrada_equipo else "Mi Equipo"

    opciones_formacion = list(FORMACIONES.keys())
    if formacion_inicial and formacion_inicial in FORMACIONES:
        formacion = formacion_inicial
    else:
        while True:
            print(f"Formaciones disponibles: {', '.join(opciones_formacion)}")
            entrada_form = input("Elegí una formación [4-3-3]: ").strip()
            if not entrada_form:
                formacion = "4-3-3"
                break
            if entrada_form in FORMACIONES:
                formacion = entrada_form
                break
            print("Formación no válida, probá de nuevo.")

    esquema = FORMACIONES[formacion]
    jugadores = []

    print(f"\nCargando 11 para {equipo} ({formacion}). Enter vacío = 'Vacante':\n")
    for codigo_linea in ("DEL", "MED", "DEF", "ARQ"):
        cantidad = esquema[codigo_linea]
        roles = obtener_roles_linea(formacion, codigo_linea, cantidad)
        print(f"--- Línea {codigo_linea} ---")
        for rol in roles:
            nombre = input(f"  {rol}: ").strip()
            jugadores.append(nombre if nombre else "Vacante")
        print()

    cargar_suplentes = input("¿Querés cargar suplentes? (s/N): ").strip().lower()
    if cargar_suplentes in ("s", "si", "sí", "y"):
        print("Escribí cada suplente y apretá Enter (Enter vacío para terminar):")
        idx = 1
        while True:
            suplente = input(f"  Suplente {idx}: ").strip()
            if not suplente:
                break
            jugadores.append(suplente)
            idx += 1

    return equipo, formacion, jugadores


def renderizar_sector(jugadores_linea, coords_linea, ancho):
    """Dibuja una línea de jugadores escalonada según posición y profundidad."""
    # Agrupamos por nivel de profundidad (0 = más adelante hacia arco rival, mayor = más atrás).
    niveles = {}
    for jugador, (x_norm, prof) in zip(jugadores_linea, coords_linea):
        niveles.setdefault(prof, []).append((x_norm, str(jugador)))

    lineas_texto = []
    for prof in sorted(niveles.keys()):
        canvas = [" "] * ancho
        items = sorted(niveles[prof], key=lambda item: item[0])
        ultimo_fin = 1
        for x_norm, nombre in items:
            etiqueta = f"[{nombre}]"
            centro = int(round(x_norm * (ancho - 1)))
            inicio = centro - len(etiqueta) // 2
            inicio = max(ultimo_fin, min(inicio, ancho - len(etiqueta) - 1))
            for i, ch in enumerate(etiqueta):
                if 0 <= inicio + i < ancho:
                    canvas[inicio + i] = ch
            ultimo_fin = inicio + len(etiqueta) + 2
        lineas_texto.append("".join(canvas).rstrip())

    return "\n".join(lineas_texto)


def dibujar_cancha(equipo, formacion, jugadores):
    if formacion not in FORMACIONES:
        print(f"Formación '{formacion}' no soportada. Usá: {', '.join(FORMACIONES)}")
        sys.exit(1)

    pool = list(jugadores)
    esquema = FORMACIONES[formacion]

    delanteros = repartir_linea(pool, esquema["DEL"])
    mediocampo = repartir_linea(pool, esquema["MED"])
    defensores = repartir_linea(pool, esquema["DEF"])
    arquero = repartir_linea(pool, esquema["ARQ"])

    mapa = MAPA_VISUAL[formacion]
    ancho = 76

    print("\n" + "=" * ancho)
    print(f"  EQUIPO: {equipo.upper()}   |   FORMACIÓN: {formacion}".center(ancho))
    print("=" * ancho)
    print("  [ARCO RIVAL] ".center(ancho, "-"))
    print()
    print(renderizar_sector(delanteros, mapa["DEL"], ancho))
    print()
    print(renderizar_sector(mediocampo, mapa["MED"], ancho))
    print()
    print(renderizar_sector(defensores, mapa["DEF"], ancho))
    print()
    print(renderizar_sector(arquero, mapa["ARQ"], ancho))
    print()
    print("  [ARCO PROPIO] ".center(ancho, "-"))
    print("=" * ancho)

    if pool:
        print("  SUPLENTES / BANCO: " + ", ".join(pool))
        print("=" * ancho)


def main():
    parser = argparse.ArgumentParser(
        description="Generador de alineaciones de fútbol para terminal."
    )
    parser.add_argument(
        "-i",
        "--interactivo",
        action="store_true",
        help="Activa el modo interactivo paso a paso",
    )
    parser.add_argument(
        "-e", "--equipo", help="Nombre del equipo"
    )
    parser.add_argument(
        "-f",
        "--formacion",
        choices=list(FORMACIONES.keys()),
        help=f"Formación táctica ({', '.join(FORMACIONES.keys())})",
    )
    parser.add_argument(
        "-j",
        "--jugadores",
        nargs="+",
        help="Lista de jugadores separados por espacio",
    )
    parser.add_argument(
        "--archivo",
        help="Ruta a un archivo JSON con {'equipo': ..., 'formacion': ..., 'jugadores': [...]}",
    )

    args = parser.parse_args()
    es_interactivo = False

    if args.archivo:
        with open(args.archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)
        equipo = datos.get("equipo", args.equipo or "Mi Equipo")
        formacion = datos.get("formacion", args.formacion or "4-3-3")
        jugadores = datos.get("jugadores", [])
    elif args.interactivo or not args.jugadores:
        es_interactivo = True
        equipo, formacion, jugadores = modo_interactivo(
            equipo_inicial=args.equipo,
            formacion_inicial=args.formacion,
        )
    else:
        equipo = args.equipo or "Mi Equipo"
        formacion = args.formacion or "4-3-3"
        jugadores = args.jugadores

    dibujar_cancha(equipo, formacion, jugadores)

    if es_interactivo:
        guardar = input("\n¿Querés guardar esta alineación en JSON? (s/N): ").strip().lower()
        if guardar in ("s", "si", "sí", "y"):
            guardar_json(equipo, formacion, jugadores)


if __name__ == "__main__":
    main()
