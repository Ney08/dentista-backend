from pydantic import BaseModel
from typing import List, Optional
import datetime


class ServicioSchema(BaseModel):
    descripcion: str
    monto: float

# ✅ USUARIOS
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str



class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None


class ResetPassword(BaseModel):
    username: str
    password: str

# ✅ DIRECCIÓN
class DireccionBase(BaseModel):
    provincia_nombre: Optional[str] = None
    municipio_nombre: Optional[str] = None
    distrito_nombre: Optional[str] = None
    seccion_nombre: Optional[str] = None
    barrio_nombre: Optional[str] = None
    calle: Optional[str] = None


# ✅ CREATE / INPUT
class DireccionCreate(DireccionBase):
    pass


# ✅ RESPONSE
class Direccion(DireccionBase):
    id: int

    class Config:
        from_attributes = True



# ✅ CLIENTE
class ClienteCreate(BaseModel):
    nombre: str
    apellido: str
    cedula: str
    telefono: str
    direccion: DireccionBase
    activo: bool = True

class Cliente(ClienteCreate):
    id: int

    class Config:
        from_attributes = True


# ✅ SERVICIOS (IMPORTANTE 🔥)
class Servicio(BaseModel):
    descripcion: str
    monto: float


# ✅ INGRESOS
class IngresoCreate(BaseModel):
    cliente_id: int
    descuento: float = 0
    cita_id: Optional[int] = None
    servicios: List[Servicio]

class Ingreso(BaseModel):
    id: int
    cliente_id: int
    descuento: float
    pagado: bool = False
    servicios: List[Servicio]

    class Config:
        from_attributes = True

class IngresoUpdateSchema(BaseModel):
    cliente_id: int
    descuento: Optional[float] = 0
    servicios: List[ServicioSchema]


# ✅ HISTORIAL
class HistorialCreate(BaseModel):
    cliente_id: int
    descripcion: str

class HistorialOut(BaseModel):
    id: int
    cliente_id: int
    descripcion: str
    fecha: datetime.datetime

    class Config:
        from_attributes = True


# ✅ CITAS

class CitaCreate(BaseModel):
    cliente_id: int
    fecha: datetime.datetime

   
    motivo: str
    detalle: Optional[str] = None
    duracion: int = 30


class Cita(BaseModel):
    id: int
    cliente_id: int
    fecha: datetime.datetime
    estado: str

   
    motivo: str
    detalle: Optional[str]
    duracion: int
    class Config:
        from_attributes = True  