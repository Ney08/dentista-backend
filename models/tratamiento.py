
from sqlalchemy import (

    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime

)


from datetime import (
    datetime,
    timezone
)


from sqlalchemy.orm import relationship

from database import Base


class Tratamiento(Base):

    __tablename__ = "tratamientos"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    cliente_id = Column(
        Integer,
        nullable=False
    )


    servicio_id = Column(

        Integer,

        ForeignKey(
            "servicios_catalogo.id"
        ),

        nullable=False

    )

    servicio = relationship(
        "ServicioCatalogo"
    )

    

    pieza = Column(
        String,
        nullable=True
    )

    estado = Column(
        String,
        default="Pendiente"
    )

    sesiones_totales = Column(
        Integer,
        default=1
    )

    sesiones_completadas = Column(
        Integer,
        default=0
    )

    
    
    
    created_at = Column(
        DateTime,
        default=lambda:
        datetime.now(timezone.utc)
    )
  


    costo = Column(
        Float,
        default=0
    )

    pagado = Column(
        Float,
        default=0
    )

    

    notas = Column(
        String,
        nullable=True
    )