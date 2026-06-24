from pydantic import BaseModel
import datetime

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
