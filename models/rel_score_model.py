from typing import Optional
from pydantic import BaseModel

class Rel_Score(BaseModel):
    estudFK: int
    actividFK: int
    nota: int