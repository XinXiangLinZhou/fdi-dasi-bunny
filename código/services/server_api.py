# 专门放和老师 server 的通信
import requests
from app.config import SERVER_URL, MY_ALIAS
from app.state import list_ip

def post_name():
    if get_gente().get(MY_ALIAS) is None:
        requests.post(f"{SERVER_URL}alias/{MY_ALIAS}")

def get_info():
    response = requests.get(f"{SERVER_URL}info")
    return response.json()

def get_recursos():
    return get_info()["Recursos"]

def get_objetivo():
    return get_info()["Objetivo"]

def get_gente():
    response = requests.get(f"{SERVER_URL}gente")
    personas = response.json()

    jugadores = {}
    for p in personas:
        jugadores[p["alias"]] = p["ip"]
        if p["alias"] != MY_ALIAS:
            list_ip.add(p["ip"])
    return jugadores