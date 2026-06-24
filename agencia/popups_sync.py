"""Sincroniza popups (avisos modales) con Supabase."""

import logging
import mimetypes
import os
from pathlib import Path

from django.conf import settings

BUCKET = 'olala-salidas'
TABLE = 'olala_popups'
_log = logging.getLogger(__name__)


def supabase_configurado():
    return bool(getattr(settings, 'USE_SUPABASE', False))


def _get_session():
    from .supabase_sync import _get_session as gs
    return gs()


def _base():
    from .supabase_sync import _base as b
    return b()


def _request(method, path, data=None, extra_headers=None):
    from .supabase_sync import _request as r
    return r(method, path, data=data, extra_headers=extra_headers)


def _existe_en_storage(object_path):
    from .supabase_sync import _existe_en_storage as existe
    return existe(object_path)


def _object_path(popup):
    nombre = os.path.basename(popup.imagen.name) if popup.imagen else ''
    return f'popups/{popup.pk}/{nombre}'


def _public_url(object_path):
    return f'{_base()}/storage/v1/object/public/{BUCKET}/{object_path}'


def _url_externa_imagen(popup):
    """URL pública ya accesible (p. ej. Cloudinary)."""
    if not popup.imagen:
        return ''
    try:
        url = popup.imagen.url
        if url.startswith(('http://', 'https://')):
            return url
    except Exception:
        pass
    return ''


def _buscar_imagen_local(popup):
    nombre = os.path.basename(popup.imagen.name) if popup.imagen else ''
    if not nombre:
        return None
    for carpeta in (
        Path(settings.MEDIA_ROOT) / 'popups',
        Path(settings.BASE_DIR) / 'media' / 'popups',
    ):
        ruta = carpeta / nombre
        if ruta.is_file():
            return ruta
    return None


def _url_imagen_existente(popup):
    """Solo devuelve URL si la imagen existe de verdad (nube o Storage)."""
    if not popup.imagen:
        return ''
    externa = _url_externa_imagen(popup)
    if externa:
        return externa
    object_path = _object_path(popup)
    if object_path.endswith('/') or object_path.endswith('/popups/'):
        return ''
    if _existe_en_storage(object_path):
        return _public_url(object_path)
    return ''


def _leer_bytes_imagen(popup):
    try:
        with popup.imagen.open('rb') as f:
            return f.read()
    except Exception as exc:
        _log.debug('Popup %s open remoto: %s', popup.pk, exc)
    local = _buscar_imagen_local(popup)
    if local:
        try:
            return local.read_bytes()
        except Exception as exc:
            _log.warning('Popup %s leer local: %s', popup.pk, exc)
    return None


def _subir_imagen(popup):
    if not popup.imagen:
        return ''

    existente = _url_imagen_existente(popup)
    if existente:
        return existente

    contenido = _leer_bytes_imagen(popup)
    if not contenido:
        _log.warning('Popup %s: imagen no disponible para subir', popup.pk)
        return ''

    nombre = os.path.basename(popup.imagen.name)
    object_path = f'popups/{popup.pk}/{nombre}'
    mime = mimetypes.guess_type(nombre)[0] or 'image/jpeg'
    url = f'{_base()}/storage/v1/object/{BUCKET}/{object_path}'
    resp = _get_session().post(
        url,
        data=contenido,
        headers={'Content-Type': mime, 'x-upsert': 'true'},
        timeout=90,
    )
    if resp.status_code not in (200, 201, 400, 409):
        _log.warning('Popup %s subida imagen: %s %s', popup.pk, resp.status_code, resp.text[:200])
        return ''
    return _public_url(object_path)


def _payload(popup, imagen_url=''):
    return {
        'id': popup.pk,
        'titulo': popup.titulo,
        'mensaje': popup.mensaje,
        'imagen_url': imagen_url,
        'fecha_desde': popup.fecha_desde.isoformat(),
        'fecha_hasta': popup.fecha_hasta.isoformat(),
        'enlace_url': popup.enlace_url or '',
        'enlace_texto': popup.enlace_texto or 'Ver más',
        'activo': popup.activo,
        'orden': popup.orden,
    }


def sincronizar_popup(popup):
    if not supabase_configurado():
        return False, 'Supabase no configurado'
    imagen_url = _subir_imagen(popup)
    payload = _payload(popup, imagen_url=imagen_url)
    _request(
        'POST',
        f'/rest/v1/{TABLE}',
        data=payload,
        extra_headers={'Prefer': 'resolution=merge-duplicates'},
    )
    return True, 'ok'


def eliminar_popup(pk):
    if not supabase_configurado():
        return
    _request('DELETE', f'/rest/v1/{TABLE}?id=eq.{pk}')


def sincronizar_todos():
    from .models import Popup
    for p in Popup.objects.all():
        sincronizar_popup(p)
