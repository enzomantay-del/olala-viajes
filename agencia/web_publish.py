"""Generación del sitio web estático público y datos para compartir en redes."""

import json
import os
import re
import shutil
from pathlib import Path

from django.conf import settings as django_settings
from django.template.loader import render_to_string
from django.urls import reverse

from .og_catalogo import contexto_og_catalogo, generar_og_catalogo
from .salidas_utils import categorizar_salidas

MESES_ES = [
    'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
]


def fecha_salida_legible(fecha):
    return f'{fecha.day} de {MESES_ES[fecha.month - 1]} de {fecha.year}'


def _nombre_archivo_foto(salida):
    if salida.foto:
        return os.path.basename(salida.foto.name)
    return None


def _es_url_remota(url):
    return url.startswith(('http://', 'https://', '//'))


def _normalizar_url_remota(url):
    if url.startswith('//'):
        return f'https:{url}'
    return url


def _copiar_fotos_a_export(salidas, dest_dir, base_url):
    """Copia fotos al sitio estático: disco local, Cloudinary o web pública anterior."""
    import urllib.error
    import urllib.request

    dst_salidas = dest_dir / 'media' / 'salidas'
    dst_salidas.mkdir(parents=True, exist_ok=True)

    carpetas_origen = [
        Path(django_settings.BASE_DIR) / 'seed_media' / 'salidas',
        Path(django_settings.MEDIA_ROOT) / 'salidas',
    ]
    for src_salidas in carpetas_origen:
        if not src_salidas.exists():
            continue
        for archivo in src_salidas.iterdir():
            if archivo.is_file():
                dest = dst_salidas / archivo.name
                if not dest.exists():
                    shutil.copy2(archivo, dest)

    for salida in salidas:
        if not salida.foto:
            continue
        nombre = _nombre_archivo_foto(salida)
        if not nombre:
            continue
        dest = dst_salidas / nombre
        if dest.exists():
            continue
        try:
            with salida.foto.open('rb') as f:
                dest.write_bytes(f.read())
            continue
        except Exception:
            pass
        try:
            url = f'{base_url.rstrip("/")}/media/salidas/{nombre}'
            urllib.request.urlretrieve(url, dest)
            if dest.stat().st_size == 0:
                dest.unlink(missing_ok=True)
        except (urllib.error.URLError, OSError, Exception):
            dest.unlink(missing_ok=True)


def _url_foto_publica(salida, base_url):
    if not salida.foto:
        return f'{base_url.rstrip("/")}/logo.png'
    url = salida.foto.url
    if _es_url_remota(url):
        return _normalizar_url_remota(url)
    if django_settings.USE_CLOUDINARY_MEDIA:
        try:
            import cloudinary.utils

            return cloudinary.utils.cloudinary_url(salida.foto.name, secure=True)[0]
        except Exception:
            pass
    nombre = _nombre_archivo_foto(salida)
    if nombre:
        return f'{base_url.rstrip("/")}/media/salidas/{nombre}'
    return f'{base_url.rstrip("/")}/logo.png'


def url_imagen_absoluta(salida, base_url):
    return _url_foto_publica(salida, base_url)


def _catalogo_en_django(base_url):
    base = base_url.rstrip('/')
    return base.endswith('/web') or 'onrender.com' in base


def url_paquete_absoluta(salida, base_url):
    base = base_url.rstrip('/')
    if _catalogo_en_django(base):
        return f'{base}/paquete/{salida.pk}/'
    return f'{base}/paquete/{salida.pk}.html'


def descripcion_og(salida):
    partes = [f'Salida {fecha_salida_legible(salida.fecha_salida)}']
    if salida.lugar_salida:
        partes.append(f'Desde {salida.lugar_salida}')
    if salida.servicios_incluidos:
        lineas = [ln.strip() for ln in salida.servicios_incluidos.splitlines() if ln.strip()][:6]
        if lineas:
            partes.append('Incluye: ' + ' · '.join(lineas))
    if salida.precio:
        simbolo = {'ARS': '$', 'USD': 'U$S', 'BRL': 'R$'}.get(salida.moneda, salida.moneda)
        partes.append(f'Desde {simbolo} {salida.precio:,.0f}')
    texto = ' | '.join(partes)
    return texto[:500] if len(texto) > 500 else texto


