from fastapi import APIRouter

from fastapi import Depends
from utils.odontograma import sincronizar_tratamiento_odontograma
from sqlalchemy.orm import (
    Session,
    joinedload
)

from sqlalchemy.orm.attributes import flag_modified
from models.odontograma import Odontograma

from datetime import (
    datetime,
    timezone
)

import models

from utils.actividad import registrar_actividad

from database import get_db

from models.tratamiento import (
    Tratamiento
)

from schemas.tratamiento import (
    TratamientoCreate
)

router = APIRouter(

    prefix="/tratamientos",

    tags=["Tratamientos"],
    
    # dependencies=[
    #         Depends(get_current_user)
    #     ]

)

def nombre_cliente_por_id(
    db: Session,
    cliente_id: int
):

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


def nombre_servicio_por_id(
    db: Session,
    servicio_id: int
):

    servicio = (
        db.query(models.ServicioCatalogo)
        .filter(models.ServicioCatalogo.id == servicio_id)
        .first()
    )

    if servicio:

        return servicio.nombre

    return f"Servicio #{servicio_id}"


def descripcion_tratamiento(
    db: Session,
    tratamiento: Tratamiento
):

    cliente_nombre = nombre_cliente_por_id(db, tratamiento.cliente_id)

    servicio_nombre = nombre_servicio_por_id(db, tratamiento.servicio_id)

    pieza =(
                f" · Pieza {tratamiento.pieza}"
                if tratamiento.pieza
                else ""
            )

    return (
        f"{cliente_nombre} · "
        f"{servicio_nombre}"
        f"{pieza}"
    )


"""
==========================================
GET BY CLIENTE
==========================================
"""

@router.get("/{cliente_id}")

def get_tratamientos(

    cliente_id: int,

    db: Session = Depends(get_db)

):

    tratamientos = (

        db.query(Tratamiento)

        .options(

            joinedload(
                Tratamiento.servicio
            )

        )

        .filter(
            Tratamiento.cliente_id
            == cliente_id
        )

        .order_by(
            Tratamiento.id.desc()
        )

        .all()

    )

    return [

        {

            "id": t.id,

            "cliente_id":
                t.cliente_id,

            "servicio_id":
                t.servicio_id,

            "servicio_nombre":

                t.servicio.nombre

                if t.servicio

                else None,

            "pieza":
                t.pieza,

            "estado":
                t.estado,

            "costo":
                t.costo,

            "pagado":
                t.pagado,

            "sesiones_totales":
                t.sesiones_totales,

            "sesiones_completadas":
                t.sesiones_completadas,

            "notas":
                t.notas,
            
            "created_at":

                t.created_at.isoformat()

            if t.created_at

            else None,


        }

        for t in tratamientos

    ]

"""
==========================================
CREATE
==========================================
"""

@router.post("/")

def create_tratamiento(

    payload: TratamientoCreate,

    db: Session = Depends(get_db)

):

    tratamiento = Tratamiento(

        cliente_id=
        payload.cliente_id,

        servicio_id=
        payload.servicio_id,

        pieza=
        payload.pieza,

        estado=
        payload.estado,

        costo=
        payload.costo,

        pagado=
        payload.pagado,

        sesiones_totales=
        payload.sesiones_totales,

        sesiones_completadas=
        payload.sesiones_completadas,

        notas=
        payload.notas

    )

    db.add(tratamiento)

    db.flush()
    
    sincronizar_tratamiento_odontograma(
        db,
        tratamiento
    )

    registrar_actividad(
        db=db,
        tipo="tratamiento",
        accion="crear",
        titulo="Tratamiento creado",
        descripcion=descripcion_tratamiento(
            db,
            tratamiento
        ),
        referencia_id=tratamiento.id,
        usuario="Sistema"
    )

    db.commit()

    db.refresh(tratamiento)

    return {

        "id":
            tratamiento.id,

        "cliente_id":
            tratamiento.cliente_id,

        "servicio_id":
            tratamiento.servicio_id,

        "servicio_nombre":

            tratamiento.servicio.nombre

            if tratamiento.servicio

            else None,

        "pieza":
            tratamiento.pieza,

        "estado":
            tratamiento.estado,

        "costo":
            tratamiento.costo,

        "pagado":
            tratamiento.pagado,

        "sesiones_totales":
            tratamiento.sesiones_totales,

        "sesiones_completadas":
            tratamiento.sesiones_completadas,

        "notas":
            tratamiento.notas,
            
        
        "created_at":

            tratamiento.created_at.isoformat()

        if tratamiento.created_at

        else None,


    }

