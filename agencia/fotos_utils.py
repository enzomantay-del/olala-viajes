"""Diagnóstico de fotos de salidas (disco local vs nube)."""

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
    }


def puede_publicar_seguro():
    resumen = resumen_fotos_salidas()
    if resumen['produccion'] and not resumen['cloudinary']:
        return False, (
            'En Render las fotos se borran del servidor. '
            'Configurá CLOUDINARY_URL en Environment (ver FLUJO-SIMPLE.md).'
        )
    if resumen['faltan'] > 0:
        return False, (
            f'Faltan {resumen["faltan"]} de {resumen["total"]} fotos en el almacenamiento. '
            'Desde tu PC ejecutá restaurar-fotos.bat (con CLOUDINARY_URL y DATABASE_URL en .env).'
        )
    return True, ''
