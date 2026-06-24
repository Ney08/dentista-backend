from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import models

from database import get_db

from schemas import DashboardResumen

router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)


@router.get(
    "/resumen",
    response_model=DashboardResumen
)
def resumen(
    db: Session = Depends(get_db)
):

    # ✅ INGRESOS PAGADOS
    ingresos_pagados = db.query(
        models.Ingreso
    ).filter(
        models.Ingreso.pagado == True
    ).all()

    total_ingresos = 0

    total_costos = 0

    for ingreso in ingresos_pagados:

        subtotal = 0

        for s in ingreso.servicios:

            subtotal += s.monto

            servicio_catalogo = db.query(
                models.ServicioCatalogo
            ).filter(
                models.ServicioCatalogo.nombre == s.descripcion
            ).first()

            if servicio_catalogo:

                total_costos += (
                    servicio_catalogo.costo_servicio or 0
                )

        itbis = subtotal * 0.18

        descuento = subtotal * (
            (ingreso.descuento or 0) / 100
        )

        total = subtotal + itbis - descuento

        total_ingresos += total

    # ✅ EGRESOS
    egresos = db.query(
        models.Egreso
    ).all()

    total_egresos = sum(
        e.monto
        for e in egresos
    )

    # ✅ PENDIENTES
    pendientes = db.query(
        models.Ingreso
    ).filter(
        models.Ingreso.pagado == False
    ).all()

    total_pendiente = 0

    for ingreso in pendientes:

        subtotal = sum(
            s.monto
            for s in ingreso.servicios
        )

        itbis = subtotal * 0.18

        descuento = subtotal * (
            (ingreso.descuento or 0) / 100
        )

        total = subtotal + itbis - descuento

        total_pendiente += total

    # ✅ CAJA
    caja = (
        total_ingresos -
        total_egresos
    )

    # ✅ GANANCIA BRUTA
    ganancia_bruta = (
        total_ingresos -
        total_costos
    )

    # ✅ GANANCIA NETA
    ganancia_neta = (
        total_ingresos -
        total_costos -
        total_egresos
    )

    return {
        "ingresos": total_ingresos,
        "egresos": total_egresos,
        "caja": caja,
        "ganancia_bruta": ganancia_bruta,
        "ganancia_neta": ganancia_neta,
        "pendiente": total_pendiente
    }