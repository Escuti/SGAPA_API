from dotenv import load_dotenv
from fastapi.responses import HTMLResponse
import uvicorn
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from routes.routes import routes_s
from routes.routes import routes_p
from routes.routes import routes_a
from routes.routes import routes_pa
from routes.routes import routes_sa
from routes.routes import routes_g
from routes.routes import routes_su
from routes.routes import routes_as
from routes.routes import routes_rgs
from routes.routes import routes_rca

app=FastAPI()
app.title="Práctica CRUD"
app.version="0.0.1"
app.description="API Description"

#Carga de Variables de Entorno
load_dotenv()

app.include_router(routes_s)
app.include_router(routes_p)
app.include_router(routes_a)
app.include_router(routes_pa)
app.include_router(routes_sa)
app.include_router(routes_g)
app.include_router(routes_su)
app.include_router(routes_as)
app.include_router(routes_rgs)
app.include_router(routes_rca)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH"],
    allow_headers=["*"]
)

@app.get(
    path="/",
    status_code=status.HTTP_200_OK,
    summary="DEFAULT",
    tags=["APP"]
)
def message():
    """ HOME API
    Return:
        Message
    """
    return HTMLResponse("<h1> SGAPA_API </h1>")