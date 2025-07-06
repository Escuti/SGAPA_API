from typing import Optional
from pydantic import BaseModel

#Un modelo es una recreación de las tablas de la BD, que nos permitirá hacer el enlace con la misma. Debe contener la misma estructura de tabla en que la BD
#Modelo de la Tabla Usuario

class Student(BaseModel):
    nombre: str
    usuario: str
    contraseña: str
    correo: str
    telefono: int
    grupo: int
    padre_familia: int
    estado: Optional[int]=1 #consultar el uso de optional
    estudlogFK: int

    #NOTA IMPORTANTE: Las llaves foráneas y las principales no deben ir en el modelo, solo los datos que se ingresan por medio del servicio POST (Un create por ejemplo)