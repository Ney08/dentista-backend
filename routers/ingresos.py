from fastapi import (
    Depends,
    File,
    UploadFile,
    HTTPException
)

from sqlalchemy.orm import (
    Session,
    joinedload
)

from datetime import (
    datetime,
    timezone
)

import uuid

import models

from database import get_db

from schemas import (
    IngresoCreate,
    IngresoUpdateSchema
)

from fastapi import APIRouter

router = APIRouter(

    prefix="/ingresos",

    tags=["Ingresos"]

)

from utils.actividad import registrar_actividad

@router.post("/")

def crear_ingreso(

    data: IngresoCreate,

    db: Session = Depends(get_db)

):

    try:

        print(
            "DATA RECIBIDA:",
            data.model_dump()
        )

    

        ingreso = models.Ingreso(

            cliente_id=data.cliente_id,

            tratamiento_id=
                getattr(
                    data,
                    "tratamiento_id",
                    None
                ),

            descuento=
                getattr(
                    data,
                    "descuento",
                    0
                ) or 0,

            pagado=False,

            cita_id=
                getattr(
                    data,
                    "cita_id",
                    None
                )

        )

        db.add(ingreso)

        db.commit()

        db.refresh(ingreso)


        servicios_data = getattr(
            data,
            "servicios",
            []
        )
        if servicios_data:

            for s in servicios_data:

                detalle_servicio = getattr(
                        s,
                        "detalle",
                        None
                    )

                servicio = models.Servicios(

                descripcion=s.descripcion,

                detalle=
                detalle_servicio.strip()
                if detalle_servicio
                else None,

                monto=s.monto,

                costo_servicio=
                s.costo_servicio,

                ingreso_id=ingreso.id

        )
        registrar_actividad(
            db=db,
            tipo="factura",
            accion="crear",
            titulo="Factura creada",
            descripcion=f"Factura #{ingreso.id}",
            referencia_id=ingreso.id
        )
        
        db.add(servicio)

        db.commit()
        
        print(
        "DATA RECIBIDA:",
        data.model_dump()
        )

        return {

            "ok": True,

            "ingreso_id":
                ingreso.id

        }

    except Exception as e:

        print(
            "ERROR REAL:",
            e
        )

        return {
            "error": str(e)
        }





@router.get("/")

def listar_ingresos(

    db: Session = Depends(get_db)

):

    try:

        ingresos = (

            db.query(models.Ingreso)

            .options(

                joinedload(
                    models.Ingreso.cliente
                ),

                joinedload(
                    models.Ingreso.servicios
                ),

                joinedload(
                    models.Ingreso.cita
                ),

                joinedload(
                    models.Ingreso.tratamiento
                )

            )

            .all()

        )

        data = []

        for i in ingresos:

            data.append({

                "id":
                    i.id,

                "cliente_id":
                    i.cliente_id,

                "tratamiento_id":
                    i.tratamiento_id,

                "cliente": {

                    "nombre":
                        i.cliente.nombre,

                    "apellido":
                        i.cliente.apellido,

                    "telefono":
                        i.cliente.telefono

                }

                if i.cliente

                else None,

             

                "tratamiento": {

                    "id":
                        i.tratamiento.id,

                    
                    "servicio":

                        i.tratamiento.servicio.nombre

                    if (
                        i.tratamiento
                        and
                        i.tratamiento.servicio
                    )

                     else None,


                    "pieza":
                        i.tratamiento.pieza,

                    "estado":
                        i.tratamiento.estado,

                    "sesiones_totales":

                        i.tratamiento
                        .sesiones_totales,

                    "sesiones_completadas":

                        i.tratamiento
                        .sesiones_completadas,

                    "costo":
                        i.tratamiento.costo,

                    "pagado":
                        i.tratamiento.pagado,
                    


                }

                if i.tratamiento

                else None,

          
                
                "balance_restante":

                    i.balance_restante or 0,

                "monto_abonado":

                    i.monto_abonado or 0,

                "servicios": [

                    {

                        "descripcion":
                            s.descripcion,
                        
                        "detalle":
                            s.detalle,

                        "monto":
                            s.monto,

                        "costo_servicio":
                            s.costo_servicio

                    }

                    for s in i.servicios

                ],

                "descuento":
                    i.descuento or 0,

                "pagado":
                    i.pagado or False,

                "created_at":

                (

                    i.created_at.isoformat()

                    if i.created_at

                    else None

                ),

                
                "fecha_pago":

                (

                    i.fecha_pago.isoformat()

                    if i.fecha_pago

                    else None

                ),


                "cita_id":
                    i.cita_id

            })

        return data

    except Exception as e:

        print(
            "💥 ERROR REAL:",
            e
        )

        return {
            "error": str(e)
        }



@router.put("/{id}")

