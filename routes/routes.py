from fastapi import APIRouter
from services.student_service import StudentService
from services.professor_service import ProfessorService
from services.adminPR_service import AdminPR_Service
from services.parent_service import Parent_Service
from services.subadmin_service import SubAdmin_Service
from services.group_service import Group_Service
from services.subject_service import Subject_Service
from services.assignment_service import Assignment_Service
from models.student_model import Student
from models.professor_model import Professor
from models.adminPR_model import AdminPR
from models.parent_model import Parent
from models.subadmin_model import SubAdmin
from models.group_model import Group
from models.subject_model import Subject
from models.assignment_model import Assignment

#Siempre que voy a crear una ruta, necesito tanto el servicio como el modelo creados anteriormente
routes_s = APIRouter(prefix="/student", tags=["Student"])

student_service = StudentService()
student_model = Student #Los errores ocurrían debido a que user_model se estaba instanciando a la clase cuando no era necesario. Esta línea no se necesita, puesto que solo es equivalente a darle un alias a User

@routes_s.get("/get-users")
async def get_all_users():
    return await student_service.get_users() #para retornar una función asíncrona, debemos usar el await, en este caso la función user_service es importada de services 

@routes_s.get("/get-user/{user_id}")
async def get_user(user_id: int):
    return await student_service.get_user_by_id(user_id)

@routes_s.post("/create-user") #El método post me permite crear un nuevo dato dentro de las tablas de la DB
async def create_user(user: Student):
    return await student_service.create_user(user)

@routes_s.patch("/change-password/{user_id}") #El método patch me permite modificar parcialmente un registro, solo tomando una parte como la contraseña o el nombre
async def update_user(id: str, new_password: str):
    return await student_service.change_password(id, new_password)

@routes_s.patch("/inactivate_user/{user_id}") 
async def update_user(user_id: int):
    return await student_service.inactivate_user(user_id)

@routes_s.patch("/toggle_user_status/{user_id}") 
async def update_user(user_id: int):
    return await student_service.toggle_user_status(user_id)

@routes_s.put("/update_user/{user_id}") 
async def update_user(user_id: int, user_data: Student):
    return await student_service.update_user(user_id, user_data)

routes_p = APIRouter(prefix="/professor", tags=["Professor"])

professor_service = ProfessorService()
professor_model= Professor #Esta llamada permite traer los servicios específicos de cada usuario

@routes_p.get("/get-users")
async def get_all_users():
    return await professor_service.get_users()

@routes_p.get("/get-user/{user_id}")
async def get_user(user_id: int):
    return await professor_service.get_user_by_id(user_id)

@routes_p.post("/create-user")
async def create_user(user: Professor):
    return await professor_service.create_user(user)

@routes_p.patch("/change-password/{user_id}")
async def update_user(id: str, new_password: str):
    return await professor_service.change_password(id, new_password)

@routes_p.patch("/inactivate_user/{user_id}") 
async def update_user(user_id: int):
    return await professor_service.inactivate_user(user_id)

@routes_p.patch("/toggle_user_status/{user_id}") 
async def update_user(user_id: int):
    return await professor_service.toggle_user_status(user_id)

@routes_p.put("/update_user/{user_id}") 
async def update_user(user_id: int, user_data: Professor):
    return await professor_service.update_user(user_id, user_data)

routes_a = APIRouter(prefix="/adminPR", tags=["Administrator"])

adminPR_service = AdminPR_Service()
adminPR_model= AdminPR

@routes_a.get("/get-users")
async def get_all_users():
    return await adminPR_service.get_users()

@routes_a.get("/get-user/{user_id}")
async def get_user(user_id: int):
    return await adminPR_service.get_user_by_id(user_id)

@routes_a.post("/create-user")
async def create_user(user: AdminPR):
    return await adminPR_service.create_user(user)

@routes_a.patch("/change-password/{user_id}")
async def update_user(id: str, new_password: str):
    return await adminPR_service.change_password(id, new_password)

@routes_a.patch("/inactivate_user/{user_id}") 
async def update_user(user_id: int):
    return await adminPR_service.inactivate_user(user_id)

@routes_a.patch("/toggle_user_status/{user_id}") 
async def update_user(user_id: int):
    return await adminPR_service.toggle_user_status(user_id)

@routes_a.put("/update_user/{user_id}") 
async def update_user(user_id: int, user_data: AdminPR):
    return await adminPR_service.update_user(user_id, user_data)

routes_pa = APIRouter(prefix="/parent", tags=["Parent"])

