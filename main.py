from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import os

import models

from database import engine, Base

from routers.auth import router as auth_router
from routers.clientes import router as clientes_router
from routers.ingresos import router as ingresos_router
from routers.citas import router as citas_router
from routers.historiales import router as historiales_router
from routers.egresos import router as egresos_router
from routers.dashboard import router as dashboard_router
from routers.tratamientos import router as tratamientos_router
from routers.servicios import router as servicios_router
from routers.odontograma import router as odontograma_router
from routers.actividad import router as actividad_router


"""
==========================================
CREATE TABLES
==========================================
"""

Base.metadata.create_all(
    bind=engine
)


"""
==========================================
APP
==========================================
"""

app = FastAPI()


"""
==========================================
FACTURAS
==========================================
"""

if not os.path.exists("facturas"):

    os.makedirs("facturas")


"""
==========================================
CORS
==========================================
"""

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


"""
==========================================
ROUTERS
==========================================
"""

app.include_router(auth_router)
app.include_router(clientes_router)
app.include_router(ingresos_router)
app.include_router(citas_router)
app.include_router(historiales_router)
app.include_router(egresos_router)
app.include_router(dashboard_router)
app.include_router(servicios_router)
app.include_router(odontograma_router)
app.include_router(tratamientos_router)
app.include_router(actividad_router)