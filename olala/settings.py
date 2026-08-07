import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

_env_path = BASE_DIR / '.env'
if _env_path.exists():
    for line in _env_path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, _, value = line.partition('=')
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'olala-viajes-clave-secreta-2024-cambiar-si-se-expone',
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('1', 'true', 'yes')

ALLOWED_HOSTS = [
    h.strip() for h in os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
    if h.strip()
]

_csrf_origins = os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_origins.split(',') if o.strip()]

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

from olala.cloudinary_config import cloudinary_disponible

_USE_CLOUDINARY = cloudinary_disponible()

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    # Solo 'cloudinary' (no cloudinary_storage: rompe collectstatic en Django 5).
    *(['cloudinary'] if _USE_CLOUDINARY else []),
    'django.contrib.staticfiles',
    'agencia',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'olala.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'agencia.context_processors.agencia_sitio',
                'agencia.context_processors.alertas_globales',
                'agencia.context_processors.estado_publicacion_web',
                'agencia.context_processors.estado_fotos_salidas',
            ],
        },
    },
]

WSGI_APPLICATION = 'olala.wsgi.application'

_db_url = os.environ.get('DATABASE_URL')
if _db_url:
    import dj_database_url
    DATABASES = {'default': dj_database_url.config(default=_db_url, conn_max_age=600)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'es-ar'
TIME_ZONE = 'America/Argentina/Buenos_Aires'
USE_I18N = True
USE_TZ = True

# Cache en memoria: evita repetir alertas/fotos en cada click del panel.
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'olala-panel',
        'TIMEOUT': 120,
    }
}

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {
        'BACKEND': (
            'cloudinary_storage.storage.MediaCloudinaryStorage'
            if _USE_CLOUDINARY
            else 'django.core.files.storage.FileSystemStorage'
        ),
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedStaticFilesStorage',
    },
}
# django-cloudinary-storage aún lee STATICFILES_STORAGE en collectstatic (Django 5 usa STORAGES).
STATICFILES_STORAGE = STORAGES['staticfiles']['BACKEND']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
USE_CLOUDINARY_MEDIA = _USE_CLOUDINARY

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Carpeta donde se genera el sitio estático antes de subir a Firebase
WEB_EXPORT_DIR = BASE_DIR / 'web-export'

# Datos de la agencia
AGENCIA_NOMBRE = 'Olalá Viajes'
AGENCIA_LEG = '19028'
AGENCIA_DISP = ''
AGENCIA_EMAIL = 'ventas@olalaviajes.tur.ar'
COTIZACION_EMAIL = os.environ.get('COTIZACION_EMAIL', AGENCIA_EMAIL)

EMAIL_BACKEND = os.environ.get(
    'EMAIL_BACKEND',
    'django.core.mail.backends.smtp.EmailBackend',
)
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'true').lower() in ('1', 'true', 'yes')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or AGENCIA_EMAIL)
AGENCIA_TELEFONO = '+54 9 3743 483429'
AGENCIA_WHATSAPP = '5493743483429'
AGENCIA_DIRECCION = 'Jardín América, Misiones, Argentina'

# URL pública del catálogo (Firebase Hosting + Supabase)
PUBLIC_WEB_BASE_URL = os.environ.get(
    'PUBLIC_WEB_BASE_URL',
    'https://olalaviajes.tur.ar',
).rstrip('/')

SUPABASE_URL = os.environ.get('SUPABASE_URL', '').strip()
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '').strip()
USE_SUPABASE = bool(SUPABASE_URL and SUPABASE_SERVICE_KEY)

# URL del panel de gestión (login). Debe ser absoluta para el HTML estático de Firebase.
PANEL_PUBLIC_URL = os.environ.get(
    'PANEL_PUBLIC_URL',
    'https://olala-viajes.onrender.com/accounts/login',
).rstrip('/')
