import threading
import uvicorn

from app.main import app
from app.config import DEFAULT_PORT, DEFAULT_HOST, MY_ALIAS
from services.server_api import post_name, get_gente
from services.monitor import loop

if __name__ == "__main__":
    post_name()

    gente = get_gente()
    my_host = gente.get(MY_ALIAS, DEFAULT_HOST)

    print(f"Starting agent {MY_ALIAS} on {my_host}:{DEFAULT_PORT}")

    thread = threading.Thread(
        target=loop,
        daemon=True,
        args=({"msg": "hola1"},)
    )
    thread.start()

    uvicorn.run(app, host=my_host, port=DEFAULT_PORT)