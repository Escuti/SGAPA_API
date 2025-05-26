from typing import Optional
from pydantic import BaseModel

class SubAdmin(BaseModel):
    usuario: str
    contraseña: str
    correo: str
    telefono: int
    id_admin: int
    estado: Optional[int]=1