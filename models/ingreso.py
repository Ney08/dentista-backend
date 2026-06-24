from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone



class Ingreso(Base):
    __tablename__ = "ingresos"

    id = Column(Integer, primary_key=True, index=True)
    
    created_at = Column(DateTime(timezone=True),default=lambda: datetime.now(timezone.utc))


    cliente_id = Column(Integer, ForeignKey("clientes.id"))

    cliente = relationship("Cliente", back_populates="ingresos")

    servicios = relationship(
        "Servicios",
        back_populates="ingreso",
        cascade="all, delete"
    )
    
    descuento = Column(Float, default=0)
    pagado = Column(Boolean, default=False)
    
    balance_restante = Column(Float, default=0)   

    monto_abonado = Column(Float, default=0)
    
    fecha_pago = Column(DateTime(timezone=True),nullable=True)
    tratamiento_id = Column(

    Integer,

    ForeignKey(
        "tratamientos.id"
    ),

    nullable=True

)

    tratamiento = relationship(
    "Tratamiento"
    )

    
    cita_id = Column(Integer, ForeignKey("citas.id"), nullable=True)

    cita = relationship("Cita")
    
    
class Servicios(Base):
    __tablename__ = "servicios"

    id = Column(Integer, primary_key=True)
    descripcion = Column(String)
    monto = Column(Float)
    detalle = Column(String, nullable=True)
    costo_servicio = Column(Float, default=0)

    ingreso_id = Column(Integer, ForeignKey("ingresos.id"))

    ingreso = relationship("Ingreso", back_populates="servicios")