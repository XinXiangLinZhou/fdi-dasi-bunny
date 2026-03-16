import threading
import uvicorn

from app.main import app
from app.config import DEFAULT_PORT, MY_ALIAS
from app.services.server_api import post_name, get_gente
from app.services.monitor import loop

if __name__ == "__main__":
    post_name()

    thread = threading.Thread(
        target=loop,
        daemon=True,
        args=({"msg": "hola1"},)
    )
    thread.start()

    host = get_gente().get(MY_ALIAS)
    uvicorn.run(app, host=host, port=DEFAULT_PORT)