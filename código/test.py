#para probar ollama
from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
import json

app = FastAPI()

class Mensaje(BaseModel):
    msg: str

my_items={"manzana":1,"pera":2,"naranja":3}
wanted_item={"pera":2, "naranja":1,"banana":1}

OLLAMA_URL="http://localhost:11434/api/generate"
DEFAULT_MODEL="ministral-3:8B"

#recibir mensaje que comunica con nosotros
@app.post("/buzon")
async def buzon(request: Request, mensaje: Mensaje):
    client_ip=  request.client.host
    print("IP:", client_ip)
    print("mensaje:", mensaje.msg)
    
    #instrucciones
    parse_prompt = f"""
       Devuelve **exclusivamente** una lista en formato JSON valido con 
       el siguiente contenido 
        "{my_items}"
       
       **No añadas texto adicional, comentarios ni explicaciones.** Solo la
       lista en JSON puro. 

       """
    
    print(parse_prompt)
    
    #recibir resultado de ollama
    r = requests.post(
        OLLAMA_URL,
        json={
            "model": DEFAULT_MODEL,
            "prompt": parse_prompt,
            "stream": False
        }
    )

    reply_raw = r.json.get("response", "")

    json_limpio = reply_raw[7:len(reply_raw) -4]
    aux = json.loads(json_limpio)
    print(aux)

    '''
    try:
        parsed = json.loads(r.json().get("response", ""))
    except json.JSONDecodeError:
        parsed = {"has": [], "wants": []}
    #instrucciones
    reply_prompt = f"""
    Con json {parsed} generado,
    calculando todos los items que tengo {my_items}
    y que necesito {wanted_item}.

    Si tiene los items que quiero → generar mensaje en formato json para realizar intercambio.
    Si no → responder:

    {{"msg":"no quiero intercambiar nada"}}

    Responde SOLO JSON válido.
    """
    #recibir resultado que voy a enviar al cliente
    r = requests.post(
        OLLAMA_URL,
        json={
            "model": DEFAULT_MODEL,
            "prompt": reply_prompt,
            "stream": False
        }
    )

    reply_raw = r.json().get("response", "")

    try:
        reply = json.loads(reply_raw)
    except json.JSONDecodeError:
        reply = {"msg": reply_raw}
    #enviar al clinete
    url = f"http://{client_ip}:8000/buzon"

    try:
        r = requests.post(url, json=reply, timeout=3)
        result = r.json()
    except Exception as e:
        result = {"error": str(e)}
    '''
    return {
        "status": "ok",
        "response": "ok"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("test:app", host="147.96.84.78", port=7700, reload=True)