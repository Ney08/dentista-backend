from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text
)

from datetime import datetime

from database import Base


class Egreso(Base):

    __tablename__ = "egresos"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    descripcion = Column(
        String,
        nullable=False
    )

    categoria = Column(
        String,
        nullable=False
    )

    monto = Column(
        Float,
        nullable=False
    )

    metodo_pago = Column(
        String,
        nullable=True
    )

    observacion = Column(
        Text,
        nullable=True
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )