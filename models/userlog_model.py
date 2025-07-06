from typing import Optional
from pydantic import BaseModel

class UserLog(BaseModel):
    username: str
    password: str