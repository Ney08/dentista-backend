from fastapi import FastAPI, Depends, File, UploadFile, Form, HTTPException
from sqlalchemy.orm import Session, joinedload
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timezone
from sqlalchemy.orm import joinedload
import models
from schemas import CitaCreate
from fastapi import APIRouter
from fastapi import HTTPException, Depends
from utils.actividad import registrar_actividad

from models.tratamiento import (
    Tratamiento
)

from database import get_db

router = APIRouter(
    prefix="/citas",
    tags=["Citas"],
    
    # dependencies=[
    #             Depends(get_current_user)
    #         ]

)

def nombre_cliente_cita(cita):

    if cita.cliente:

        return (
            f"{cita.cliente.nombre} "
            f"{cita.cliente.apellido}"
        )

    return f"Cliente #{cita.cliente_id}"


@router.post("/")
def crear_cita(data: CitaCreate, db: Session = Depends(get_db)):

    # ✅ VALIDAR DUPLICADO (MISMA FECHA EXACTA)
    existe = db.query(models.Cita).filter(
        models.Cita.fecha == data.fecha
    ).first()

    if existe:
        raise HTTPException(
            status_code=400,
            detail="Ya hay una cita en ese horario ❌"
        )

    # ✅ VALIDAR MOTIVO
    if not data.motivo:
        raise HTTPException(
            status_code=400,
            detail="El motivo es obligatorio ⚠️"
        )

    # ✅ CREAR CITA
    cita = models.Cita(
        cliente_id=data.cliente_id,
        fecha=data.fecha,
        motivo=data.motivo,
        tratamiento_id=data.tratamiento_id,# ✅ NUEVO
        detalle=data.detalle or None,  # ✅ NUEVO
        duracion=data.duracion or 30   # ✅ NUEVO
    )

    db.add(cita)
    db.commit()
    db.refresh(cita)

    return cita



@router.get("/")
def listar_citas(db: Session = Depends(get_db)):

    
    citas = db.query(models.Cita).options(

        joinedload(models.Cita.cliente),

        joinedload(models.Cita.tratamiento)

        .joinedload(Tratamiento.servicio)

        ).all()


    data = []

    for c in citas:
        data.append({
            "id": c.id,
            "cliente_id": c.cliente_id,
            "tratamiento": {

                 "id":
                    c.tratamiento.id,

                "servicio":
                    c.tratamiento.servicio.nombre

                 if c.tratamiento.servicio

                 else None,

                "pieza":
                     c.tratamiento.pieza,

                "estado":
                    c.tratamiento.estado,

                "sesiones_totales":
                    c.tratamiento.sesiones_totales,

                "sesiones_completadas":
                    c.tratamiento.sesiones_completadas,
                    

                "costo":
                    c.tratamiento.costo,

                "pagado":
                    c.tratamiento.pagado


            } if c.tratamiento else None,


           
            "cliente": {
                "nombre": c.cliente.nombre,
                "apellido": c.cliente.apellido
            } if c.cliente else None,

            "fecha": c.fecha.isoformat() if c.fecha else None,
            "estado": c.estado,
            "motivo": c.motivo,
            "detalle": c.detalle,
            "duracion": c.duracion
        })

    return data





@router.put("/{id}/completar")
def completar_cita(

    id: int,

    db: Session = Depends(get_db)

):

    cita = (

        db.query(models.Cita)

        .filter(
            models.Cita.id == id
        )

        .first()

    )

    if not cita:

        raise HTTPException(

            status_code=404,

            detail="Cita no encontrada"

        )

    """
    ==========================================
    COMPLETE CITA
    ==========================================
    """

    cita.estado = "completada"

    """
    ==========================================
    UPDATE TRATAMIENTO
    ==========================================
    """

    if cita.tratamiento_id:

        tratamiento = (

            db.query(Tratamiento)

            .filter(
                Tratamiento.id
                == cita.tratamiento_id
            )

            .first()

        )

        if tratamiento:

            """
            AUMENTAR SESIONES
            """

            tratamiento.sesiones_completadas += 1

            """
            AUTO COMPLETE
            """

            balance = (

                float(tratamiento.costo)

                -

                float(tratamiento.pagado)

            )

            if (

                tratamiento
                .sesiones_completadas

                >=

                tratamiento
                .sesiones_totales

                and

                balance <= 0

            ):

                tratamiento.estado = (
                    "Completado"
                )

            else:

                tratamiento.estado = (
                    "En progreso"
                )
    registrar_actividad(
        db=db,
        tipo="cita",
        accion="completar",
        titulo="Cita completada",
        descripcion=(
            f"{nombre_cliente_cita(cita)} · "
            f"{cita.motivo}"
        ),
        referencia_id=cita.id,
        usuario="Sistema"
    )
    db.commit()

    db.refresh(cita)

    return cita


    

@router.get("/debug/citas")
def debug_citas(db: Session = Depends(get_db)):
    return db.query(models.Cita).all()



@router.put("/{id}/cancelar")
def cancelar_cita(id: int, db: Session = Depends(get_db)):

    cita = db.query(models.Cita).filter(models.Cita.id == id).first()

    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    cita.estado = "cancelada"
    
    registrar_actividad(
        db=db,
        tipo="cita",
        accion="cancelar",
        titulo="Cita cancelada",
        descripcion=(
            f"{nombre_cliente_cita(cita)} · "
            f"{cita.motivo}"
        ),
        referencia_id=cita.id,
        usuario="Sistema"
    )

    db.commit()
    db.refresh(cita)

    return {
        "id": cita.id,
        "estado": cita.estado
    }


@router.put("/{id}")
def actualizar_cita(id: int, data: CitaCreate, db: Session = Depends(get_db)):

    cita = db.query(models.Cita).filter(models.Cita.id == id).first()

    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    
    fecha_anterior = cita.fecha
    cita.cliente_id = data.cliente_id
    cita.fecha = data.fecha
    cita.motivo = data.motivo
    cita.detalle = data.detalle
    cita.duracion = data.duracion
    
    cita.tratamiento_id = data.tratamiento_id
    
    
    accion = (
        "reagendar"
        if fecha_anterior != data.fecha
        else "actualizar"
    )

    titulo = (
        "Cita reagendada"
        if accion == "reagendar"
        else "Cita actualizada"
    )

    registrar_actividad(
        db=db,
        tipo="cita",
        accion=accion,
        titulo=titulo,
        descripcion=(
            f"{nombre_cliente_cita(cita)} · "
            f"{cita.motivo}"
        ),
        referencia_id=cita.id,
        usuario="Sistema"
    )


    db.commit()
    db.refresh(cita)

    return cita