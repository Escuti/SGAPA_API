from fastapi.responses import JSONResponse
import pymysql
import pymysql.cursors
from db.db_mysql import get_db_connection
from models.rel_group_subject_model import Rel_Group_Subject

class Rel_Group_Subject_Service:
    def __init__(self):
        self.con=get_db_connection()
        if self.con is None:
            print("No se ha podido establecer conexión con la BD")

    async def get_relGS(self):
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM rel_grupo_materia")
                relGS=cursor.fetchall()

                return JSONResponse(
                    status_code=200,
                    #este content es un diccionario con clave valor
                    content={
                        "success": True,
                        "message": "Relaciones desplegadas",
                        "data": relGS if relGS else []
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
        
    async def get_relGS_by_id(self, id_relGS):
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql="SELECT * FROM rel_grupo_materia WHERE id_relGS = %s"
                cursor.execute(sql, (id_relGS,))
                relGS=cursor.fetchone()

                if relGS:
                    return JSONResponse(
                        status_code=200,
                        content={
                            "success": True,
                            "message": "Relaciones desplegadas",
                            "data": relGS
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
        
    async def create_relGS(self, relGS_data: Rel_Group_Subject):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                dup="SELECT COUNT(*) FROM rel_grupo_materia WHERE materiaFK = %s"
                cursor.execute(dup, (relGS_data.materiaFK,))
                result=cursor.fetchone()

                if result[0] > 0:
                    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "La relación ya existe",
                            "data": None
                        }
                )

                sql='''INSERT INTO rel_grupo_materia (grupoFK, materiaFK)
                VALUES ( %s, %s)'''
                cursor.execute(sql, (relGS_data.grupoFK, relGS_data.materiaFK))
                self.con.commit()

                if cursor.lastrowid:
                     
                    return JSONResponse(
                        status_code=201,
                        content={
                            "success": True,
                            "message": "Se ha creado la relación con éxito",
                            "data": {"id_relGS" : cursor.lastrowid}
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
    
    async def update_relGS(self, id_relGS: int, relGS_data: Rel_Group_Subject):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = "SELECT COUNT(*) FROM rel_grupo_materia WHERE id_relGS=%s"
                cursor.execute(sql, (id_relGS,))
                result = cursor.fetchone()

                if result[0] == 0:
                    return JSONResponse(content={"success": False, "message": "Relación no encontrada."}, status_code=404)

                # Actualizar campos (excepto estado)
                update_sql = """
                    UPDATE rel_grupo_materia
                    SET grupoFK=%s, materiaFK=%s
                    WHERE id_relGS=%s
                """
                cursor.execute(update_sql, (
                    relGS_data.grupoFK, relGS_data.materiaFK,
                    id_relGS
                ))
                self.con.commit()

                if cursor.rowcount > 0:
                    return JSONResponse(content={"success": True, "message": "Relación actualizada correctamente."}, status_code=200)
                else:
                    return JSONResponse(content={"success": False, "message": "No se realizaron cambios."}, status_code=409)

        except Exception as e:
            self.con.rollback()
            return JSONResponse(content={"success": False, "message": f"Error al actualizar la relación: {str(e)}"}, status_code=500)