"""
==========================================
UPDATE
==========================================
"""

@router.put("/{tratamiento_id}")

def update_tratamiento(

    tratamiento_id: int,

    payload: TratamientoCreate,

    db: Session = Depends(get_db)

):

    tratamiento = (

        db.query(Tratamiento)

        .options(

            joinedload(
                Tratamiento.servicio
            )

        )

        .filter(
            Tratamiento.id
            == tratamiento_id
        )

        .first()

    )

    if not tratamiento:

        return {
            "error":
            "Tratamiento no encontrado"
        }
    estado_anterior = tratamiento.estado
    tratamiento.servicio_id = (
        payload.servicio_id
    )

    tratamiento.pieza = (
        payload.pieza
    )

    tratamiento.estado = (
        payload.estado
    )

    tratamiento.costo = (
        payload.costo
    )

    tratamiento.pagado = (
        payload.pagado
    )

    tratamiento.sesiones_totales = (
        payload.sesiones_totales
    )

    tratamiento.sesiones_completadas = (
        payload.sesiones_completadas
    )

    tratamiento.notas = (
        payload.notas
    )

    """
    ==========================================
    AUTO COMPLETE
    ==========================================
    """

    balance = (

        float(tratamiento.costo)

        -

        float(tratamiento.pagado)

    )

    if (

        balance <= 0

        and

        tratamiento
        .sesiones_completadas

        >=

        tratamiento
        .sesiones_totales

    ):

        tratamiento.estado = (
            "Completado"
        )

    elif (

        tratamiento
        .sesiones_completadas > 0

    ):

        tratamiento.estado = (
            "En progreso"
        )
    accion = (
        "completar"
        if tratamiento.estado == "Completado"
        and estado_anterior != "Completado"
        else "actualizar"
    )

    titulo = (
        "Tratamiento completado"
        if accion == "completar"
        else "Tratamiento actualizado"
    )
    
    sincronizar_tratamiento_odontograma(
        db,
        tratamiento
    )

    registrar_actividad(
        db=db,
        tipo="tratamiento",
        accion=accion,
        titulo=titulo,
        descripcion=descripcion_tratamiento(
            db,
            tratamiento
        ),
        referencia_id=tratamiento.id,
        usuario="Sistema"
    )
        
    db.commit()

    db.refresh(tratamiento)

    return {

        "id":
            tratamiento.id,

        "cliente_id":
            tratamiento.cliente_id,

        "servicio_id":
            tratamiento.servicio_id,

        "servicio_nombre":

            tratamiento.servicio.nombre

            if tratamiento.servicio

            else None,

        "pieza":
            tratamiento.pieza,

        "estado":
            tratamiento.estado,

        "costo":
            tratamiento.costo,

        "pagado":
            tratamiento.pagado,

        "sesiones_totales":
            tratamiento.sesiones_totales,

        "sesiones_completadas":
            tratamiento.sesiones_completadas,

        "notas":
            tratamiento.notas

    }

"""
==========================================
DELETE
==========================================
"""

@router.delete("/{tratamiento_id}")

def delete_tratamiento(

    tratamiento_id: int,

    db: Session = Depends(get_db)

):

    tratamiento = (

        db.query(Tratamiento)

        .filter(
            Tratamiento.id
            == tratamiento_id
        )

        .first()

    )

    if not tratamiento:

        return {
            "error":
            "Tratamiento no encontrado"
        }

    tratamiento_id_ref = tratamiento.id

    descripcion = descripcion_tratamiento(
        db,
        tratamiento
    )
    
    registrar_actividad(
        db=db,
        tipo="tratamiento",
        accion="eliminar",
        titulo="Tratamiento eliminado",
        descripcion=descripcion,
        referencia_id=tratamiento_id_ref,
        usuario="Sistema"
    )
    
    tratamiento.estado = "Eliminado"

    sincronizar_tratamiento_odontograma(
        db,
        tratamiento
    )

    db.delete(tratamiento)

    db.commit()

    return {

        "message":
            "Tratamiento eliminado ✅"

    }

"""
==========================================
REGISTRAR PAGO
==========================================
"""

@router.put("/{tratamiento_id}/pago")

