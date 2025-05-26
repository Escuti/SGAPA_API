from fastapi.responses import JSONResponse
import pymysql
import pymysql.cursors
from db.db_mysql import get_db_connection
from models.subadmin_model import SubAdmin

class SubAdmin_Service:
    def __init__(self):
        self.con=get_db_connection()
        if self.con is None:
            print("No se ha podido establecer conexión con la BD")

    async def get_users(self):
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM sub_admin")
                users=cursor.fetchall()

                return JSONResponse(
                    status_code=200,
                    #este content es un diccionario con clave valor
                    content={
                        "success": True,
                        "message": "Subadministradores encontrados",
                        "data": users if users else []
                    }
                )
        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al consultar subadministradores {str(e)} ",
                        "data": None
                    }
                )
        
    async def get_user_by_id(self, user_id):
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql="SELECT * FROM sub_admin WHERE id_sadmin = %s"
                cursor.execute(sql, (user_id,))
                user=cursor.fetchone()

                if user:
                    return JSONResponse(
                        status_code=200,
                        content={
                            "success": True,
                            "message": "Subadministrador encontrado",
                            "data": user
                        }
                )
                else:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "success": True,
                            "message": "Subadministrador no encontrado",
                            "data": None
                        }
                )

        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al consultar el subadministrador {str(e)} ",
                        "data": None
                    }
                )
        
    async def create_user(self, user_data: SubAdmin):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                dup="SELECT COUNT(*) FROM sub_admin WHERE correo = %s"
                cursor.execute(dup, (user_data.correo,))
                result=cursor.fetchone()

                if result[0] > 0:
                    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "Subadministrador ya se encuentra registrado",
                            "data": None
                        }
                )

                sql='''INSERT INTO sub_admin (usuario, contraseña, correo, telefono, id_admin, estado)
                VALUES ( %s, %s, %s, %s, %s, %s)'''
                cursor.execute(sql, (user_data.usuario, user_data.contraseña, user_data.correo, user_data.telefono, user_data.id_admin, user_data.estado))
                self.con.commit()

                if cursor.lastrowid:
                     
                    return JSONResponse(
                        status_code=201,
                        content={
                            "success": True,
                            "message": "Se registró el subadministrador con éxito",
                            "data": {"user_id" : cursor.lastrowid}
                        }
                )
                else:    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "No se pudo registrar el subadministrador",
                            "data": None
                        }
                )

        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al registrar el subadministrador {str(e)} ",
                        "data": None
                    }
                )
        
    async def change_password(self, user_id: int, new_password: str):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                dup="SELECT COUNT(*) FROM sub_admin WHERE id_sadmin = %s"
                cursor.execute(dup, (user_id,))
                result=cursor.fetchone()

                if result[0] == 0:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "El subadministrador no se encuentra registrado",
                            "data": None
                        }
                )

                sql="UPDATE sub_admin SET contraseña=%s WHERE id_sadmin=%s"
                cursor.execute(sql, (new_password, user_id))
                self.con.commit()

                if cursor.rowcount>0:
                     
                    return JSONResponse(
                        status_code=201,
                        content={
                            "success": True,
                            "message": "Se realizó la actualización del subadministrador con éxito",
                            "data": {"filas afectadas" : cursor.rowcount}
                        }
                )
                else:    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "No se pudo actualizar el subadministrador",
                            "data": None
                        }
                )

        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al actualizar el subadministrador {str(e)} ",
                        "data": None
                    }
                )
        
    async def inactivate_user(self, user_id: int):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = "SELECT COUNT(*) FROM sub_admin WHERE id_sadmin=%s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()
                
                if result[0] == 0: 
                    return JSONResponse(
                        content={
                            "success": False, 
                            "message": "Subadministrador no encontrado."}, 
                            status_code=404)

                sql = "UPDATE sub_admin SET estado=0 WHERE id_sadmin=%s"
                cursor.execute(sql, (user_id,))
                self.con.commit()

                if cursor.rowcount > 0:
                    return JSONResponse(content={"success": True, "message": "Subadministrador inactivado exitosamente."}, status_code=200)
                else:
                    return JSONResponse(content={"success": False, "message": "No se realizaron cambios."}, status_code=400)
                
        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                content={
                    "success": False, 
                    "message": f"Error al inactivar subadministrador: {str(e)}"}, 
                    status_code=500)
        
    async def toggle_user_status(self, user_id: int): #Se podría optimizar este servicio!!!!!
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = "SELECT estado FROM sub_admin WHERE id_sadmin=%s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()

                if not result:
                    return JSONResponse(content={"success": False, "message": "Subadministrador no encontrado."}, status_code=404)

                estado_actual = result[0]
                nuevo_estado = 0 if estado_actual == 1 else 1

                update_sql = "UPDATE sub_admin SET estado=%s WHERE id_sadmin=%s"
                cursor.execute(update_sql, (nuevo_estado, user_id))
                self.con.commit()

                return JSONResponse(content={"success": True, "message": "Estado actualizado correctamente."}, status_code=200)
        except Exception as e:
            self.con.rollback()
            return JSONResponse(content={"success": False, "message": f"Error al cambiar estado: {str(e)}"}, status_code=500)
        
    async def update_user(self, user_id: int, user_data: SubAdmin):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = "SELECT COUNT(*) FROM sub_admin WHERE id_sadmin=%s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()

                if result[0] == 0:
                    return JSONResponse(content={"success": False, "message": "Subadministrador no encontrado."}, status_code=404)

                # Actualizar campos (excepto estado)
                update_sql = """
                    UPDATE sub_admin
                    SET usuario=%s, contraseña=%s, correo=%s, telefono=%s, id_admin=%s
                    WHERE id_sadmin=%s
                """
                cursor.execute(update_sql, (
                    user_data.contraseña,
                    user_data.correo,
                    user_data.telefono,
                    user_id
                ))
                self.con.commit()

                if cursor.rowcount > 0:
                    return JSONResponse(content={"success": True, "message": "Subadministrador actualizado correctamente."}, status_code=200)
                else:
                    return JSONResponse(content={"success": False, "message": "No se realizaron cambios."}, status_code=409)

        except Exception as e:
            self.con.rollback()
            return JSONResponse(content={"success": False, "message": f"Error al actualizar subadministrador: {str(e)}"}, status_code=500)