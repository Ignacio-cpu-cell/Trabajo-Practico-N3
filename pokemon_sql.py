import sqlite3
import requests
from fastapi import HTTPException

DB_FILE = "cache_pokemones.db"


def obtener_conexion():
    """Devuelve la conexión configurada para leer filas como diccionarios."""
    con = sqlite3.connect(DB_FILE)
    con.row_factory = sqlite3.Row
    return con


def inicializar_db():
    """Crea la tabla pokemones en SQLite con sus 10 atributos."""
    con = obtener_conexion()
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS pokemones (
        id INTEGER PRIMARY KEY,
        nombre TEXT NOT NULL,
        tipo TEXT NOT NULL,
        altura INTEGER NOT NULL,
        peso INTEGER NOT NULL,
        experiencia_base INTEGER NOT NULL,
        hp INTEGER NOT NULL,
        ataque INTEGER NOT NULL,
        defensa INTEGER NOT NULL,
        velocidad INTEGER NOT NULL
    );
    """)
    con.commit()
    con.close()


def buscar_en_db(clave: str):
    """Busca un Pokémon en SQLite por id o nombre."""
    inicializar_db()
    clave_limpia = str(clave).strip().lower()
    con = obtener_conexion()
    cur = con.cursor()

    if clave_limpia.isdigit():
        cur.execute("SELECT * FROM pokemones WHERE id = ? OR LOWER(nombre) = ?", (int(clave_limpia), clave_limpia))
    else:
        cur.execute("SELECT * FROM pokemones WHERE LOWER(nombre) = ?", (clave_limpia,))

    row = cur.fetchone()
    con.close()

    if row:
        return dict(row)
    return None


def guardar_en_db(pokemon: dict):
    """Inserta o reemplaza un Pokémon en la base de datos."""
    inicializar_db()
    con = obtener_conexion()
    cur = con.cursor()
    cur.execute("""
    INSERT OR REPLACE INTO pokemones 
    (id, nombre, tipo, altura, peso, experiencia_base, hp, ataque, defensa, velocidad)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, (
        pokemon["id"], pokemon["nombre"], pokemon["tipo"], pokemon["altura"], pokemon["peso"],
        pokemon["experiencia_base"], pokemon["hp"], pokemon["ataque"], pokemon["defensa"], pokemon["velocidad"]
    ))
    con.commit()
    con.close()


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

    stats = {item["stat"]["name"]: item["base_stat"] for item in data.get("stats", [])}
    types = data.get("types", [])
    tipo_principal = types["type"]["name"] if types else "desconocido"

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


def obtener_pokemon_sql(clave: str):
    """Lógica principal de caché para SQLite."""
    pokemon_local = buscar_en_db(clave)
    if pokemon_local:
        return "SQLite", pokemon_local

    pokemon_api = consultar_pokeapi(clave)
    guardar_en_db(pokemon_api)
    return "PokeAPI", pokemon_api
