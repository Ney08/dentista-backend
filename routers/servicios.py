from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from utils.actividad import registrar_actividad

import models

from database import get_db

from schemas import ServicioCreate, Servicio


router = APIRouter(
    prefix="/servicios",
    tags=["Servicios"]
)


@router.get(
    "/",
    response_model=list[Servicio]
)
def listar_servicios(
    db: Session = Depends(get_db)
):

    return db.query(
        models.ServicioCatalogo
    ).all()


@router.post(
    "/",
    response_model=Servicio
)
def crear_servicio(
    data: ServicioCreate,
    db: Session = Depends(get_db)
):

    existe = db.query(
        models.ServicioCatalogo
    ).filter(
        models.ServicioCatalogo.nombre == data.nombre
    ).first()

    if existe:

        raise HTTPException(
            status_code=400,
            detail="Servicio ya existe ❌"
        )

    servicio = models.ServicioCatalogo(
        nombre=data.nombre,
        descripcion=data.descripcion,
        precio=data.precio,
        costo_servicio=data.costo_servicio
    )

    db.add(servicio)

    db.flush()

    registrar_actividad(
        db=db,
        tipo="servicio",
        accion="crear",
        titulo="Servicio creado",
        descripcion=(
            f"{servicio.nombre} · "
            f"RD$ {servicio.precio}"
        ),
        referencia_id=servicio.id,
        usuario="Sistema"
    )

    db.commit()

    db.refresh(servicio)

    return servicio


@router.put(
    "/{id}",
    response_model=Servicio
)
def actualizar_servicio(
    id: int,
    data: ServicioCreate,
    db: Session = Depends(get_db)
):

    servicio = db.query(
        models.ServicioCatalogo
    ).filter(
        models.ServicioCatalogo.id == id
    ).first()

    if not servicio:

        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado ❌"
        )

    servicio.nombre = data.nombre
    servicio.descripcion = data.descripcion
    servicio.precio = data.precio
    servicio.costo_servicio = data.costo_servicio

    registrar_actividad(
        db=db,
        tipo="servicio",
        accion="actualizar",
        titulo="Servicio actualizado",
        descripcion=(
            f"{servicio.nombre} · "
            f"RD$ {servicio.precio}"
        ),
        referencia_id=servicio.id,
        usuario="Sistema"
    )

    db.commit()

    db.refresh(servicio)

    return servicio


@router.delete("/{id}")
def eliminar_servicio(
    id: int,
    db: Session = Depends(get_db)
):

    servicio = db.query(
        models.ServicioCatalogo
    ).filter(
        models.ServicioCatalogo.id == id
    ).first()

    if not servicio:

        raise HTTPException(
            status_code=404,
            detail="Servicio no encontrado ❌"
        )

    servicio_id = servicio.id

    servicio_nombre = servicio.nombre

    servicio_precio = servicio.precio

    registrar_actividad(
        db=db,
        tipo="servicio",
        accion="eliminar",
        titulo="Servicio eliminado",
        descripcion=(
            f"{servicio_nombre} · "
            f"RD$ {servicio_precio}"
        ),
        referencia_id=servicio_id,
        usuario="Sistema"
    )

    db.delete(servicio)

    db.commit()

    return {
        "message": "Servicio eliminado ✅"
    }