import threading
import time
import requests

from fastapi import FastAPI, Request
from pydantic import BaseModel

app = FastAPI()

SERVER_URL = "http://172.16.82.142:7719/"
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "ministral-3:8B"

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "finish_trade",
            "description": "Usa esta herramienta solo cuando el intercambio ya esté claramente aceptado por ambas partes.",
            "parameters": {
                "type": "object",
                "properties": {
                    "give": {"type": "object"},
                    "receive": {"type": "object"},
                    "message": {"type": "string"}
                },
                "required": ["give", "receive", "message"]
            }
        }
    }
]

ip_time = {}

sleep_time = 30
ping_time = 60

list_ip = set()
list_ping = set()

chat_history = {}
chat_status = {}

MAX_HISTORY = 12
lock = threading.Lock()


def postName():
    try:
        gente = getGente()
        if gente.get("bunny") is None:
            requests.post(SERVER_URL + "alias/bunny", timeout=3)
    except Exception as e:
        print("postName error:", e)


def getInfo():
    return requests.get(SERVER_URL + "info", timeout=3).json()


def getRecursos():
    return getInfo()["Recursos"]


def getObjetivo():
    return getInfo()["Objetivo"]


def getGente():
    personas = requests.get(SERVER_URL + "gente", timeout=3).json()
    return {p["alias"]: p["ip"] for p in personas}


def getGenteAlias():
    personas = requests.get(SERVER_URL + "gente", timeout=3).json()
    return {p["ip"]: p["alias"] for p in personas}


def postObject(ip, object):
    requests.post(SERVER_URL + "paquetes/" + getGenteAlias().get(ip), json=object, timeout=3)


class Mensaje(BaseModel):
    msg: str


def ensure_chat(ip: str):
    with lock:
        chat_history.setdefault(ip, [])
        chat_status.setdefault(ip, "chatting")


def add_history(ip: str, role: str, text: str):
    ensure_chat(ip)
    with lock:
        chat_history[ip].append({"role": role, "content": text})
        chat_history[ip] = chat_history[ip][-MAX_HISTORY:]


# ========= Ollama =========

def generar_respuesta_ollama(ip: str) -> str:
    recursos = getRecursos()
    objetivo = getObjetivo()

    ensure_chat(ip)

    with lock:
        history = list(chat_history[ip])

    system_prompt = f"""
Eres un jugador experto de Catan.
Tu objetivo es: {objetivo}
Tus recursos actuales son: {recursos}

Reglas:
- Responde en español, mensajes cortos.
- Solo negocia con los recursos que tienes.
- Si te conviene → acepta.
- Si no → rechaza o contraoferta.

REGLA CRÍTICA (NO FALLAR):
Cuando alguien dice "X por Y":
- El otro jugador TE DA X
- El otro jugador QUIERE Y

Por tanto:
- give = lo que TÚ entregas (Y)
- receive = lo que TÚ recibes (X)

Ejemplo:
"3 arroz por 1 tela"
→ give = {{ "tela": 1 }}
→ receive = {{ "arroz": 3 }}

- Nunca inviertas esto.
- Nunca inventes recursos.

Cuando el intercambio esté cerrado, usa finish_trade.
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
        print("Ollama:", r.text)

        r.raise_for_status()
        result = r.json()
        msg = result.get("message", {})

        # 🔧 TOOL CALL → ejecutar intercambio
        if "tool_calls" in msg:
            for call in msg["tool_calls"]:
                if call["function"]["name"] == "finish_trade":
                    args = call["function"]["arguments"]

                    print("TRADE FINAL:", args)

                    give = args.get("give", {})
                    receive = args.get("receive", {})

                    # enviar recursos al otro jugador
                    if give:
                        try:
                            postObject(ip, give)
                            print("Enviado:", give)
                        except Exception as e:
                            print("Error enviando:", e)

                    # log de lo recibido
                    if receive:
                        print("Recibido:", receive)

                    # cerrar chat
                    with lock:
                        chat_status[ip] = "success"

                    return args.get("message", "trato hecho")

        return msg.get("content", "").strip()

    except Exception as e:
        print("Ollama error:", e)
        return "¿Qué recursos tienes?"


# ========= Comunicación =========

@app.post("/buzon")
async def buzon(request: Request, mensaje: Mensaje):
    client_ip = request.client.host
    texto = mensaje.msg
    now = time.time()

    print("IP:", client_ip, "MSG:", texto)

    with lock:
        ip_time[client_ip] = now
        list_ping.discard(client_ip)

    ensure_chat(client_ip)
    add_history(client_ip, "user", texto)

    with lock:
        if chat_status.get(client_ip) != "chatting":
            return {"status": chat_status[client_ip]}

    respuesta = generar_respuesta_ollama(client_ip)
    add_history(client_ip, "assistant", respuesta)

    result = ping(client_ip, {"msg": respuesta})

    return {"status": "sent", "response": result}


def update_ip():
    global list_ip, list_ping

    try:
        gente = getGente()
        my_ip = gente.get("bunny")

        new_ips = {
            ip for alias, ip in gente.items()
            if alias != "bunny" and ip != my_ip and ip != "127.0.0.1"
        }

        with lock:
            list_ip = new_ips

            for ip in new_ips:
                if ip not in ip_time:
                    list_ping.add(ip)

            for ip in set(ip_time) - new_ips:
                ip_time.pop(ip, None)
                list_ping.discard(ip)
                chat_history.pop(ip, None)
                chat_status.pop(ip, None)

    except Exception as e:
        print("update_ip error:", e)


def ping(ip, msg):
    try:
        r = requests.post(f"http://{ip}:7720/buzon", json=msg, timeout=10)
        if r.status_code == 200:
            with lock:
                ip_time[ip] = time.time()
                list_ping.discard(ip)
            return r.json()
    except:
        pass
    return None


def check_inactive_ips():
    now = time.time()
    with lock:
        for ip in list_ip:
            if ip_time.get(ip, 0) + ping_time < now:
                if chat_status.get(ip) == "chatting":
                    list_ping.add(ip)


def iniciar_chat_si_hace_falta(ip: str):
    ensure_chat(ip)

    with lock:
        if chat_status[ip] != "chatting":
            return
        if chat_history[ip]:
            return

    msg = generar_respuesta_ollama(ip)
    add_history(ip, "assistant", msg)
    ping(ip, {"msg": msg})


def loop():
    while True:
        try:
            update_ip()
            check_inactive_ips()

            with lock:
                targets = list(list_ping)

            for ip in targets:
                iniciar_chat_si_hace_falta(ip)

        except Exception as e:
            print("loop error:", e)

        time.sleep(sleep_time)


if __name__ == "__main__":
    import uvicorn

    postName()

    threading.Thread(target=loop, daemon=True).start()

    uvicorn.run(app, host=getGente().get("bunny"), port=7720)
