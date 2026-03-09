import threading

from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import time
app = FastAPI()

SERVER_URL = "http://147.96.81.252:7719/"
ip_time={}
#hacer ping cada 60s
sleep_time=30
#si no responde en 60s, cierrar conexion
ping_time=60
#lista de ip de los jugadores
list_ip=set()

#post name
def postName():
    if getGente().get("bunny") is None:
        name=requests.post(SERVER_URL+"alias/bunny")
#get info
def getInfo():
    info=requests.get(SERVER_URL+"info")
    informacion=info.json()
    return informacion
# get Recursos
def getRecursos():
    informacion=getInfo()
    recursos=informacion["Recursos"]
    return recursos
#get Objetivos
def getObjetivo():
    informacion=getInfo()
    objetivo=informacion["Objetivo"]
    return objetivo
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
    result=ping(client_ip,send_data)
    return {
        "status": "sent",
        "response": result
    }
    
def update_ip():
    global list_ip
    try:
        gente = getGente()
    except Exception as e:
        print("Error updating IP list:", e)
def ping(ip,msg):
    url = f"http://{ip}:7720/buzon"

    try:
        r = requests.post(url, json=msg, timeout=2)

        if r.status_code == 200:
            ip_time[ip] = time.time()
            return r.json()

    except requests.exceptions.Timeout:
        print(f"{ip} no responde (timeout)")

    except requests.exceptions.RequestException as e:
        print("Ping error:", e)

    return None
def loop(msg):
    while True:
        update_ip()
        for ip in list_ip:
            #si no responde en 60s, cierrar conexion
            if ip not in ip_time or time.time() - ip_time[ip] > ping_time:
                print(f"IP {ip} is not responding.")
                ip_time[ip] = time.time()  # Mark as not responding
            # elif time.time() - ip_time[ip] > sleep_time:
            #     continue
            else:
                ping(ip,msg)
if __name__ == "__main__":
    import uvicorn
    postName()
    thread=threading.Thread(target=loop,daemon=True,args=({"msg":"hola"},))
    thread.start()
    uvicorn.run("main:app", host=getGente().get("bunny"), port=7720, reload=True)