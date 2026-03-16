import threading

from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import time
app = FastAPI()

SERVER_URL = "http://147.96.81.252:7719/"
ip_time={}
#hacer ping cada 30s
sleep_time=30
#si no responde en 60s, cierrar conexion
ping_time=60
#lista de ip de los jugadores
list_ip=set()
#lista de ip de los jugadores que hay que hacer ping para empezar la comunicacion
list_ping = set()
lock = threading.Lock()
#post name
def postName():
    if getGente().get("bunny") is None:
        requests.post(SERVER_URL+"alias/bunny")

#get info
def getInfo():
    info=requests.get(SERVER_URL+"info")
    return info.json()

# get Recursos
def getRecursos():
    informacion=getInfo()
    return informacion["Recursos"]

#get Objetivos
def getObjetivo():
    informacion=getInfo()
    return informacion["Objetivo"]

#get gente, obtenemos los ip y nombre de los jugadores
def getGente():
    gente = requests.get(SERVER_URL + "gente")
    personas = gente.json()
    jugadores = {}
    for p in personas:
        jugadores[p["alias"]] = p["ip"]
        if p["alias"] != "bunny":
            list_ip.update([p["ip"]])
    return jugadores


#mensaje formato json
class Mensaje(BaseModel):
    msg: str


@app.post("/buzon")
async def buzon(request: Request, mensaje: Mensaje):

    client_ip = request.client.host

    print("IP:", client_ip)
    print("mensaje:", mensaje.msg)
    send_data = {
        "msg": "hola"
    }
    now = time.time()
    ip_time[client_ip] = now
    if client_ip in list_ping:
            list_ping.discard(client_ip)
    result=ping(client_ip,send_data)
    return {
        "status": "sent",
        "response": result
    }

def update_ip():
    global list_ip, list_ping

    try:
        gente = getGente()
        new_ips = {ip for alias, ip in gente.items() if alias != "bunny"}

        with lock:
            list_ip = new_ips

            # nuevas IP, añadir a la lista de ping
            for ip in new_ips:
                if ip not in ip_time:
                    list_ping.add(ip)

            # ips antiguas, eliminar de ip_time y lista de ping
            old_ips = set(ip_time.keys()) - new_ips
            for ip in old_ips:
                ip_time.pop(ip, None)
                list_ping.discard(ip)

    except Exception as e:
        print("Error updating IP list:", e)

def ping(ip,msg):
    url = f"http://{ip}:7720/buzon"

    try:
        r = requests.post(url, json=msg, timeout=5)

        if r.status_code == 200:
            with lock:
                ip_time[ip] = time.time()
                list_ping.discard(ip)
            return r.json()


    except requests.exceptions.RequestException:
        pass

    return None

def check_inactive_ips():
   # Ips que no han respondido en ping_time segundos, añadir a lista de ping
    now = time.time()

    with lock:
        for ip in list_ip:
            last = ip_time.get(ip)

            if last is None:
                list_ping.add(ip)
            elif now - last > ping_time:
                list_ping.add(ip)

def loop(msg):
   while True:
        try:
            # actualizar la lista de IPs y la lista de ping cada ciclo
            update_ip()
            check_inactive_ips()

            # copiar la lista de ping para iterar sin bloquearla
            with lock:
                current_ping_list = list(list_ping)

            # hacer ping a cada IP en la lista de ping
            for ip in current_ping_list:
                print(f"Ping a {ip}")
                ping(ip, msg)

        except Exception as e:
            print("Loop error:", e)

        time.sleep(sleep_time)

if __name__ == "__main__":
    import uvicorn
    postName()
    thread=threading.Thread(target=loop,daemon=True,args=({"msg":"hola1"},))
    thread.start()
    uvicorn.run(app, host=getGente().get("bunny"), port=7720)
