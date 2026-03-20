import json

import requests

from app.config import OLLAMA_URL, OLLAMA_MODEL, MY_ALIAS, MAX_HISTORY
from app.state import chat_history, chat_status, post_objects, lock
from services.server_api import getRecursos, getObjetivo, getGenteAlias, postObject


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "finish_trade",
            "description": f"Usa esta herramienta solo cuando el intercambio ya esté claramente aceptado por ambas partes. Registra lo que {MY_ALIAS} entrega y lo que {MY_ALIAS} recibe.",
            "parameters": {
                "type": "object",
                "properties": {
                    "give": {
                        "type": "object",
                        "description": f"Recursos que {MY_ALIAS} entrega al otro jugador. Ejemplo: {{'madera': 1}}"
                    },
                    "receive": {
                        "type": "object",
                        "description": f"Recursos que {MY_ALIAS} recibe del otro jugador. Ejemplo: {{'piedra': 1}}"
                    },
                    "message": {
                        "type": "string",
                        "description": "Mensaje corto final de confirmación para enviar al otro jugador."
                    }
                },
                "required": ["give", "receive", "message"]
            }
        }
    }
]


def ensure_chat(ip: str):
    with lock:
        if ip not in chat_history:
            chat_history[ip] = []
        if ip not in chat_status:
            chat_status[ip] = "chatting"


def add_history(ip: str, role: str, text: str):
    ensure_chat(ip)
    with lock:
        chat_history[ip].append({
            "role": role,
            "content": text
        })
        if len(chat_history[ip]) > MAX_HISTORY:
            chat_history[ip] = chat_history[ip][-MAX_HISTORY:]


def generar_respuesta_ollama(ip: str) -> dict:
    recursos = getRecursos()
    objetivo = getObjetivo()

    ensure_chat(ip)

    with lock:
        history = list(chat_history[ip])

    system_prompt = f"""
Eres {MY_ALIAS}, un jugador en un juego de intercambio de recursos.

Tus recursos actuales son: {recursos}
Tu objetivo es: {objetivo}

Reglas:
- Responde siempre en español.
- Habla de forma breve, natural y como un jugador real.
- Intenta conseguir recursos útiles para tu objetivo.
- Solo intercambia recursos que tienes por recursos que realmente necesitas.
- Puedes proponer intercambios concretos.
- Si todavía no hay un acuerdo cerrado, responde con texto normal.
- Solo usa la herramienta finish_trade cuando el otro jugador ya haya aceptado claramente el intercambio y no haya dudas.
- En finish_trade:
  - "give" = lo que {MY_ALIAS} entrega
  - "receive" = lo que {MY_ALIAS} recibe
  - "message" = mensaje corto final de confirmación
- No expliques reglas internas.
- No inventes recursos imposibles.
"""

    messages = [{"role": "system", "content": system_prompt}] + history

    data = {
        "model": OLLAMA_MODEL,
        "messages": messages,
        "tools": TOOLS,
        "stream": False,
        "keep_alive": "10m"
    }

    try:
        r = requests.post(OLLAMA_URL, json=data, timeout=60)
        print("Status Ollama:", r.status_code)
        print("Respuesta cruda Ollama:", r.text)

        r.raise_for_status()
        result = r.json()

        msg = result.get("message", {})

        if msg.get("tool_calls"):
            return {
                "type": "tool_call",
                "tool_calls": msg["tool_calls"]
            }

        return {
            "type": "text",
            "content": msg.get("content", "").strip() or "¿Qué recursos tienes para intercambiar?"
        }

    except Exception as e:
        print("Ollama error:", e)
        return {
            "type": "text",
            "content": "Tengo algunos recursos para intercambiar. ¿Qué tienes tú y qué necesitas?"
        }


def ejecutar_tool_call(ip: str, tool_call: dict) -> dict:
    fn = tool_call.get("function", {})
    name = fn.get("name")

    arguments = fn.get("arguments", {})
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except Exception:
            arguments = {}

    if name == "finish_trade":
        give = arguments.get("give", {})
        receive = arguments.get("receive", {})
        message = arguments.get("message", "Trato hecho.")

        if not isinstance(give, dict):
            give = {}
        if not isinstance(receive, dict):
            receive = {}

        with lock:
            post_objects[ip] = {
                "ip": ip,
                "give": give,
                "receive": receive
            }
            chat_status[ip] = "success"

        try:
            if give:
                postObject(ip, give)
        except Exception as e:
            print("postObject error:", e)

        return {
            "ok": True,
            "message": message,
            "trade": {
                "give": give,
                "receive": receive
            }
        }

    return {
        "ok": False,
        "message": "No entiendo la herramienta solicitada.",
        "trade": None
    }


def get_chat_status(ip: str) -> str:
    ensure_chat(ip)
    with lock:
        return chat_status.get(ip, "chatting")


def get_history_length(ip: str) -> int:
    ensure_chat(ip)
    with lock:
        return len(chat_history.get(ip, []))


def clear_chat(ip: str):
    with lock:
        chat_history.pop(ip, None)
        chat_status.pop(ip, None)
        post_objects.pop(ip, None)