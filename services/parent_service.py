from fastapi.responses import JSONResponse
import pymysql
import pymysql.cursors
from db.db_mysql import get_db_connection
from models.parent_model import Parent

class Parent_Service:
    def __init__(self):
        self.con=get_db_connection()
        if self.con is None:
            print("No se ha podido establecer conexión con la BD")

    async def get_users(self):
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM padre_familia")
                users=cursor.fetchall()

                return JSONResponse(
                    status_code=200,
                    #este content es un diccionario con clave valor
                    content={
                        "success": True,
                        "message": "Acudientes encontrados",
                        "data": users if users else []
                    }
                )
        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al consultar acudientes {str(e)} ",
                        "data": None
                    }
                )
        
    async def get_user_by_id(self, user_id):
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql="SELECT * FROM padre_familia WHERE id_pfamilia = %s"
                cursor.execute(sql, (user_id,))
                user=cursor.fetchone()

                if user:
                    
                    return JSONResponse(
                        status_code=200,
                        content={
                            "success": True,
                            "message": "Acudiente encontrado",
                            "data": user
                        }
                )
                else:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "success": True,
                            "message": "Acudiente no encontrado",
                            "data": None
                        }
                )

        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al consultar el acudiente {str(e)} ",
                        "data": None
                    }
                )
        
    async def create_user(self, user_data: Parent):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                dup="SELECT COUNT(*) FROM padre_familia WHERE correo = %s"
                cursor.execute(dup, (user_data.correo,))
                result=cursor.fetchone()

                if result[0] > 0:
                    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "Acudiente ya se encuentra registrado",
                            "data": None
                        }
                )

                sql='''INSERT INTO padre_familia (nombre, correo, contraseña, telefono, estado)
                VALUES ( %s, %s, %s, %s, %s)'''
                cursor.execute(sql, (user_data.nombre, user_data.correo, user_data.contraseña, user_data.telefono, user_data.estado))
                self.con.commit()

                if cursor.lastrowid:
                     
                    return JSONResponse(
                        status_code=201,
                        content={
                            "success": True,
                            "message": "Se registró el acudiente con éxito",
                            "data": {"user_id" : cursor.lastrowid}
                        }
                )
                else:    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "No se pudo registrar el acudiente",
                            "data": None
                        }
                )

        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al registrar el acudiente {str(e)} ",
                        "data": None
                    }
                )
        
    async def change_password(self, user_id: int, new_password: str):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                dup="SELECT COUNT(*) FROM padre_familia WHERE id_pfamilia = %s"
                cursor.execute(dup, (user_id,))
                result=cursor.fetchone()

                if result[0] == 0:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "El acudiente no se encuentra registrado",
                            "data": None
                        }
                )

                sql="UPDATE padre_familia SET contraseña=%s WHERE id_pfamilia=%s"
                cursor.execute(sql, (new_password, user_id))
                self.con.commit()

                if cursor.rowcount>0:
                     
                    return JSONResponse(
                        status_code=201,
                        content={
                            "success": True,
                            "message": "Se realizó la actualización del acudiente con éxito",
                            "data": {"filas afectadas" : cursor.rowcount}
                        }
                )
                else:    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "No se pudo actualizar el acudiente",
                            "data": None
                        }
                )

        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al actualizar el acudiente {str(e)} ",
                        "data": None
                    }
                )
        
    async def inactivate_user(self, user_id: int):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = "SELECT COUNT(*) FROM padre_familia WHERE id_pfamilia=%s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()
                
                if result[0] == 0: 
                    return JSONResponse(
                        content={
                            "success": False, 
                            "message": "Acudiente no encontrado."}, 
                            status_code=404)

                sql = "UPDATE padre_familia SET estado=0 WHERE id_pfamilia=%s"
                cursor.execute(sql, (user_id,))
                self.con.commit()

                if cursor.rowcount > 0:
                    return JSONResponse(content={"success": True, "message": "Acudiente inactivado exitosamente."}, status_code=200)
                else:
                    return JSONResponse(content={"success": False, "message": "No se realizaron cambios."}, status_code=400)
                
        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                content={
                    "success": False, 
                    "message": f"Error al inactivar acudiente: {str(e)}"}, 
                    status_code=500)
        
    async def toggle_user_status(self, user_id: int): #Se podría optimizar este servicio!!!!!
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = "SELECT estado FROM padre_familia WHERE id_pfamilia=%s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()

                if not result:
                    return JSONResponse(content={"success": False, "message": "Acudiente no encontrado."}, status_code=404)

                estado_actual = result[0]
                nuevo_estado = 0 if estado_actual == 1 else 1

                update_sql = "UPDATE padre_familia SET estado=%s WHERE id_pfamilia=%s"
                cursor.execute(update_sql, (nuevo_estado, user_id))
                self.con.commit()

                return JSONResponse(content={"success": True, "message": "Estado actualizado correctamente."}, status_code=200)
        except Exception as e:
            self.con.rollback()
            return JSONResponse(content={"success": False, "message": f"Error al cambiar estado: {str(e)}"}, status_code=500)
        
    async def update_user(self, user_id: int, user_data: Parent):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = "SELECT COUNT(*) FROM padre_familia WHERE id_pfamilia=%s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()

                if result[0] == 0:
                    return JSONResponse(content={"success": False, "message": "Acudiente no encontrado."}, status_code=404)

                # Actualizar campos (excepto estado)
                update_sql = """
                    UPDATE padre_familia
                    SET nombre=%s, correo=%s, contraseña=%s, telefono=%s
                    WHERE id_pfamilia=%s
                """
                cursor.execute(update_sql, (
                    user_data.nombre,
                    user_data.correo,
                    user_data.contraseña,
                    user_data.telefono,
                    user_id
                ))
                self.con.commit()

                if cursor.rowcount > 0:
                    return JSONResponse(content={"success": True, "message": "Acudiente actualizado correctamente."}, status_code=200)
                else:
                    return JSONResponse(content={"success": False, "message": "No se realizaron cambios."}, status_code=409)

        except Exception as e:
            self.con.rollback()
            return JSONResponse(content={"success": False, "message": f"Error al actualizar acudiente: {str(e)}"}, status_code=500)