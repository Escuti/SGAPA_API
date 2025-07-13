from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
import pymysql
import pymysql.cursors
from db.db_mysql import get_db_connection
from models.rel_score_model import Rel_Score
from fastapi import UploadFile
import os

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
                        "message": "Entregas desplegadas",
                        "data": jsonable_encoder(relCAL) if relCAL else []
                    }
                )
        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al desplegar entregas {str(e)} ",
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
        
    async def upload_relCAL(self, file: UploadFile, relCAL_data: Rel_Score, estudFK: int): #Servicio que permite subir actividades al estudiante

        try:
            self.con.ping(reconnect=True)
            os.makedirs("uploads", exist_ok=True)
            file_path = f"uploads/{estudFK}_{file.filename}"

            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())

            with self.con.cursor() as cursor:
                cursor.execute(
                    "SELECT id_relCAL FROM rel_calificacion WHERE actividFK = %s",
                    (relCAL_data.actividFK)
                )
                relCAL = cursor.fetchone()

                if not relCAL:
                    return JSONResponse(
                        status_code=404,
                        content={"success": False, "message": "Entrega no encontrada"}
                    )

                sql = '''
                    UPDATE rel_calificacion
                    SET estudFK = %s, archivo_url = %s, comentario = %s
                    WHERE id_relCAL = %s
                '''
                cursor.execute(sql, (
                    estudFK,
                    file_path,
                    relCAL_data.comentario,
                    relCAL[0]  
                ))
                self.con.commit()

                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "Entrega actualizada",
                        "data": {"id_relCAL": relCAL[0]}
                    }
                )
        except Exception as e:
            self.con.rollback()
            if 'file_path' in locals():
                os.remove(file_path)
            return JSONResponse(
                status_code=500,
                content={"success": False, "message": f"Error: {str(e)}"}
            )
    
    async def grade_relCAL(self, relCAL_data: Rel_Score): #Servicio que permite calificar actividades al docente
        try:
            with self.con.cursor() as cursor:
                cursor.execute(
                    "SELECT id_relCAL FROM rel_calificacion WHERE actividFK = %s",
                    (relCAL_data.actividFK)
                )
                relCAL = cursor.fetchone()
                
                if not relCAL:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "success": False,
                            "message": "Entrega no encontrada",
                            "data": None
                        }
                    )

                #Actualizar solo nota y feedback ignorando campos innecasarios del modelo
                sql = """
                UPDATE rel_calificacion 
                SET nota = %s, 
                    feedback = %s
                WHERE id_relCAL = %s
                """
                cursor.execute(sql, (
                    relCAL_data.nota,   
                    relCAL_data.feedback,
                    relCAL[0]  
                ))
                self.con.commit()

                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "Calificación registrada",
                        "data": {
                            "id_relCAL": relCAL[0],
                            "actividad": relCAL_data.actividFK
                        }
                    }
                )

        except Exception as e:
            self.con.rollback()
            import logging
            logging.error(f"Error en grade_relCAL: {str(e)}")
            
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": "Error interno al procesar la calificación",
                    "data": None
                }
            )