def mensaje_whatsapp(salida, paquete_url):
    lineas = [
        f'🗺️ *{salida.nombre_paquete}*',
        f'📅 Salida: {fecha_salida_legible(salida.fecha_salida)}',
    ]
    if salida.lugar_salida:
        lineas.append(f'📍 Desde: {salida.lugar_salida}')
    if salida.servicios_incluidos:
        lineas.append('')
        lineas.append('*Incluye:*')
        for ln in salida.servicios_incluidos.splitlines():
            t = ln.strip()
            if t:
                lineas.append(f'✓ {t}')
    if salida.precio:
        simbolo = {'ARS': '$', 'USD': 'U$S', 'BRL': 'R$'}.get(salida.moneda, salida.moneda)
        lineas.append(f'💰 Desde {simbolo} {salida.precio:,.0f} ({salida.moneda})')
    lineas.append('')
    lineas.append(f'👉 Ver paquete: {paquete_url}')
    lineas.append('')
    lineas.append('Consultá disponibilidad con Olalá Viajes ✈️')
    return '\n'.join(lineas)


def preparar_salida_web(salida, base_url, modo='django'):
    """Agrega atributos usados en plantillas (compartir, OG, enlaces)."""
    salida.fecha_legible = fecha_salida_legible(salida.fecha_salida)
    salida.paquete_url = url_paquete_absoluta(salida, base_url)
    salida.imagen_url_absoluta = url_imagen_absoluta(salida, base_url)
    salida.og_description = descripcion_og(salida)
    salida.share_text = mensaje_whatsapp(salida, salida.paquete_url)
    salida.share_title = salida.nombre_paquete
    salida.share_payload_json = json.dumps(
        {
            'url': salida.paquete_url,
            'text': salida.share_text,
            'title': salida.share_title,
        },
        ensure_ascii=False,
    )

    nombre_foto = _nombre_archivo_foto(salida)
    salida.flyer_url_absoluta = f'{base_url.rstrip("/")}/flyers/{salida.pk}.jpg'
    if modo == 'static':
        salida.paquete_href = f'paquete/{salida.pk}.html'
        if salida.foto:
            url_abs = _url_foto_publica(salida, base_url)
            if _es_url_remota(url_abs):
                salida.imagen_src = _normalizar_url_remota(url_abs)
                salida.imagen_es_absoluta = True
            else:
                salida.imagen_src = f'media/salidas/{nombre_foto}' if nombre_foto else 'logo.png'
                salida.imagen_es_absoluta = False
        else:
            salida.imagen_src = 'logo.png'
            salida.imagen_es_absoluta = False
        salida.flyer_href = f'flyers/{salida.pk}.jpg'
    else:
        salida.paquete_href = reverse('web_publica_paquete', kwargs={'pk': salida.pk})
        if salida.foto:
            salida.imagen_src = _url_foto_publica(salida, base_url)
        else:
            salida.imagen_src = '/static/img/logo-olala.png'
        salida.flyer_href = reverse('web_publica_flyer', kwargs={'pk': salida.pk})

    return salida


def _url_panel_publico(request=None):
    """URL absoluta del login del panel (para enlaces desde la web estática)."""
    url = django_settings.PANEL_PUBLIC_URL.rstrip('/')
    if url.startswith('http'):
        if '/accounts/login' not in url:
            url = f'{url}/accounts/login'
        return f'{url}/'
    if request:
        return request.build_absolute_uri(reverse('login'))
    return 'https://olala-viajes.onrender.com/accounts/login/'


def _contexto_agencia(request=None):
    return {
        'agencia_nombre': django_settings.AGENCIA_NOMBRE,
        'agencia_leg': django_settings.AGENCIA_LEG,
        'agencia_disp': django_settings.AGENCIA_DISP,
        'agencia_email': django_settings.AGENCIA_EMAIL,
        'agencia_telefono': django_settings.AGENCIA_TELEFONO,
        'agencia_whatsapp': django_settings.AGENCIA_WHATSAPP,
        'agencia_direccion': django_settings.AGENCIA_DIRECCION,
        'panel_url': _url_panel_publico(request),
    }