def registrar_pago(

    tratamiento_id: int,

    monto: float,

    db: Session = Depends(get_db)

):

    tratamiento = (

        db.query(Tratamiento)

        .options(

            joinedload(
                Tratamiento.servicio
            )

        )

        .filter(
            Tratamiento.id
            == tratamiento_id
        )

        .first()

    )

    if not tratamiento:

        return {
            "error":
            "Tratamiento no encontrado"
        }

    """
    ==========================================
    SUMAR PAGO
    ==========================================
    """

    tratamiento.pagado = (

        float(tratamiento.pagado)

        +

        float(monto)

    )

    """
    ==========================================
    AUTO COMPLETE
    ==========================================
    """

    balance = (

        float(tratamiento.costo)

        -

        float(tratamiento.pagado)

    )

    if (

        balance <= 0

        and

        tratamiento
        .sesiones_completadas

        >=

        tratamiento
        .sesiones_totales

    ):

        tratamiento.estado = (
            "Completado"
        )

    else:

        tratamiento.estado = (
            "En progreso"
        )

        
    sincronizar_tratamiento_odontograma(
        db,
        tratamiento
    )

    registrar_actividad(
        db=db,
        tipo="tratamiento",
        accion="pago",
        titulo="Pago registrado en tratamiento",
        descripcion=(
            f"{descripcion_tratamiento(db, tratamiento)} · "
            f"RD$ {monto}"
        ),
        referencia_id=tratamiento.id,
        usuario="Sistema"
    )


    db.commit()

    db.refresh(tratamiento)

    return {

        "id":
            tratamiento.id,

        "cliente_id":
            tratamiento.cliente_id,

        "servicio_id":
            tratamiento.servicio_id,

        "servicio_nombre":

            tratamiento.servicio.nombre

            if tratamiento.servicio

            else None,

        "pieza":
            tratamiento.pieza,

        "estado":
            tratamiento.estado,

        "costo":
            tratamiento.costo,

        "pagado":
            tratamiento.pagado,

        "sesiones_totales":
            tratamiento.sesiones_totales,

        "sesiones_completadas":
            tratamiento.sesiones_completadas,

        "notas":
            tratamiento.notas

    }
    
    
    
    
    
@router.post("/sync-odontograma/{cliente_id}")
def sync_tratamientos_odontograma(

    cliente_id: int,

    db: Session = Depends(get_db)

):

    tratamientos = (

        db.query(Tratamiento)

        .filter(
            Tratamiento.cliente_id == cliente_id
        )

        .all()

    )

    odontograma = (

        db.query(Odontograma)

        .filter(
            Odontograma.cliente_id == cliente_id
        )

        .first()

    )

    if odontograma and odontograma.odontograma:

        data = dict(
            odontograma.odontograma
        )

    else:

        data = {}

    sincronizados = []

    for tratamiento in tratamientos:

        if not tratamiento.pieza:

            continue

        pieza = str(
            tratamiento.pieza
        )

        estado_normalizado = (
            tratamiento.estado or ""
        ).strip().lower()

        esta_completado = (
            estado_normalizado == "completado"
        )

        pieza_data = dict(
            data.get(
                pieza,
                {}
            )
        )

        pieza_data.setdefault(
            "top",
            None
        )

        pieza_data.setdefault(
            "left",
            None
        )

        pieza_data.setdefault(
            "center",
            None
        )

        pieza_data.setdefault(
            "right",
            None
        )

        pieza_data.setdefault(
            "bottom",
            None
        )
        
        
        
        
        servicio = (
            db.query(models.ServicioCatalogo)
            .filter(
                models.ServicioCatalogo.id == tratamiento.servicio_id
            )
            .first()
        )

        
        servicio_nombre = (
            servicio.nombre
            if servicio
            else "Tratamiento"
        )


        meta = dict(
            pieza_data.get(
                "meta",
                {}
            )
        )
        
        
        meta["tratamiento_completado"] = esta_completado

        meta["tratamiento_id"] = tratamiento.id

        meta["servicio_id"] = tratamiento.servicio_id
        
        meta["servicio_nombre"] = servicio_nombre
        
        meta["estado_tratamiento"] = tratamiento.estado

        pieza_data["meta"] = meta

        data[pieza] = pieza_data

        
        sincronizados.append({
            "tratamiento_id": tratamiento.id,
            "pieza": pieza,
            "estado": tratamiento.estado,
            "servicio_nombre": servicio_nombre,
            "tratamiento_completado": esta_completado
        })


    if odontograma:

        odontograma.odontograma = data

        flag_modified(
            odontograma,
            "odontograma"
        )

    else:

        odontograma = Odontograma(

            cliente_id=cliente_id,

            odontograma=data

        )

        db.add(odontograma)

    db.commit()

    db.refresh(odontograma)

    return {
        "message": "Odontograma sincronizado ✅",
        "cliente_id": cliente_id,
        "total_tratamientos": len(tratamientos),
        "sincronizados": sincronizados,
        "odontograma": odontograma.odontograma
    }