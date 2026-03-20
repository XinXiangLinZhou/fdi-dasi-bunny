from ollama import chat, ChatResponse
from pydantic import BaseModel

DEFAULT_MODEL="llama3.2"
OBJECTIVE = "Necesito 4 de vino y 1 de agua"
INIT_RSC = "Tengo 3 de tela y 1 de madera"
TEST_MESSAGE = "Buenas, te ofrezco 3 de vino y 2 de agua. A cambio necesito 2 de tela y 1 de madera"

SYSTEM_ROLE = f'''Eres un jugador de Catan que debe intercambiar recursos con otro jugadores. 
    Tu objetivo son conseguir estos recursos {OBJECTIVE}.
    Tienes estos inicialmente {INIT_RSC}. Genera 2 salidas, una de lo que me ofrecen y otra de lo que me piden.
'''


class Recurso (BaseModel) : 
    nombre: str 
    cantidad : int 


class ListaRecursos (BaseModel) : 
    recursos : list[Recurso]

response : ChatResponse= chat(
    model = DEFAULT_MODEL,

    messages = [
        {
        'role' : "system",'content' : SYSTEM_ROLE
        },
        {
        'role' : "user" , 'content' : TEST_MESSAGE,
        }
    ] ,

    format = ListaRecursos.model_json_schema(),
) 

recursos = ListaRecursos.model_validate_json(response.message.content)

print(recursos)