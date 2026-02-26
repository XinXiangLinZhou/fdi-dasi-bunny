'''import requests
#from fastapi import FastAPI
def main():
    print("Hello from fdi-dasi-bunny!")


#app = FastAPI()
SERVER_URL = "http://147.96.81.252:7719/"


# @app.on_event("startup")
# def startup_event():
#     requests.post(
#         f"{SERVER_URL}/agents/register",
#         json={
#             "agent_id": "agente_01",
#             "tipo": "backend"
#         }
#     )


#post name

#name=requests.post(SERVER_URL+"alias/bunny")
name="bunny"
#get info
info=requests.get(SERVER_URL+"info")
informacion=info.json()
recursos=informacion["Recursos"]
objetivo=informacion["Objetivo"]
#print(recursos["queso"],objetivo)
#get gente
gente=requests.get(SERVER_URL+"gente")
personas=gente.json()
jugadores={}
jugadores={p["alias"]:p["ip"] for p in personas if p["alias"] != name}
print(jugadores)




print(gente.text)
'''

from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
app=FastAPI()

class IncomingMessage(BaseModel):
    message:str

@app.post("/buzon")

async def buzon(request: Request):
    client_ip=request.client.host
    print(client_ip)
    #print(request.msg)
def buzon(data: IncomingMessage):
    print("recibido: ",data.message)
    try:
        r=requests.post(
            json={"msg":"¿Que recursos tienes?"},
            verify=False
        )
    except Exception as e:
        print("Error:",e)
    return{"status":"ok"}



if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
