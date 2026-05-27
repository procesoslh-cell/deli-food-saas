from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from src.db.session import get_db
from src.models.models import Product, BOMItem, ProductionOrder
from src.services.pricing import suggested_price

router = APIRouter(prefix='/manufacturing', tags=['manufacturing'])

class BOMItemIn(BaseModel):
    material_id: int
    quantity: float
    waste_percent: float = 0

class ProductionIn(BaseModel):
    product_id: int
    quantity: float
    margin_percent: float | None = None
    notes: str = ''

@router.get('/bom/{product_id}')
def get_bom(product_id: int, db: Session = Depends(get_db)):
    return db.query(BOMItem).filter(BOMItem.product_id == product_id).all()

@router.post('/bom/{product_id}')
def add_bom_item(product_id: int, payload: BOMItemIn, db: Session = Depends(get_db)):
    if not db.get(Product, product_id): raise HTTPException(404, 'Producto elaborado no encontrado')
    if not db.get(Product, payload.material_id): raise HTTPException(404, 'Materia prima no encontrada')
    item = BOMItem(product_id=product_id, **payload.model_dump())
    db.add(item); db.commit(); db.refresh(item)
    return item

@router.get('/cost/{product_id}')
def calculate_cost(product_id: int, db: Session = Depends(get_db)):
    items = db.query(BOMItem).filter(BOMItem.product_id == product_id).all()
    total = 0
    details = []
    for item in items:
        needed = item.quantity * (1 + item.waste_percent / 100)
        line = needed * item.material.cost
        total += line
        details.append({'material': item.material.name, 'quantity': item.quantity, 'waste_percent': item.waste_percent, 'line_cost': round(line, 2)})
    return {'product_id': product_id, 'unit_cost': round(total, 2), 'details': details}

@router.post('/produce')
def produce(payload: ProductionIn, db: Session = Depends(get_db)):
    product = db.get(Product, payload.product_id)
    if not product: raise HTTPException(404, 'Producto no encontrado')
    items = db.query(BOMItem).filter(BOMItem.product_id == product.id).all()
    if not items: raise HTTPException(400, 'Cargá la lista de materiales antes de elaborar')
    unit_cost = 0
    for item in items:
        required = item.quantity * payload.quantity * (1 + item.waste_percent / 100)
        if item.material.stock < required:
            raise HTTPException(400, f'Stock insuficiente de {item.material.name}. Requerido: {required} {item.material.unit}')
        item.material.stock -= required
        unit_cost += item.quantity * (1 + item.waste_percent / 100) * item.material.cost
    product.stock += payload.quantity
    product.cost = round(unit_cost, 2)
    if payload.margin_percent is not None:
        product.margin_percent = payload.margin_percent
    product.suggested_price = suggested_price(product.cost, product.margin_percent)
    order = ProductionOrder(product_id=product.id, quantity=payload.quantity, unit_cost=product.cost, total_cost=round(product.cost * payload.quantity, 2), suggested_price=product.suggested_price, notes=payload.notes)
    db.add(order); db.commit(); db.refresh(order)
    return order
