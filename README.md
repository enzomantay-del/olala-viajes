# Olala Viajes

Sistema de gestión para agencia de viajes (clientes, reservas, cobros, salidas de operadoras) y catálogo web público. Desarrollado para Olalá Viajes, Jardín América, Misiones, Argentina.

## Funcionalidades

- **Panel interno:** clientes, proveedores, reservas multi-servicio, cobros, pagos a proveedores, recibos y vouchers PDF
- **Salidas:** catálogo de paquetes de operadoras, PDF, mensaje WhatsApp, flyers JPG 9:16, publicación de web estática
- **Web pública** (`/web/`): catálogo para consultas por WhatsApp (sin reservas online automáticas)

## Tecnologías

- Python 3, Django 5
- SQLite (desarrollo)
- ReportLab, Pillow
- Bootstrap 5 (panel), HTML/CSS propio (web pública)

## Instalación

```bash
cd olala-viajes
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- **Panel (uso diario):** https://olala-viajes.onrender.com/
- **Web para clientes:** https://olala-viajes.web.app

Guía simple: **[FLUJO-SIMPLE.md](FLUJO-SIMPLE.md)**

Desarrollo local (opcional): `iniciar.bat` → http://127.0.0.1:8000/

## Configuración

Copiá `.env.example` a `.env` (opcional):

| Variable | Descripción |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Clave secreta (obligatoria en producción) |
| `DJANGO_DEBUG` | `False` en producción |
| `DJANGO_ALLOWED_HOSTS` | Dominios permitidos, separados por coma |
| `FIREBASE_TOKEN` | Token CI para publicar a Firebase desde Render (`firebase login:ci`) |
| `PANEL_PUBLIC_URL` | URL del login del panel (enlace en la web de Firebase) |
| `PUBLIC_WEB_BASE_URL` | URL del sitio en Firebase, ej. `https://olala-viajes.web.app` |

Datos de la agencia en `olala/settings.py` (`AGENCIA_*`).

## Publicar la web

**Salidas → Publicar en web** en el panel (Render o PC). Actualiza **olala-viajes.web.app** en 1–2 minutos.

Ver **[FLUJO-SIMPLE.md](FLUJO-SIMPLE.md)**. El archivo `publicar-web.bat` es opcional (respaldo en PC).

## Autor

**Enzo Gabriel Mantay**  
[LinkedIn](https://linkedin.com/in/enzomantay)
