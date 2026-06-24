from pydantic import BaseModel

from typing import Optional


class TratamientoBase(BaseModel):

    cliente_id: int

    servicio_id: int

    pieza: Optional[str] = None

    estado: Optional[str] = "Pendiente"

    sesiones_totales: int = 1

    sesiones_completadas: int = 0

    costo: float = 0

    pagado: float = 0

    notas: Optional[str] = None


class TratamientoCreate(
    TratamientoBase
):
    pass


class Tratamiento(
    TratamientoBase
):

    id: int

   

    servicio_nombre: Optional[str] = None

    class Config:

        from_attributes = True