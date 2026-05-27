from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.models.models import User
router=APIRouter(prefix='/auth', tags=['auth'])
class LoginIn(BaseModel): email:str; password:str=''
@router.post('/login')
def login(payload:LoginIn, db:Session=Depends(get_db)):
    user=db.query(User).filter(User.email==payload.email, User.active==True).first()
    if not user:
        raise HTTPException(401,'Usuario no encontrado. Demo: admin@delifood.local')
    return {'token':'demo-local-token','user':{'id':user.id,'name':user.name,'email':user.email,'role':user.role.name if user.role else 'Usuario','branch':user.branch.name if user.branch else 'Deli Food'}}
