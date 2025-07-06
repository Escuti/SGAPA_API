from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from passlib.hash import bcrypt
import pymysql
import pymysql.cursors
from db.db_mysql import get_db_connection
from models.userlog_model import UserLog

class UserLog_Service:
    def __init__(self):
        self.con = get_db_connection()
        if self.con is None:
            print("No se ha podido establecer conexión con la BD")

    async def login_user(self, data: UserLog):
        try:
            #Hacemos verificación por username, para traer la información de la tabla correspondiente
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT * FROM usuarioslog WHERE username = %s"
                cursor.execute(sql, (data.username,))
                user = cursor.fetchone() #Con este fetch cargamos también las contraseñas encriptadas en hash

                if not user:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "success": False,
                            "message": "Usuario no encontrado",
                            "data": None
                        }
                    )

                if not bcrypt.verify(data.password, user["password_hash"]):
                    return JSONResponse(
                        status_code=401,
                        content={
                            "success": False,
                            "message": "Contraseña incorrecta",
                            "data": None
                        }
                    )
                #Asignamos variables a la información cargada en la tupla
                user_id = user["id_userlog"]
                tipo_usuario = user["tipo_usuario"]
                detalle_id = None

                #Revisamos el tipo de usuario y ejecutamos otra consulta para traer la información
                if tipo_usuario == "administrador":
                    cursor.execute(
                        "SELECT id_admin FROM admin_pr WHERE adminlogFK = %s", 
                        (user_id,)
                    )
                    admin = cursor.fetchone()
                    detalle_id = admin["id_admin"] if admin else None

                elif tipo_usuario == "docente":
                    cursor.execute(
                        "SELECT id_doc FROM docente WHERE doclogFK = %s", 
                        (user_id,)
                    )
                    docente = cursor.fetchone()
                    detalle_id = docente["id_doc"] if docente else None
                
                elif tipo_usuario == "estudiante":
                    cursor.execute(
                        "SELECT id_estud FROM estudiante WHERE estudlogFK = %s", 
                        (user_id,)
                    )
                    estudiante = cursor.fetchone()
                    detalle_id = estudiante["id_estud"] if estudiante else None

                elif tipo_usuario == "acudiente":
                    cursor.execute(
                        "SELECT id_pfamilia FROM padre_familia WHERE acudlogFK = %s", 
                        (user_id,)
                    )
                    acudiente = cursor.fetchone()
                    detalle_id = acudiente["id_pfamilia"] if acudiente else None

                return {
                    "id_usuario": user_id,
                    "tipo_usuario": tipo_usuario,
                    "id_detalle": detalle_id,
                    "mensaje": f"Login exitoso como {tipo_usuario}"
                }

        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": f"Error al iniciar sesión: {str(e)}",
                    "data": None
                }
            )