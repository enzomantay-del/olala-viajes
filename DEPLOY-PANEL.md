# Acceder al panel desde cualquier dispositivo

La web en **Firebase** (`olala-viajes.web.app`) es solo el catálogo estático.  
El **panel de gestión** (reservas, salidas, flyers) es la aplicación **Django** y debe estar en un servidor con internet.

## Opción recomendada: Render.com (gratis)

### 1. Subir el proyecto a GitHub

Si aún no está, subí la carpeta `olala-viajes` a un repositorio en GitHub.

### 2. Crear el servicio en Render

1. Entrá a https://render.com y creá cuenta.
2. **New → Web Service** → conectá tu repo `olala-viajes`.
3. Render detecta `render.yaml` o configurá manualmente:
   - **Build:** `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate --noinput`
   - **Start:** `gunicorn olala.wsgi:application --bind 0.0.0.0:$PORT`

### 3. Variables de entorno en Render

| Variable | Valor ejemplo |
|----------|----------------|
| `DJANGO_SECRET_KEY` | (generar una clave larga aleatoria) |
| `DJANGO_DEBUG` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `olala-viajes.onrender.com` |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://olala-viajes.onrender.com` |
| `PANEL_PUBLIC_URL` | `https://olala-viajes.onrender.com/accounts/login/` |
| `PUBLIC_WEB_BASE_URL` | `https://olala-viajes.web.app` |

(Ajustá el dominio si Render te asigna otro, ej. `olala-viajes-xxxx.onrender.com`.)

### 4. Crear usuario administrador

En Render: **Shell** del servicio, o en local apuntando a la misma base:

```bash
python manage.py createsuperuser
```

### 5. Acceder desde el celular o cualquier PC

- **Panel:** `https://TU-SERVICIO.onrender.com/accounts/login/`
- **Catálogo Django (vivo):** `https://TU-SERVICIO.onrender.com/web/`
- **Admin Django:** `https://TU-SERVICIO.onrender.com/admin/`

### 6. Enlace en la web pública de Firebase

En tu PC, en `.env` del proyecto:

```
PANEL_PUBLIC_URL=https://TU-SERVICIO.onrender.com/accounts/login/
```

Luego **Salidas → Publicar en web** y **firebase deploy**.

En el pie de `olala-viajes.web.app` aparecerá **“Acceso agencia (panel)”**.

---

## Importante sobre datos

- En Render **gratis**, el disco es efímero: subí `db.sqlite3` y `media/` o usá **PostgreSQL** (Render ofrece base gratis).
- Para PostgreSQL en Render, agregá la base y la variable `DATABASE_URL` que Render inyecta automáticamente.

---

## Opción rápida solo para probar (túnel)

Con el servidor local encendido:

```bash
ngrok http 8000
```

Usá la URL `https://xxxx.ngrok.io/accounts/login/` — cambia cada vez que reiniciás ngrok. No sirve como solución permanente.

---

## Resumen

| Qué | Dónde |
|-----|--------|
| Clientes ven paquetes | `olala-viajes.web.app` (Firebase) |
| Vos gestionás la agencia | `https://TU-SERVICIO.onrender.com/` (Django en internet) |
| Enlace desde la web pública | Pie de página → Acceso agencia |
