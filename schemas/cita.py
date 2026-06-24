from pydantic import BaseModel

from typing import Optional

import datetime


class CitaCreate(BaseModel):

    cliente_id: int

    tratamiento_id: Optional[int] = None

    fecha: datetime.datetime

    motivo: str

    detalle: Optional[str] = None

    duracion: int = 30


class Cita(BaseModel):

    id: int

    cliente_id: int

    tratamiento_id: Optional[int] = None

    fecha: datetime.datetime

    estado: str

    motivo: str

    detalle: Optional[str]

    duracion: int

    class Config:

        from_attributes = True
