"""Generación del sitio web estático público y datos para compartir en redes."""

import json
import os
import re
import shutil
from pathlib import Path

from django.conf import settings as django_settings
from django.template.loader import render_to_string
from django.urls import reverse

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


def url_imagen_absoluta(salida, base_url):
    nombre = _nombre_archivo_foto(salida)
    if nombre:
        return f'{base_url.rstrip("/")}/media/salidas/{nombre}'
    return f'{base_url.rstrip("/")}/logo.png'


def url_paquete_absoluta(salida, base_url):
    return f'{base_url.rstrip("/")}/paquete/{salida.pk}.html'


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
        salida.imagen_src = f'media/salidas/{nombre_foto}' if nombre_foto else 'logo.png'
        salida.flyer_href = f'flyers/{salida.pk}.jpg'
    else:
        salida.paquete_href = reverse('web_publica_paquete', kwargs={'pk': salida.pk})
        if salida.foto:
            salida.imagen_src = salida.foto.url
        else:
            salida.imagen_src = '/static/img/logo-olala.png'
        salida.flyer_href = reverse('salida_flyer', kwargs={'pk': salida.pk})

    return salida


def _url_panel_publico(request=None):
    """URL absoluta del login del panel (para enlaces desde la web estática)."""
    if django_settings.PANEL_PUBLIC_URL:
        url = django_settings.PANEL_PUBLIC_URL.rstrip('/')
        if '/accounts/login' not in url:
            url = f'{url}/accounts/login'
        return f'{url}/'
    if request:
        return request.build_absolute_uri(reverse('login'))
    return '/accounts/login/'


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
    }

    dest_dir = Path(django_settings.BASE_DIR).parent / 'olala-viajes-web'
    dest_dir.mkdir(exist_ok=True)
    paquete_dir = dest_dir / 'paquete'
    paquete_dir.mkdir(exist_ok=True)

    html_index = render_to_string('web_publica.html', ctx, request=request)
    html_index = _adaptar_html_index_estatico(html_index)
    (dest_dir / 'index.html').write_text(html_index, encoding='utf-8')

    for s in salidas:
        html_p = render_to_string(
            'web_publica_paquete.html',
            {**ctx, 'salida': s, 's': s},
            request=request,
        )
        html_p = _adaptar_html_paquete_estatico(html_p)
        (paquete_dir / f'{s.pk}.html').write_text(html_p, encoding='utf-8')

    src_salidas = Path(django_settings.MEDIA_ROOT) / 'salidas'
    dst_salidas = dest_dir / 'media' / 'salidas'
    if src_salidas.exists():
        dst_salidas.mkdir(parents=True, exist_ok=True)
        for archivo in src_salidas.iterdir():
            if archivo.is_file():
                shutil.copy2(archivo, dst_salidas / archivo.name)

    img_dir = Path(django_settings.BASE_DIR) / 'static' / 'img'
    logo_src = img_dir / 'logo-blanco.png'
    if not logo_src.exists():
        logo_src = img_dir / 'logo.png'
    if not logo_src.exists():
        logo_src = img_dir / 'logo-olala.png'
    if logo_src.exists():
        shutil.copy2(logo_src, dest_dir / 'logo.png')

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
