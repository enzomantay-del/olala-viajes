"""Configuración segura de Cloudinary (no rompe el build si la URL está mal)."""

import os


def cloudinary_disponible():
    """True si Cloudinary está configurado y la URL es válida."""
    return _configurar_cloudinary()


def _configurar_cloudinary():
    url = os.environ.get('CLOUDINARY_URL', '').strip()
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', '').strip()
    api_key = os.environ.get('CLOUDINARY_API_KEY', '').strip()
    api_secret = os.environ.get('CLOUDINARY_API_SECRET', '').strip()

    if not url and not (cloud_name and api_key and api_secret):
        return False

    try:
        import cloudinary

        if url:
            if not url.startswith('cloudinary://'):
                return False
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
