"""Sincronización de fotos: respaldo en el repo + Cloudinary (solución permanente)."""

import os
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.files.storage import default_storage


def _seed_dir():
    return Path(settings.BASE_DIR) / 'seed_media' / 'salidas'


def _media_dir():
    return Path(settings.MEDIA_ROOT) / 'salidas'


def _buscar_archivo_local(nombre):
    for carpeta in (_media_dir(), _seed_dir()):
        ruta = carpeta / nombre
        if ruta.is_file():
            return ruta
    return None


def _subir_seed_completo_a_nube():
    """Sube todas las fotos de seed_media/ a Cloudinary (respaldo permanente en el repo)."""
    if not settings.USE_CLOUDINARY_MEDIA:
        return 0

    seed = _seed_dir()
    if not seed.is_dir():
        return 0

    subidas = 0
    for archivo in seed.iterdir():
        if not archivo.is_file():
            continue
        dest = f'salidas/{archivo.name}'
        try:
            if default_storage.exists(dest):
                continue
        except Exception:
            pass
        with open(archivo, 'rb') as f:
            default_storage.save(dest, File(f))
        subidas += 1
    return subidas


def sincronizar_todas_las_fotos():
    """
    1) Sube seed_media/ completo a Cloudinary.
    2) Por cada salida en la DB, asegura que su foto exista (seed o media local).
    """
    from .models import Salida

    seed_subidas = _subir_seed_completo_a_nube()
    subidas = 0
    ya_ok = 0
    sin_archivo = 0

    for salida in Salida.objects.exclude(foto='').exclude(foto__isnull=True):
        nombre = os.path.basename(salida.foto.name)
        if not nombre:
            continue

        try:
            if salida.foto.storage.exists(salida.foto.name):
                ya_ok += 1
                continue
        except Exception:
            pass

        local = _buscar_archivo_local(nombre)
        if not local:
            sin_archivo += 1
            continue

        with open(local, 'rb') as archivo:
            salida.foto.save(nombre, File(archivo), save=True)
        subidas += 1

    return {
        'subidas': subidas + seed_subidas,
        'ya_ok': ya_ok,
        'sin_archivo': sin_archivo,
        'cloudinary': settings.USE_CLOUDINARY_MEDIA,
    }
