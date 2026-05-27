
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from src.db.session import get_db
from src.models.models import Product, ProductType
from src.services.pricing import suggested_price
router = APIRouter(prefix='/products', tags=['products'])
class ProductIn(BaseModel):
    sku: str; name: str; category_id: int; product_type: ProductType = ProductType.resale; unit: str = 'unidad'; barcode: Optional[str] = None; supplier_id: Optional[int]=None; branch_id: Optional[int]=None; stock: float = 0; min_stock: float = 0; reorder_point: float = 0; lead_time_days:int=3; cost: float = 0; margin_percent: float = 35; manual_price: Optional[float] = None
class StockMove(BaseModel): quantity_delta: float; reason: str='Ajuste manual'
@router.get('')
def list_products(search: str = '', db: Session = Depends(get_db)):
    q = db.query(Product).filter(Product.active == True)
    if search: q = q.filter((Product.name.ilike(f'%{search}%')) | (Product.sku.ilike(f'%{search}%')) | (Product.barcode.ilike(f'%{search}%')))
    return q.order_by(Product.name).all()
@router.post('')
def create_product(payload: ProductIn, db: Session = Depends(get_db)):
    data = payload.model_dump(); data['suggested_price'] = suggested_price(data['cost'], data['margin_percent'])
    product = Product(**data); db.add(product); db.commit(); db.refresh(product); return product
@router.put('/{product_id}')
def update_product(product_id:int, payload:ProductIn, db:Session=Depends(get_db)):
    product=db.get(Product, product_id)
    if not product: raise HTTPException(404,'Producto no encontrado')
    data=payload.model_dump(); data['suggested_price']=suggested_price(data['cost'], data['margin_percent'])
    for k,v in data.items(): setattr(product,k,v)
    db.commit(); db.refresh(product); return product
@router.patch('/{product_id}/stock')
def update_stock(product_id: int, payload:StockMove, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if not product: raise HTTPException(404, 'Producto no encontrado')
    product.stock += payload.quantity_delta
    db.commit(); db.refresh(product); return product
