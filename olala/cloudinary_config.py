"""Configuración segura de Cloudinary (no rompe el build si la URL está mal)."""

import os


def _url_cloudinary_valida(url):
    if not url or not url.startswith('cloudinary://'):
        return False
    if '<' in url or '>' in url or 'your_' in url.lower():
        return False
    return '@' in url and ':' in url.split('://', 1)[-1]


def cloudinary_disponible():
    """True si Cloudinary está configurado correctamente."""
    url = os.environ.get('CLOUDINARY_URL', '').strip()
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', '').strip()
    api_key = os.environ.get('CLOUDINARY_API_KEY', '').strip()
    api_secret = os.environ.get('CLOUDINARY_API_SECRET', '').strip()

    # URL inválida en el entorno rompe "import cloudinary" aunque existan las 3 variables.
    if url and not _url_cloudinary_valida(url):
        os.environ.pop('CLOUDINARY_URL', None)
        url = ''

    if not _url_cloudinary_valida(url) and not (cloud_name and api_key and api_secret):
        return False

    try:
        import cloudinary

        if _url_cloudinary_valida(url):
            cloudinary.config()
        else:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
                secure=True,
            )
        return True
    except Exception:
        return False
