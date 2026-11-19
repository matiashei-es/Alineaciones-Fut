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


def modo_interactivo(equipo_inicial=None, formacion_inicial=None):
    """Pide equipo, formación y jugadores diferenciando cada posición."""
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

    return equipo, formacion, jugadores


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

    ancho = 64
    print("\n" + "=" * ancho)
    print(f"  EQUIPO: {equipo.upper()}   |   FORMACIÓN: {formacion}".center(ancho))
    print("=" * ancho)
    print("  [ARCO RIVAL] ".center(ancho, "-"))
    print()
    print("  DELANTEROS:  " + "   -   ".join(delanteros))
    print()
    print("  MEDIOCAMPO:  " + "   -   ".join(mediocampo))
    print()
    print("  DEFENSORES:  " + "   -   ".join(defensores))
    print()
    print("  ARQUERO:     " + "   -   ".join(arquero))
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
        help="Formación táctica (4-3-3, 4-4-2, 3-5-2)",
    )
    parser.add_argument(
        "-j",
        "--jugadores",
        nargs="+",
        help="Lista de jugadores separados por espacio (delanteros a arquero)",
    )
    parser.add_argument(
        "--archivo",
        help="Ruta a un archivo JSON con {'equipo': ..., 'formacion': ..., 'jugadores': [...]}",
    )

    args = parser.parse_args()

    if args.archivo:
        with open(args.archivo, "r", encoding="utf-8") as f:
            datos = json.load(f)
        equipo = datos.get("equipo", args.equipo or "Mi Equipo")
        formacion = datos.get("formacion", args.formacion or "4-3-3")
        jugadores = datos.get("jugadores", [])
    elif args.interactivo or not args.jugadores:
        equipo, formacion, jugadores = modo_interactivo(
            equipo_inicial=args.equipo,
            formacion_inicial=args.formacion,
        )
    else:
        equipo = args.equipo or "Mi Equipo"
        formacion = args.formacion or "4-3-3"
        jugadores = args.jugadores

    dibujar_cancha(equipo, formacion, jugadores)


if __name__ == "__main__":
    main()