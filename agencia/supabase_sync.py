"""Sincroniza salidas con Supabase (rápido: omite archivos ya subidos)."""

import hashlib
import json
import logging
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
TIMEOUT_SUBIDA = 90
TIMEOUT_HEAD = 8

_HTTP = None
_CACHE_REMOTO = None
_log = logging.getLogger(__name__)


def supabase_configurado():
    return bool(getattr(settings, 'USE_SUPABASE', False))


def _get_session():
    global _HTTP
    if _HTTP is None:
        s = requests.Session()
        key = settings.SUPABASE_SERVICE_KEY
        s.headers.update({
            'apikey': key,
            'Authorization': f'Bearer {key}',
        })
        _HTTP = s
    return _HTTP


def _base():
    return settings.SUPABASE_URL.rstrip('/')


def _public_url(object_path):
    return f'{_base()}/storage/v1/object/public/{BUCKET}/{object_path}'


def _existe_en_storage(object_path):
    try:
        r = _get_session().head(_public_url(object_path), timeout=TIMEOUT_HEAD, verify=VERIFY)
        return r.status_code == 200
    except requests.RequestException:
        return False


def _request(method, path, data=None, extra_headers=None):
    url = f'{_base()}{path}'
    headers = dict(extra_headers or {})
    body = None
    if data is not None:
        headers['Content-Type'] = 'application/json'
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
    resp = _get_session().request(method, url, headers=headers, data=body, timeout=30, verify=VERIFY)
    if resp.status_code >= 400:
        raise RuntimeError(f'Supabase {method} {path} → {resp.status_code}: {resp.text[:400]}')
    if resp.text:
        return resp.json()
    return None


def _cargar_cache_remoto():
    global _CACHE_REMOTO
    if _CACHE_REMOTO is not None:
        return _CACHE_REMOTO
    try:
        rows = _request('GET', f'/rest/v1/{TABLE}?select=id,imagen_url,flyer_url') or []
        _CACHE_REMOTO = {int(r['id']): r for r in rows}
    except Exception:
        _CACHE_REMOTO = {}
    return _CACHE_REMOTO


def _hash_salida(salida):
    partes = [
        salida.nombre_paquete,
        str(salida.fecha_salida),
        salida.lugar_salida or '',
        salida.descripcion or '',
        salida.servicios_incluidos or '',
        str(salida.precio),
        salida.moneda or '',
        str(salida.cupos),
        str(salida.agotado),
        str(salida.pasa_por_jardin_america),
        str(salida.vacaciones_invierno),
        str(getattr(salida, 'salida_confirmada', False)),
        json.dumps(salida.get_categorias_slugs(), sort_keys=True),
        os.path.basename(salida.foto.name) if salida.foto else '',
    ]
    return hashlib.md5('|'.join(partes).encode('utf-8')).hexdigest()


def _stamp_path(salida):
    return Path(settings.MEDIA_ROOT) / 'flyers' / f'{salida.pk}.sync'


def _salida_cambio(salida):
    stamp = _stamp_path(salida)
    h = _hash_salida(salida)
    if stamp.exists() and stamp.read_text(encoding='utf-8').strip() == h:
        return False
    return True


def _marcar_sincronizada(salida):
    _stamp_path(salida).write_text(_hash_salida(salida), encoding='utf-8')


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


def _url_foto_existente(salida):
    if not salida.foto:
        return ''
    remoto = _cargar_cache_remoto().get(salida.pk, {})
    if remoto.get('imagen_url'):
        return remoto['imagen_url']
    try:
        url = salida.foto.url
        if url.startswith(('http://', 'https://')):
            return url
    except Exception:
        pass
    nombre = os.path.basename(salida.foto.name)
    object_path = f'{salida.pk}/{nombre}'
    if _existe_en_storage(object_path):
        return _public_url(object_path)
    return ''


