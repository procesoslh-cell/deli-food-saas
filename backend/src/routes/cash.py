
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from src.db.session import get_db
from src.models.models import CashSession, Payment, PaymentMethodType, Customer, AccountMovement
router=APIRouter(prefix='/cash', tags=['cash'])
class OpenCash(BaseModel): branch_id:int; opening_amount:float=0; opened_by_id:int|None=None
class CloseCash(BaseModel): closing_amount:float
class AccountPayment(BaseModel): customer_id:int; amount:float; description:str='Pago cuenta corriente'
@router.get('/sessions')
def sessions(db:Session=Depends(get_db)): return db.query(CashSession).order_by(CashSession.opened_at.desc()).limit(50).all()
@router.post('/open')
def open_cash(p:OpenCash, db:Session=Depends(get_db)):
    c=CashSession(branch_id=p.branch_id, opening_amount=p.opening_amount, opened_by_id=p.opened_by_id); db.add(c); db.commit(); db.refresh(c); return c
@router.post('/{session_id}/close')
def close_cash(session_id:int,p:CloseCash,db:Session=Depends(get_db)):
    c=db.get(CashSession,session_id)
    if not c: raise HTTPException(404,'Caja no encontrada')
    payments=db.query(func.coalesce(func.sum(Payment.amount),0)).filter(Payment.cash_session_id==session_id, Payment.method!=PaymentMethodType.account).scalar() or 0
    c.expected_amount=round(c.opening_amount+float(payments),2); c.closing_amount=p.closing_amount; c.difference=round(p.closing_amount-c.expected_amount,2); c.status='closed'; c.closed_at=datetime.utcnow(); db.commit(); db.refresh(c); return c
@router.get('/accounts/customers')
def customers(db:Session=Depends(get_db)): return db.query(Customer).filter(Customer.active==True).order_by(Customer.name).all()
@router.post('/accounts/payment')
def account_payment(p:AccountPayment, db:Session=Depends(get_db)):
    cust=db.get(Customer,p.customer_id)
    if not cust: raise HTTPException(404,'Cliente no encontrado')
    cust.balance -= p.amount
    mov=AccountMovement(customer_id=cust.id, amount=-p.amount, description=p.description)
    db.add(mov); db.commit(); db.refresh(mov); return mov
