"""Diagnóstico de fotos de salidas."""

from django.conf import settings


def resumen_fotos_salidas():
    from .models import Salida

    con_foto = Salida.objects.exclude(foto='').exclude(foto__isnull=True)
    total = con_foto.count()
    ok = 0
    faltan = 0
    faltan_nombres = []

    for salida in con_foto:
        try:
            if settings.USE_CLOUDINARY_MEDIA:
                url = salida.foto.url
                if url.startswith(('http://', 'https://', '//')):
                    ok += 1
                    continue
            if salida.foto.storage.exists(salida.foto.name):
                ok += 1
            else:
                faltan += 1
                faltan_nombres.append(salida.nombre_paquete)
        except Exception:
            faltan += 1
            faltan_nombres.append(salida.nombre_paquete)

    return {
        'total': total,
        'ok': ok,
        'faltan': faltan,
        'faltan_nombres': faltan_nombres[:5],
        'cloudinary': settings.USE_CLOUDINARY_MEDIA,
        'supabase': getattr(settings, 'USE_SUPABASE', False),
        'produccion': not settings.DEBUG,
        'tiene_respaldo': (settings.BASE_DIR / 'seed_media' / 'salidas').is_dir(),
    }


def puede_publicar_seguro():
    """Verifica que haya fotos locales o remotas antes de sincronizar a Supabase."""
    resumen = resumen_fotos_salidas()
    if resumen['faltan'] > 0 and resumen['tiene_respaldo']:
        from .fotos_cloudinary import sincronizar_todas_las_fotos
        if settings.USE_CLOUDINARY_MEDIA:
            sincronizar_todas_las_fotos()
            resumen = resumen_fotos_salidas()
    if resumen['faltan'] > 0:
        return False, (
            f'Faltan {resumen["faltan"]} fotos en disco. '
            'Verificá que existan en seed_media/salidas/ o volvé a subirlas.'
        )
    return True, ''
