import time

from fastapi import APIRouter, Request

from app.models.message import Mensaje
from app.state import ip_time, list_ping, lock
from services.peer_api import ping
from services.ollama_agent import (
    ensure_chat,
    add_history,
    generar_respuesta_ollama,
    ejecutar_tool_call,
    get_chat_status,
)

router = APIRouter()


@router.post("/buzon")
async def buzon(request: Request, mensaje: Mensaje):
    client_ip = request.client.host
    texto_recibido = mensaje.msg
    now = time.time()

    print("IP:", client_ip)
    print("mensaje:", texto_recibido)

    with lock:
        ip_time[client_ip] = now
        list_ping.discard(client_ip)

    ensure_chat(client_ip)
    add_history(client_ip, "user", texto_recibido)

    status = get_chat_status(client_ip)
    if status != "chatting":
        return {"status": status}

    respuesta = generar_respuesta_ollama(client_ip)

    if respuesta["type"] == "text":
        respuesta_texto = respuesta["content"]
        add_history(client_ip, "assistant", respuesta_texto)

        result = ping(client_ip, {"msg": respuesta_texto})

        return {
            "status": "sent",
            "response": result
        }

    if respuesta["type"] == "tool_call":
        tool_calls = respuesta["tool_calls"]

        if not tool_calls:
            return {"status": "error", "msg": "tool_calls vacío"}

        tool_result = ejecutar_tool_call(client_ip, tool_calls[0])

        respuesta_texto = tool_result["message"]
        add_history(client_ip, "assistant", respuesta_texto)

        result = ping(client_ip, {"msg": respuesta_texto})

        return {
            "status": "success" if tool_result["ok"] else "error",
            "response": result,
            "trade": tool_result.get("trade")
        }

    return {"status": "error", "msg": "respuesta no válida de Ollama"}