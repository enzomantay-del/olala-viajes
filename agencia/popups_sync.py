"""Sincroniza popups (avisos modales) con Supabase."""

import mimetypes
import os

from django.conf import settings

BUCKET = 'olala-salidas'
TABLE = 'olala_popups'


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


def _url_imagen(popup):
    if not popup.imagen:
        return ''
    try:
        url = popup.imagen.url
        if url.startswith(('http://', 'https://')):
            return url
    except Exception:
        pass
    object_path = f'popups/{popup.pk}/{os.path.basename(popup.imagen.name)}'
    return f'{_base()}/storage/v1/object/public/{BUCKET}/{object_path}'


def _subir_imagen(popup):
    if not popup.imagen:
        return ''
    existente = _url_imagen(popup)
    if existente.startswith('http'):
        return existente
    try:
        with popup.imagen.open('rb') as f:
            contenido = f.read()
    except Exception:
        return ''
    nombre = os.path.basename(popup.imagen.name)
    object_path = f'popups/{popup.pk}/{nombre}'
    mime = mimetypes.guess_type(nombre)[0] or 'image/jpeg'
    url = f'{_base()}/storage/v1/object/{BUCKET}/{object_path}'
    resp = _get_session().post(
        url,
        data=contenido,
        headers={'Content-Type': mime, 'x-upsert': 'true'},
        timeout=60,
    )
    if resp.status_code not in (200, 201, 400, 409):
        return ''
    return f'{_base()}/storage/v1/object/public/{BUCKET}/{object_path}'


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
