"""Estado de la publicación web (archivo compartido entre hilos y requests)."""

import json
import threading
from datetime import datetime
from pathlib import Path

from django.conf import settings

_lock = threading.Lock()
_running = False


def _status_path():
    return Path(settings.BASE_DIR) / '.publish_status.json'


def _ahora():
    return datetime.now().strftime('%d/%m/%Y %H:%M')


def leer_estado():
    path = _status_path()
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return None


def publicacion_en_curso():
    estado = leer_estado()
    return bool(estado and estado.get('state') == 'running')


def iniciar_publicacion():
    global _running
    with _lock:
        if _running or publicacion_en_curso():
            return False
        _running = True
        _status_path().write_text(
            json.dumps(
                {
                    'state': 'running',
                    'message': 'Generando sitio y subiendo a olala-viajes.web.app…',
                    'started': _ahora(),
                },
                ensure_ascii=False,
            ),
            encoding='utf-8',
        )
        return True


def finalizar_publicacion(ok, mensaje, detalle=''):
    global _running
    with _lock:
        _running = False
        _status_path().write_text(
            json.dumps(
                {
                    'state': 'ok' if ok else 'error',
                    'message': mensaje,
                    'detalle': detalle,
                    'finished': _ahora(),
                },
                ensure_ascii=False,
            ),
            encoding='utf-8',
        )


def limpiar_estado():
    path = _status_path()
    if path.exists():
        path.unlink(missing_ok=True)
