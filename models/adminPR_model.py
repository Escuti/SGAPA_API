from typing import Optional
from pydantic import BaseModel

class AdminPR(BaseModel):
    usuario: str
    contraseña: str
    correo: str
    telefono: int
    estado: Optional[int]=1