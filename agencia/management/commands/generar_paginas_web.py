from django.core.management.base import BaseCommand

from agencia.models import Salida
from agencia.sitio_estatico import asegurar_assets_sitio, generar_paginas_paquetes
from agencia.supabase_sync import _cargar_cache_remoto, imagen_og_compartir, supabase_configurado


class Command(BaseCommand):
    help = 'Genera paquete/{id}.html con imagen para WhatsApp/Facebook (sin sync completo).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flyers',
            action='store_true',
            help='Regenerar flyers antes (más lento, mejora vista previa).',
        )

    def handle(self, *args, **options):
        if supabase_configurado():
            _cargar_cache_remoto()
        if options['flyers']:
            from agencia.supabase_sync import sincronizar_todas_las_salidas
            self.stdout.write('Sincronizando flyers…')
            sincronizar_todas_las_salidas(forzar_flyers=True)
            _cargar_cache_remoto()

        salidas = list(Salida.objects.select_related('operadora').order_by('fecha_salida'))
        imagenes = {}
        for s in salidas:
            remoto = _cargar_cache_remoto().get(s.pk, {}) if supabase_configurado() else {}
            imagenes[s.pk] = imagen_og_compartir(
                s,
                imagen_url=remoto.get('imagen_url', ''),
                flyer_url=remoto.get('flyer_url', ''),
            )
        asegurar_assets_sitio()
        n = generar_paginas_paquetes(salidas, imagenes)
        self.stdout.write(self.style.SUCCESS(f'Listo: {n} páginas en sitio-publico/paquete/'))
