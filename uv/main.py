from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests

app = FastAPI()

# SERVER_URL = "http://147.96.81.252:7719/"
# #post name
# name=requests.post(SERVER_URL+"alias/bunny")
# #get info
# info=requests.get(SERVER_URL+"info")
# informacion=info.json()
# recursos=informacion["Recursos"]
# objetivo=informacion["Objetivo"]
# #print(recursos["queso"],objetivo)
# #get gente
# gente=requests.get(SERVER_URL+"gente")
# personas=gente.json()
# jugadores={}
# jugadores={p["alias"]:p["ip"] for p in personas}

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

    url = f"http://{client_ip}:7720/buzon"

    try:
        r = requests.post(url, json=send_data, timeout=3)
        result = r.json()
    except Exception as e:
        result = {"error": str(e)}

    return {
        "status": "sent",
        "response": result
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="147.96.84.78", port=7720, reload=True)


