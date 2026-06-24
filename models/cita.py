from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import relationship

from database import Base


class Cita(Base):

    __tablename__ = "citas"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    cliente_id = Column(
        Integer,
        ForeignKey("clientes.id")
    )

    tratamiento_id = Column(

        Integer,

        ForeignKey(
            "tratamientos.id"
        ),

        nullable=True

    )

    fecha = Column(DateTime)

    estado = Column(
        String,
        default="pendiente"
    )

    motivo = Column(String)

    detalle = Column(
        String,
        nullable=True
    )

    duracion = Column(
        Integer,
        default=30
    )

    

    cliente = relationship(
        "Cliente"
    )

    tratamiento = relationship(
        "Tratamiento"
    )
