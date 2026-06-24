from sqlalchemy.orm import Session, joinedload
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
import os
from utils.actividad import registrar_actividad
import models
from schemas import HistorialCreate
from fastapi import APIRouter
from fastapi import HTTPException, Depends
from fastapi import Query
from typing import Optional
from database import get_db




router = APIRouter(
    prefix="/historiales",
    tags=["Historiales"],
    # dependencies=[
    #         Depends(get_current_user)
    #     ]
)

def nombre_cliente_por_id(db: Session, cliente_id: int):

    cliente = (
        db.query(models.Cliente)
        .filter(models.Cliente.id == cliente_id)
        .first()
    )

    if cliente:

        return (
            f"{cliente.nombre} "
            f"{cliente.apellido}"
        )

    return f"Cliente #{cliente_id}"

@router.post("/")
def crear_historial(
    data: HistorialCreate,
    db: Session = Depends(get_db)
):

    historial = models.Historial(

        cliente_id=data.cliente_id,

        descripcion=data.descripcion

    )

    db.add(historial)

    db.flush()

    registrar_actividad(
        db=db,
        tipo="historial",
        accion="crear",
        titulo="Historial clínico creado",
        descripcion=(
            f"{nombre_cliente_por_id(db, historial.cliente_id)} · "
            f"{historial.descripcion[:80]}"
        ),
        referencia_id=historial.id,
        usuario="Sistema"
    )

    db.commit()

    db.refresh(historial)

    return historial


@router.get("/clientes/{cliente_id}/historial")
def ver_historial(cliente_id: int, db: Session = Depends(get_db)):
    return db.query(models.Historial).filter(
        models.Historial.cliente_id == cliente_id
    ).all()
    
    
    
@router.delete("/{historial_id}")
def eliminar_historial(
    historial_id: int,
    db: Session = Depends(get_db)
):

    historial = db.query(
        models.Historial
    ).filter(
        models.Historial.id == historial_id
    ).first()

    if not historial:

        raise HTTPException(
            status_code=404,
            detail="Historial no encontrado"
        )

    cliente_id = historial.cliente_id

    descripcion_historial = historial.descripcion or ""

    historial_id_ref = historial.id

    registrar_actividad(
        db=db,
        tipo="historial",
        accion="eliminar",
        titulo="Historial clínico eliminado",
        descripcion=(
            f"{nombre_cliente_por_id(db, cliente_id)} · "
            f"{descripcion_historial[:80]}"
        ),
        referencia_id=historial_id_ref,
        usuario="Sistema"
    )

    db.delete(historial)

    db.commit()

    return {
        "message": "Historial eliminado ✅"
    }




@router.put("/{historial_id}")
def actualizar_historial(
    historial_id: int,
    data: HistorialCreate,
    db: Session = Depends(get_db)
):

    historial = db.query(
        models.Historial
    ).filter(
        models.Historial.id == historial_id
    ).first()

    if not historial:

        raise HTTPException(
            status_code=404,
            detail="Historial no encontrado"
        )

    historial.descripcion = data.descripcion

    registrar_actividad(
        db=db,
        tipo="historial",
        accion="actualizar",
        titulo="Historial clínico actualizado",
        descripcion=(
            f"{nombre_cliente_por_id(db, historial.cliente_id)} · "
            f"{historial.descripcion[:80]}"
        ),
        referencia_id=historial.id,
        usuario="Sistema"
    )

    db.commit()

    db.refresh(historial)

    return historial