from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Sube fotos faltantes a Cloudinary desde seed_media/ y media/salidas/.'

    def handle(self, *args, **options):
        try:
            from agencia.fotos_cloudinary import sincronizar_todas_las_fotos

            r = sincronizar_todas_las_fotos()
            self.stdout.write(
                f'Fotos: {r["ya_ok"]} ya en nube, {r["subidas"]} subidas, '
                f'{r["sin_archivo"]} sin archivo local.'
            )
            if not r['cloudinary']:
                self.stdout.write(
                    self.style.WARNING(
                        'Cloudinary no configurado. Revisá CLOUDINARY_URL en Render.'
                    )
                )
        except Exception as exc:
            self.stdout.write(
                self.style.WARNING(f'No se pudieron sincronizar fotos: {exc}')
            )
