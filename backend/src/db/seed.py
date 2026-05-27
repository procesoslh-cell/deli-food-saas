
from datetime import datetime, timedelta
from src.db.session import Base, engine, SessionLocal
from src.models.models import Category, Product, ProductType, Role, Branch, User, Supplier, Customer, Sale, SaleItem, SaleStatus, Payment, PaymentMethodType, CashSession
from src.routes.auth import hash_password

DEFAULT_CATEGORIES = [
    ('Comestibles de almacén', 'Productos secos, conservas, yerba, arroz, fideos y mercadería general'),
    ('Supermercado', 'Limpieza, perfumería, bazar, papel y varios'),
    ('Bebidas sin alcohol', 'Gaseosas, aguas, jugos, soda, aguas saborizadas y energizantes'),
    ('Bebidas con alcohol', 'Cervezas, vinos, aperitivos y bebidas alcohólicas'),
    ('Dulces y golosinas', 'Caramelos, chocolates, alfajores, snacks dulces y galletitas'),
    ('Fiambres', 'Fiambres feteados, por pieza y envasados'),
    ('Quesos', 'Quesos blandos, duros, untables y rallados'),
    ('Picadas envasadas', 'Tablas, bandejas y combos listos'),
    ('Pollería', 'Pollo entero, trozado, pata muslo y cortes'),
    ('Fabricación propia - frescos', 'Milanesas, albóndigas y elaborados frescos'),
    ('Congelados fabricación propia', 'Pizzas, empanadas, chipacitos, torta de queso y canelones'),
    ('Materias primas', 'Insumos para fabricación y recetas'),
]

SAMPLE_PRODUCTS = [
    ('MAT-HARINA-0001', 'Harina 0000', 'Materias primas', ProductType.raw_material, 'kg', 25, 420, 0, 8, 10),
    ('MAT-MUZZ-0001', 'Mozzarella', 'Materias primas', ProductType.raw_material, 'kg', 10, 5200, 0, 4, 6),
    ('MAT-POLLO-0001', 'Pechuga de pollo', 'Materias primas', ProductType.raw_material, 'kg', 15, 3100, 0, 6, 8),
    ('FAB-MILA-0001', 'Milanesa de pollo fabricación propia', 'Fabricación propia - frescos', ProductType.manufactured, 'kg', 8, 3900, 40, 3, 5),
    ('FAB-ALBO-0001', 'Albóndigas fabricación propia', 'Fabricación propia - frescos', ProductType.manufactured, 'kg', 6, 3600, 42, 3, 5),
    ('FAB-PIZZA-0001', 'Pizza muzzarella congelada', 'Congelados fabricación propia', ProductType.manufactured, 'unidad', 12, 2600, 45, 5, 8),
    ('FAB-EMP-0001', 'Empanadas congeladas docena', 'Congelados fabricación propia', ProductType.manufactured, 'docena', 10, 5100, 45, 4, 7),
    ('REV-AGUA-0001', 'Agua mineral 1.5L', 'Bebidas sin alcohol', ProductType.resale, 'unidad', 48, 850, 35, 12, 18),
    ('REV-CERV-0001', 'Cerveza lata 473ml', 'Bebidas con alcohol', ProductType.resale, 'unidad', 72, 1100, 35, 24, 36),
    ('REV-FIAM-0001', 'Jamón cocido feteado', 'Fiambres', ProductType.resale, 'kg', 6, 7200, 35, 2, 4),
]

def seed():
    Base.metadata.create_all(bind=engine)
    # Migración mínima para instalaciones existentes sin Alembic.
    # Permite agregar contraseña a bases ya creadas.
    with engine.begin() as conn:
        try:
            conn.exec_driver_sql("ALTER TABLE users ADD COLUMN password_hash VARCHAR DEFAULT ''")
        except Exception:
            pass
    db = SessionLocal()
    try:
        if not db.query(Branch).first():
            db.add_all([Branch(name='Deli Food - Casa Central', address='Sucursal principal'), Branch(name='Deli Food - Depósito', address='Stock y producción')])
            db.commit()
        branch = db.query(Branch).first()
        if not db.query(Role).first():
            db.add_all([Role(name='Administrador', permissions='all'), Role(name='Cajero', permissions='sales,cash'), Role(name='Producción', permissions='inventory,manufacturing'), Role(name='Compras', permissions='purchases,suppliers')])
            db.commit()
        admin_role = db.query(Role).filter_by(name='Administrador').first()
        admin = db.query(User).filter(User.email == 'admin@delifood.local').first()
        if not admin:
            db.add(User(name='Administrador Deli Food', email='admin@delifood.local', password_hash=hash_password('admin123'), role_id=admin_role.id, branch_id=branch.id))
        elif not admin.password_hash:
            admin.password_hash = hash_password('admin123')
        if not db.query(Supplier).first():
            db.add_all([Supplier(name='Proveedor General', phone=''), Supplier(name='Distribuidora Bebidas', phone=''), Supplier(name='Frigorífico y Pollería', phone='')])
        if not db.query(Customer).first():
            db.add(Customer(name='Consumidor final'))
        db.commit()
        existing = {c.name: c for c in db.query(Category).all()}
        for name, desc in DEFAULT_CATEGORIES:
            if name not in existing:
                db.add(Category(name=name, description=desc))
        db.commit()
        cats = {c.name: c for c in db.query(Category).all()}
        supplier = db.query(Supplier).first()
        for sku, name, cat, ptype, unit, stock, cost, margin, min_stock, reorder in SAMPLE_PRODUCTS:
            if not db.query(Product).filter(Product.sku == sku).first():
                suggested = round(cost * (1 + margin/100), 2) if cost else 0
                db.add(Product(sku=sku, name=name, category_id=cats[cat].id, supplier_id=supplier.id, branch_id=branch.id, product_type=ptype, unit=unit, stock=stock, min_stock=min_stock, reorder_point=reorder, cost=cost, margin_percent=margin, suggested_price=suggested))
        db.commit()
        # Ventas demo para dashboard y forecast
        if not db.query(Sale).first():
            products = db.query(Product).filter(Product.product_type != ProductType.raw_material).all()
            for day in range(1, 22):
                sale = Sale(customer_name='Consumidor final', status=SaleStatus.invoiced, branch_id=branch.id, created_at=datetime.utcnow()-timedelta(days=day))
                db.add(sale); db.flush()
                total = 0
                for p in products[:3 + (day % 3)]:
                    qty = 1 + (day % 4)
                    price = p.manual_price or p.suggested_price or round(p.cost*1.35,2)
                    line = round(qty*price,2)
                    sale.items.append(SaleItem(product_id=p.id, quantity=qty, unit_price=price, total=line))
                    total += line
                sale.subtotal = total; sale.total = total; sale.paid_total = total
                sale.payments.append(Payment(method=PaymentMethodType.cash if day%2 else PaymentMethodType.debit, amount=total))
            db.commit()
    finally:
        db.close()
