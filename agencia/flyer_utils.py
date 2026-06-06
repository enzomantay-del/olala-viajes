"""Generación de flyers verticales 9:16 (1080×1920) para salidas."""

import os
from pathlib import Path

from django.conf import settings as django_settings
from PIL import Image, ImageDraw, ImageFont, ImageOps

_MESES = [
    'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
]


def fecha_salida_legible(fecha):
    return f'{fecha.day} de {_MESES[fecha.month - 1]} de {fecha.year}'

ANCHO = 1080
ALTO = 1920
MARGEN = 48

# Zonas fijas (evita que el precio tape el texto)
Y_HEADER_ALTO = 360
Y_FOTO_TOP = Y_HEADER_ALTO
Y_FOTO_BOTTOM = 720
Y_CONTENIDO_TOP = 738
Y_PRECIO_TOP = 1540
Y_PRECIO_ALTO = 168
Y_PIE_TOP = 1730
Y_PIE_ALTO = 190

COLOR_NARANJA = (249, 115, 22)
COLOR_BLANCO = (255, 255, 255)
COLOR_GRIS_CLARO = (203, 213, 225)
COLOR_GRIS = (148, 163, 184)
COLOR_TEAL = (14, 116, 144)
COLOR_ROJO = (220, 38, 38)
COLOR_CHECK = (34, 197, 94)

# Fondo reutilizable (evita recalcular 2M píxeles por cada flyer)
_CACHE_FONDO = None


def _ruta_logo():
    base = Path(django_settings.BASE_DIR) / 'static' / 'img'
    for nombre in ('logo-blanco.png', 'logo.png', 'logo-olala.png'):
        ruta = base / nombre
        if ruta.exists():
            return ruta
    return None


def _cargar_fuente(tamano, negrita=False):
    candidatos = []
    if os.name == 'nt':
        win = Path(os.environ.get('WINDIR', 'C:/Windows')) / 'Fonts'
        candidatos.extend([
            win / ('arialbd.ttf' if negrita else 'arial.ttf'),
            win / ('segoeuib.ttf' if negrita else 'segoeui.ttf'),
        ])
    candidatos.extend([
        Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if negrita else 'DejaVuSans.ttf'),
    ])
    for ruta in candidatos:
        if ruta.exists():
            try:
                return ImageFont.truetype(str(ruta), tamano)
            except OSError:
                continue
    return ImageFont.load_default()


def _ancho_texto(draw, texto, fuente):
    if hasattr(draw, 'textlength'):
        return draw.textlength(texto, font=fuente)
    bbox = draw.textbbox((0, 0), texto, font=fuente)
    return bbox[2] - bbox[0]


def _alto_texto(fuente):
    if hasattr(fuente, 'size'):
        return int(fuente.size * 1.25)
    return 32


def _envolver_lineas(draw, texto, fuente, ancho_max):
    palabras = texto.split()
    if not palabras:
        return []
    lineas, actual = [], []
    for palabra in palabras:
        prueba = ' '.join(actual + [palabra]) if actual else palabra
        if _ancho_texto(draw, prueba, fuente) <= ancho_max:
            actual.append(palabra)
        else:
            if actual:
                lineas.append(' '.join(actual))
            actual = [palabra]
    if actual:
        lineas.append(' '.join(actual))
    return lineas


def _gradiente_vertical(ancho, alto, color_arriba, color_abajo):
    """Degradado rápido: 1×2 píxeles escalado (no bucle por fila)."""
    base = Image.new('RGB', (1, 2))
    base.putpixel((0, 0), color_arriba)
    base.putpixel((0, 1), color_abajo)
    return base.resize((ancho, alto), Image.Resampling.BILINEAR)


def _fondo_degradado_completo():
    global _CACHE_FONDO
    if _CACHE_FONDO is None:
        _CACHE_FONDO = _gradiente_vertical(
            ANCHO, ALTO,
            (12, 95, 140),
            (10, 28, 52),
        )
    return _CACHE_FONDO.copy()


def _overlay_degradado(img_rgba, y_inicio, color_rgb, alpha_max=240):
    """Superpone degradado oscuro desde y_inicio (rápido)."""
    alto = img_rgba.height - y_inicio
    if alto <= 0:
        return img_rgba
    grad = Image.new('L', (1, alto))
    pixels = grad.load()
    for y in range(alto):
        pixels[0, y] = int((y / alto) * alpha_max)
    grad = grad.resize((img_rgba.width, alto), Image.Resampling.BILINEAR)
    capa = Image.new('RGBA', (img_rgba.width, alto), (*color_rgb, 255))
    capa.putalpha(grad)
    base = img_rgba.copy()
    base.paste(capa, (0, y_inicio), capa)
    return base


