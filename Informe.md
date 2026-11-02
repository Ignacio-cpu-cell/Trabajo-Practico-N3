#Informe Comparativo: Caché en CSV vs SQLite

Observación de tiempos (`tiempo_ms`) al consultar el mismo Pokémon
Al realizar la primera solicitud para un Pokémon (por ejemplo, `pikachu`), el origen devuelto es `"PokeAPI"` y el tiempo de respuesta varía aprox. entre los 300 y 800 ms (dependiendo de la demora de red de la API externa)

Al realizar la segunda solicitud consecutiva para el mismo Pokémon, el origen cambia a `"CSV"` o `"SQLite"`, y el tiempo se reduce drásticamente a un rango de 0.05 a 0.5 ms

  
Esta aceleracion ocurre porque la primera consulta debe realizar una petición HTTP a través de Internet hacia los servidores de PokéAPI, procesar el JSON externo e ingresar el registro en el almacenamiento local.
En la segunda consulta, el sistema intercepta el pedido en la capa intermedia (caché) y lee los datos almacenados localmente en disco, eliminando la demora de red y respondiendo en una fracción mínima de tiempo.


#Diferencia entre CSV y SQLite a medida que crece el volumen de datos

**Con un volumen bajo (1 a 50 Pokémon):** 
La diferencia de tiempo entre CSV y SQLite es prácticamente imperceptible.
Incluso el archivo CSV puede llegar a responder levemente más rápido debido a la baja sobrecarga de inicialización.


**Con un volumen alto (cientos o miles de registros):** 
  - CSV
    El módulo CSV debe recorrer el archivo fila por fila desde el principio hasta encontrar la coincidencia. Si se busca el Pokémon n.° 1000, deberá leer e interpretar las 999 filas anteriores en memoria.
  - SQLite
    SQLite busca por`id`. Esto permite localizar directamente el registro deseado sin necesidad de inspeccionar toda la base de datos.


#Conclusión: Ventajas de una Base de Datos frente a un Archivo Plano
Para tareas de almacenamiento, búsqueda, filtrado y escalabilidad, una base de datos como SQLite presenta ventajas estructurales sobre un archivo CSV:

1. Eficiencia en Búsqueda e Indexación: Indexa las claves primarias (`id`), evitando búsquedas lineales secuenciales.

2. Tipado de Datos Estricto: Preserva de forma nativa los tipos numéricos (`INTEGER`, `REAL`), a diferencia del CSV, que almacena todo como texto y requiere conversiones explícitas al leer.

3. Consistencia y Concurrencia (Propiedades ACID): Evita la corrupción de datos ante múltiples peticiones simultáneas (escrituras concurrentes), mientras que un archivo CSV abierto en modo *append* corre riesgo de colisión o bloqueos.

4. Capacidad de Consulta Compleja: Permite realizar filtros, ordenamientos y agrupamientos con SQL (`WHERE`, `ORDER BY`, `JOIN`) directamente en el motor, sin necesidad de cargar y procesar toda la información manualmente en Python.
