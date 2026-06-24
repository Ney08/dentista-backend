from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base



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

    cliente = relationship("Cliente", back_populates="direccion")


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String)
    apellido = Column(String) 
    cedula = Column(String, unique=True, index=True)
    telefono = Column(String)
    direccion = relationship("Direccion", back_populates="cliente", uselist=False)
    activo = Column(Boolean, default=True)
    ingresos = relationship("Ingreso", back_populates="cliente")