from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.db.session import get_db
from src.models.models import User, Role, Branch
from src.routes.auth import hash_password

router = APIRouter(prefix='/admin', tags=['admin'])

class BranchIn(BaseModel):
    name: str
    address: str = ''

class RoleIn(BaseModel):
    name: str
    permissions: str = ''

class UserIn(BaseModel):
    name: str
    email: str
    password: str
    role_id: int
    branch_id: int

class PasswordResetIn(BaseModel):
    password: str

@router.get('/branches')
def branches(db: Session = Depends(get_db)):
    return db.query(Branch).filter(Branch.active == True).all()

@router.post('/branches')
def create_branch(p: BranchIn, db: Session = Depends(get_db)):
    b = Branch(**p.model_dump())
    db.add(b)
    db.commit()
    db.refresh(b)
    return b

@router.get('/roles')
def roles(db: Session = Depends(get_db)):
    return db.query(Role).all()

@router.post('/roles')
def create_role(p: RoleIn, db: Session = Depends(get_db)):
    r = Role(**p.model_dump())
    db.add(r)
    db.commit()
    db.refresh(r)
    return r

@router.get('/users')
def users(db: Session = Depends(get_db)):
    return db.query(User).filter(User.active == True).all()

@router.post('/users')
def create_user(p: UserIn, db: Session = Depends(get_db)):
    if len(p.password) < 6:
        raise HTTPException(status_code=400, detail='La contraseña debe tener al menos 6 caracteres')
    if db.query(User).filter(User.email == p.email).first():
        raise HTTPException(status_code=400, detail='Ya existe un usuario con ese email')
    data = p.model_dump()
    password = data.pop('password')
    u = User(**data, password_hash=hash_password(password))
    db.add(u)
    db.commit()
    db.refresh(u)
    return u

@router.patch('/users/{user_id}/password')
def reset_password(user_id: int, payload: PasswordResetIn, db: Session = Depends(get_db)):
    if len(payload.password) < 6:
        raise HTTPException(status_code=400, detail='La contraseña debe tener al menos 6 caracteres')
    user = db.query(User).filter(User.id == user_id, User.active == True).first()
    if not user:
        raise HTTPException(status_code=404, detail='Usuario no encontrado')
    user.password_hash = hash_password(payload.password)
    db.commit()
    return {'ok': True}
