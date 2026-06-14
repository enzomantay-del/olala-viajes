"""Genera assets y páginas HTML estáticas para compartir en redes (Open Graph)."""

import html
import shutil
from pathlib import Path
from urllib.parse import quote

from django.conf import settings

from .og_catalogo import OG_DESCRIPCION, generar_og_catalogo
from .web_publish import descripcion_og, fecha_salida_legible, url_imagen_absoluta

SITIO = Path(settings.BASE_DIR) / 'sitio-publico'
ASSETS = SITIO / 'assets'
PAQUETE_DIR = SITIO / 'paquete'


def _base_url():
    return getattr(settings, 'PUBLIC_WEB_BASE_URL', 'https://olala-viajes.web.app').rstrip('/')


OG_CATALOGO_STORAGE = 'og/og-catalogo.jpg'
OG_CATALOGO_PUBLIC_URL = (
    'https://ldtfdsipdjrmcgcsbrfc.supabase.co/storage/v1/object/public/'
    'olala-salidas/og/og-catalogo.jpg'
)


def _subir_og_catalogo_supabase(ruta_local):
    from .supabase_sync import supabase_configurado

    if not supabase_configurado() or not ruta_local.is_file():
        return OG_CATALOGO_PUBLIC_URL
    from .supabase_sync import BUCKET, TIMEOUT_SUBIDA, VERIFY, _get_session, _base

    url = f'{_base()}/storage/v1/object/{BUCKET}/{OG_CATALOGO_STORAGE}'
    resp = _get_session().post(
        url,
        data=ruta_local.read_bytes(),
        headers={'Content-Type': 'image/jpeg', 'x-upsert': 'true'},
        timeout=TIMEOUT_SUBIDA,
        verify=VERIFY,
    )
    if resp.status_code not in (200, 201, 400, 409):
        return OG_CATALOGO_PUBLIC_URL
    return OG_CATALOGO_PUBLIC_URL


def asegurar_assets_sitio():
    """Logo blanco + imagen OG del catálogo (local y Supabase para WhatsApp)."""
    ASSETS.mkdir(parents=True, exist_ok=True)
    src_logo = Path(settings.BASE_DIR) / 'static' / 'img' / 'logo-blanco.png'
    if src_logo.is_file():
        shutil.copy2(src_logo, ASSETS / 'logo-blanco.png')
    ruta_og = generar_og_catalogo(ASSETS)
    _subir_og_catalogo_supabase(ruta_og)
    return ruta_og


