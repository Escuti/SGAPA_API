from typing import Optional
from pydantic import BaseModel

class Parent(BaseModel): #Podría ser necesario agregar el dato usuario
    nombre: str
    usuario: str
    correo: str
    contraseña: str
    telefono: int
    estado: Optional[int]=1
    acudlogFK: int