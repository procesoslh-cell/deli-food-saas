from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import hashlib
import os
import secrets
from src.db.session import get_db
from src.models.models import User

router = APIRouter(prefix='/auth', tags=['auth'])

def hash_password(password: str) -> str:
    secret = os.getenv('SECRET_KEY', 'deli-food-local-secret')
    return hashlib.sha256((secret + '::' + password).encode('utf-8')).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    if not password_hash:
        return False
    return secrets.compare_digest(hash_password(password), password_hash)

class LoginIn(BaseModel):
    email: str
    password: str

class ChangePasswordIn(BaseModel):
    email: str
    current_password: str
    new_password: str

@router.post('/login')
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email, User.active == True).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail='Usuario o contraseña incorrectos')
    return {
        'token': 'local-session-token',
        'user': {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'role': user.role.name if user.role else 'Usuario',
            'branch': user.branch.name if user.branch else 'Deli Food'
        }
    }

@router.post('/change-password')
def change_password(payload: ChangePasswordIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email, User.active == True).first()
    if not user or not verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=401, detail='Usuario o contraseña actual incorrectos')
    if len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail='La nueva contraseña debe tener al menos 6 caracteres')
    user.password_hash = hash_password(payload.new_password)
    db.commit()
    return {'ok': True, 'message': 'Contraseña actualizada'}