def actualizar_ingreso(

    id: int,

    data: IngresoUpdateSchema,

    db: Session = Depends(get_db)

):

    ingreso = (

        db.query(models.Ingreso)

        .filter(
            models.Ingreso.id == id
        )

        .first()

    )

    if not ingreso:

        raise HTTPException(

            status_code=404,

            detail="Ingreso no encontrado"

        )

    ingreso.cliente_id = (
        data.cliente_id
    )

    ingreso.descuento = (
        data.descuento
    )

   

    
    db.query(models.Servicios).filter(
        models.Servicios.ingreso_id == id
    ).delete()


    

    for s in data.servicios:

        nuevo = models.Servicios(

            ingreso_id=id,

            descripcion=s.descripcion,
            
            detalle=
                getattr(
                    s,
                    "detalle",
                    None
                ),

            monto=s.monto,

            costo_servicio=
                s.costo_servicio

        )

        db.add(nuevo)
    registrar_actividad(
        db=db,
        tipo="factura",
        accion="editar",
        titulo="Factura actualizada",
        descripcion=f"Factura #{ingreso.id}",
        referencia_id=ingreso.id
    )
    db.commit()

    db.refresh(ingreso)

    return {

        "id":
            ingreso.id,

        "cliente_id":
            ingreso.cliente_id,

        "tratamiento_id":
            ingreso.tratamiento_id,

        "cliente": {

            "nombre":
                ingreso.cliente.nombre,

            "apellido":
                ingreso.cliente.apellido,

            "telefono":
                ingreso.cliente.telefono

        }

        if ingreso.cliente

        else None,

        "servicios": [

            {

                "descripcion":
                    s.descripcion,
                    
                "detalle":
                    s.detalle,


                "monto":
                    s.monto,

                "costo_servicio":
                    s.costo_servicio

            }

            for s in ingreso.servicios

        ],

        "descuento":
            ingreso.descuento or 0,

        "pagado":
            ingreso.pagado or False,

        "created_at":

            ingreso.created_at.isoformat()

            if ingreso.created_at

            else None

    }



@router.put("/{id}/pagar")

def marcar_pagado(

    id: int,

    db: Session = Depends(get_db)

):

    ingreso = (

        db.query(models.Ingreso)

        .options(

            joinedload(
                models.Ingreso.servicios
            )

        )

        .filter(
            models.Ingreso.id == id
        )

        .first()

    )

    if not ingreso:

        raise HTTPException(

            status_code=404,

            detail="No encontrado"

        )

    if ingreso.pagado:

        raise HTTPException(

            status_code=400,

            detail="La factura ya fue pagada"

        )

    ingreso.pagado = True

    ingreso.fecha_pago = (
        datetime.now(timezone.utc)
    )

   

    if ingreso.cita_id:

        cita = (

            db.query(models.Cita)

            .filter(
                models.Cita.id
                == ingreso.cita_id
            )

            .first()

        )

        if cita:

            cita.estado = (
                "completada"
            )

  

    if ingreso.tratamiento_id:

        tratamiento = (

            db.query(models.Tratamiento)

            .filter(
                models.Tratamiento.id
                ==
                ingreso.tratamiento_id
            )

            .first()

        )

        if tratamiento:

           

            total_pagado = sum(

                s.monto

                for s in ingreso.servicios

            )

            tratamiento.pagado = (

                float(tratamiento.pagado or 0)

                +

                float(total_pagado)

            )

            

            tratamiento.sesiones_completadas += 1


            if tratamiento.pagado > tratamiento.costo:

             tratamiento.pagado = (
            tratamiento.costo
            )

            balance = (

            float(tratamiento.costo or 0)

            -

            float(tratamiento.pagado or 0)

            )
            
            ingreso.balance_restante = balance

            ingreso.monto_abonado = total_pagado

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

    
    registrar_actividad(
        db=db,
        tipo="factura",
        accion="pagar",
        titulo="Factura pagada",
        descripcion=f"Factura #{ingreso.id}",
        referencia_id=ingreso.id
    )

    db.commit()

    db.refresh(ingreso)

    return {

        "id":
            ingreso.id,

        "cliente_id":
            ingreso.cliente_id,

        "tratamiento_id":
            ingreso.tratamiento_id,

        "pagado":
            ingreso.pagado,

        "fecha_pago":

            (

                ingreso.fecha_pago.isoformat()

                if ingreso.fecha_pago

                else None

            )

    }



@router.post("/{ingreso_id}/factura")

async def guardar_factura(

    ingreso_id: int,

    file: UploadFile = File(...)

):

    filename = (
        f"{uuid.uuid4()}_{file.filename}"
    )

    ruta = f"facturas/{filename}"

    with open(ruta, "wb") as f:

        f.write(
            await file.read()
        )

    return {

        "message":
            "Factura guardada ✅",

        "archivo":
            ruta,

        "ingreso_id":
            ingreso_id

    }