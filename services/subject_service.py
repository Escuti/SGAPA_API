from fastapi.responses import JSONResponse
import pymysql
import pymysql.cursors
from db.db_mysql import get_db_connection
from models.subject_model import Subject

class Subject_Service:
    def __init__(self):
        self.con=get_db_connection()
        if self.con is None:
            print("No se ha podido establecer conexión con la BD")

    async def get_subjects(self):
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM materias")
                subjects=cursor.fetchall()

                return JSONResponse(
                    status_code=200,
                    #este content es un diccionario con clave valor
                    content={
                        "success": True,
                        "message": "Materias desplegadas",
                        "data": subjects if subjects else []
                    }
                )
        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al desplegar materias {str(e)} ",
                        "data": None
                    }
                )
        
    async def get_subject_by_id(self, subject_id):
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql="SELECT * FROM materias WHERE id_materia = %s"
                cursor.execute(sql, (subject_id,))
                subject=cursor.fetchone()

                if subject:
                    return JSONResponse(
                        status_code=200,
                        content={
                            "success": True,
                            "message": "Materia desplegada",
                            "data": subject
                        }
                )
                else:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "success": True,
                            "message": "Materia no encontrada",
                            "data": None
                        }
                )

        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al desplegar la materia {str(e)} ",
                        "data": None
                    }
                )
        
    async def create_subject(self, subject_data: Subject):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                dup="SELECT COUNT(*) FROM materias WHERE nombremat = %s"
                cursor.execute(dup, (subject_data.nombremat,))
                result=cursor.fetchone()

                if result[0] > 0:
                    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "La materia ya existe",
                            "data": None
                        }
                )

                sql='''INSERT INTO materias (nombremat)
                VALUES ( %s)'''
                cursor.execute(sql, (subject_data.nombremat))
                self.con.commit()

                if cursor.lastrowid:
                     
                    return JSONResponse(
                        status_code=201,
                        content={
                            "success": True,
                            "message": "Se ha creado la materia con éxito",
                            "data": {"subject_id" : cursor.lastrowid}
                        }
                )
                else:    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "No se pudo crear la materia",
                            "data": None
                        }
                )

        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al crear la materia {str(e)} ",
                        "data": None
                    }
                )
    
    async def update_subject(self, subject_id: int, subject_data: Subject):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = "SELECT COUNT(*) FROM materias WHERE id_materia=%s"
                cursor.execute(sql, (subject_id,))
                result = cursor.fetchone()

                if result[0] == 0:
                    return JSONResponse(content={"success": False, "message": "Materia no encontrada."}, status_code=404)

                # Actualizar campos (excepto estado)
                update_sql = """
                    UPDATE materias
                    SET nombremat=%s
                    WHERE id_materia=%s
                """
                cursor.execute(update_sql, (
                    subject_data.nombremat,
                    subject_id
                ))
                self.con.commit()

                if cursor.rowcount > 0:
                    return JSONResponse(content={"success": True, "message": "Materia actualizada correctamente."}, status_code=200)
                else:
                    return JSONResponse(content={"success": False, "message": "No se realizaron cambios."}, status_code=409)

        except Exception as e:
            self.con.rollback()
            return JSONResponse(content={"success": False, "message": f"Error al actualizar la materia: {str(e)}"}, status_code=500)