def _degradado_sobre_foto(img, y_inicio, intensidad=240):
    return _overlay_degradado(img.convert('RGBA'), y_inicio, (8, 30, 55), intensidad).convert('RGB')


def _degradado_barra_logo(img, alto_barra=170):
    """Solo oscurece la franja superior del logo (rápido)."""
    rgba = img.convert('RGBA')
    grad = Image.new('L', (1, alto_barra))
    pixels = grad.load()
    for y in range(alto_barra):
        pixels[0, y] = int(200 - (y / alto_barra) * 80)
    grad = grad.resize((rgba.width, alto_barra), Image.Resampling.BILINEAR)
    capa = Image.new('RGBA', (rgba.width, alto_barra), (8, 25, 45, 255))
    capa.putalpha(grad)
    rgba.paste(capa, (0, 0), capa)
    return rgba.convert('RGB')


def _icono_check(draw, x, y, tam=28):
    """Ícono de tilde dibujado (no depende de fuentes Unicode)."""
    draw.ellipse([x, y, x + tam, y + tam], fill=COLOR_NARANJA)
    cx, cy = x + tam // 2, y + tam // 2
    draw.line(
        [(cx - 7, cy), (cx - 2, cy + 6), (cx + 8, cy - 7)],
        fill=COLOR_BLANCO,
        width=4,
        joint='curve',
    )


def _dibujar_cabecera_logo(canvas):
    """Franja superior exclusiva para el logo (la foto no la tapa)."""
    draw = ImageDraw.Draw(canvas)
    draw.rectangle([0, 0, ANCHO, Y_HEADER_ALTO], fill=(6, 32, 58))
    draw.rectangle([0, Y_HEADER_ALTO - 5, ANCHO, Y_HEADER_ALTO], fill=COLOR_NARANJA)

    logo_path = _ruta_logo()
    if not logo_path:
        return
    try:
        logo = Image.open(logo_path).convert('RGBA')
        max_w, max_h = 800, Y_HEADER_ALTO - 32
        ratio = min(max_w / logo.width, max_h / logo.height)
        nuevo = (int(logo.width * ratio), int(logo.height * ratio))
        logo = logo.resize(nuevo, Image.Resampling.LANCZOS)
        px = (ANCHO - logo.width) // 2
        py = (Y_HEADER_ALTO - logo.height) // 2
        canvas.paste(logo, (px, py), logo)
    except Exception:
        pass


