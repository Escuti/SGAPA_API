from typing import Optional
from pydantic import BaseModel

class Rel_Group_Subject(BaseModel):
    grupoFK: int
    materiaFK: int