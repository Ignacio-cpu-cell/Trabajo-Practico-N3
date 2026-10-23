import time
from fastapi import FastAPI, Query
from pokemon_csv import obtener_pokemon_csv
from pokemon_sql import obtener_pokemon_sql

app = FastAPI(
    title="PokéAPI Cache API — TP N.º 3",
    description="API intermedia con mecanismo de caché en CSV y SQLite"
)

@app.get("/")
def bienvenido():
    return {"mensaje": "API de Caché PokéAPI lista. Consulta /pokemon/{clave}"}


@app.get("/pokemon/{clave}")
def get_pokemon(
    clave: str, 
    modo: str = Query("sqlite", description="Modo de almacenamiento: 'sqlite' o 'csv'")
):
    """
    Endpoint principal exigido por la consigna.
    Permite seleccionar el motor con el query param ?modo=sqlite o ?modo=csv.
    """
    inicio = time.perf_counter()
    modo_limpio = modo.strip().lower()

    if modo_limpio == "csv":
        origen, datos = obtener_pokemon_csv(clave)
    else:
        origen, datos = obtener_pokemon_sql(clave)

    fin = time.perf_counter()
    tiempo_ms = round((fin - inicio) * 1000, 2)

    return {
        "origen": origen,
        "datos": datos,
        "tiempo_ms": tiempo_ms
    }


@app.get("/pokemon_csv/{clave}")
def get_pokemon_csv_directo(clave: str):
    """Endpoint explícito para probar exclusivamente la versión CSV."""
    inicio = time.perf_counter()
    origen, datos = obtener_pokemon_csv(clave)
    fin = time.perf_counter()
    return {
        "origen": origen,
        "datos": datos,
        "tiempo_ms": round((fin - inicio) * 1000, 2)
    }


@app.get("/pokemon_sql/{clave}")
def get_pokemon_sql_directo(clave: str):
    """Endpoint explícito para probar exclusivamente la versión SQLite."""
    inicio = time.perf_counter()
    origen, datos = obtener_pokemon_sql(clave)
    fin = time.perf_counter()
    return {
        "origen": origen,
        "datos": datos,
        "tiempo_ms": round((fin - inicio) * 1000, 2)
    }
