# 专门放和老师 server 的通信
import requests

from app.config import SERVER_URL, MY_ALIAS


def postName():
    try:
        gente = getGente()
        if gente.get(MY_ALIAS) is None:
            requests.post(SERVER_URL + f"alias/{MY_ALIAS}", timeout=3)
    except Exception as e:
        print("postName error:", e)


def getInfo():
    info = requests.get(SERVER_URL + "info", timeout=3)
    return info.json()


def getRecursos():
    informacion = getInfo()
    return informacion["Recursos"]


def getObjetivo():
    informacion = getInfo()
    return informacion["Objetivo"]


def getGente():
    gente = requests.get(SERVER_URL + "gente", timeout=3)
    personas = gente.json()

    jugadores = {}
    for p in personas:
        jugadores[p["alias"]] = p["ip"]

    return jugadores


def getGenteAlias():
    gente = requests.get(SERVER_URL + "gente", timeout=3)
    personas = gente.json()

    jugadores = {}
    for p in personas:
        jugadores[p["ip"]] = p["alias"]

    return jugadores


def postObject(ip, obj):
    alias = getGenteAlias().get(ip)
    if alias is None:
        print(f"postObject error: no alias encontrado para IP {ip}")
        return

    requests.post(
        SERVER_URL + "paquetes/" + alias,
        json=obj,
        timeout=3
    )   