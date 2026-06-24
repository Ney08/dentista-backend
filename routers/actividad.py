from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models

from database import get_db

from schemas import ActividadCreate


router = APIRouter(
    prefix="/actividades",
    tags=["Actividades"]
)


@router.get("/")

def listar_actividades(
    limit: int = 20,
    db: Session = Depends(get_db)
):

    actividades = (

        db.query(models.ActividadSistema)

        .order_by(
            models.ActividadSistema.created_at.desc()
        )

        .limit(limit)

        .all()

    )

    return actividades


@router.post("/")

def crear_actividad(
    data: ActividadCreate,
    db: Session = Depends(get_db)
):

    actividad = models.ActividadSistema(

        tipo=data.tipo,

        accion=data.accion,

        titulo=data.titulo,

        descripcion=data.descripcion,

        referencia_id=data.referencia_id,

        usuario=data.usuario

    )

    db.add(actividad)

    db.commit()

    db.refresh(actividad)

    return actividad




