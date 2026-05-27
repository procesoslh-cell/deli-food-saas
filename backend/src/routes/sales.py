
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from src.db.session import get_db
from src.models.models import Sale, SaleItem, Product, SaleStatus, Payment, PaymentMethodType, Customer, AccountMovement
router = APIRouter(prefix='/sales', tags=['sales'])
class SaleItemIn(BaseModel): product_id:int; quantity:float; unit_price:float|None=None
class PaymentIn(BaseModel): method:PaymentMethodType=PaymentMethodType.cash; amount:float; reference:str=''; cash_session_id:int|None=None
class SaleIn(BaseModel): customer_id:int|None=None; branch_id:int|None=None; customer_name:str='Consumidor final'; status:SaleStatus=SaleStatus.quote; items:List[SaleItemIn]; payments:List[PaymentIn]=[]; notes:str=''
@router.get('')
def list_sales(db:Session=Depends(get_db)): return db.query(Sale).order_by(Sale.created_at.desc()).limit(100).all()
@router.post('')
def create_sale(payload:SaleIn, db:Session=Depends(get_db)):
    customer = db.get(Customer,payload.customer_id) if payload.customer_id else None
    sale=Sale(customer_id=payload.customer_id, branch_id=payload.branch_id, customer_name=customer.name if customer else payload.customer_name, status=payload.status, notes=payload.notes)
    subtotal=0
    for incoming in payload.items:
        product=db.get(Product,incoming.product_id)
        if not product: raise HTTPException(404,'Producto no encontrado')
        price=incoming.unit_price if incoming.unit_price is not None else (product.manual_price or product.suggested_price)
        line=round(price*incoming.quantity,2)
        if payload.status==SaleStatus.invoiced:
            if product.stock < incoming.quantity: raise HTTPException(400,f'Stock insuficiente de {product.name}')
            product.stock -= incoming.quantity
        subtotal += line; sale.items.append(SaleItem(product_id=product.id, quantity=incoming.quantity, unit_price=price, total=line))
    sale.subtotal=round(subtotal,2); sale.total=sale.subtotal
    paid=0
    for p in payload.payments:
        sale.payments.append(Payment(method=p.method, amount=p.amount, reference=p.reference, cash_session_id=p.cash_session_id)); paid+=p.amount
    sale.paid_total=round(paid,2)
    if payload.status==SaleStatus.invoiced and customer and paid < sale.total:
        diff=round(sale.total-paid,2); customer.balance += diff; sale.payments.append(Payment(method=PaymentMethodType.account, amount=diff, reference='Cuenta corriente')); sale.paid_total=sale.total
        sale.notes=(sale.notes+' | ' if sale.notes else '')+f'Saldo a cuenta corriente: {diff}'
        db.add(AccountMovement(customer_id=customer.id, amount=diff, description='Venta en cuenta corriente'))
    db.add(sale); db.commit(); db.refresh(sale); return sale
@router.post('/{sale_id}/invoice')
def invoice_sale(sale_id:int, db:Session=Depends(get_db)):
    sale=db.get(Sale,sale_id)
    if not sale: raise HTTPException(404,'Venta no encontrada')
    if sale.status==SaleStatus.invoiced: return sale
    for item in sale.items:
        if item.product.stock < item.quantity: raise HTTPException(400,f'Stock insuficiente de {item.product.name}')
    for item in sale.items: item.product.stock -= item.quantity
    sale.status=SaleStatus.invoiced; sale.arca_status='ready_for_future_integration'; db.commit(); db.refresh(sale); return sale

@router.delete('/{sale_id}')
def delete_sale(sale_id:int, restore_stock: bool = True, db:Session=Depends(get_db)):
    sale=db.get(Sale,sale_id)
    if not sale: raise HTTPException(404,'Venta no encontrada')
    if sale.status==SaleStatus.invoiced and restore_stock:
        for item in sale.items:
            if item.product:
                item.product.stock += item.quantity
    sale.status=SaleStatus.cancelled
    sale.notes=(sale.notes+' | ' if sale.notes else '')+'Venta anulada/eliminada desde frontend'
    db.commit(); db.refresh(sale); return {'ok':True,'sale_id':sale.id,'status':sale.status}
