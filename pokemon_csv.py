import csv
import os
import requests
from fastapi import HTTPException

CSV_FILE = "cache_pokemones.csv"
FIELDNAMES = ["id", "nombre", "tipo", "altura", "peso", "experiencia_base", "hp", "ataque", "defensa", "velocidad"]


def inicializar_csv():
    """Crea el archivo CSV con sus encabezados si aún no existe."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()


def buscar_en_csv(clave: str):
    """Busca un Pokémon en el CSV por nombre o id."""
    inicializar_csv()
    clave_limpia = str(clave).strip().lower()

    with open(CSV_FILE, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Evitar errores si hay filas vacías o mal formadas
            if not row or not row.get("nombre") or not row.get("id"):
                continue

            if row["nombre"].lower() == clave_limpia or str(row["id"]) == clave_limpia:
                return {
                    "id": int(row["id"]),
                    "nombre": row["nombre"],
                    "tipo": row["tipo"],
                    "altura": int(row["altura"]),
                    "peso": int(row["peso"]),
                    "experiencia_base": int(row["experiencia_base"]),
                    "hp": int(row["hp"]),
                    "ataque": int(row["ataque"]),
                    "defensa": int(row["defensa"]),
                    "velocidad": int(row["velocidad"])
                }
    return None


def guardar_en_csv(pokemon: dict):
    """Agrega un registro de Pokémon al archivo CSV."""
    inicializar_csv()
    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(pokemon)


def consultar_pokeapi(clave: str) -> dict:
    """Consulta la PokéAPI oficial y extrae los 10 atributos requeridos."""
    clave_limpia = str(clave).strip().lower()
    url = f"https://pokeapi.co/api/v2/pokemon/{clave_limpia}"

    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 404:
            raise HTTPException(status_code=404, detail=f"El Pokémon '{clave}' no existe en PokéAPI.")
        if response.status_code != 200:
            raise HTTPException(status_code=502, detail="Error de respuesta al consultar la PokéAPI.")
        data = response.json()
    except requests.RequestException:
        raise HTTPException(status_code=502, detail="No se pudo establecer conexión con la PokéAPI.")

    # Extracción del tipo principal (types es una lista)
    types_list = data.get("types", [])
    tipo_principal = types_list[0]["type"]["name"] if types_list else "desconocido"

    # Extracción de estadísticas
    stats = {item["stat"]["name"]: item["base_stat"] for item in data.get("stats", [])}

    return {
        "id": int(data["id"]),
        "nombre": str(data["name"]).lower(),
        "tipo": str(tipo_principal),
        "altura": int(data.get("height", 0)),
        "peso": int(data.get("weight", 0)),
        "experiencia_base": int(data.get("base_experience", 0) or 0),
        "hp": int(stats.get("hp", 0)),
        "ataque": int(stats.get("attack", 0)),
        "defensa": int(stats.get("defense", 0)),
        "velocidad": int(stats.get("speed", 0))
    }


def obtener_pokemon_csv(clave: str):
    """Lógica principal de caché para CSV."""
    pokemon_local = buscar_en_csv(clave)
    if pokemon_local:
        return "CSV", pokemon_local

    pokemon_api = consultar_pokeapi(clave)
    guardar_en_csv(pokemon_api)
    return "PokeAPI", pokemon_api
