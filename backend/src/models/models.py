
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, date
from src.db.session import Base
import enum

class ProductType(str, enum.Enum):
    resale = 'resale'
    manufactured = 'manufactured'
    raw_material = 'raw_material'

class SaleStatus(str, enum.Enum):
    quote = 'quote'
    invoiced = 'invoiced'
    cancelled = 'cancelled'

class PaymentMethodType(str, enum.Enum):
    cash = 'cash'
    debit = 'debit'
    credit = 'credit'
    transfer = 'transfer'
    account = 'account'
    qr = 'qr'

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'))
    branch_id = Column(Integer, ForeignKey('branches.id'))
    active = Column(Boolean, default=True)
    role = relationship('Role')
    branch = relationship('Branch')

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    permissions = Column(Text, default='')

class Branch(Base):
    __tablename__ = 'branches'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    address = Column(String, default='')
    active = Column(Boolean, default=True)

class Supplier(Base):
    __tablename__ = 'suppliers'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    cuit = Column(String, default='')
    phone = Column(String, default='')
    email = Column(String, default='')
    active = Column(Boolean, default=True)

class Customer(Base):
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    document = Column(String, default='')
    phone = Column(String, default='')
    credit_limit = Column(Float, default=0)
    balance = Column(Float, default=0)
    active = Column(Boolean, default=True)

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text, default='')
    active = Column(Boolean, default=True)
    products = relationship('Product', back_populates='category')

class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    barcode = Column(String, nullable=True, index=True)
    name = Column(String, nullable=False, index=True)
    category_id = Column(Integer, ForeignKey('categories.id'))
    supplier_id = Column(Integer, ForeignKey('suppliers.id'), nullable=True)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=True)
    product_type = Column(Enum(ProductType), default=ProductType.resale)
    unit = Column(String, default='unidad')
    stock = Column(Float, default=0)
    min_stock = Column(Float, default=0)
    reorder_point = Column(Float, default=0)
    lead_time_days = Column(Integer, default=3)
    cost = Column(Float, default=0)
    margin_percent = Column(Float, default=35)
    suggested_price = Column(Float, default=0)
    manual_price = Column(Float, nullable=True)
    active = Column(Boolean, default=True)
    category = relationship('Category', back_populates='products')
    supplier = relationship('Supplier')
    branch = relationship('Branch')

class BOMItem(Base):
    __tablename__ = 'bom_items'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    material_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Float, nullable=False)
    waste_percent = Column(Float, default=0)
    product = relationship('Product', foreign_keys=[product_id])
    material = relationship('Product', foreign_keys=[material_id])

class ProductionOrder(Base):
    __tablename__ = 'production_orders'
    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey('products.id'))
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=True)
    quantity = Column(Float, nullable=False)
    unit_cost = Column(Float, default=0)
    total_cost = Column(Float, default=0)
    suggested_price = Column(Float, default=0)
    notes = Column(Text, default='')
    created_at = Column(DateTime, default=datetime.utcnow)
    product = relationship('Product')

class PurchaseOrder(Base):
    __tablename__ = 'purchase_orders'
    id = Column(Integer, primary_key=True)
    supplier_id = Column(Integer, ForeignKey('suppliers.id'))
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=True)
    status = Column(String, default='draft')
    total = Column(Float, default=0)
    notes = Column(Text, default='')
    created_at = Column(DateTime, default=datetime.utcnow)
    supplier = relationship('Supplier')
    items = relationship('PurchaseItem', back_populates='purchase', cascade='all, delete-orphan')

class PurchaseItem(Base):
    __tablename__ = 'purchase_items'
    id = Column(Integer, primary_key=True)
    purchase_id = Column(Integer, ForeignKey('purchase_orders.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Float, nullable=False)
    unit_cost = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    purchase = relationship('PurchaseOrder', back_populates='items')
    product = relationship('Product')

class Sale(Base):
    __tablename__ = 'sales'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=True)
    branch_id = Column(Integer, ForeignKey('branches.id'), nullable=True)
    customer_name = Column(String, default='Consumidor final')
    status = Column(Enum(SaleStatus), default=SaleStatus.quote)
    subtotal = Column(Float, default=0)
    tax_total = Column(Float, default=0)
    total = Column(Float, default=0)
    paid_total = Column(Float, default=0)
    arca_status = Column(String, default='pending_integration')
    notes = Column(Text, default='')
    created_at = Column(DateTime, default=datetime.utcnow)
    items = relationship('SaleItem', back_populates='sale', cascade='all, delete-orphan')
    payments = relationship('Payment', back_populates='sale', cascade='all, delete-orphan')
    customer = relationship('Customer')

class SaleItem(Base):
    __tablename__ = 'sale_items'
    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey('sales.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total = Column(Float, nullable=False)
    sale = relationship('Sale', back_populates='items')
    product = relationship('Product')

class CashSession(Base):
    __tablename__ = 'cash_sessions'
    id = Column(Integer, primary_key=True)
    branch_id = Column(Integer, ForeignKey('branches.id'))
    opened_by_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    status = Column(String, default='open')
    opening_amount = Column(Float, default=0)
    closing_amount = Column(Float, nullable=True)
    expected_amount = Column(Float, default=0)
    difference = Column(Float, default=0)
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    branch = relationship('Branch')

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=True)
    cash_session_id = Column(Integer, ForeignKey('cash_sessions.id'), nullable=True)
    method = Column(Enum(PaymentMethodType), default=PaymentMethodType.cash)
    amount = Column(Float, nullable=False)
    reference = Column(String, default='')
    created_at = Column(DateTime, default=datetime.utcnow)
    sale = relationship('Sale', back_populates='payments')

class AccountMovement(Base):
    __tablename__ = 'account_movements'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'))
    sale_id = Column(Integer, ForeignKey('sales.id'), nullable=True)
    amount = Column(Float, nullable=False)
    description = Column(String, default='')
    created_at = Column(DateTime, default=datetime.utcnow)
    customer = relationship('Customer')
