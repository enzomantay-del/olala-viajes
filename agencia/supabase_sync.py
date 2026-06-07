"""Sincroniza salidas y fotos con Supabase (catálogo público en Firebase/Netlify)."""

import json
import mimetypes
import os
import urllib.error
import urllib.request
from pathlib import Path

from django.conf import settings

from .salidas_utils import categorizar_salida

BUCKET = 'olala-salidas'
TABLE = 'olala_salidas'
MESES = [
    'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
]


def supabase_configurado():
    return bool(getattr(settings, 'USE_SUPABASE', False))


def _headers(prefer=None):
    key = settings.SUPABASE_SERVICE_KEY
    headers = {
        'apikey': key,
        'Authorization': f'Bearer {key}',
    }
    if prefer:
        headers['Prefer'] = prefer
    return headers


def _request(method, path, data=None, extra_headers=None):
    url = f'{settings.SUPABASE_URL.rstrip("/")}{path}'
    body = None
    headers = _headers()
    if extra_headers:
        headers.update(extra_headers)
    if data is not None:
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read()
            if not raw:
                return None
            return json.loads(raw.decode('utf-8'))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode('utf-8', errors='replace')
        raise RuntimeError(f'Supabase {method} {path} → {exc.code}: {detail[:400]}') from exc


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
            with urllib.request.urlopen(url, timeout=60) as resp:
                return resp.read(), os.path.basename(salida.foto.name)
    except Exception:
        pass
    return None, None


def _subir_foto_storage(salida):
    contenido, nombre = _leer_bytes_foto(salida)
    if not contenido or not nombre:
        return ''

    object_path = f'{salida.pk}/{nombre}'
    mime = mimetypes.guess_type(nombre)[0] or 'application/octet-stream'
    url = (
        f'{settings.SUPABASE_URL.rstrip("/")}/storage/v1/object/'
        f'{BUCKET}/{object_path}'
    )
    headers = _headers()
    headers['Content-Type'] = mime
    headers['x-upsert'] = 'true'
    req = urllib.request.Request(url, data=contenido, headers=headers, method='POST')
    try:
        urllib.request.urlopen(req, timeout=120)
    except urllib.error.HTTPError as exc:
        if exc.code not in (400, 409):
            detail = exc.read().decode('utf-8', errors='replace')
            raise RuntimeError(f'No se pudo subir foto a Supabase: {detail[:300]}') from exc
        # 409 = ya existe; seguimos con la URL pública

    public_url = (
        f'{settings.SUPABASE_URL.rstrip("/")}/storage/v1/object/public/'
        f'{BUCKET}/{object_path}'
    )
    return public_url


def _payload_salida(salida, imagen_url=''):
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

    payload = _payload_salida(salida, imagen_url=imagen_url)
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
