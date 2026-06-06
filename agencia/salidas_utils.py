"""Utilidades compartidas para salidas y web pública."""

import re
import unicodedata

CATEGORIA_CHOICES = [
    ('argentina', 'Argentina'),
    ('brasil', 'Brasil'),
    ('termas', 'Termas'),
    ('playas', 'Playas'),
    ('caribe', 'Caribe'),
    ('europa', 'Europa'),
    ('mundo', 'Mundo'),
    ('naturaleza', 'Naturaleza'),
]

# slug -> (emoji, etiqueta)
CATEGORIAS_WEB = {
    'argentina': ('🇦🇷', 'Argentina'),
    'brasil': ('🇧🇷', 'Brasil'),
    'termas': ('♨️', 'Termas'),
    'playas': ('🏖️', 'Playas'),
    'caribe': ('🏝️', 'Caribe'),
    'europa': ('🇪🇺', 'Europa'),
    'mundo': ('🌍', 'Mundo'),
    'naturaleza': ('🦭', 'Naturaleza'),
}

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


def inferir_categorias(salida):
    """Sugiere categorías (migración o paquetes sin categorías guardadas)."""
    texto = _texto_completo(salida)
    cats = set()

    if any(_coincide(texto, k) for k in (
        'puerto madryn', 'madryn', 'ballenas', 'pinguinos', 'punta tombo', 'valdes', 'peninsula de valdes',
    )):
        cats.update(['argentina', 'naturaleza'])
        return sorted(cats)

    if any(_coincide(texto, k) for k in (
        'punta cana', 'mar caribe', 'caribe', 'bavaro', 'republica dominicana',
        'dominicana', 'cancun', 'riviera maya',
    )):
        cats.update(['caribe', 'playas', 'mundo'])

    if any(_coincide(texto, k) for k in (
        'europa', 'turquia', 'grecia', 'atenas', 'china', 'estambul', 'paris', 'roma',
        'barcelona', 'madrid', 'venecia', 'mikonos', 'santorini', 'capadocia', 'pekin',
    )):
        cats.update(['europa', 'mundo'])

    if any(_coincide(texto, k) for k in (
        'fortaleza', 'cumbuco', 'meireles', 'natal', 'porto de galinhas', 'jericoacoara',
        'florianopolis', 'costa do sauipe',
    )):
        cats.update(['playas'])
        if _es_brasil(salida, texto):
            cats.add('brasil')

    if any(_coincide(texto, k) for k in (
        'termas de rio hondo', 'rio hondo', 'villa carlos paz', 'federacion',
        'colon entre rios', 'santa teresa',
    )):
        cats.add('termas')

    if _es_brasil(salida, texto):
        cats.add('brasil')

    if any(_coincide(texto, k) for k in (
        'bariloche', 'mendoza', 'salta', 'ushuaia', 'calafate', 'iguazu', 'tucuman',
        'cataratas', 'patagonia', 'rio hondo', 'termas de rio hondo',
    )):
        cats.add('argentina')

    if cats & {'caribe', 'europa', 'mundo'} and 'naturaleza' not in cats:
        cats.discard('argentina')

    if not cats:
        cats.add('argentina')

    return sorted(cats)


def aplicar_categorias_web(salida):
    """Asigna atributos de categoría para plantillas (soporta varias por paquete)."""
    cats = salida.get_categorias_slugs()
    if not cats:
        cats = inferir_categorias(salida)

    salida.cats = cats
    salida.cat = cats[0]
    labels = [CATEGORIAS_WEB[c][1] for c in cats if c in CATEGORIAS_WEB]
    salida.cat_label = ' · '.join(labels) if labels else 'Viajes'
    salida.emoji = CATEGORIAS_WEB.get(cats[0], ('✈️', 'Viajes'))[0]
    return salida


def aplicar_categorias_salidas(salidas):
    for s in salidas:
        aplicar_categorias_web(s)
    return salidas


# Compatibilidad con imports antiguos
def categorizar_salida(salida):
    return aplicar_categorias_web(salida)


def categorizar_salidas(salidas):
    return aplicar_categorias_salidas(salidas)
