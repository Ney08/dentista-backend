from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ActividadCreate(BaseModel):

    tipo: str

    accion: str

    titulo: str

    descripcion: Optional[str] = None

    referencia_id: Optional[int] = None

    usuario: Optional[str] = None


class ActividadOut(BaseModel):

    id: int

    tipo: str

    accion: str

    titulo: str

    descripcion: Optional[str] = None

    referencia_id: Optional[int] = None

    usuario: Optional[str] = None

    created_at: datetime

    class Config:
        from_attributes = True