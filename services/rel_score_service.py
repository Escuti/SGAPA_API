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
            os.makedirs("uploads", exist_ok=True)#Uso del OS para que se cree la carpeta donde se almacerán los archivos de la actividad
                                                #Lo optimo es cambiar este OS por una conexión con servicios cloud como AWS, pero se opta por esto temporalmente a la actual version 0.11.4 API y 0.7.0 Front
                                                
            file_path = f"uploads/{estudFK}_{file.filename}"
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())

            with self.con.cursor() as cursor:

                cursor.execute(
                    "SELECT COUNT(*) FROM rel_calificacion WHERE estudFK = %s AND actividFK = %s",
                    (estudFK, relCAL_data.actividFK)
                )
                if cursor.fetchone()[0] > 0:
                    os.remove(file_path)
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "Una entrega ya ha sido subida",
                            "data": None
                        }
                    )

                sql='''INSERT INTO rel_calificacion (estudFK, actividFK, archivo_url, comentario)
                VALUES ( %s, %s, %s, %s)'''
                cursor.execute(sql, (relCAL_data.estudFK, relCAL_data.actividFK, file_path, relCAL_data.comentario))
                self.con.commit()

                if cursor.lastrowid:
                     
                    return JSONResponse(
                        status_code=201,
                        content={
                            "success": True,
                            "message": "Entrega subida exitosamente",
                            "data": {"id_relCAL" : cursor.lastrowid}
                        }
                )
                else:    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "No se pudo subir la entrega",
                            "data": None
                        }
                )

        except Exception as e:
            self.con.rollback()
            if 'file_path' in locals():  # Elimina archivo en caso de error
                os.remove(file_path)
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al subir la entrega {str(e)} ",
                        "data": None
                    }
                )
    
    async def grade_relCAL(self, relCAL_data: Rel_Score): #Servicio que permite calificar actividades al docente
        try:
            with self.con.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) FROM rel_calificacion WHERE estudFK = %s AND actividFK = %s",
                    (relCAL_data.estudFK, relCAL_data.actividFK)
                )
                if cursor.fetchone()[0] == 0:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "success": False,
                            "message": "Entrega no encontrada",
                            "data": None
                        }
                    )

                sql = """
                UPDATE rel_calificacion 
                SET nota = %s, 
                    feedback = %s
                WHERE estudFK = %s AND actividFK = %s
                """
                cursor.execute(sql, (
                    relCAL_data.nota,
                    relCAL_data.feedback,
                    relCAL_data.estudFK,
                    relCAL_data.actividFK
                ))
                self.con.commit()

                return JSONResponse(
                    status_code=200,
                    content={
                        "success": True,
                        "message": "Calificación registrada",
                        "data": {
                            "estudiante": relCAL_data.estudFK,
                            "actividad": relCAL_data.actividFK
                        }
                    }
                )

        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "message": f"Error al calificar: {str(e)}",
                    "data": None
                }
            )