from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class EgresoBase(BaseModel):

    descripcion: str

    categoria: str

    monto: float

    metodo_pago: Optional[str] = None

    observacion: Optional[str] = None


class EgresoCreate(EgresoBase):
    pass


class Egreso(EgresoBase):

    id: int

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )