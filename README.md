Para la ejecución del sistema es necesario:

-Disponer de Python instalado.

-Tener configurado uv para la gestión de dependencias.

-Contar con el servidor del juego en funcionamiento.

-Tener Ollama instalado y ejecutando el modelo seleccionado.

-Disponer de conectividad entre los jugadores.

Pasos básicos de ejecución:

-Iniciar el servidor del juego.

-Ejecutar Ollama con el modelo correspondiente.

    bin/ollama run ministral-3:8B
    
-Lanzar la aplicación FastAPI.

    uv run run.py
    
-Verificar el registro del agente.

-Iniciar la interacción entre jugadores.
