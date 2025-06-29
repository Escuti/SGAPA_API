from typing import Optional
from pydantic import BaseModel

class Parent(BaseModel): #Podría ser necesario agregar el dato usuario
    nombre: str
    correo: str
    contraseña: str
    telefono: int
    estado: Optional[int]=1