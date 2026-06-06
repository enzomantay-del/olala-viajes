from django.core.management.base import BaseCommand

from agencia.fotos_cloudinary import sincronizar_todas_las_fotos


class Command(BaseCommand):
    help = 'Sube fotos faltantes a Cloudinary desde seed_media/ y media/salidas/.'

    def handle(self, *args, **options):
        r = sincronizar_todas_las_fotos()
        self.stdout.write(
            f'Fotos: {r["ya_ok"]} ya en nube, {r["subidas"]} subidas, '
            f'{r["sin_archivo"]} sin archivo local.'
        )
        if not r['cloudinary']:
            self.stdout.write(
                self.style.WARNING(
                    'CLOUDINARY_URL no configurado. En Render las fotos nuevas se pierden al reiniciar.'
                )
            )
