import time
from fastapi import APIRouter, Request

from app.models.mensaje import Mensaje
from app.state import ip_time, list_ping
from services.peer_api import ping

router = APIRouter()

@router.post("/buzon")
async def buzon(request: Request, mensaje: Mensaje):
    client_ip = request.client.host

    print("IP:", client_ip)
    print("mensaje:", mensaje.msg)

    send_data = {"msg": "hola"}

    ip_time[client_ip] = time.time()
    if client_ip in list_ping:
        list_ping.discard(client_ip)

    result = ping(client_ip, send_data)

    return {
        "status": "sent",
        "response": result
    }