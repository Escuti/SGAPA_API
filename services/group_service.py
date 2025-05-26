from fastapi.responses import JSONResponse
import pymysql
import pymysql.cursors
from db.db_mysql import get_db_connection
from models.group_model import Group

class Group_Service:
    def __init__(self):
        self.con=get_db_connection()
        if self.con is None:
            print("No se ha podido establecer conexión con la BD")

    async def get_groups(self):
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT * FROM grupo")
                groups=cursor.fetchall()

                return JSONResponse(
                    status_code=200,
                    #este content es un diccionario con clave valor
                    content={
                        "success": True,
                        "message": "Grupos desplegados",
                        "data": groups if groups else []
                    }
                )
        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al desplegar grupos {str(e)} ",
                        "data": None
                    }
                )
        
    async def get_group_by_id(self, group_id):
        try:
            with self.con.cursor(pymysql.cursors.DictCursor) as cursor:
                sql="SELECT * FROM grupo WHERE id_grupo = %s"
                cursor.execute(sql, (group_id,))
                group=cursor.fetchone()

                if group:
                    return JSONResponse(
                        status_code=200,
                        content={
                            "success": True,
                            "message": "Grupo desplegado",
                            "data": group
                        }
                )
                else:
                    return JSONResponse(
                        status_code=404,
                        content={
                            "success": True,
                            "message": "Grupo no encontrado",
                            "data": None
                        }
                )

        except Exception as e:
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al desplegar el grupo {str(e)} ",
                        "data": None
                    }
                )
        
    async def create_group(self, group_data: Group):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                dup="SELECT COUNT(*) FROM grupo WHERE grupo = %s"
                cursor.execute(dup, (group_data.grupo,))
                result=cursor.fetchone()

                if result[0] > 0:
                    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "El grupo ya existe",
                            "data": None
                        }
                )

                sql='''INSERT INTO grupo (grupo)
                VALUES ( %s)'''
                cursor.execute(sql, (group_data.grupo))
                self.con.commit()

                if cursor.lastrowid:
                     
                    return JSONResponse(
                        status_code=201,
                        content={
                            "success": True,
                            "message": "Se ha creado el grupo con éxito",
                            "data": {"group_id" : cursor.lastrowid}
                        }
                )
                else:    
                    return JSONResponse(
                        status_code=400,
                        content={
                            "success": False,
                            "message": "No se pudo crear el grupo",
                            "data": None
                        }
                )

        except Exception as e:
            self.con.rollback()
            return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "message": f"Error al crear el grupo {str(e)} ",
                        "data": None
                    }
                )
    
    async def update_group(self, group_id: int, group_data: Group):
        try:
            self.con.ping(reconnect=True)
            with self.con.cursor() as cursor:
                sql = "SELECT COUNT(*) FROM grupo WHERE id_grupo=%s"
                cursor.execute(sql, (group_id,))
                result = cursor.fetchone()

                if result[0] == 0:
                    return JSONResponse(content={"success": False, "message": "Grupo no encontrado."}, status_code=404)

                # Actualizar campos (excepto estado)
                update_sql = """
                    UPDATE grupo
                    SET grupo=%s
                    WHERE id_grupo=%s
                """
                cursor.execute(update_sql, (
                    group_data.grupo,
                    group_id
                ))
                self.con.commit()

                if cursor.rowcount > 0:
                    return JSONResponse(content={"success": True, "message": "Grupo actualizado correctamente."}, status_code=200)
                else:
                    return JSONResponse(content={"success": False, "message": "No se realizaron cambios."}, status_code=409)

        except Exception as e:
            self.con.rollback()
            return JSONResponse(content={"success": False, "message": f"Error al actualizar el grupo: {str(e)}"}, status_code=500)