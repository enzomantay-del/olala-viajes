"""Subida del sitio estático a Firebase Hosting."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from django.conf import settings


def _firebase_dir():
    return Path(settings.BASE_DIR)


def _firebase_cmd_base():
    """Comando base: npx (Render/Linux) o firebase.cmd (Windows)."""
    if sys.platform == 'win32':
        npm_firebase = Path(os.environ.get('APPDATA', '')) / 'npm' / 'firebase.cmd'
        if npm_firebase.exists():
            return [str(npm_firebase)]
    local_npx = shutil.which('npx')
    if local_npx:
        return [local_npx, 'firebase-tools']
    return ['firebase']


def _entorno_deploy():
    env = os.environ.copy()
    token = os.environ.get('FIREBASE_TOKEN', '').strip()
    if token:
        env['FIREBASE_TOKEN'] = token
    return env


def verificar_firebase_auth():
    """Devuelve (ok, mensaje)."""
    cmd = _firebase_cmd_base() + ['hosting:sites:list', '--project', 'turigest-ja']
    try:
        result = subprocess.run(
            cmd,
            cwd=str(_firebase_dir()),
            capture_output=True,
            text=True,
            timeout=90,
            env=_entorno_deploy(),
        )
    except FileNotFoundError:
        return False, (
            'Firebase CLI no disponible. En Render: agregá FIREBASE_TOKEN. '
            'En tu PC: npm install y firebase.cmd login --reauth'
        )
    except subprocess.TimeoutExpired:
        return False, 'Firebase tardó demasiado en responder.'

    salida = f'{result.stdout or ""}{result.stderr or ""}'
    if result.returncode == 0:
        return True, 'Conexión con Firebase OK.'

    if os.environ.get('FIREBASE_TOKEN'):
        return False, f'FIREBASE_TOKEN inválido o expirado. {salida[-200:]}'

    if 'reauth' in salida.lower() or 'credentials are no longer valid' in salida.lower():
        return False, 'Sesión de Firebase expirada. Ejecutá: firebase.cmd login --reauth'
    if 'not logged in' in salida.lower():
        return False, 'No hay sesión en Firebase. Ejecutá: firebase.cmd login --reauth'

    return False, salida.strip() or 'No se pudo verificar Firebase.'


def deploy_olala_hosting():
    """Devuelve (ok, mensaje, detalle)."""
    cmd = _firebase_cmd_base() + [
        'deploy',
        '--only',
        'hosting:olala',
        '--project',
        'turigest-ja',
        '--non-interactive',
    ]
    try:
        result = subprocess.run(
            cmd,
            cwd=str(_firebase_dir()),
            capture_output=True,
            text=True,
            timeout=300,
            env=_entorno_deploy(),
        )
    except FileNotFoundError:
        return False, 'Firebase CLI no encontrado.', ''
    except subprocess.TimeoutExpired:
        return False, 'El deploy tardó más de 5 minutos.', ''

    salida = f'{result.stdout or ""}{result.stderr or ""}'.strip()
    if result.returncode == 0:
        return True, 'Sitio publicado en https://olala-viajes.web.app', salida[-400:]

    if 'reauth' in salida.lower() or 'credentials are no longer valid' in salida.lower():
        return False, 'Firebase rechazó la sesión.', salida[-400:]

    resumen = salida.splitlines()[-1] if salida else 'Error desconocido.'
    return False, f'Deploy falló: {resumen}', salida[-400:]
