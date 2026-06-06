"""Estado de la publicación web (archivo compartido entre procesos)."""

import json
import threading
import time
from datetime import datetime
from pathlib import Path

from django.conf import settings

_lock = threading.Lock()
_running = False
TIMEOUT_SEGUNDOS = 12 * 60


def _status_path():
    return Path(settings.BASE_DIR) / '.publish_status.json'


def _ahora():
    return datetime.now().strftime('%d/%m/%Y %H:%M')


def leer_estado():
    path = _status_path()
    if not path.exists():
        return None
    try:
        estado = json.loads(path.read_text(encoding='utf-8'))
    except (json.JSONDecodeError, OSError):
        return None
    if estado.get('state') == 'running' and _publicacion_expirada(estado):
        finalizar_publicacion(
            False,
            'La publicación anterior quedó colgada (timeout). Podés intentar de nuevo.',
            '',
        )
        return leer_estado()
    return estado


def _publicacion_expirada(estado):
    iniciado = estado.get('started_at')
    if iniciado is None:
        return False
    return (time.time() - float(iniciado)) > TIMEOUT_SEGUNDOS


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
                    'started_at': time.time(),
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


def reiniciar_publicacion():
    """Limpia un estado colgado para poder publicar de nuevo."""
    global _running
    with _lock:
        _running = False
        path = _status_path()
        if path.exists():
            path.unlink(missing_ok=True)


def limpiar_estado():
    reiniciar_publicacion()
