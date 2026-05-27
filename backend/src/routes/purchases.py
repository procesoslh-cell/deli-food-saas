
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from src.db.session import get_db
from src.models.models import Supplier, PurchaseOrder, PurchaseItem, Product
router=APIRouter(prefix='/purchases', tags=['purchases'])
class SupplierIn(BaseModel): name:str; cuit:str=''; phone:str=''; email:str=''
class PurchaseItemIn(BaseModel): product_id:int; quantity:float; unit_cost:float
class PurchaseIn(BaseModel): supplier_id:int; branch_id:int|None=None; status:str='received'; items:List[PurchaseItemIn]; notes:str=''
@router.get('/suppliers')
def suppliers(db:Session=Depends(get_db)): return db.query(Supplier).filter(Supplier.active==True).order_by(Supplier.name).all()
@router.post('/suppliers')
def create_supplier(p:SupplierIn, db:Session=Depends(get_db)): s=Supplier(**p.model_dump()); db.add(s); db.commit(); db.refresh(s); return s
@router.get('')
def purchases(db:Session=Depends(get_db)): return db.query(PurchaseOrder).order_by(PurchaseOrder.created_at.desc()).limit(100).all()
@router.post('')
def create_purchase(p:PurchaseIn, db:Session=Depends(get_db)):
    if not db.get(Supplier,p.supplier_id): raise HTTPException(404,'Proveedor no encontrado')
    po=PurchaseOrder(supplier_id=p.supplier_id, branch_id=p.branch_id, status=p.status, notes=p.notes); total=0
    for it in p.items:
        prod=db.get(Product,it.product_id)
        if not prod: raise HTTPException(404,'Producto no encontrado')
        line=round(it.quantity*it.unit_cost,2); total+=line
        po.items.append(PurchaseItem(product_id=prod.id, quantity=it.quantity, unit_cost=it.unit_cost, total=line))
        if p.status=='received': prod.stock += it.quantity; prod.cost=it.unit_cost; prod.suggested_price=round(prod.cost*(1+prod.margin_percent/100),2)
    po.total=round(total,2); db.add(po); db.commit(); db.refresh(po); return po
@router.get('/replenishment')
def replenishment(db:Session=Depends(get_db)):
    rows=[]
    for p in db.query(Product).filter(Product.active==True).all():
        threshold=max(p.min_stock or 0, p.reorder_point or 0)
        if p.stock <= threshold:
            suggested=max((threshold*2)-p.stock, 1)
            rows.append({'product_id':p.id,'sku':p.sku,'name':p.name,'stock':p.stock,'threshold':threshold,'suggested_quantity':round(suggested,2),'supplier':p.supplier.name if p.supplier else 'Sin proveedor'})
    return rows
