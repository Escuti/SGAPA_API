from fastapi.responses import JSONResponse
import pymysql
import pymysql.cursors
from db.db_mysql import get_db_connection
from models.student_model import Student
#importamos todo lo que hemos creado anteriormente, tanto el método de conexión de db como el modelo se usuario

class StudentService:
    def __init__(self):
        self.con=get_db_connection()
        if self.con is None:
            print("No se ha podido establecer conexión con la BD")

    #función asíncrona, o también función que se ejecuta debajo de otras funciones sin interrumpir el proceso de estas
    async def get_users(self):

        '''consulta de los usuarios de la tabla usuario'''
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM estudiante")
                users=cursor.fetchall()

                return JSONResponse(
                    status_code=200,
                    #este content es un diccionario con clave valor
                    content={
                        "success": True,
                        "message": "Estudiantes encontrados",
                        "data": users if users else []
                    }
                )
        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al consultar estudiantes {str(e)} ",
                        "data": None
                    }
                )
        
    async def get_user_by_id(self, user_id):
        '''consulta de los estudiantes de la tabla estudiante por su id'''
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql="SELECT * FROM estudiante WHERE id_estud = %s"
                cursor.execute(sql, (user_id,)) #finaliza el parámetro con , debido a que es una tupla
                user=cursor.fetchone()

                if user:
                    
                    return JSONResponse(
                        status_code=200,
                        #este content es un diccionario con clave valor
                        content={
                            "success": True,
                            "message": "Estudiante encontrado",
                            "data": user
                        }
                )
                else:
                    return JSONResponse(
                        status_code=404,
                        #este content es un diccionario con clave valor
                        content={
                            "success": True,
                            "message": "Estudiante no encontrado",
                            "data": None
                        }
                )

        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al consultar el estudiante {str(e)} ",
                        "data": None
                    }
                )
        
    async def create_user(self, user_data: Student):
        '''crea estudiantes nuevos'''
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                dup="SELECT COUNT(*) FROM estudiante WHERE correo = %s" #Esta sentencia SQL daba error debido a que el (*) estaba separado del COUNT y debe ir junto
                cursor.execute(dup, (user_data.correo,)) #finaliza el parámetro con , debido a que es una tupla
                result=cursor.fetchone()

                if result[0] > 0:
                    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "Estudiante ya se encuentra registrado",
                            "data": None
                        }
                )

                sql='''INSERT INTO estudiante (nombre, usuario, contraseña, correo, telefono, id_grupo, id_pfamilia, estado)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
                cursor.execute(sql, (user_data.nombre, user_data.usuario, user_data.contraseña, user_data.correo, user_data.telefono, user_data.id_grupo, user_data.id_pfamilia, user_data.estado))
                self.con.commit() # ES NECESARIO QUE LA CREACIÓN DE USUARIO INCLUYA QUÉ ROL TIENE ESTE USUARIO, AGREGAR TABLA EN BD Y EN COMODINES DE SENTENCIA SQL

                if cursor.lastrowid:
                     
                    return JSONResponse(
                        status_code=201,
                        content={
                            "success": True,
                            "message": "Se registró el estudiante con éxito",
                            "data": {"user_id" : cursor.lastrowid}
                        }
                )
                else:    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "No se pudo registrar el estudiante",
                            "data": None
                        }
                )

        except Exception as e:
            self.con.rollback() #rollback es el opuesto del commit, por lo que en lugar de enviar la info, la detiene
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al registrar el estudiante {str(e)} ",
                        "data": None
                    }
                )
        
    async def change_password(self, user_id: int, new_password: str):
        '''cambia la contraseña'''
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                dup="SELECT COUNT(*) FROM estudiante WHERE id_estud = %s"
                cursor.execute(dup, (user_id,))
                result=cursor.fetchone()

                if result[0] == 0: #result es la variable que almacena el registro en el método, y que nos permite saber si este existe o no para ejecutar condiciones
                    #si result es igual a 0, entonces no existe, si es igual a 1, entonces sí
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "El estudiante no se encuentra registrado",
                            "data": None
                        }
                )

                sql="UPDATE estudiante SET contraseña=%s WHERE id_estud=%s"
                cursor.execute(sql, (new_password, user_id))
                self.con.commit()

                if cursor.rowcount>0:
                     
                    return JSONResponse(
                        status_code=201,
                        content={
                            "success": True,
                            "message": "Se realizó la actualización del estudiante con éxito",
                            "data": {"filas afectadas" : cursor.rowcount}
                        }
                )
                else:    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "No se pudo actualizar el estudiante",
                            "data": None
                        }
                )

        except Exception as e:
            self.con.rollback() #rollback es el opuesto del commit, por lo que en lugar de enviar la info, la detiene
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al actualizar el estudiante {str(e)} ",
                        "data": None
                    }
                )
        
    async def inactivate_user(self, user_id: int):
        """Inactiva un usuario cambiando su estado a 0 y retorna JSONResponse."""
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                # Verificar si el usuario existe
                sql = "SELECT COUNT(*) FROM estudiante WHERE id_estud=%s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()
                
                if result[0] == 0:  # Si el usuario no existe
                    return JSONResponse(
                        content={
                            "success": False, 
                            "message": "Estudiante no encontrado."}, 
                            status_code=404)

                # Inactivar usuario
                sql = "UPDATE estudiante SET estado=0 WHERE id_estud=%s"
                cursor.execute(sql, (user_id,))
                self.con.commit()  # Confirmar la transacción

                if cursor.rowcount > 0:
                    return JSONResponse(content={"success": True, "message": "Estudiante inactivado exitosamente."}, status_code=200)
                else:
                    return JSONResponse(content={"success": False, "message": "No se realizaron cambios."}, status_code=400)
        except Exception as e:
            self.con.rollback()  # Deshacer la transacción
            return JSONResponse(
                content={
                    "success": False, 
                    "message": f"Error al inactivar estudiante: {str(e)}"}, 
                    status_code=500)
        
    async def toggle_user_status(self, user_id: int): #Se podría optimizar este servicio!!!!!
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                # Obtener estado actual
                sql = "SELECT estado FROM estudiante WHERE id_estud=%s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()

                if not result:
                    return JSONResponse(content={"success": False, "message": "Estudiante no encontrado."}, status_code=404)

                estado_actual = result[0]
                nuevo_estado = 0 if estado_actual == 1 else 1

                update_sql = "UPDATE estudiante SET estado=%s WHERE id_estud=%s"
                cursor.execute(update_sql, (nuevo_estado, user_id))
                self.con.commit()

                return JSONResponse(content={"success": True, "message": "Estado actualizado correctamente."}, status_code=200)
        except Exception as e:
            self.con.rollback()
            return JSONResponse(content={"success": False, "message": f"Error al cambiar estado: {str(e)}"}, status_code=500)
        
    async def update_user(self, user_id: int, user_data: Student):
        """
        Actualiza los datos de un usuario excepto el campo 'estado'.
        """
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                # Verificar si el usuario existe
                sql = "SELECT COUNT(*) FROM estudiante WHERE id_estud=%s"
                cursor.execute(sql, (user_id,))
                result = cursor.fetchone()

                if result[0] == 0:
                    return JSONResponse(content={"success": False, "message": "Estudiante no encontrado."}, status_code=404)

                # Actualizar campos (excepto estado)
                update_sql = """
                    UPDATE estudiante
                    SET nombre=%s, usuario=%s, contraseña=%s, correo=%s, telefono=%s, id_grupo=%s, id_pfamilia=%s
                    WHERE id_estud=%s
                """
                cursor.execute(update_sql, (
                    user_data.nombre,
                    user_data.usuario,
                    user_data.contraseña,
                    user_data.correo,
                    user_data.telefono,
                    user_data.id_grupo,
                    user_data.id_pfamilia,
                    user_id
                ))
                self.con.commit()

                if cursor.rowcount > 0:
                    return JSONResponse(content={"success": True, "message": "Estudiante actualizado correctamente."}, status_code=200)
                else:
                    return JSONResponse(content={"success": False, "message": "No se realizaron cambios."}, status_code=409)

        except Exception as e:
            self.con.rollback()
            return JSONResponse(content={"success": False, "message": f"Error al actualizar estudiante: {str(e)}"}, status_code=500)