def _html_paquete(salida, base_url, imagen_url):
    nombre = html.escape(salida.nombre_paquete)
    desc = html.escape(descripcion_og(salida))
    fecha = html.escape(fecha_salida_legible(salida.fecha_salida))
    lugar = html.escape(salida.lugar_salida or '')
    pagina = f'{base_url}/paquete/{salida.pk}.html'
    img_og = html.escape(imagen_url)
    sim = {'ARS': '$', 'USD': 'U$S', 'BRL': 'R$'}.get(salida.moneda, salida.moneda)
    precio_html = ''
    if salida.precio:
        precio = f'{sim} {salida.precio:,.0f}'.replace(',', '.')
        precio_html = f'''
          <div class="detalle-precio">
            <div class="detalle-precio-desde">desde</div>
            <div class="detalle-precio-valor">{precio}</div>
            <div class="detalle-precio-moneda">por persona · {html.escape(salida.moneda or "ARS")}</div>
          </div>'''
    servicios = ''
    if salida.servicios_incluidos:
        items = ''.join(
            f'<li>{html.escape(ln.strip())}</li>'
            for ln in salida.servicios_incluidos.splitlines() if ln.strip()
        )
        servicios = f'<h3>Incluye</h3><ul>{items}</ul>'
    descripcion = f'<p>{html.escape(salida.descripcion)}</p>' if salida.descripcion else ''
    hero = (
        f'<img src="{img_og}" alt="{nombre}">'
        if imagen_url else ''
    )
    wa = getattr(settings, 'OLALA_WHATSAPP', '5493743483429')
    wa_link = f'https://wa.me/{wa}?text={quote(f"Hola! Consulto por {salida.nombre_paquete}")}'

    return f'''<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{nombre} — Olalá Viajes</title>
  <meta name="description" content="{desc}">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Olalá Viajes">
  <meta property="og:title" content="{nombre} — Olalá Viajes">
  <meta property="og:description" content="{desc}">
  <meta property="og:image" content="{img_og}">
  <meta property="og:image:secure_url" content="{img_og}">
  <meta property="og:image:type" content="image/jpeg">
  <meta property="og:url" content="{html.escape(pagina)}">
  <meta property="og:locale" content="es_AR">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{nombre}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{img_og}">
  <link rel="image_src" href="{img_og}">
  <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../css/catalogo.css">
  <style>
    .detalle {{ max-width: 900px; margin: 90px auto 40px; padding: 0 20px; }}
    .detalle img {{ width: 100%; max-height: 420px; object-fit: cover; border-radius: 12px; margin-bottom: 20px; }}
    .detalle h1 {{ font-size: 1.6rem; margin-bottom: 12px; }}
    .detalle-meta {{ color: #64748b; margin-bottom: 16px; }}
    .detalle ul {{ margin: 12px 0 20px 20px; }}
    .btn-volver {{ display: inline-block; margin-bottom: 20px; color: #0e7490; font-weight: 600; }}
    .detalle-cta {{ margin-top: 28px; padding-top: 24px; border-top: 1px solid var(--borde); display: flex; flex-direction: column; align-items: flex-start; gap: 20px; }}
    .detalle-precio-desde {{ font-size: .85rem; color: var(--texto-s); font-weight: 600; text-transform: uppercase; letter-spacing: .06em; margin-bottom: 4px; }}
    .detalle-precio-valor {{ font-size: clamp(2rem, 6vw, 2.75rem); font-weight: 800; color: var(--teal); line-height: 1.1; }}
    .detalle-precio-moneda {{ font-size: .9rem; color: var(--texto-s); margin-top: 6px; }}
    .btn-consultar-detalle {{ display: inline-flex; align-items: center; justify-content: center; background: #25D366; color: white; font-family: 'Poppins', sans-serif; font-size: 1rem; font-weight: 700; padding: 14px 28px; border-radius: 10px; text-decoration: none; width: 100%; max-width: 320px; }}
    @media (min-width: 520px) {{ .detalle-cta {{ flex-direction: row; align-items: center; justify-content: space-between; gap: 32px; }} .btn-consultar-detalle {{ width: auto; }} }}
  </style>
</head>
<body>
  <nav class="navbar">
    <a href="../index.html"><img src="../assets/logo-blanco.png" alt="Olalá Viajes" class="nav-logo"></a>
  </nav>
  <main class="detalle">
    <a href="../index.html" class="btn-volver">← Todos los paquetes</a>
    {hero}
    <h1>{nombre}</h1>
    <div class="detalle-meta">📅 {fecha}{f' · 📍 {lugar}' if lugar else ''}</div>
    {descripcion}
    {servicios}
    <div class="detalle-cta">
      {precio_html or '<div></div>'}
      <a class="btn-consultar-detalle" href="{wa_link}" target="_blank" rel="noopener">Consultar por WhatsApp</a>
    </div>
  </main>
</body>
</html>
'''


def generar_paginas_paquetes(salidas, imagenes_por_id=None):
    """Crea sitio-publico/paquete/{id}.html con Open Graph para WhatsApp/Facebook."""
    base = _base_url()
    PAQUETE_DIR.mkdir(parents=True, exist_ok=True)
    imagenes_por_id = imagenes_por_id or {}
    ids_vivos = set()
    for salida in salidas:
        ids_vivos.add(salida.pk)
        imagen = imagenes_por_id.get(salida.pk) or url_imagen_absoluta(salida, base)
        (PAQUETE_DIR / f'{salida.pk}.html').write_text(
            _html_paquete(salida, base, imagen),
            encoding='utf-8',
        )
    for viejo in PAQUETE_DIR.glob('*.html'):
        try:
            if int(viejo.stem) not in ids_vivos:
                viejo.unlink()
        except ValueError:
            pass
    return len(ids_vivos)
