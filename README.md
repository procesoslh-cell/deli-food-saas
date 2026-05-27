# Deli Food SaaS ERP

Versión final productiva local para Deli Food, diseñada y desarrollada por **NEXO Consultora**.

## Incluye
- Login inicial con frase inspiradora rotativa.
- Interfaz visual estilo ERP/Odoo.
- Inventario editable con SKU, código de barras, unidades, stock mínimo y alertas.
- Nomenclador de unidades: unidad, kg, gramo, docena, media docena, litro, pack, bandeja y caja.
- Fabricación con lista de materiales, cálculo de costo, precio sugerido y carga automática de stock elaborado.
- Ventas con búsqueda de productos por nombre, SKU o código, presupuestos, facturación y anulación/eliminación.
- Compras/proveedores con reposición sugerida automática.
- Dashboard con ventas, stock, productos más vendidos, forecast y alertas.
- Caja, medios de pago, cuentas corrientes, usuarios, roles y multi-sucursal.
- Preparado para futura integración ARCA, lector de código de barras y despliegue en nube.

## Usuario demo
Email:
```txt
admin@delifood.local
```
Contraseña: podés dejarla vacía en la versión demo local.

## Ejecutar backend en Windows PowerShell
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn src.main:app --reload --reload-dir src
```

Swagger:
```txt
http://127.0.0.1:8000/docs
```

## Ejecutar frontend
En otra terminal:
```powershell
cd frontend
npm install
npm run dev
```

Abrir la URL que indique Vite, por ejemplo:
```txt
http://localhost:5173
```

## Producción / nube
Para subirlo a la nube, usar backend FastAPI + base PostgreSQL y frontend estático. Antes de exponerlo a clientes reales conviene activar autenticación JWT real, HTTPS, backups automáticos, variables de entorno y roles/permisos estrictos.


## Usuario inicial

Email: admin@delifood.local
Contraseña: admin123

Desde Usuarios y sucursales se pueden crear usuarios con contraseña, cambiar clave y eliminar usuarios.