def _adaptar_html_index_estatico(html):
    html = html.replace('src="/media/', 'src="media/')
    html = html.replace('src="/static/img/logo-olala.png"', 'src="logo.png"')
    html = re.sub(r'href="/web/paquete/(\d+)/"', r'href="paquete/\1.html"', html)
    html = re.sub(r"href='/web/paquete/(\d+)/'", r"href='paquete/\1.html'", html)
    return html


def _escribir_redirect_panel(dest_dir):
    """
    Página de redirección en /accounts/login/ para Firebase.
    Si el navegador tiene caché vieja con href="/accounts/login/", igual llega al panel en Render.
    """
    panel_url = _url_panel_publico()
    login_dir = dest_dir / 'accounts' / 'login'
    login_dir.mkdir(parents=True, exist_ok=True)
    html = f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta http-equiv="refresh" content="0;url={panel_url}">
  <title>Panel Olalá Viajes</title>
  <script>location.replace({json.dumps(panel_url)});</script>
  <style>
    body {{ font-family: system-ui, sans-serif; text-align: center; padding: 48px 20px; color: #334155; }}
    a {{ color: #0e7490; font-weight: 600; }}
  </style>
</head>
<body>
  <p>Redirigiendo al panel de gestión…</p>
  <p><a href="{panel_url}">Ir al panel de Olalá Viajes</a></p>
</body>
</html>
'''
    (login_dir / 'index.html').write_text(html, encoding='utf-8')


def _adaptar_html_paquete_estatico(html):
    html = html.replace('src="/media/', 'src="../media/')
    html = html.replace('src="/static/img/logo-olala.png"', 'src="../logo.png"')
    html = html.replace('href="/web/"', 'href="../index.html"')
    html = html.replace("href='/web/'", "href='../index.html'")
    return html


def generar_sitio_web_estatico(request=None):
    """
    Genera index.html y paquete/{pk}.html en olala-viajes-web.
    Devuelve (dest_dir, cantidad_salidas).
    """
    from django.utils import timezone
    from .models import Salida

    base_url = django_settings.PUBLIC_WEB_BASE_URL
    hoy = timezone.now().date()
    salidas = list(Salida.objects.filter(fecha_salida__gte=hoy).order_by('fecha_salida'))
    categorizar_salidas(salidas)
    for s in salidas:
        preparar_salida_web(s, base_url, modo='static')

    ctx = {
        'salidas': salidas,
        'web_base_url': base_url,
        'es_estatico': True,
        **_contexto_agencia(request),
        **contexto_og_catalogo(base_url),
    }

    dest_dir = Path(django_settings.WEB_EXPORT_DIR)
    dest_dir.mkdir(exist_ok=True)
    paquete_dir = dest_dir / 'paquete'
    paquete_dir.mkdir(exist_ok=True)

    html_index = render_to_string('web_publica.html', ctx, request=request)
    html_index = _adaptar_html_index_estatico(html_index)
    (dest_dir / 'index.html').write_text(html_index, encoding='utf-8')
    _escribir_redirect_panel(dest_dir)

    for s in salidas:
        html_p = render_to_string(
            'web_publica_paquete.html',
            {**ctx, 'salida': s, 's': s},
            request=request,
        )
        html_p = _adaptar_html_paquete_estatico(html_p)
        (paquete_dir / f'{s.pk}.html').write_text(html_p, encoding='utf-8')

    _copiar_fotos_a_export(salidas, dest_dir, base_url)

    img_dir = Path(django_settings.BASE_DIR) / 'static' / 'img'
    logo_src = img_dir / 'logo-blanco.png'
    if not logo_src.exists():
        logo_src = img_dir / 'logo.png'
    if not logo_src.exists():
        logo_src = img_dir / 'logo-olala.png'
    if logo_src.exists():
        shutil.copy2(logo_src, dest_dir / 'logo.png')

    generar_og_catalogo(dest_dir)

    from .flyer_utils import generar_flyers_lote

    flyers_web = dest_dir / 'flyers'
    num_flyers = generar_flyers_lote(salidas, flyers_web)

    # Copiar flyers al panel (sin regenerarlos)
    media_flyers = Path(django_settings.MEDIA_ROOT) / 'flyers'
    media_flyers.mkdir(parents=True, exist_ok=True)
    if flyers_web.exists():
        for jpg in flyers_web.glob('*.jpg'):
            shutil.copy2(jpg, media_flyers / jpg.name)

    return dest_dir, len(salidas), num_flyers
