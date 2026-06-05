"""Utilidades compartidas para salidas y web pública."""

CATEGORIAS = [
    ('termas', ['terma', 'prata', 'federaci'], '♨️', 'Termas'),
    ('brasil', ['fortaleza', 'gramado', 'canela', 'blumenau', 'cerveza'], '🇧🇷', 'Brasil'),
    ('europa', ['europa', 'turqu', 'grecia', 'atenas', 'china', 'estambul'], '🌍', 'Europa & Mundo'),
]


def categorizar_salida(salida):
    """Asigna cat, emoji y cat_label en el objeto salida (in-place)."""
    nombre = salida.nombre_paquete.lower()
    salida.cat = 'argentina'
    salida.emoji = '🇦🇷'
    salida.cat_label = 'Argentina'
    for cat, claves, emoji, label in CATEGORIAS:
        if any(c in nombre for c in claves):
            salida.cat = cat
            salida.emoji = emoji
            salida.cat_label = label
            break


def categorizar_salidas(salidas):
    for s in salidas:
        categorizar_salida(s)
    return salidas
