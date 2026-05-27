
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.db.session import get_db
from src.models.models import Product, Sale, SaleItem, SaleStatus, Payment
router = APIRouter(prefix='/dashboard', tags=['dashboard'])
@router.get('/summary')
def summary(db: Session = Depends(get_db)):
    since=datetime.utcnow()-timedelta(days=90)
    revenue=db.query(func.coalesce(func.sum(Sale.total),0)).filter(Sale.status==SaleStatus.invoiced).scalar()
    stock_value=db.query(func.coalesce(func.sum(Product.stock*Product.cost),0)).scalar()
    low_stock=db.query(Product).filter(Product.stock <= func.coalesce(Product.min_stock,0), Product.active==True).all()
    top=(db.query(Product.name,func.sum(SaleItem.quantity).label('qty'),func.sum(SaleItem.total).label('total')).join(SaleItem,Product.id==SaleItem.product_id).join(Sale,Sale.id==SaleItem.sale_id).filter(Sale.status==SaleStatus.invoiced).group_by(Product.id).order_by(func.sum(SaleItem.quantity).desc()).limit(10).all())
    payment_mix=(db.query(Payment.method,func.sum(Payment.amount)).group_by(Payment.method).all())
    forecast=[]
    for p in db.query(Product).filter(Product.active==True).all():
        sold30=(db.query(func.coalesce(func.sum(SaleItem.quantity),0)).join(Sale,Sale.id==SaleItem.sale_id).filter(Sale.status==SaleStatus.invoiced,Sale.created_at>=datetime.utcnow()-timedelta(days=30),SaleItem.product_id==p.id).scalar() or 0)
        sold90=(db.query(func.coalesce(func.sum(SaleItem.quantity),0)).join(Sale,Sale.id==SaleItem.sale_id).filter(Sale.status==SaleStatus.invoiced,Sale.created_at>=since,SaleItem.product_id==p.id).scalar() or 0)
        avg30=float(sold30)/30; avg90=float(sold90)/90; seasonal=max(avg30,avg90)
        days_left=round(p.stock/seasonal,1) if seasonal else None
        coverage_target=14 + (p.lead_time_days or 3)
        suggested=max(round((seasonal*coverage_target)-p.stock,2),0) if seasonal else max((p.reorder_point or p.min_stock or 0)-p.stock,0)
        forecast.append({'product':p.name,'stock':p.stock,'daily_avg_30':round(avg30,2),'daily_avg_90':round(avg90,2),'seasonal_daily_demand':round(seasonal,2),'days_left':days_left,'coverage_target_days':coverage_target,'suggested_purchase':suggested})
    return {'brand':'Deli Food','revenue':round(float(revenue),2),'stock_value':round(float(stock_value),2),'low_stock_count':len(low_stock),'low_stock':[{'name':p.name,'stock':p.stock,'min_stock':p.min_stock} for p in low_stock],'top_products':[{'name':r[0],'quantity':float(r[1]),'total':float(r[2])} for r in top],'forecast':forecast,'payment_mix':[{'method':str(m.value if hasattr(m,'value') else m),'total':float(t)} for m,t in payment_mix]}
