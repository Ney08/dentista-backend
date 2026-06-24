from sqlalchemy import (
    Column,
    Integer,
    String,
    Float
)

from database import Base


class ServicioCatalogo(Base):

    __tablename__ = "servicios_catalogo"

    id = Column(Integer, primary_key=True, index=True)

    nombre = Column(String, nullable=False)

    descripcion = Column(String, nullable=True)

    precio = Column(Float, nullable=False)

    costo_servicio = Column(Float, default=0)
