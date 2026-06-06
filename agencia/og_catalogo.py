"""Imagen y metadatos Open Graph para compartir el catálogo principal."""

import json
from pathlib import Path

from django.conf import settings as django_settings
from PIL import Image, ImageDraw

from .flyer_utils import _alto_texto, _ancho_texto, _cargar_fuente, _ruta_logo

OG_ANCHO = 1200
OG_ALTO = 630

OG_DESCRIPCION = (
    'Ingresá y conocé todos los paquetes que tenemos para ofrecerte. '
    'Salidas desde Posadas y Jardín América. Consultanos por WhatsApp.'
)


def contexto_og_catalogo(base_url=None):
    url = (base_url or django_settings.PUBLIC_WEB_BASE_URL).rstrip('/')
    share_text = (
        '✈️ *Olalá Viajes*\n\n'
        'Ingresá y conocé todos los paquetes que tenemos para ofrecerte 👇\n\n'
        f'{url}/'
    )
    return {
        'og_title': 'Olalá Viajes — Paquetes turísticos',
        'og_description': OG_DESCRIPCION,
        'og_image_url': f'{url}/og-catalogo.jpg',
        'og_url': f'{url}/',
        'catalogo_share_text': share_text,
        'catalogo_share_text_json': json.dumps(share_text, ensure_ascii=False),
    }


def generar_og_catalogo(dest_dir):
    """Genera og-catalogo.jpg (1200×630) para vista previa en WhatsApp y redes."""
    dest_dir = Path(dest_dir)
    fondo = Image.new('RGB', (OG_ANCHO, OG_ALTO), (15, 23, 42))
    draw = ImageDraw.Draw(fondo)
    draw.rectangle([(0, OG_ALTO - 100), (OG_ANCHO, OG_ALTO)], fill=(14, 116, 144))

    logo_y = 150
    logo_path = _ruta_logo()
    if logo_path:
        logo = Image.open(logo_path).convert('RGBA')
        max_ancho = 420
        if logo.width > max_ancho:
            escala = max_ancho / logo.width
            logo = logo.resize((max_ancho, int(logo.height * escala)), Image.Resampling.LANCZOS)
        x = (OG_ANCHO - logo.width) // 2
        fondo.paste(logo, (x, logo_y), logo)
        logo_y += logo.height + 36
    else:
        logo_y = 220

    fuente_titulo = _cargar_fuente(34, negrita=True)
    fuente_sub = _cargar_fuente(24, negrita=False)
    linea1 = 'Paquetes turísticos 2026'
    linea2 = 'Catálogo de paquetes · Temporada 2026'
    w1 = _ancho_texto(draw, linea1, fuente_titulo)
    w2 = _ancho_texto(draw, linea2, fuente_sub)
    draw.text(((OG_ANCHO - w1) / 2, logo_y), linea1, font=fuente_titulo, fill=(255, 255, 255))
    draw.text(((OG_ANCHO - w2) / 2, logo_y + _alto_texto(fuente_titulo) + 10), linea2, font=fuente_sub, fill=(203, 213, 225))

    tagline = 'Ingresá y conocé todos nuestros destinos'
    fuente_tag = _cargar_fuente(22, negrita=True)
    wt = _ancho_texto(draw, tagline, fuente_tag)
    draw.text(((OG_ANCHO - wt) / 2, OG_ALTO - 72), tagline, font=fuente_tag, fill=(249, 115, 22))

    salida = dest_dir / 'og-catalogo.jpg'
    fondo.save(salida, 'JPEG', quality=90, optimize=True)
    return salida
