from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import pymysql
import pymysql.cursors
from db.db_mysql import get_db_connection
from models.rel_score_model import Rel_Score

class Rel_Score_Service:
    def __init__(self):
        self.con=get_db_connection()
        if self.con is None:
            print("No se ha podido establecer conexión con la BD")

    async def get_relCAL(self):
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM rel_calificacion")
                relCAL=cursor.fetchall()

                return JSONResponse(
                    status_code=200,
                    #este content es un diccionario con clave valor
                    content={
                        "success": True,
                        "message": "Relaciones desplegadas",
                        "data": jsonable_encoder(relCAL) if relCAL else []
                    }
                )
        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al desplegar relaciones {str(e)} ",
                        "data": None
                    }
                )
        
    async def get_relCAL_by_id(self, id_relCAL):
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql="SELECT * FROM rel_calificacion WHERE id_relCAL = %s"
                cursor.execute(sql, (id_relCAL,))
                relCAL=cursor.fetchone()

                if relCAL:
                    return JSONResponse(
                        status_code=200,
                        content={
                            "success": True,
                            "message": "Relaciones desplegadas",
                            "data": relCAL
                        }
                )
                else:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "success": True,
                            "message": "Relaciones no encontradas",
                            "data": None
                        }
                )

        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al desplegar las relaciones {str(e)} ",
                        "data": None
                    }
                )
        
    async def create_relCAL(self, relCAL_data: Rel_Score):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                '''dup="SELECT COUNT(*) FROM rel_calificacion WHERE nota = %s"
                cursor.execute(dup, (relCAL_data.nota,))
                result=cursor.fetchone()

                if result[0] > 0:
                    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "La relación ya existe",
                            "data": None
                        }
                )''' #Se comenta porque no es necesario verificar si hay duplicado en calificaciones

                sql='''INSERT INTO rel_calificacion (estudFK, actividFK, nota)
                VALUES ( %s, %s, %s)'''
                cursor.execute(sql, (relCAL_data.estudFK, relCAL_data.actividFK, relCAL_data.nota))
                self.con.commit()

                if cursor.lastrowid:
                     
                    return JSONResponse(
                        status_code=201,
                        content={
                            "success": True,
                            "message": "Se ha creado la relación con éxito",
                            "data": {"id_relCAL" : cursor.lastrowid}
                        }
                )
                else:    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "No se pudo crear la relación",
                            "data": None
                        }
                )

        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al crear la relación {str(e)} ",
                        "data": None
                    }
                )
    
    async def update_relCAL(self, id_relCAL: int, relCAL_data: Rel_Score):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = "SELECT COUNT(*) FROM rel_calificacion WHERE id_relCAL=%s"
                cursor.execute(sql, (id_relCAL,))
                result = cursor.fetchone()

                if result[0] == 0:
                    return JSONResponse(content={"success": False, "message": "Relación no encontrada."}, status_code=404)

                # Actualizar campos (excepto estado)
                update_sql = """
                    UPDATE rel_calificaciones
                    SET estudFK=%s, actividFK=%s, nota=%s
                    WHERE id_relCAL=%s
                """
                cursor.execute(update_sql, (
                    relCAL_data.estudFK, relCAL_data.actividFK, relCAL_data.nota,
                    id_relCAL
                ))
                self.con.commit()

                if cursor.rowcount > 0:
                    return JSONResponse(content={"success": True, "message": "Relación actualizada correctamente."}, status_code=200)
                else:
                    return JSONResponse(content={"success": False, "message": "No se realizaron cambios."}, status_code=409)

        except Exception as e:
            self.con.rollback()
            return JSONResponse(content={"success": False, "message": f"Error al actualizar la relación: {str(e)}"}, status_code=500)