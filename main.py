from fastapi import FastAPI, Depends, File, UploadFile, Form, HTTPException
from sqlalchemy.orm import Session, joinedload
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
from sqlalchemy.exc import IntegrityError
from database import SessionLocal, engine
from sqlalchemy import text
import models
from schemas import UserCreate, UserLogin, ClienteCreate, IngresoCreate, HistorialCreate, CitaCreate, ServicioSchema, IngresoUpdateSchema
from fastapi import APIRouter
from fastapi import HTTPException, Depends

router = APIRouter()

# ✅ Seguridad
from security import hash_password, verify_password

# ✅ Crear tablas
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# ✅ Crear carpeta facturas
if not os.path.exists("facturas"):
    os.makedirs("facturas")

# ✅ CORS


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ✅ DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# =========================
# ✅ USUARIOS (LOGIN REAL)
# =========================

@app.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):

    existe = db.query(models.User).filter_by(username=data.username).first()

    if existe:
        raise HTTPException(400, "Usuario ya existe ❌")

    nuevo = models.User(
        username=data.username,
        password=hash_password(data.password)
    )

    db.add(nuevo)
    db.commit()

    return {"msg": "Usuario creado ✅"}


@app.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):

    user = db.query(models.User).filter_by(username=data.username).first()
    print("RECIBIDO:", data)
    if not user:
        raise HTTPException(400, "Usuario no existe ❌")

    if not verify_password(data.password, user.password):
        raise HTTPException(400, "Contraseña incorrecta ❌")

    return {
        "token": "fake-jwt-for-now",
        "user": user.username
    }

# @app.put("/users/{user_id}")
# def actualizar_usuario(user_id: int, data: schemas.UserCreate, db: Session = Depends(get_db)):

#     user = db.query(models.User).filter(models.User.id == user_id).first()

#     if not user:
#         raise HTTPException(404, "Usuario no encontrado ❌")

#     # ✅ actualizar username
#     user.username = data.username

#     # ✅ actualizar password (IMPORTANTE → hash)
#     user.password = hash_password(data.password)

#     db.commit()

#     return {"msg": "Usuario actualizado ✅"}



@app.put("/users/reset")
def reset_password(data: UserCreate, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.username == data.username).first()

    if not user:
        raise HTTPException(404, "Usuario no encontrado ❌")

    user.password = hash_password(data.password)

    db.commit()

    return {"msg": "Contraseña actualizada ✅"}


# =========================
# CLIENTES
# =========================




import re

@app.post("/clientes/")
def crear_cliente(data: ClienteCreate, db: Session = Depends(get_db)):

    # ✅ limpiar cédula
    cedula = data.cedula.strip()

    # ✅ VALIDAR SI YA EXISTE
    existe = db.query(models.Cliente).filter(
        models.Cliente.cedula == cedula
    ).first()

    if existe:
        return {"error": "La cédula ya está registrada ❌"}

    # ✅ crear cliente
    nuevo_cliente = models.Cliente(
        nombre=data.nombre,
        apellido=data.apellido,
        cedula=cedula,
        telefono=data.telefono
    )

    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)

    # ✅ crear dirección
    direccion = models.Direccion(
        provincia_nombre=data.direccion.provincia_nombre,
        municipio_nombre=data.direccion.municipio_nombre,
        distrito_nombre=data.direccion.distrito_nombre,
        seccion_nombre=data.direccion.seccion_nombre,
        barrio_nombre=data.direccion.barrio_nombre,
        calle=data.direccion.calle,
        cliente_id=nuevo_cliente.id
    )

    db.add(direccion)
    db.commit()

    return nuevo_cliente




@app.get("/clientes/")
def listar_clientes(db: Session = Depends(get_db), cedula: str = None):

    query = db.query(models.Cliente).options(
        joinedload(models.Cliente.direccion)
    )

    if cedula:
        return query.filter(models.Cliente.cedula == cedula.strip()).all()

    return query.all()


@app.put("/clientes/{cliente_id}")
def actualizar_cliente(cliente_id: int, data: ClienteCreate, db: Session = Depends(get_db)):

    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()

    if not cliente:
        raise HTTPException(404, "Cliente no encontrado ❌")

    # ✅ actualizar cliente
    cliente.nombre = data.nombre
    cliente.apellido = data.apellido
    cliente.telefono = data.telefono

    # ✅ actualizar dirección
    direccion = db.query(models.Direccion).filter(
        models.Direccion.cliente_id == cliente_id
    ).first()
    
    print("📥 DATA RECIBIDA:", data)
    print("📍 DIRECCION RECIBIDA:", data.direccion)

    if direccion:
        
        print("🏙️ PROVINCIA:", data.direccion.provincia_nombre)
        print("🏘️ MUNICIPIO:", data.direccion.municipio_nombre)

        direccion.provincia_nombre = data.direccion.provincia_nombre
        direccion.municipio_nombre = data.direccion.municipio_nombre
        direccion.distrito_nombre = data.direccion.distrito_nombre
        direccion.barrio_nombre = data.direccion.barrio_nombre
        direccion.seccion_nombre = data.direccion.seccion_nombre
        direccion.calle = data.direccion.calle

    else:
        direccion = models.Direccion(
            provincia_nombre=data.direccion.provincia_nombre,
            municipio_nombre=data.direccion.municipio_nombre,
            distrito_nombre=data.direccion.distrito_nombre,
            barrio_nombre=data.direccion.barrio_nombre,
            seccion_nombre=data.direccion.seccion_nombre,
            calle=data.direccion.calle,
            cliente_id=cliente_id
        )
        db.add(direccion)

    db.commit()
    db.refresh(cliente)

    return cliente