def imagen_og_salida(salida):
    """URL absoluta HTTPS de la foto del paquete."""
    url = _url_foto_existente(salida)
    if url.startswith(('http://', 'https://')):
        return url
    from .web_publish import url_imagen_absoluta

    base = getattr(settings, 'PUBLIC_WEB_BASE_URL', 'https://olala-viajes.web.app')
    abs_url = url_imagen_absoluta(salida, base)
    if abs_url.startswith(('http://', 'https://')):
        return abs_url
    return f'{base.rstrip("/")}/assets/og-catalogo.jpg'


def _formato_og_compatible(url):
    if not url:
        return False
    low = url.lower().split('?')[0]
    return low.endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif'))


def imagen_og_compartir(salida, imagen_url='', flyer_url=''):
    """Imagen para WhatsApp/Facebook (JPG/PNG/WebP; evita AVIF/JFIF)."""
    base = getattr(settings, 'PUBLIC_WEB_BASE_URL', 'https://olala-viajes.web.app').rstrip('/')
    foto = imagen_url or imagen_og_salida(salida)
    flyer = flyer_url or _url_flyer_existente(salida)
    if not flyer:
        flyer = (_cargar_cache_remoto().get(salida.pk) or {}).get('flyer_url', '')
    if not flyer and _existe_en_storage(f'{salida.pk}/flyer.jpg'):
        flyer = _public_url(f'{salida.pk}/flyer.jpg')

    if _formato_og_compatible(foto):
        return foto
    if flyer and flyer.startswith(('http://', 'https://')):
        return flyer
    if foto.startswith(('http://', 'https://')):
        return foto
    return f'{base}/assets/og-catalogo.jpg'


def _subir_foto_si_falta(salida):
    existente = _url_foto_existente(salida)
    if existente:
        return existente

    if not salida.foto:
        return ''

    nombre = os.path.basename(salida.foto.name)
    object_path = f'{salida.pk}/{nombre}'
    contenido = None

    local = _buscar_foto_local(salida)
    if local:
        contenido = local.read_bytes()
    else:
        try:
            with salida.foto.open('rb') as f:
                contenido = f.read()
        except Exception:
            pass

    if not contenido:
        return existente

    mime = mimetypes.guess_type(nombre)[0] or 'application/octet-stream'
    url = f'{_base()}/storage/v1/object/{BUCKET}/{object_path}'
    resp = _get_session().post(
        url,
        data=contenido,
        headers={'Content-Type': mime, 'x-upsert': 'true'},
        timeout=TIMEOUT_SUBIDA,
        verify=VERIFY,
    )
    if resp.status_code not in (200, 201, 400, 409):
        raise RuntimeError(f'Foto: {resp.status_code} {resp.text[:200]}')
    return _public_url(object_path)


def _url_flyer_existente(salida):
    object_path = f'{salida.pk}/flyer.jpg'
    if _existe_en_storage(object_path):
        return _public_url(object_path)
    remoto = _cargar_cache_remoto().get(salida.pk, {})
    return remoto.get('flyer_url') or ''


def _flyer_falta(salida):
    """True si el paquete aún no tiene flyer en Storage ni URL en Supabase."""
    return not _url_flyer_existente(salida)


def _subir_flyer_si_falta(salida, forzar=False):
    existente = _url_flyer_existente(salida)
    if existente and not forzar and not _salida_cambio(salida):
        return existente

    from .flyer_utils import generar_flyer_salida

    categorizar_salida(salida)
    ruta = Path(settings.MEDIA_ROOT) / 'flyers' / f'{salida.pk}.jpg'
    ruta.parent.mkdir(parents=True, exist_ok=True)

    if forzar or _salida_cambio(salida) or not ruta.exists() or ruta.stat().st_size == 0:
        generar_flyer_salida(salida, ruta)

    if existente and not forzar and not _salida_cambio(salida):
        return existente

    object_path = f'{salida.pk}/flyer.jpg'
    url = f'{_base()}/storage/v1/object/{BUCKET}/{object_path}'
    resp = _get_session().post(
        url,
        data=ruta.read_bytes(),
        headers={'Content-Type': 'image/jpeg', 'x-upsert': 'true'},
        timeout=TIMEOUT_SUBIDA,
        verify=VERIFY,
    )
    if resp.status_code not in (200, 201, 400, 409):
        raise RuntimeError(f'Flyer: {resp.status_code} {resp.text[:200]}')
    return _public_url(object_path)


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
        'salida_confirmada': bool(getattr(salida, 'salida_confirmada', False)),
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


