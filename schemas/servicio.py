from pydantic import (
    BaseModel,
    ConfigDict
)

from typing import Optional


class ServicioBase(BaseModel):

    nombre: str

    descripcion: Optional[str] = None

    precio: float

    costo_servicio: float = 0


class ServicioCreate(ServicioBase):
    pass


class Servicio(ServicioBase):

    id: int

    model_config = ConfigDict(
        from_attributes=True
    )