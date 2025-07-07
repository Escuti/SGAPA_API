from passlib.hash import bcrypt
from fastapi.responses import JSONResponse
import pymysql
import pymysql.cursors
from db.db_mysql import get_db_connection
from models.adminPR_model import AdminPR

class AdminPR_Service:
    def __init__(self):
        self.con=get_db_connection()
        if self.con is None:
            print("No se ha podido establecer conexión con la BD")

    async def get_users(self):

        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM admin_pr")
                users=cursor.fetchall()

                return JSONResponse(
                    status_code=200,
                    #este content es un diccionario con clave valor
                    content={
                        "success": True,
                        "message": "Administradores encontrados",
                        "data": users if users else []
                    }
                )
        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al consultar administradores {str(e)} ",
                        "data": None
                    }
                )
        
    async def get_user_by_id(self, user_id):
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql="SELECT * FROM admin_pr WHERE id_admin = %s"
                cursor.execute(sql, (user_id,))
                user=cursor.fetchone()

                if user:
                    
                    return JSONResponse(
                        status_code=200,
                        content={
                            "success": True,
                            "message": "Administrador encontrado",
                            "data": user
                        }
                )
                else:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "success": True,
                            "message": "Administrador no encontrado",
                            "data": None
                        }
                )

        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al consultar el administrador {str(e)} ",
                        "data": None
                    }
                )
        
    async def create_user(self, user_data: AdminPR):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                dup="SELECT COUNT(*) FROM admin_pr WHERE correo = %s"
                cursor.execute(dup, (user_data.correo,))
                result=cursor.fetchone()

                if result[0] > 0:
                    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "Administrador ya se encuentra registrado",
                            "data": None
                        }
                )

                #Proceso de encriptación automática de contraseña, cada vez que se crea un registro nuevo.
                password_hash = bcrypt.hash(user_data.contraseña)

                insert_log = '''
                INSERT INTO usuarioslog (username, email, password_hash, tipo_usuario)
                VALUES (%s, %s, %s, %s)''' #Se incluye tanto correo como contraseña en el insert a usuarioslog

                cursor.execute(insert_log, (user_data.usuario, user_data.correo, password_hash, "administrador"))
                id_userlog = cursor.lastrowid

                sql='''INSERT INTO admin_pr (usuario, contraseña, correo, telefono, estado, adminlogFK)
                VALUES (%s, %s, %s, %s, %s, %s)'''
                cursor.execute(sql, (user_data.usuario, user_data.contraseña, user_data.correo, user_data.telefono, user_data.estado, id_userlog))
                self.con.commit()

                if cursor.lastrowid:
                     
                    return JSONResponse(
                        status_code=201,
                        content={
                            "success": True,
                            "message": "Se registró el administrador con éxito",
                            "data": {"user_id" : cursor.lastrowid}
                        }
                )
                else:    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "No se pudo registrar el administrador",
                            "data": None
                        }
                )

        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al registrar el administrador {str(e)} ",
                        "data": None
                    }
                )
        
    async def change_password(self, user_id: int, new_password: str):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                dup="SELECT COUNT(*) FROM admin_pr WHERE id_admin = %s"
                cursor.execute(dup, (user_id,))
                result=cursor.fetchone()

                if result[0] == 0:
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "El administrador no se encuentra registrado",
                            "data": None
                        }
                )

                sql="UPDATE admin_pr SET contraseña=%s WHERE id_admin=%s"
                cursor.execute(sql, (new_password, user_id))
                self.con.commit()

                if cursor.rowcount>0:
                     
                    return JSONResponse(
                        status_code=201,
                        content={
                            "success": True,
                            "message": "Se realizó la actualización del administrador con éxito",
                            "data": {"filas afectadas" : cursor.rowcount}
                        }
                )
                else:    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "No se pudo actualizar el administrador",
                            "data": None
                        }
                )

        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al actualizar el administrador {str(e)} ",
                        "data": None
                    }
                )
        
    async def inactivate_user(self, user_id: int):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = "SELECT COUNT(*) FROM admin_pr WHERE id_admin=%s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()
                
                if result[0] == 0: 
                    return JSONResponse(
                        content={
                            "success": False, 
                            "message": "Administrador no encontrado."}, 
                            status_code=404)

                sql = "UPDATE admin_pr SET estado=0 WHERE id_admin=%s"
                cursor.execute(sql, (user_id,))
                self.con.commit()

                if cursor.rowcount > 0:
                    return JSONResponse(content={"success": True, "message": "Administrador inactivado exitosamente."}, status_code=200)
                else:
                    return JSONResponse(content={"success": False, "message": "No se realizaron cambios."}, status_code=400)
                
        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                content={
                    "success": False, 
                    "message": f"Error al inactivar administrador: {str(e)}"}, 
                    status_code=500)
        
    async def toggle_user_status(self, user_id: int): #Se podría optimizar este servicio!!!!!
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = "SELECT estado FROM admin_pr WHERE id_admin=%s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()

                if not result:
                    return JSONResponse(content={"success": False, "message": "Administrador no encontrado."}, status_code=404)

                estado_actual = result[0]
                nuevo_estado = 0 if estado_actual == 1 else 1

                update_sql = "UPDATE admin_pr SET estado=%s WHERE id_admin=%s"
                cursor.execute(update_sql, (nuevo_estado, user_id))
                self.con.commit()

                return JSONResponse(content={"success": True, "message": "Estado actualizado correctamente."}, status_code=200)
        except Exception as e:
            self.con.rollback()
            return JSONResponse(content={"success": False, "message": f"Error al cambiar estado: {str(e)}"}, status_code=500)
        
    async def update_user(self, user_id: int, user_data: AdminPR):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = "SELECT COUNT(*) FROM admin_pr WHERE id_admin=%s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()

                if result[0] == 0:
                    return JSONResponse(content={"success": False, "message": "Administrador no encontrado."}, status_code=404)

                # Actualizar campos (excepto estado)
                update_sql = """
                    UPDATE admin_pr
                    SET usuario=%s, contraseña=%s, correo=%s, telefono=%s
                    WHERE id_admin=%s
                """
                cursor.execute(update_sql, (
                    user_data.usuario,
                    user_data.contraseña,
                    user_data.correo,
                    user_data.telefono,
                    user_id
                ))
                #Re-formateamos contraseña ingresada en update
                password_hash = bcrypt.hash(user_data.contraseña)

                update_log = '''
                UPDATE usuarioslog SET username=%s, password_hash=%s
                WHERE id_userlog = (
                SELECT adminlogFK FROM admin_PR WHERE id_admin = %s)
                '''  #Actualización de credenciales desde update

                cursor.execute(update_log, (
                    user_data.usuario,
                    password_hash,
                    user_id
                ))

                self.con.commit()

                if cursor.rowcount > 0:
                    return JSONResponse(content={"success": True, "message": "Administrador actualizado correctamente."}, status_code=200)
                else:
                    return JSONResponse(content={"success": False, "message": "No se realizaron cambios."}, status_code=409)

        except Exception as e:
            self.con.rollback()
            return JSONResponse(content={"success": False, "message": f"Error al actualizar administrador: {str(e)}"}, status_code=500)