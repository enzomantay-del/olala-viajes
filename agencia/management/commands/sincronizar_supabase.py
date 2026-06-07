from django.core.management.base import BaseCommand

from agencia.supabase_sync import sincronizar_todas_las_salidas, supabase_configurado


class Command(BaseCommand):
    help = 'Sube todas las salidas y fotos a Supabase (catálogo público).'

    def handle(self, *args, **options):
        if not supabase_configurado():
            self.stderr.write('Configurá SUPABASE_URL y SUPABASE_SERVICE_KEY en .env')
            return
        n = sincronizar_todas_las_salidas()
        self.stdout.write(self.style.SUCCESS(f'Sincronizadas {n} salidas en Supabase.'))