def _dibujar_zona_foto(canvas, salida):
    alto_foto = Y_FOTO_BOTTOM - Y_FOTO_TOP
    zona = Image.new('RGB', (ANCHO, alto_foto), (10, 70, 100))
    foto_ok = False
    if salida.foto:
        try:
            with salida.foto.open('rb') as archivo:
                portada = ImageOps.fit(
                    Image.open(archivo).convert('RGB'),
                    (ANCHO, alto_foto),
                    method=Image.Resampling.LANCZOS,
                )
                zona = portada
                foto_ok = True
        except Exception:
            pass

    if not foto_ok:
        draw = ImageDraw.Draw(zona)
        cat = getattr(salida, 'cat_label', 'Viajes')
        fuente = _cargar_fuente(90, negrita=True)
        draw.text((ANCHO // 2, alto_foto // 2), cat[:14], font=fuente, fill=(120, 180, 200), anchor='mm')

    canvas.paste(zona, (0, Y_FOTO_TOP))
    recorte = canvas.crop((0, Y_FOTO_TOP, ANCHO, Y_FOTO_BOTTOM))
    recorte = _degradado_sobre_foto(recorte, int(alto_foto * 0.45), 255)
    canvas.paste(recorte, (0, Y_FOTO_TOP))


def _dibujar_titulo_hero(draw, salida, y_inicio):
    margen = MARGEN
    ancho_txt = ANCHO - margen * 2
    y = y_inicio

    cat = getattr(salida, 'cat_label', None)
    if cat:
        fuente_cat = _cargar_fuente(24, negrita=True)
        tw = _ancho_texto(draw, cat.upper(), fuente_cat) + 32
        draw.rounded_rectangle(
            [margen, y, margen + tw, y + 44],
            radius=20,
            fill=COLOR_NARANJA,
        )
        draw.text((margen + 16, y + 8), cat.upper(), font=fuente_cat, fill=COLOR_BLANCO)
        y += 56

    fuente_titulo = _cargar_fuente(72, negrita=True)
    for linea in _envolver_lineas(draw, salida.nombre_paquete, fuente_titulo, ancho_txt)[:3]:
        draw.text((margen + 2, y + 2), linea, font=fuente_titulo, fill=(0, 30, 50))
        draw.text((margen, y), linea, font=fuente_titulo, fill=COLOR_BLANCO)
        y += 76
    return y


def _dibujar_badge(draw, x, y, texto, fuente):
    tw = _ancho_texto(draw, texto, fuente) + 28
    draw.rounded_rectangle([x, y, x + tw, y + 38], radius=19, fill=(20, 120, 150))
    draw.text((x + 14, y + 7), texto, font=fuente, fill=COLOR_BLANCO)
    return tw + 10


def _dibujar_precio(draw, salida):
    if not salida.precio or salida.agotado:
        return
    y = Y_PRECIO_TOP
    simbolo = {'ARS': '$', 'USD': 'U$S', 'BRL': 'R$'}.get(salida.moneda, salida.moneda)
    precio_txt = f'{simbolo} {salida.precio:,.0f}'.replace(',', '.')

    # Sombra / borde
    draw.rounded_rectangle(
        [MARGEN + 4, y + 4, ANCHO - MARGEN + 4, y + Y_PRECIO_ALTO + 4],
        radius=22,
        fill=(180, 80, 10),
    )
    draw.rounded_rectangle(
        [MARGEN, y, ANCHO - MARGEN, y + Y_PRECIO_ALTO],
        radius=22,
        fill=COLOR_NARANJA,
    )
    draw.rounded_rectangle(
        [MARGEN + 3, y + 3, ANCHO - MARGEN - 3, y + Y_PRECIO_ALTO - 3],
        radius=20,
        fill=(255, 130, 50),
    )

    fuente_label = _cargar_fuente(24, negrita=True)
    fuente_precio = _cargar_fuente(78, negrita=True)
    fuente_sub = _cargar_fuente(22)
    draw.text((MARGEN + 28, y + 18), 'PRECIO DESDE', font=fuente_label, fill=(255, 240, 230))
    draw.text((MARGEN + 28, y + 52), precio_txt, font=fuente_precio, fill=COLOR_BLANCO)
    draw.text(
        (MARGEN + 28, y + 128),
        f'por persona  ·  {salida.moneda}',
        font=fuente_sub,
        fill=(255, 250, 245),
    )


def _dibujar_pie(draw):
    y = Y_PIE_TOP
    draw.line([(MARGEN, y), (ANCHO - MARGEN, y)], fill=(60, 160, 190), width=2)

    fuente_tel = _cargar_fuente(48, negrita=True)
    fuente_wa = _cargar_fuente(30)
    fuente_leg = _cargar_fuente(22)

    telefono = django_settings.AGENCIA_TELEFONO
    draw.text((ANCHO // 2, y + 28), telefono, font=fuente_tel, fill=COLOR_BLANCO, anchor='mt')
    draw.text(
        (ANCHO // 2, y + 82),
        'WhatsApp  ·  Consultá disponibilidad',
        font=fuente_wa,
        fill=COLOR_GRIS_CLARO,
        anchor='mt',
    )
    leg = f'Olalá Viajes  ·  Leg. {django_settings.AGENCIA_LEG}  ·  Disp. {django_settings.AGENCIA_DISP}'
    draw.text((ANCHO // 2, y + 128), leg, font=fuente_leg, fill=COLOR_GRIS, anchor='mt')


def generar_flyer_salida(salida, ruta_salida):
    """Genera un JPG 9:16 con datos del paquete y logo Olalá."""
    ruta_salida = Path(ruta_salida)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)

    canvas = _fondo_degradado_completo()

    # 1) Foto debajo del encabezado
    _dibujar_zona_foto(canvas, salida)

    # 2) Logo siempre encima (franja superior dedicada)
    _dibujar_cabecera_logo(canvas)

    draw = ImageDraw.Draw(canvas)

    # Título sobre la foto (parte inferior del hero)
    _dibujar_titulo_hero(draw, salida, Y_FOTO_BOTTOM - 290)

    # --- Contenido (zona fija, sin operadora) ---
    y = Y_CONTENIDO_TOP
    y_max = Y_PRECIO_TOP - 24
    ancho_txt = ANCHO - MARGEN * 2 - 40
    indent_serv = MARGEN + 38

    fuente_label = _cargar_fuente(26, negrita=True)
    fuente_valor = _cargar_fuente(38, negrita=True)
    fuente_serv = _cargar_fuente(30)
    fuente_badge = _cargar_fuente(24, negrita=True)
    fuente_lugar = _cargar_fuente(28)

    # Fecha + lugar en tarjeta semitransparente
    draw.rounded_rectangle(
        [MARGEN, y, ANCHO - MARGEN, y + 128],
        radius=16,
        fill=(20, 80, 110),
    )
    draw.text((MARGEN + 22, y + 16), 'SALIDA', font=fuente_label, fill=COLOR_NARANJA)
    draw.text(
        (MARGEN + 22, y + 48),
        fecha_salida_legible(salida.fecha_salida),
        font=fuente_valor,
        fill=COLOR_BLANCO,
    )
    if salida.lugar_salida:
        draw.text(
            (MARGEN + 22, y + 90),
            f'Desde {salida.lugar_salida}',
            font=fuente_lugar,
            fill=COLOR_GRIS_CLARO,
        )
    y += 142

    # Badges
    badges = []
    if salida.pasa_por_jardin_america:
        badges.append('Jardín América')
    if salida.vacaciones_invierno:
        badges.append('Vac. Invierno')
    if salida.cupos and not salida.agotado:
        badges.append(
            f'¡Últimos {salida.cupos}!' if salida.cupos < 10 else f'{salida.cupos} lugares'
        )
    if badges:
        x = MARGEN
        for badge in badges:
            tw = _dibujar_badge(draw, x, y, badge, fuente_badge)
            if x + tw > ANCHO - MARGEN:
                x = MARGEN
                y += 48
            else:
                x += tw
        y += 52

    # Itinerario corto (sin operadora)
    if salida.descripcion and y < y_max - 80:
        desc = salida.descripcion.strip()
        if len(desc) > 100:
            desc = desc[:97] + '…'
        draw.text((MARGEN, y), 'ITINERARIO', font=fuente_label, fill=COLOR_NARANJA)
        y += 30
        for linea in _envolver_lineas(draw, desc, fuente_serv, ancho_txt)[:2]:
            draw.text((MARGEN, y), linea, font=fuente_serv, fill=COLOR_GRIS_CLARO)
            y += 32
        y += 12

    # Servicios con íconos dibujados
    if salida.servicios_incluidos and y < y_max - 60:
        draw.text((MARGEN, y), 'INCLUYE', font=fuente_label, fill=COLOR_NARANJA)
        y += 34
        lineas_serv = [
            ln.strip() for ln in salida.servicios_incluidos.splitlines() if ln.strip()
        ]
        alto_linea = _alto_texto(fuente_serv)
        max_lineas = max(1, (y_max - y) // (alto_linea + 6))
        for serv in lineas_serv[:max_lineas]:
            if y + alto_linea > y_max:
                break
            _icono_check(draw, MARGEN, y + 2, 28)
            for sub in _envolver_lineas(draw, serv, fuente_serv, ancho_txt)[:2]:
                draw.text((indent_serv, y), sub, font=fuente_serv, fill=COLOR_BLANCO)
                y += alto_linea
            y += 6

    # Agotado (encima del precio si aplica)
    if salida.agotado:
        y_ag = Y_PRECIO_TOP - 70
        draw.rounded_rectangle(
            [MARGEN, y_ag, ANCHO - MARGEN, y_ag + 58],
            radius=14,
            fill=COLOR_ROJO,
        )
        draw.text(
            (ANCHO // 2, y_ag + 12),
            '¡AGOTADO!',
            font=_cargar_fuente(40, negrita=True),
            fill=COLOR_BLANCO,
            anchor='mt',
        )

    # Precio y pie en posición fija
    _dibujar_precio(draw, salida)
    _dibujar_pie(draw)

    canvas.save(ruta_salida, 'JPEG', quality=93, optimize=True)
    return ruta_salida


def generar_flyers_lote(salidas, directorio):
    """Genera flyers/{pk}.jpg para cada salida en el directorio indicado."""
    import logging

    directorio = Path(directorio)
    directorio.mkdir(parents=True, exist_ok=True)
    generados = 0
    log = logging.getLogger(__name__)
    for salida in salidas:
        try:
            generar_flyer_salida(salida, directorio / f'{salida.pk}.jpg')
            generados += 1
        except Exception as exc:
            log.exception('Flyer salida %s: %s', salida.pk, exc)
    return generados