parent_service = Parent_Service()
parent_model= Parent

@routes_pa.get("/get-users")
async def get_all_users():
    return await parent_service.get_users()

@routes_pa.get("/get-user/{user_id}")
async def get_user(user_id: int):
    return await parent_service.get_user_by_id(user_id)

@routes_pa.post("/create-user")
async def create_user(user: Parent):
    return await parent_service.create_user(user)

@routes_pa.patch("/change-password/{user_id}")
async def update_user(id: str, new_password: str):
    return await parent_service.change_password(id, new_password)

@routes_pa.patch("/inactivate_user/{user_id}") 
async def update_user(user_id: int):
    return await parent_service.inactivate_user(user_id)

@routes_pa.patch("/toggle_user_status/{user_id}") 
async def update_user(user_id: int):
    return await parent_service.toggle_user_status(user_id)

@routes_pa.put("/update_user/{user_id}") 
async def update_user(user_id: int, user_data: Parent):
    return await parent_service.update_user(user_id, user_data)

routes_sa = APIRouter(prefix="/subadmin", tags=["SubAdmin"])

subadmin_service = SubAdmin_Service()
subadmin_model= SubAdmin

@routes_sa.get("/get-users")
async def get_all_users():
    return await subadmin_service.get_users()

@routes_sa.get("/get-user/{user_id}")
async def get_user(user_id: int):
    return await subadmin_service.get_user_by_id(user_id)

@routes_sa.post("/create-user")
async def create_user(user: SubAdmin):
    return await subadmin_service.create_user(user)

@routes_sa.patch("/change-password/{user_id}")
async def update_user(id: str, new_password: str):
    return await subadmin_service.change_password(id, new_password)

@routes_sa.patch("/inactivate_user/{user_id}") 
async def update_user(user_id: int):
    return await subadmin_service.inactivate_user(user_id)

@routes_sa.patch("/toggle_user_status/{user_id}") 
async def update_user(user_id: int):
    return await subadmin_service.toggle_user_status(user_id)

@routes_sa.put("/update_user/{user_id}") 
async def update_user(user_id: int, user_data: SubAdmin):
    return await subadmin_service.update_user(user_id, user_data)

routes_g = APIRouter(prefix="/groups", tags=["Groups"])

group_service = Group_Service()
group_model= Group

@routes_g.get("/get-groups")
async def get_all_groups():
    return await group_service.get_groups()

@routes_g.get("/get-group/{group_id}")
async def get_group(group_id: int):
    return await group_service.get_group_by_id(group_id)

@routes_g.post("/create-group")
async def create_group(group: Group):
    return await group_service.create_group(group)

@routes_g.put("/update_group/{group_id}") 
async def update_group(group_id: int, group_data: Group):
    return await group_service.update_group(group_id, group_data)

routes_su = APIRouter(prefix="/subjects", tags=["Subjects"]) #ES NECESARIO CAMBIAR LA FORMA EN QUE FUNIONA LA FK, DEBIDO A QUE SOLO PERMITE ASIGNAR UNA MATERIA A UN ÚNICO GRUPO

subject_service = Subject_Service()
subject_model= Subject

@routes_su.get("/get-subjects")
async def get_all_subjects():
    return await subject_service.get_subjects()

@routes_su.get("/get-subject/{subject_id}")
async def get_subject(subject_id: int):
    return await subject_service.get_subject_by_id(subject_id)

@routes_su.post("/create-subject")
async def create_subject(subject: Subject):
    return await subject_service.create_subject(subject)

@routes_su.put("/update_subject/{subject_id}") 
async def update_subject(subject_id: int, subject_data: Subject):
    return await subject_service.update_subject(subject_id, subject_data)

routes_as = APIRouter(prefix="/assignments", tags=["Assignments"])

assignment_service = Assignment_Service()
assignment_model= Assignment

@routes_as.get("/get-assignments")
async def get_all_assignments():
    return await assignment_service.get_assignments()

@routes_as.get("/get-assignment/{assignment_id}")
async def get_assignment(assignment_id: int):
    return await assignment_service.get_assignment_by_id(assignment_id)

@routes_as.post("/create-assignment")
async def create_assignment(assignment: Assignment):
    return await assignment_service.create_assignment(assignment)

@routes_as.put("/update_assignment/{assignment_id}") 
async def update_assignment(assignment_id: int, assignment_data: Assignment):
    return await assignment_service.update_assignment(assignment_id, assignment_data)