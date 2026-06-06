"""Sincroniza fotos en Cloudinary (ya no se usa Firebase desde Render)."""

from django.db import connections

from .fotos_cloudinary import sincronizar_todas_las_fotos
from .publish_status import actualizar_progreso, finalizar_publicacion


def ejecutar_publicacion_web():
    """Mantiene compatibilidad con manage.py publicar_sitio_web (solo sincroniza fotos)."""
    connections.close_all()
    try:
        actualizar_progreso('Sincronizando fotos en Cloudinary…')
        sincronizar_todas_las_fotos()
        from django.conf import settings

        url = settings.PUBLIC_WEB_BASE_URL.rstrip('/') + '/'
        finalizar_publicacion(
            True,
            f'Fotos sincronizadas. Catálogo en {url}',
            '',
        )
    except Exception as exc:
        finalizar_publicacion(False, f'Error: {exc}', '')