def sincronizar_salida(salida, forzar_flyers=False, rapido=False, progreso=None):
    if not supabase_configurado():
        return False, 'Supabase no configurado'

    remoto = _cargar_cache_remoto().get(salida.pk)
    if remoto and not forzar_flyers and not _salida_cambio(salida) and not _flyer_falta(salida):
        if progreso:
            progreso(salida)
        return True, 'sin cambios'

    imagen_url = _subir_foto_si_falta(salida)
    flyer_url = ''
    generar_flyer = (
        not rapido
        or forzar_flyers
        or _salida_cambio(salida)
        or _flyer_falta(salida)
    )
    if generar_flyer:
        try:
            flyer_url = _subir_flyer_si_falta(salida, forzar=forzar_flyers)
        except Exception as exc:
            _log.warning('Flyer salida %s: %s', salida.pk, exc)
            flyer_url = _url_flyer_existente(salida)
    else:
        flyer_url = _url_flyer_existente(salida)

    payload = _payload_salida(salida, imagen_url=imagen_url, flyer_url=flyer_url)
    _request(
        'POST',
        f'/rest/v1/{TABLE}',
        data=payload,
        extra_headers={'Prefer': 'resolution=merge-duplicates'},
    )
    _marcar_sincronizada(salida)
    if remoto is not None:
        remoto.update({'imagen_url': imagen_url, 'flyer_url': flyer_url})

    try:
        from .alertas import verificar_alertas_para_salida
        verificar_alertas_para_salida(payload)
    except Exception:
        pass

    from .sitio_estatico import generar_paginas_paquetes

    img_og = imagen_og_compartir(salida, imagen_url=imagen_url, flyer_url=flyer_url)
    try:
        generar_paginas_paquetes([salida], {salida.pk: img_og})
    except Exception:
        pass

    if progreso:
        progreso(salida)
    return True, 'ok'


def ocultar_salida(pk):
    if not supabase_configurado():
        return
    _request('PATCH', f'/rest/v1/{TABLE}?id=eq.{pk}', data={'visible': False})


def sincronizar_todas_las_salidas(forzar_flyers=False, callback=None):
    if not supabase_configurado():
        raise RuntimeError('Configurá SUPABASE_URL y SUPABASE_SERVICE_KEY en .env')

    from .models import Salida

    salidas = list(Salida.objects.select_related('operadora').order_by('fecha_salida'))
    total = len(salidas)
    _cargar_cache_remoto()

    ok = 0
    sin_cambios = 0
    errores = []
    for i, salida in enumerate(salidas, start=1):
        if callback:
            callback(i, total, salida.nombre_paquete)
        try:
            _, estado = sincronizar_salida(salida, forzar_flyers=forzar_flyers)
            ok += 1
            if estado == 'sin cambios':
                sin_cambios += 1
        except Exception as exc:
            errores.append(f'{salida.nombre_paquete}: {exc}')

    from .sitio_estatico import asegurar_assets_sitio, generar_paginas_paquetes

    imagenes = {}
    for salida in salidas:
        remoto = _cargar_cache_remoto().get(salida.pk, {})
        imagenes[salida.pk] = imagen_og_compartir(
            salida,
            imagen_url=remoto.get('imagen_url', ''),
            flyer_url=remoto.get('flyer_url', ''),
        )

    asegurar_assets_sitio()
    generar_paginas_paquetes(salidas, imagenes)

    if errores:
        raise RuntimeError(f'Sincronizadas {ok}/{total}, error: {errores[0]}')
    return ok, sin_cambios
