from typing import Optional
from pydantic import BaseModel

class Professor(BaseModel):
    nombre: str
    usuario: str
    correo: str
    contraseña: str
    telefono: int
    estado: Optional[int]=1
    doclogFK: int