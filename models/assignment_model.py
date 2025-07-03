from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class Assignment(BaseModel):
    titulo: str
    descripcion: str
    fecha: datetime
    grupo: int
    materias: int