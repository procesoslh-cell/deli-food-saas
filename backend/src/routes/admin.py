
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.db.session import get_db
from src.models.models import User, Role, Branch
router = APIRouter(prefix='/admin', tags=['admin'])
class BranchIn(BaseModel): name:str; address:str=''
class RoleIn(BaseModel): name:str; permissions:str=''
class UserIn(BaseModel): name:str; email:str; role_id:int; branch_id:int
@router.get('/branches')
def branches(db:Session=Depends(get_db)): return db.query(Branch).filter(Branch.active==True).all()
@router.post('/branches')
def create_branch(p:BranchIn, db:Session=Depends(get_db)): b=Branch(**p.model_dump()); db.add(b); db.commit(); db.refresh(b); return b
@router.get('/roles')
def roles(db:Session=Depends(get_db)): return db.query(Role).all()
@router.post('/roles')
def create_role(p:RoleIn, db:Session=Depends(get_db)): r=Role(**p.model_dump()); db.add(r); db.commit(); db.refresh(r); return r
@router.get('/users')
def users(db:Session=Depends(get_db)): return db.query(User).filter(User.active==True).all()
@router.post('/users')
def create_user(p:UserIn, db:Session=Depends(get_db)): u=User(**p.model_dump()); db.add(u); db.commit(); db.refresh(u); return u
