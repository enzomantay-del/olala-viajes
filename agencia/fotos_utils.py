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
        'produccion': not settings.DEBUG,
        'tiene_respaldo': (settings.BASE_DIR / 'seed_media' / 'salidas').is_dir(),
    }


def puede_publicar_seguro():
    """Sincroniza fotos automáticamente y solo bloquea si falta Cloudinary en producción."""
    from .fotos_cloudinary import sincronizar_todas_las_fotos

    resumen = resumen_fotos_salidas()
    if resumen['produccion'] and not resumen['cloudinary']:
        return False, (
            'Falta CLOUDINARY_URL en Render. Sin eso las fotos se pierden. '
            'Agregala en Environment (cloudinary.com → API Keys).'
        )

    if resumen['faltan'] > 0:
        sincronizar_todas_las_fotos()
        resumen = resumen_fotos_salidas()

    if resumen['faltan'] > 0:
        return False, (
            f'Aún faltan {resumen["faltan"]} fotos. '
            'Hacé git push (incluye seed_media/) y esperá el redeploy de Render.'
        )

    return True, ''
