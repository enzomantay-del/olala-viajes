"""Genera y despliega el sitio (proceso aparte, no se corta con Gunicorn)."""

from django.core.management.base import BaseCommand

from agencia.publish_worker import ejecutar_publicacion_web


class Command(BaseCommand):
    help = 'Publica olala-viajes.web.app (usado en segundo plano desde el panel).'

    def handle(self, *args, **options):
        self.stdout.write('Iniciando publicación web…')
        ejecutar_publicacion_web()
        self.stdout.write('Publicación finalizada.')
