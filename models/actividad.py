from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime
)

from datetime import (
    datetime,
    timezone
)

from database import Base


class ActividadSistema(Base):

    __tablename__ = "actividad_sistema"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    tipo = Column(
        String,
        nullable=False
    )

    accion = Column(
        String,
        nullable=False
    )

    titulo = Column(
        String,
        nullable=False
    )

    descripcion = Column(
        String,
        nullable=True
    )

    referencia_id = Column(
        Integer,
        nullable=True
    )

    usuario = Column(
        String,
        nullable=True
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )
