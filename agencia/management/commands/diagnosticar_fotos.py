"""Muestra cuántas fotos de salidas existen realmente en el almacenamiento."""

import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from agencia.models import Salida


class Command(BaseCommand):
    help = 'Lista salidas con foto y si el archivo existe en disco o Cloudinary.'

    def handle(self, *args, **options):
        carpeta = Path(settings.MEDIA_ROOT) / 'salidas'
        archivos_local = {p.name for p in carpeta.iterdir() if p.is_file()} if carpeta.is_dir() else set()

        con_foto = Salida.objects.exclude(foto='').exclude(foto__isnull=True)
        ok = 0
        faltan = 0

        self.stdout.write(f'Cloudinary: {"sí" if settings.USE_CLOUDINARY_MEDIA else "no"}')
        self.stdout.write(f'Archivos en {carpeta}: {len(archivos_local)}')
        self.stdout.write('')

        for salida in con_foto.order_by('pk'):
            nombre = os.path.basename(salida.foto.name)
            en_local = nombre in archivos_local
            en_storage = False
            try:
                en_storage = salida.foto.storage.exists(salida.foto.name)
            except Exception:
                pass
            if en_local or en_storage:
                ok += 1
                estado = 'OK'
            else:
                faltan += 1
                estado = self.style.ERROR('FALTA')
            self.stdout.write(f'  [{estado}] #{salida.pk} {nombre}')

        self.stdout.write('')
        self.stdout.write(f'Total con foto en base: {con_foto.count()} · OK: {ok} · Faltan: {faltan}')
        if faltan:
            self.stdout.write(
                self.style.WARNING(
                    'Ejecutá: python manage.py subir_fotos_salidas  (con CLOUDINARY_URL en .env)'
                )
            )
