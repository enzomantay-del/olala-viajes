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

- Panel: http://127.0.0.1:8000/ (requiere login)
- Web pública: http://127.0.0.1:8000/web/

En Windows podés usar `iniciar.bat`.

## Configuración

Copiá `.env.example` a `.env` (opcional):

| Variable | Descripción |
|----------|-------------|
| `DJANGO_SECRET_KEY` | Clave secreta (obligatoria en producción) |
| `DJANGO_DEBUG` | `False` en producción |
| `DJANGO_ALLOWED_HOSTS` | Dominios permitidos, separados por coma |
| `OLALA_FIREBASE_DEPLOY` | `True` para ejecutar `firebase deploy` al publicar la web |
| `PANEL_PUBLIC_URL` | URL del login del panel en internet (enlace en la web de Firebase) |
| `PUBLIC_WEB_BASE_URL` | URL del sitio en Firebase, ej. `https://olala-viajes.web.app` |

Datos de la agencia en `olala/settings.py` (`AGENCIA_*`).

## Panel desde cualquier dispositivo

Firebase solo sirve el catálogo estático. Para gestionar la agencia desde el celular u otra PC, subí Django a un host con internet (p. ej. **Render**). Guía paso a paso: **[DEPLOY-PANEL.md](DEPLOY-PANEL.md)**.

Resumen: desplegá el proyecto → configurá `PANEL_PUBLIC_URL` en Render y en tu `.env` local → **Publicar en web** + `firebase deploy` → en `olala-viajes.web.app` aparece **Acceso agencia (panel)**.

## Publicar la web

1. En el panel: **Salidas → Publicar en web** genera HTML, páginas por paquete y **flyers JPG** (1080×1920) en `../olala-viajes-web/flyers/`
2. Descargar un flyer individual: **Salidas** → ícono de imagen en cada fila, o desde la web pública (botón de descarga)
3. Con `OLALA_FIREBASE_DEPLOY=True` y Firebase CLI instalado, también despliega a **olala-viajes.web.app**

## Autor

**Enzo Gabriel Mantay**  
[LinkedIn](https://linkedin.com/in/enzomantay)
