
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import models
from database import get_db
from schemas import UserCreate, UserLogin, UserUpdate
from security import hash_password, verify_password


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)





# =========================
# ✅ USUARIOS (LOGIN REAL)
# =========================

@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):

    existe = db.query(models.User).filter_by(username=data.username).first()

    if existe:
        raise HTTPException(400, "Usuario ya existe ❌")

    nuevo = models.User(
        username=data.username,
        password=hash_password(data.password)
    )

    db.add(nuevo)
    db.commit()

    return {"msg": "Usuario creado ✅"}


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):

    user = db.query(models.User).filter_by(username=data.username).first()
    print("RECIBIDO:", data)
    if not user:
        raise HTTPException(400, "Usuario no existe ❌")

    if not verify_password(data.password, user.password):
        raise HTTPException(400, "Contraseña incorrecta ❌")

    return {
        "token": "fake-jwt-for-now",
        "user": user.username
    }



@router.put("/users/reset")
def reset_password(data: UserCreate, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.username == data.username).first()

    if not user:
        raise HTTPException(404, "Usuario no encontrado ❌")

    user.password = hash_password(data.password)

    db.commit()

    return {"msg": "Contraseña actualizada ✅"}


@router.put("/users/{user_id}")
def actualizar_usuario(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(404, "Usuario no encontrado ❌")

    if data.username:
        user.username = data.username

    if data.password:
        user.password = hash_password(data.password)

    db.commit()

    return {"msg": "Usuario actualizado ✅"}