from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime



class Historial(Base):
    __tablename__ = "historiales"

    id = Column(Integer, primary_key=True)

    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    descripcion = Column(String)
    fecha = Column(DateTime, default=datetime.utcnow)

    cliente = relationship("Cliente")
