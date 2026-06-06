"""Lanza la publicación en un proceso separado (funciona en Render/Linux)."""

import os
import subprocess
import sys
from pathlib import Path


def lanzar_publicacion_en_segundo_plano(base_dir):
    """
    En Linux (Render) usa fork+exec para que el proceso no muera con Gunicorn.
    En Windows usa subprocess con log.
    """
    base_dir = Path(base_dir)
    manage_py = base_dir / 'manage.py'
    log_path = base_dir / '.publish_log.txt'

    env = os.environ.copy()
    env.setdefault('DJANGO_SETTINGS_MODULE', 'olala.settings')

    if os.name != 'nt':
        pid = os.fork()
        if pid == 0:
            os.setsid()
            with open(log_path, 'w', encoding='utf-8') as log:
                os.dup2(log.fileno(), 1)
                os.dup2(log.fileno(), 2)
            os.execvpe(
                sys.executable,
                [sys.executable, str(manage_py), 'publicar_sitio_web'],
                env,
            )
        if pid > 0:
            return True, ''
        return False, 'No se pudo crear el proceso de publicación.'

    with open(log_path, 'w', encoding='utf-8') as log:
        subprocess.Popen(
            [sys.executable, str(manage_py), 'publicar_sitio_web'],
            cwd=str(base_dir),
            stdout=log,
            stderr=subprocess.STDOUT,
            env=env,
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
        )
    return True, ''
