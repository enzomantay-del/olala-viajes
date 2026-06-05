"""Utilidades compartidas para salidas y web pública."""

import re
import unicodedata

# Orden: la primera categoría que coincida gana (de más específica a más general).
CATEGORIAS = [
    (
        'caribe',
        [
            'punta cana', 'mar caribe', 'caribe', 'bavaro', 'bávaro', 'republica dominicana',
            'república dominicana', 'dominicana', 'cancun', 'cancún', 'riviera maya',
            'playa del carmen', 'aruba', 'curazao', 'curacao', 'bahamas', 'jamaica',
        ],
        '🏝️',
        'Caribe',
    ),
    (
        'europa',
        [
            'europa', 'turquia', 'turquía', 'grecia', 'atenas', 'china', 'estambul',
            'paris', 'parís', 'roma', 'barcelona', 'madrid', 'venecia', 'suiza',
            'francia', 'italia', 'españa', 'mikonos', 'mykonos', 'santorini',
            'capadocia', 'pamukkale', 'pekin', 'pekín', 'shanghai', 'shanghái',
        ],
        '🌍',
        'Europa & Mundo',
    ),
    (
        'playa',
        [
            'fortaleza', 'cumbuco', 'meireles', 'puerto madryn', 'madryn', 'mar del plata',
            'pinamar', 'villa gesell', 'costa atlantica', 'costa atlántica',
            'frente al mar', 'natal', 'jericoacoara', 'florianopolis',
            'florianópolis', 'costa do sauipe', 'playa bavaro', 'playa meireles',
        ],
        '🏖️',
        'Playa',
    ),
    (
        'termas',
        [
            'termas de rio hondo', 'rio hondo', 'villa carlos paz', 'carlos paz',
            'federacion', 'federación', 'colon entre rios', 'colón entre ríos',
            'santa teresa', 'laguna de guayatayoc', 'santiago del estero termal',
        ],
        '♨️',
        'Termas',
    ),
    (
        'brasil',
        [
            'brasil', 'brasileiro', 'brasileña', 'gramado', 'canela', 'blumenau',
            'igrejinha', 'snowland', 'piratuba', 'prata thermas',
            'pratas thermas', 'termas romanas', 'recanto maestro', 'restinga seca',
            'restinga sêca', 'rio grande do sul', 'santa catarina', 'porto alegre',
            'life infinity', 'villa aconchego', 'afago mareiro', 'cerveza',
            'camboriu', 'camboriú',
        ],
        '🇧🇷',
        'Brasil',
    ),
]

_MARCAS_BRASIL = {
    'brasil', 'gramado', 'canela', 'blumenau', 'piratuba', 'igrejinha', 'snowland',
    'prata thermas', 'pratas thermas', 'termas romanas', 'recanto maestro', 'restinga',
    'rio grande do sul', 'santa catarina', 'life infinity', 'villa aconchego',
    'afago mareiro', 'camboriu', 'camboriú', 'brasileiro', 'fortaleza',
}


def _normalizar(texto):
    texto = unicodedata.normalize('NFKD', texto or '')
    texto = texto.encode('ascii', 'ignore').decode('ascii')
    return texto.lower()


def _texto_completo(salida):
    partes = [
        salida.nombre_paquete,
        getattr(salida, 'descripcion', '') or '',
        getattr(salida, 'servicios_incluidos', '') or '',
    ]
    if getattr(salida, 'operadora', None):
        partes.append(str(salida.operadora))
    return _normalizar(' '.join(partes))


def _coincide(texto, clave):
    clave = _normalizar(clave)
    if not clave:
        return False
    if ' ' in clave or len(clave) > 8:
        return clave in texto
    return re.search(rf'\b{re.escape(clave)}\b', texto) is not None


def _es_brasil(salida, texto):
    if getattr(salida, 'moneda', None) == 'BRL':
        return True
    return any(_coincide(texto, marca) for marca in _MARCAS_BRASIL)


def _coincide_categoria(texto, claves):
    return any(_coincide(texto, clave) for clave in claves)


def categorizar_salida(salida):
    """Asigna cat, emoji y cat_label en el objeto salida (in-place)."""
    texto = _texto_completo(salida)
    es_brasil = _es_brasil(salida, texto)

    for cat, claves, emoji, label in CATEGORIAS:
        if cat == 'termas' and es_brasil:
            continue
        if _coincide_categoria(texto, claves):
            salida.cat = cat
            salida.emoji = emoji
            salida.cat_label = label
            return salida

    if es_brasil:
        salida.cat = 'brasil'
        salida.emoji = '🇧🇷'
        salida.cat_label = 'Brasil'
        return salida

    salida.cat = 'argentina'
    salida.emoji = '🇦🇷'
    salida.cat_label = 'Argentina'
    return salida


def categorizar_salidas(salidas):
    for s in salidas:
        categorizar_salida(s)
    return salidas
