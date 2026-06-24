from pydantic import BaseModel
from typing import  Optional



# class ServicioSchema(BaseModel):
#     descripcion: str
#     monto: float

# ✅ USUARIOS
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str



class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None


class ResetPassword(BaseModel):
    username: str
    password: str