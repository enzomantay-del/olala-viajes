"""Sincroniza salidas y fotos con Supabase (catálogo público en Firebase/Netlify)."""

import json
import mimetypes
import os
from pathlib import Path

import certifi
import requests
from django.conf import settings

from .salidas_utils import categorizar_salida

BUCKET = 'olala-salidas'
TABLE = 'olala_salidas'
VERIFY = certifi.where()
TIMEOUT = 120


def supabase_configurado():
    return bool(getattr(settings, 'USE_SUPABASE', False))


def _session():
    s = requests.Session()
    key = settings.SUPABASE_SERVICE_KEY
    s.headers.update({
        'apikey': key,
        'Authorization': f'Bearer {key}',
    })
    return s


def _request(method, path, data=None, extra_headers=None):
    url = f'{settings.SUPABASE_URL.rstrip("/")}{path}'
    headers = extra_headers or {}
    if data is not None:
        headers['Content-Type'] = 'application/json'
    resp = _session().request(
        method,
        url,
        headers=headers,
        data=json.dumps(data, ensure_ascii=False).encode('utf-8') if data is not None else None,
        timeout=TIMEOUT,
        verify=VERIFY,
    )
    if resp.status_code >= 400:
        raise RuntimeError(f'Supabase {method} {path} → {resp.status_code}: {resp.text[:400]}')
    if resp.text:
        return resp.json()
    return None


def _buscar_foto_local(salida):
    nombre = os.path.basename(salida.foto.name) if salida.foto else ''
    if not nombre:
        return None
    for carpeta in (
        Path(settings.MEDIA_ROOT) / 'salidas',
        Path(settings.BASE_DIR) / 'seed_media' / 'salidas',
    ):
        ruta = carpeta / nombre
        if ruta.is_file():
            return ruta
    return None


def _leer_bytes_foto(salida):
    if not salida.foto:
        return None, None
    try:
        with salida.foto.open('rb') as f:
            return f.read(), os.path.basename(salida.foto.name)
    except Exception:
        pass
    local = _buscar_foto_local(salida)
    if local:
        return local.read_bytes(), local.name
    try:
        url = salida.foto.url
        if url.startswith(('http://', 'https://')):
            r = requests.get(url, timeout=60, verify=VERIFY)
            r.raise_for_status()
            return r.content, os.path.basename(salida.foto.name)
    except Exception:
        pass
    return None, None


def _subir_bytes_storage(object_path, contenido, mime='image/jpeg'):
    url = (
        f'{settings.SUPABASE_URL.rstrip("/")}/storage/v1/object/'
        f'{BUCKET}/{object_path}'
    )
    resp = _session().post(
        url,
        data=contenido,
        headers={'Content-Type': mime, 'x-upsert': 'true'},
        timeout=TIMEOUT,
        verify=VERIFY,
    )
    if resp.status_code not in (200, 201, 400, 409):
        raise RuntimeError(f'No se pudo subir archivo: {resp.status_code} {resp.text[:300]}')
    return (
        f'{settings.SUPABASE_URL.rstrip("/")}/storage/v1/object/public/'
        f'{BUCKET}/{object_path}'
    )


def _subir_foto_storage(salida):
    contenido, nombre = _leer_bytes_foto(salida)
    if not contenido or not nombre:
        return ''

    object_path = f'{salida.pk}/{nombre}'
    mime = mimetypes.guess_type(nombre)[0] or 'application/octet-stream'
    return _subir_bytes_storage(object_path, contenido, mime)


def _subir_flyer_storage(salida):
    from .flyer_utils import generar_flyer_salida

    categorizar_salida(salida)
    ruta = Path(settings.MEDIA_ROOT) / 'flyers' / f'{salida.pk}.jpg'
    ruta.parent.mkdir(parents=True, exist_ok=True)
    if not ruta.exists() or ruta.stat().st_size == 0:
        generar_flyer_salida(salida, ruta)
    return _subir_bytes_storage(f'{salida.pk}/flyer.jpg', ruta.read_bytes(), 'image/jpeg')


def _payload_salida(salida, imagen_url='', flyer_url=''):
    categorizar_salida(salida)
    operadora = ''
    if salida.operadora_id and salida.operadora:
        operadora = str(salida.operadora)
    precio = float(salida.precio) if salida.precio is not None else None
    return {
        'id': salida.pk,
        'nombre_paquete': salida.nombre_paquete,
        'fecha_salida': salida.fecha_salida.isoformat(),
        'lugar_salida': salida.lugar_salida or '',
        'descripcion': salida.descripcion or '',
        'servicios_incluidos': salida.servicios_incluidos or '',
        'imagen_url': imagen_url,
        'flyer_url': flyer_url,
        'precio': precio,
        'moneda': salida.moneda or 'ARS',
        'cupos': salida.cupos,
        'agotado': bool(salida.agotado),
        'pasa_por_jardin_america': bool(salida.pasa_por_jardin_america),
        'vacaciones_invierno': bool(salida.vacaciones_invierno),
        'categorias': salida.get_categorias_slugs(),
        'cats': getattr(salida, 'cats', salida.get_categorias_slugs()),
        'cat': getattr(salida, 'cat', 'argentina'),
        'cat_label': getattr(salida, 'cat_label', 'Argentina'),
        'emoji': getattr(salida, 'emoji', '✈️'),
        'operadora_nombre': operadora,
        'visible': True,
    }


def sincronizar_salida(salida):
    if not supabase_configurado():
        return False, 'Supabase no configurado (SUPABASE_URL + SUPABASE_SERVICE_KEY en .env)'

    imagen_url = ''
    if salida.foto:
        imagen_url = _subir_foto_storage(salida)

    flyer_url = ''
    try:
        flyer_url = _subir_flyer_storage(salida)
    except Exception:
        pass

    payload = _payload_salida(salida, imagen_url=imagen_url, flyer_url=flyer_url)
    _request(
        'POST',
        f'/rest/v1/{TABLE}',
        data=payload,
        extra_headers={'Prefer': 'resolution=merge-duplicates'},
    )
    return True, imagen_url or 'sin foto'


def ocultar_salida(pk):
    if not supabase_configurado():
        return
    _request('PATCH', f'/rest/v1/{TABLE}?id=eq.{pk}', data={'visible': False})


def sincronizar_todas_las_salidas():
    if not supabase_configurado():
        raise RuntimeError('Configurá SUPABASE_URL y SUPABASE_SERVICE_KEY en .env')

    from .models import Salida

    ok = 0
    errores = []
    for salida in Salida.objects.select_related('operadora').order_by('fecha_salida'):
        try:
            sincronizar_salida(salida)
            ok += 1
        except Exception as exc:
            errores.append(f'{salida.nombre_paquete}: {exc}')

    if errores:
        raise RuntimeError(f'Sincronizadas {ok}, con error {len(errores)}: {errores[0]}')
    return ok
