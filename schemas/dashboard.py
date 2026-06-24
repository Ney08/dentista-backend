from pydantic import BaseModel


class DashboardResumen(BaseModel):

    ingresos: float

    egresos: float

    caja: float

    ganancia_bruta: float

    ganancia_neta: float

    pendiente: float
