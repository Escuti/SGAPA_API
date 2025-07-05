from fastapi.responses import JSONResponse
import pymysql
import pymysql.cursors
from fastapi.encoders import jsonable_encoder
from db.db_mysql import get_db_connection
from models.assignment_model import Assignment

class Assignment_Service:
    def __init__(self):
        self.con=get_db_connection()
        if self.con is None:
            print("No se ha podido establecer conexión con la BD")

    async def get_assignments(self):
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM actividades")
                assignments=cursor.fetchall()

                return JSONResponse(
                    status_code=200,
                    #este content es un diccionario con clave valor
                    content={
                        "success": True,
                        "message": "actividades desplegadas",
                        "data": jsonable_encoder(assignments) if assignments else [] #el jsonable_encoder permite convertir el datetime a string
                    }
                )
        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al desplegar actividades {str(e)} ",
                        "data": None
                    }
                )
        
    async def get_assignment_by_id(self, assignment_id):
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql="SELECT * FROM actividades WHERE id_activid = %s"
                cursor.execute(sql, (assignment_id,))
                assignment=cursor.fetchone()

                if assignment:
                    return JSONResponse(
                        status_code=200,
                        content={
                            "success": True,
                            "message": "Actividad desplegada",
                            "data": assignment
                        }
                )
                else:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "success": True,
                            "message": "Actividad no encontrada",
                            "data": None
                        }
                )

        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al desplegar la actividad {str(e)} ",
                        "data": None
                    }
                )
        
    async def create_assignment(self, assignment_data: Assignment):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                dup="SELECT COUNT(*) FROM actividades WHERE titulo = %s"
                cursor.execute(dup, (assignment_data.titulo,))
                result=cursor.fetchone()

                if result[0] > 0:
                    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "La actividad ya existe",
                            "data": None
                        }
                )

                sql='''INSERT INTO actividades (titulo, descripcion, fecha, grupo, materias)
                VALUES ( %s, %s, %s, %s, %s)'''
                cursor.execute(sql, (assignment_data.titulo, assignment_data.descripcion, assignment_data.fecha, assignment_data.grupo, assignment_data.materias))
                self.con.commit()

                if cursor.lastrowid:
                     
                    return JSONResponse(
                        status_code=201,
                        content={
                            "success": True,
                            "message": "Se ha creado la actividad con éxito",
                            "data": {"assignment_id" : cursor.lastrowid}
                        }
                )
                else:    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "No se pudo crear la actividad",
                            "data": None
                        }
                )

        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al crear el actividad {str(e)} ",
                        "data": None
                    }
                )
    
    async def update_assignment(self, assignment_id: int, assignment_data: Assignment):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = "SELECT COUNT(*) FROM actividades WHERE id_activid=%s"
                cursor.execute(sql, (assignment_id,))
                result = cursor.fetchone()

                if result[0] == 0:
                    return JSONResponse(content={"success": False, "message": "Actividad no encontrada."}, status_code=404)

                # Actualizar campos (excepto estado)
                update_sql = """
                    UPDATE actividades
                    SET titulo=%s, descripcion=%s, fecha=%s, grupo=%s, materias=%s
                    WHERE id_activid=%s
                """
                cursor.execute(update_sql, (
                    assignment_data.titulo,
                    assignment_data.descripcion,
                    assignment_data.fecha,
                    assignment_data.grupo,
                    assignment_data.materias,
                    assignment_id
                ))
                self.con.commit()

                if cursor.rowcount > 0:
                    return JSONResponse(content={"success": True, "message": "Actividad actualizada correctamente."}, status_code=200)
                else:
                    return JSONResponse(content={"success": False, "message": "No se realizaron cambios."}, status_code=409)

        except Exception as e:
            self.con.rollback()
            return JSONResponse(content={"success": False, "message": f"Error al actualizar la actividad: {str(e)}"}, status_code=500)