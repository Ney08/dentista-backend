from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified
import models

from database import get_db

from models.odontograma import Odontograma

from schemas.odontograma import (
    OdontogramaPayload
)

from utils.actividad import registrar_actividad


router = APIRouter(
    prefix="/odontograma",
    tags=["Odontograma"],
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


@router.get("/{cliente_id}")
def get_odontograma(
    cliente_id: int,
    db: Session = Depends(get_db)
):

    odontograma = (
        db.query(Odontograma)
        .filter(
            Odontograma.cliente_id
            == cliente_id
        )
        .first()
    )

    if not odontograma:

        return {}

    return odontograma.odontograma


@router.put("/{cliente_id}")
def save_odontograma(

    cliente_id: int,

    payload: OdontogramaPayload,

    db: Session = Depends(get_db)

):

    try:

        odontograma = (

            db.query(Odontograma)

            .filter(
                Odontograma.cliente_id
                == cliente_id
            )

            .first()

        )

        odontograma_anterior = (
            odontograma.odontograma
            if odontograma and odontograma.odontograma
            else {}
        )

        data = {}

        for tooth, face in payload.odontograma.items():

            pieza_anterior = (
                odontograma_anterior.get(
                    tooth,
                    {}
                )
            )

            meta_anterior = (
                pieza_anterior.get(
                    "meta",
                    {}
                )
            )

            data[tooth] = {

                "top":
                    face.top,

                "left":
                    face.left,

                "center":
                    face.center,

                "right":
                    face.right,

                "bottom":
                    face.bottom,

                "meta":
                    meta_anterior

            }

        es_nuevo = False

        if odontograma:

            odontograma.odontograma = data
            
            flag_modified(
                    odontograma,
                    "odontograma"
                )


        else:

            es_nuevo = True

            odontograma = Odontograma(

                cliente_id=cliente_id,

                odontograma=data

            )

            db.add(odontograma)

            db.flush()

        registrar_actividad(
            db=db,
            tipo="odontograma",
            accion=(
                "crear"
                if es_nuevo
                else "actualizar"
            ),
            titulo=(
                "Odontograma creado"
                if es_nuevo
                else "Odontograma actualizado"
            ),
            descripcion=(
                f"{nombre_cliente_por_id(db, cliente_id)}"
            ),
            referencia_id=cliente_id,
            usuario="Sistema"
        )

        db.commit()

        db.refresh(odontograma)

        return {

            "success": True,

            "odontograma":
                odontograma.odontograma

        }

    except Exception as e:

        print(e)

        raise e


@router.delete("/{cliente_id}")
def delete_odontograma(

    cliente_id: int,

    db: Session = Depends(get_db)

):

    odontograma = (

        db.query(Odontograma)

        .filter(
            Odontograma.cliente_id
            == cliente_id
        )

        .first()

    )

    if not odontograma:

        raise HTTPException(

            status_code=404,

            detail="Odontograma no encontrado"

        )

    registrar_actividad(
        db=db,
        tipo="odontograma",
        accion="eliminar",
        titulo="Odontograma eliminado",
        descripcion=(
            f"{nombre_cliente_por_id(db, cliente_id)}"
        ),
        referencia_id=cliente_id,
        usuario="Sistema"
    )

    db.delete(odontograma)

    db.commit()

    return {

        "success": True,

        "message":
            "Odontograma eliminado"

    }
