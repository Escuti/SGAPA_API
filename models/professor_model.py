from typing import Optional
from pydantic import BaseModel

class Professor(BaseModel):
    usuario: str
    correo: str
    contraseña: str
    telefono: int
    estado: Optional[int]=1