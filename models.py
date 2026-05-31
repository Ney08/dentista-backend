from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)


class Direccion(Base):
    __tablename__ = "direcciones"

    id = Column(Integer, primary_key=True)

    provincia_nombre = Column(String)
    municipio_nombre = Column(String)
    distrito_nombre = Column(String)
    seccion_nombre = Column(String)
    barrio_nombre = Column(String)
    calle = Column(String)

    cliente_id = Column(Integer, ForeignKey("clientes.id"))

    # ✅ ESTA LÍNEA ES LA QUE FALTA
    cliente = relationship("Cliente", back_populates="direccion")


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String)
    apellido = Column(String) 
    cedula = cedula = Column(String, unique=True, index=True)
    telefono = Column(String)
    direccion = relationship("Direccion", back_populates="cliente")

    ingresos = relationship("Ingreso", back_populates="cliente")


class Ingreso(Base):
    __tablename__ = "ingresos"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    cliente_id = Column(Integer, ForeignKey("clientes.id"))

    cliente = relationship("Cliente", back_populates="ingresos")

    servicios = relationship(
        "Servicios",
        back_populates="ingreso",
        cascade="all, delete"
    )
    
    descuento = Column(Float, default=0)
    pagado = Column(Boolean, default=False)



class Servicios(Base):
    __tablename__ = "servicios"

    id = Column(Integer, primary_key=True)
    descripcion = Column(String)
    monto = Column(Float)

    ingreso_id = Column(Integer, ForeignKey("ingresos.id"))

    ingreso = relationship("Ingreso", back_populates="servicios")







class Historial(Base):
    __tablename__ = "historiales"

    id = Column(Integer, primary_key=True)

    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    descripcion = Column(String)
    fecha = Column(DateTime, default=datetime.utcnow)

    cliente = relationship("Cliente")






from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship

class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True)

    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    fecha = Column(DateTime)

    estado = Column(String, default="pendiente")

    # ✅ NUEVOS CAMPOS
    motivo = Column(String)
    detalle = Column(String, nullable=True)

    cliente = relationship("Cliente")
