from django.core.management.base import BaseCommand

from agencia.supabase_sync import sincronizar_todas_las_salidas, supabase_configurado


class Command(BaseCommand):
    help = 'Sube salidas a Supabase (rápido: omite fotos/flyers ya en la nube).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flyers',
            action='store_true',
            help='Regenerar y resubir todos los flyers (más lento).',
        )

    def handle(self, *args, **options):
        if not supabase_configurado():
            self.stderr.write('Configurá SUPABASE_URL y SUPABASE_SERVICE_KEY en .env')
            return

        forzar = options['flyers']

        def progreso(i, total, nombre):
            self.stdout.write(f'  [{i}/{total}] {nombre}…', ending='\r')
            self.stdout.flush()

        self.stdout.write('Sincronizando (modo rápido)…')
        if forzar:
            self.stdout.write('Regenerando flyers…')

        n, omitidas = sincronizar_todas_las_salidas(forzar_flyers=forzar, callback=progreso)
        self.stdout.write('')
        msg = f'Listo: {n} salidas en Supabase.'
        if omitidas:
            msg += f' ({omitidas} sin cambios, omitidas)'
        self.stdout.write(self.style.SUCCESS(msg))
