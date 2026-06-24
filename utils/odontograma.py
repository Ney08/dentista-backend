from datetime import datetime, timezone

import models

from sqlalchemy.orm.attributes import flag_modified

from models.odontograma import Odontograma


def sincronizar_tratamiento_odontograma(
    db,
    tratamiento
):

    if not tratamiento:
        return

    if not tratamiento.pieza:
        return

    pieza = str(
        tratamiento.pieza
    )

    estado_normalizado = (
        tratamiento.estado or ""
    ).strip().lower()

    esta_completado = (
        estado_normalizado == "completado"
    )

    servicio = (
        db.query(models.ServicioCatalogo)
        .filter(
            models.ServicioCatalogo.id
            == tratamiento.servicio_id
        )
        .first()
    )

    servicio_nombre = (
        servicio.nombre
        if servicio
        else "Tratamiento"
    )

    odontograma = (

        db.query(Odontograma)

        .filter(
            Odontograma.cliente_id
            == tratamiento.cliente_id
        )

        .first()

    )

    if odontograma and odontograma.odontograma:

        data = dict(
            odontograma.odontograma
        )

    else:

        data = {}

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

    if esta_completado:

        meta["tratamiento_completado_at"] = (
            datetime.now(timezone.utc)
            .isoformat()
        )

    else:

        meta.pop(
            "tratamiento_completado_at",
            None
        )

    pieza_data["meta"] = meta

    data[pieza] = pieza_data

    if odontograma:

        odontograma.odontograma = data

        flag_modified(
            odontograma,
            "odontograma"
        )

    else:

        odontograma = Odontograma(

            cliente_id=tratamiento.cliente_id,

            odontograma=data

        )

        db.add(odontograma)

        db.flush()