@app.delete("/clientes/{cliente_id}")
def eliminar_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(models.Cliente).filter(models.Cliente.id == cliente_id).first()

    if cliente:
        db.delete(cliente)
        db.commit()
        return {"mensaje": "Cliente eliminado"}

    raise HTTPException(404, "Cliente no encontrado")


# =========================
# INGRESOS (FACTURAS)
# =========================

@app.post("/ingresos/")
def crear_ingreso(data: IngresoCreate, db: Session = Depends(get_db)):

    try:
        print("DATA RECIBIDA:", data.dict())

        ingreso = models.Ingreso(
            cliente_id=data.cliente_id,
            descuento=getattr(data, "descuento", 0) or 0,
            pagado=False,
            cita_id=getattr(data, "cita_id", None)
        )

        db.add(ingreso)
        db.commit()
        db.refresh(ingreso)

        # ✅ PROTEGER SI servicios viene vacío
        servicios_data = getattr(data, "servicios", [])

        if servicios_data:
            for s in servicios_data:
                servicio = models.Servicios(
                    descripcion=s.descripcion,
                    monto=s.monto,
                    ingreso_id=ingreso.id
                )
                db.add(servicio)

        db.commit()

        return {"ok": True}

    except Exception as e:
        print("ERROR REAL:", e)
        return {"error": str(e)}


@app.get("/ingresos/")
def listar_ingresos(db: Session = Depends(get_db)):

    try:
        ingresos = db.query(models.Ingreso).options(
            joinedload(models.Ingreso.cliente),
            joinedload(models.Ingreso.servicios),
            joinedload(models.Ingreso.cita)
        ).all()

        data = []

        for i in ingresos:
            data.append({
                "id": i.id,
                "cliente_id": i.cliente_id,

                "cliente": {
                    "nombre": i.cliente.nombre,
                    "apellido": i.cliente.apellido
                } if i.cliente else None,

                "servicios": [
                    {
                        "descripcion": s.descripcion,
                        "monto": s.monto
                    }
                    for s in i.servicios
                ],

                "descuento": i.descuento or 0,
                "pagado": i.pagado or False,

                "created_at": i.created_at.isoformat() if i.created_at else None,
                "fecha_pago": i.fecha_pago.isoformat() if i.fecha_pago else None,

                "cita_id": i.cita_id
            })

        return data

    except Exception as e:
        print("💥 ERROR REAL:", e)
        return {"error": str(e)}


@app.put("/ingresos/{id}")
def actualizar_ingreso(id: int, data: IngresoUpdateSchema, db: Session = Depends(get_db)):

    ingreso = db.query(models.Ingreso).filter(models.Ingreso.id == id).first()

    if not ingreso:
        raise HTTPException(status_code=404, detail="Ingreso no encontrado")

    ingreso.cliente_id = data.cliente_id
    ingreso.descuento = data.descuento

    # ✅ borrar servicios
    db.query(models.Servicios).filter(models.Servicios.ingreso_id == id).delete()

    # ✅ agregar servicios nuevos
    for s in data.servicios:
        nuevo = models.Servicios(
            ingreso_id=id,
            descripcion=s.descripcion,
            monto=s.monto
        )
        db.add(nuevo)

    db.commit()
    db.refresh(ingreso)

    # ✅ 🔥 IMPORTANTE: reconstruir respuesta igual que GET
    return {
        "id": ingreso.id,
        "cliente_id": ingreso.cliente_id,
        "cliente": {
            "nombre": ingreso.cliente.nombre,
            "apellido": ingreso.cliente.apellido
        } if ingreso.cliente else None,
        "servicios": [
            {
                "descripcion": s.descripcion,
                "monto": s.monto
            }
            for s in ingreso.servicios
        ],
        "descuento": ingreso.descuento or 0,
        "pagado": ingreso.pagado or False,
        "created_at": ingreso.created_at.isoformat() if ingreso.created_at else None
    }







