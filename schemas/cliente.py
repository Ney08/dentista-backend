from pydantic import BaseModel
from typing import Optional


class ClienteCreate(BaseModel):
    nombre: str
    apellido: str
    cedula: str
    telefono: str
    direccion: DireccionBase
    activo: bool = True

class Cliente(ClienteCreate):
    id: int

    class Config:
        from_attributes = True
        
        
        
        
# ✅ DIRECCIÓN
class DireccionBase(BaseModel):
    provincia_nombre: Optional[str] = None
    municipio_nombre: Optional[str] = None
    distrito_nombre: Optional[str] = None
    seccion_nombre: Optional[str] = None
    barrio_nombre: Optional[str] = None
    calle: Optional[str] = None


# ✅ CREATE / INPUT
class DireccionCreate(DireccionBase):
    pass


# ✅ RESPONSE
class Direccion(DireccionBase):
    id: int

    class Config:
        from_attributes = True



# ✅ IMPORTANTE Pydantic v2
ClienteCreate.model_rebuild()
Cliente.model_rebuild()
