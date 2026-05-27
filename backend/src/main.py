
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.db.seed import seed
from src.routes import categories, products, manufacturing, sales, dashboard, admin, purchases, cash, auth
app = FastAPI(title='Deli Food SaaS API', version='2.0.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])
@app.on_event('startup')
def on_startup(): seed()
app.include_router(auth.router); app.include_router(categories.router); app.include_router(products.router); app.include_router(manufacturing.router); app.include_router(sales.router); app.include_router(dashboard.router); app.include_router(admin.router); app.include_router(purchases.router); app.include_router(cash.router)
@app.get('/')
def root(): return {'name':'Deli Food SaaS','docs':'/docs','style':'odoo-inspired'}


@app.get("/health")
def health():
    return {"status": "ok", "app": "Deli Food SaaS"}