@app.put("/ingresos/{id}/pagar")
def marcar_pagado(id: int, db: Session = Depends(get_db)):

    ingreso = db.query(models.Ingreso).filter(models.Ingreso.id == id).first()

    if not ingreso:
        raise HTTPException(status_code=404, detail="No encontrado")

    # ✅ marcar pagado
    ingreso.pagado = True

    # ✅ guardar fecha_pago
    ingreso.fecha_pago = datetime.utcnow()

    # ✅ 🔥 NUEVO: completar cita automáticamente
    if ingreso.cita_id:
        cita = db.query(models.Cita).filter(models.Cita.id == ingreso.cita_id).first()
        if cita:
            cita.estado = "completada"

    db.commit()
    db.refresh(ingreso)

    # ✅ devolver formato consistente
    return {
        "id": ingreso.id,
        "cliente_id": ingreso.cliente_id,

        "cliente": {
            "nombre": ingreso.cliente.nombre,
            "apellido": ingreso.cliente.apellido
        } if ingreso.cliente else None,

        "servicios": [
            {
                "descripcion": s.descripcion,
                "monto": s.monto
            }
            for s in ingreso.servicios
        ],

        "descuento": ingreso.descuento or 0,
        "pagado": ingreso.pagado,
        "fecha_pago": ingreso.fecha_pago.isoformat() if ingreso.fecha_pago else None,

        # ✅ opcional pero recomendado
        "cita_id": ingreso.cita_id,

        "created_at": ingreso.created_at.isoformat() if ingreso.created_at else None 
    }




# =========================
# FACTURAS PDF
# =========================

@app.post("/facturas/")
async def guardar_factura(
    file: UploadFile = File(...),
    ingreso_id: int = Form(...)
):
    ruta = f"facturas/{file.filename}"

    with open(ruta, "wb") as f:
        f.write(await file.read())

    return {
        "message": "Factura guardada",
        "archivo": ruta,
        "ingreso_id": ingreso_id
    }

# =========================
# HISTORIAL
# =========================


@app.post("/historiales/")
def crear_historial(data: HistorialCreate, db: Session = Depends(get_db)):
    historial = models.Historial(
        cliente_id=data.cliente_id,
        descripcion=data.descripcion
    )

    db.add(historial)
    db.commit()
    db.refresh(historial)

    return historial


@app.get("/clientes/{cliente_id}/historial")
def ver_historial(cliente_id: int, db: Session = Depends(get_db)):
    return db.query(models.Historial).filter(
        models.Historial.cliente_id == cliente_id
    ).all()



# =========================
# CITAS
# =========================
from fastapi import HTTPException

@app.post("/citas/")
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
        motivo=data.motivo,         # ✅ NUEVO
        detalle=data.detalle or None  # ✅ NUEVO
    )

    db.add(cita)
    db.commit()
    db.refresh(cita)

    return cita



@app.get("/citas/")
def listar_citas(db: Session = Depends(get_db)):

    citas = db.query(models.Cita).options(
        joinedload(models.Cita.cliente) ✅🔥
    ).all()

    data = []

    for c in citas:
        data.append({
            "id": c.id,
            "cliente_id": c.cliente_id,

            # ✅ ESTO ES LO QUE TE FALTABA
            "cliente": {
                "nombre": c.cliente.nombre,
                "apellido": c.cliente.apellido
            } if c.cliente else None,

            "fecha": c.fecha.isoformat() if c.fecha else None,
            "estado": c.estado,
            "motivo": c.motivo,
            "detalle": c.detalle
        })

    return data





@app.put("/citas/{id}/completar")
def completar_cita(id: int, db: Session = Depends(get_db)):

    cita = db.query(models.Cita).filter(models.Cita.id == id).first()

    if not cita:
        raise HTTPException(404, "No encontrada")

    cita.estado = "completada"
    db.commit()

    return cita

    

@app.get("/debug/citas")
def debug_citas(db: Session = Depends(get_db)):
    return db.query(models.Cita).all()




@app.put("/citas/{id}/cancelar")
def cancelar_cita(id: int, db: Session = Depends(get_db)):

    cita = db.query(models.Cita).filter(models.Cita.id == id).first()

    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    cita.estado = "cancelada"
    db.commit()

    return cita

@app.put("/citas/{id}")
def actualizar_cita(id: int, data: CitaCreate, db: Session = Depends(get_db)):

    cita = db.query(models.Cita).filter(models.Cita.id == id).first()

    if not cita:
        raise HTTPException(status_code=404, detail="Cita no encontrada")

    cita.cliente_id = data.cliente_id
    cita.fecha = data.fecha
    cita.motivo = data.motivo
    cita.detalle = data.detalle

    db.commit()
    db.refresh(cita)

    return cita





@app.get("/fix-db")
def fix_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("ALTER TABLE ingresos ADD COLUMN fecha_pago TIMESTAMP;"))
        db.commit()
        return {"ok": True}
    except Exception as e:
        return {"error": str(e)}
