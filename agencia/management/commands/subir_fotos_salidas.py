"""Sube fotos locales de media/salidas al almacenamiento configurado (p. ej. Cloudinary)."""

import os
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from agencia.models import Salida


class Command(BaseCommand):
    help = (
        'Sube las fotos guardadas en media/salidas/ y las asocia a cada salida. '
        'Útil para restaurar imágenes desde tu PC después de configurar Cloudinary.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--carpeta',
            type=str,
            default='',
            help='Carpeta con las fotos (por defecto: MEDIA_ROOT/salidas)',
        )
        parser.add_argument(
            '--forzar',
            action='store_true',
            help='Vuelve a subir aunque la foto ya exista en el almacenamiento',
        )

    def handle(self, *args, **options):
        if options['carpeta']:
            carpeta = Path(options['carpeta'])
        else:
            media = Path(settings.MEDIA_ROOT) / 'salidas'
            seed = Path(settings.BASE_DIR) / 'seed_media' / 'salidas'
            carpeta = media if media.is_dir() else seed
        if not carpeta.is_dir():
            self.stderr.write(self.style.ERROR(f'No existe la carpeta: {carpeta}'))
            return

        archivos = {p.name: p for p in carpeta.iterdir() if p.is_file()}
        if not archivos:
            self.stderr.write(self.style.WARNING(f'Sin archivos en {carpeta}'))
            return

        subidas = 0
        omitidas = 0
        sin_archivo = 0

        for salida in Salida.objects.exclude(foto='').exclude(foto__isnull=True):
            nombre = os.path.basename(salida.foto.name)
            local = archivos.get(nombre)
            if not local:
                sin_archivo += 1
                self.stdout.write(f'  Sin archivo local: {salida.pk} — {nombre}')
                continue

            if not options['forzar']:
                try:
                    if salida.foto.storage.exists(salida.foto.name):
                        omitidas += 1
                        continue
                except Exception:
                    pass

            with open(local, 'rb') as f:
                salida.foto.save(nombre, File(f), save=True)
            subidas += 1
            self.stdout.write(self.style.SUCCESS(f'  Subida: {salida.pk} — {nombre}'))

        self.stdout.write('')
        self.stdout.write(
            f'Listo: {subidas} subidas, {omitidas} ya existían, '
            f'{sin_archivo} sin archivo local ({len(archivos)} archivos en carpeta).'
        )
        if not settings.USE_CLOUDINARY_MEDIA:
            self.stdout.write(
                self.style.WARNING(
                    'CLOUDINARY_URL no está configurado: las fotos quedan en disco local '
                    '(en Render se pierden al reiniciar).'
                )
            )
