# Pydantic 模型
from pydantic import BaseModel

class Mensaje(BaseModel):
    msg: str


class ListaRecursos(BaseModel):
    recursos: str
    cantidad: int
    accion: str  # aceptar, rechazar, contraoferta