# Generador de Pedidos a Proveedores

Aplicación web interna para automatizar el envío de pedidos y reclamos a proveedores. El operador selecciona el producto y el proveedor, completa un formulario mínimo, y el sistema genera y envía el mail automáticamente desde una cuenta de Gmail autorizada.

**Demo:** https://email-sender-vangian.onrender.com

---

## El problema que resuelve

Empresas con catálogos de productos y múltiples proveedores redactan mails de pedido, garantía o reclamo de forma manual — uno por uno. Esto genera errores, inconsistencias y tiempo perdido.

Este sistema centraliza productos, proveedores y plantillas de mail, y automatiza la composición y el envío.

---

## Stack

| Capa | Tecnología |
|------|-----------|
| Backend | Python · FastAPI · SQLAlchemy |
| Frontend | Streamlit |
| Base de datos | PostgreSQL (Neon) |
| Storage de fotos | Cloudinary |
| Envío de mail | Gmail API via Google OAuth 2.0 |
| Deploy | Render (backend + frontend separados) |

---

## Funcionalidades

- **ABM completo** de marcas, proveedores, productos y plantillas de mail
- **Carga masiva desde Excel** para marcas, proveedores y productos
- **Formulario de pedido** con selección de producto, proveedor y plantilla
- **Vista previa editable** del mail antes del envío (subject y body)
- **Adjuntos** — fotos del producto y archivo Excel opcionales
- **Historial de envíos** con filtros por proveedor y producto
- **Autenticación JWT** con sesión persistida en cookies (8 horas)
- **Google OAuth 2.0** para envío de mails desde cuenta Gmail autorizada

---

## Estructura del proyecto

```
├── backend/
│   ├── models/          # Modelos Pydantic
│   ├── routers/         # Endpoints (auth, brands, providers, products, mails, google_auth)
│   └── main.py
├── frontend/
│   ├── app.py           # Punto de entrada — login y navegación
│   ├── src/             # Páginas de la app
│   └── utils/           # Funciones compartidas y caché
├── modules/             # Módulos del backend (auth, db, mail, storage, google_oauth)
├── db/                  # Scripts SQL (create_db.sql, init.sql)
└── requirements.txt
```

---

## Variables de entorno

Crear un archivo `.env` en la raíz con las siguientes variables:

```env
# Base de datos
DATABASE_URL=postgresql://...

# Autenticación JWT
SECRET_KEY=
USER_USERNAME=
USER_PASSWORD=

# Cloudinary
CLOUDINARY_CLOUD_NAME=
CLOUDINARY_API_KEY=
CLOUDINARY_API_SECRET=

# Google OAuth
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=http://localhost:8000/google/callback

# URLs
API_URL=http://localhost:8000
FRONTEND_URL=http://localhost:8501
```

---

## Correr en local

```bash
# Instalar dependencias
pip install -r requirements.txt

# Backend
uvicorn backend.main:app --reload

# Frontend (en otra terminal)
streamlit run frontend/app.py
```

---

## Deploy

- **Backend y frontend** deployados como Web Services separados en Render
- **Base de datos** en Neon (PostgreSQL — free tier sin expiración de datos)
- **Fotos** almacenadas en Cloudinary
- **Mail** enviado via Gmail API con Google OAuth 2.0
