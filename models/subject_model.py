from typing import Optional
from pydantic import BaseModel

class Subject(BaseModel):
    nombre: str
    id_grupo: int