"""Sincroniza testimonios con Supabase."""

import json
import mimetypes
import os

from django.conf import settings

BUCKET = 'olala-salidas'
TABLE = 'olala_testimonios'


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


def _url_foto(testimonio):
    if not testimonio.foto:
        return ''
    try:
        url = testimonio.foto.url
        if url.startswith(('http://', 'https://')):
            return url
    except Exception:
        pass
    object_path = f'testimonios/{testimonio.pk}/{os.path.basename(testimonio.foto.name)}'
    return f'{_base()}/storage/v1/object/public/{BUCKET}/{object_path}'


def _subir_foto(testimonio):
    if not testimonio.foto:
        return ''
    existente = _url_foto(testimonio)
    if existente.startswith('http'):
        return existente
    try:
        with testimonio.foto.open('rb') as f:
            contenido = f.read()
    except Exception:
        return ''
    nombre = os.path.basename(testimonio.foto.name)
    object_path = f'testimonios/{testimonio.pk}/{nombre}'
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


def _payload(testimonio, foto_url=''):
    destino = testimonio.destino_label or ''
    if testimonio.salida_id and testimonio.salida:
        if not destino:
            destino = testimonio.salida.nombre_paquete
    return {
        'id': testimonio.pk,
        'salida_id': testimonio.salida_id,
        'nombre_cliente': testimonio.nombre_cliente,
        'destino_label': destino,
        'texto': testimonio.texto,
        'foto_url': foto_url,
        'emoji_destino': testimonio.emoji_destino or '✈️',
        'estrellas': testimonio.estrellas or 5,
        'anio': testimonio.anio,
        'orden': testimonio.orden,
        'visible': testimonio.visible,
    }


def sincronizar_testimonio(testimonio):
    if not supabase_configurado():
        return False, 'Supabase no configurado'
    foto_url = _subir_foto(testimonio)
    payload = _payload(testimonio, foto_url=foto_url)
    _request(
        'POST',
        f'/rest/v1/{TABLE}',
        data=payload,
        extra_headers={'Prefer': 'resolution=merge-duplicates'},
    )
    return True, 'ok'


def ocultar_testimonio(pk):
    if not supabase_configurado():
        return
    _request('PATCH', f'/rest/v1/{TABLE}?id=eq.{pk}', data={'visible': False})


def sincronizar_todos():
    from .models import Testimonio
    for t in Testimonio.objects.select_related('salida').order_by('orden'):
        sincronizar_testimonio(t)
