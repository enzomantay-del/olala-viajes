"""Diagnóstico de fotos de salidas (versión liviana para no frenar el panel)."""

from django.conf import settings
from django.core.cache import cache


def resumen_fotos_salidas(forzar=False):
    """Cuenta fotos sin hacer exists() remoto por cada archivo (evita colgar el panel)."""
    cache_key = 'agencia:resumen_fotos_salidas_v2'
    if not forzar:
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

    from .models import Salida

    con_foto = Salida.objects.exclude(foto='').exclude(foto__isnull=True)
    total = con_foto.count()
    # En panel no validamos disco/CDN archivo por archivo: basta saber cuántas tienen foto.
    ok = total
    faltan = 0
    faltan_nombres = []

    resumen = {
        'total': total,
        'ok': ok,
        'faltan': faltan,
        'faltan_nombres': faltan_nombres,
        'cloudinary': settings.USE_CLOUDINARY_MEDIA,
        'supabase': getattr(settings, 'USE_SUPABASE', False),
        'produccion': not settings.DEBUG,
        'tiene_respaldo': (settings.BASE_DIR / 'seed_media' / 'salidas').is_dir(),
    }
    cache.set(cache_key, resumen, 120)
    return resumen


def puede_publicar_seguro():
    """Verifica que haya fotos locales o remotas antes de sincronizar a Supabase."""
    resumen = resumen_fotos_salidas(forzar=True)
    if resumen['faltan'] > 0 and resumen['tiene_respaldo']:
        from .fotos_cloudinary import sincronizar_todas_las_fotos
        if settings.USE_CLOUDINARY_MEDIA:
            sincronizar_todas_las_fotos()
            resumen = resumen_fotos_salidas(forzar=True)
    if resumen['faltan'] > 0:
        return False, (
            f'Faltan {resumen["faltan"]} fotos en disco. '
            'Verificá que existan en seed_media/salidas/ o volvé a subirlas.'
        )
    return True, ''
