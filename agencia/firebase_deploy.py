"""Subida del sitio estático a Firebase Hosting."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

from django.conf import settings

FIREBASE_TOOLS_VERSION = '13.35.1'


def _firebase_dir():
    return Path(settings.BASE_DIR)


def _firebase_bin_path():
    base = Path(settings.BASE_DIR)
    if sys.platform == 'win32':
        return base / 'node_modules' / '.bin' / 'firebase.cmd'
    return base / 'node_modules' / '.bin' / 'firebase'


def _asegurar_firebase_cli():
    """Instala firebase-tools si no está (Render a veces no conserva node_modules)."""
    bin_path = _firebase_bin_path()
    if bin_path.exists():
        return True, ''

    npm = shutil.which('npm')
    if not npm:
        return False, 'npm no está disponible en el servidor. Contactá soporte de Render.'

    try:
        result = subprocess.run(
            [
                npm,
                'install',
                f'firebase-tools@{FIREBASE_TOOLS_VERSION}',
                '--no-audit',
                '--no-fund',
                '--prefer-offline',
            ],
            cwd=str(_firebase_dir()),
            capture_output=True,
            text=True,
            timeout=300,
        )
    except subprocess.TimeoutExpired:
        return False, 'Instalar firebase-tools tardó demasiado (timeout).'
    except OSError as exc:
        return False, f'No se pudo ejecutar npm: {exc}'

    if result.returncode != 0:
        detalle = (result.stderr or result.stdout or '').strip()[-400:]
        return False, f'No se pudo instalar firebase-tools. {detalle}'

    if not bin_path.exists():
        return False, 'firebase-tools se instaló pero no se encontró el ejecutable.'

    return True, ''


def _firebase_cmd_base():
    """Comando base: binario local del proyecto."""
    ok, msg = _asegurar_firebase_cli()
    if not ok:
        raise RuntimeError(msg)
    return [str(_firebase_bin_path())]


def _entorno_deploy():
    env = os.environ.copy()
    token = os.environ.get('FIREBASE_TOKEN', '').strip()
    if token:
        env['FIREBASE_TOKEN'] = token
    return env


def _mensaje_error_firebase(salida):
    texto = (salida or '').strip()
    bajo = texto.lower()

    if 'missing packages' in bajo or (
        'firebase-tools' in bajo and ('npm error' in bajo or 'enoent' in bajo)
    ):
        return (
            'Firebase CLI no está instalado en Render. '
            'Esperá a que termine el deploy y volvé a publicar.'
        )

    if not os.environ.get('FIREBASE_TOKEN', '').strip():
        return (
            'Falta FIREBASE_TOKEN en Render → Environment. '
            'Generalo con: firebase login:ci'
        )

    if any(
        x in bajo
        for x in (
            'authentication error',
            'invalid refresh token',
            'credentials are no longer valid',
            'failed to authenticate',
            'not logged in',
            'reauth',
        )
    ):
        return (
            'FIREBASE_TOKEN inválido o expirado. '
            'En tu PC ejecutá: firebase login:ci y pegá el token nuevo en Render.'
        )

    return texto[-350:] if texto else 'No se pudo verificar Firebase.'


def verificar_firebase_auth():
    """Devuelve (ok, mensaje)."""
    try:
        cmd = _firebase_cmd_base() + ['hosting:sites:list', '--project', 'turigest-ja']
    except RuntimeError as exc:
        return False, str(exc)

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
        return False, 'Firebase CLI no encontrado después de instalar.'
    except subprocess.TimeoutExpired:
        return False, 'Firebase tardó demasiado en responder.'

    salida = f'{result.stdout or ""}{result.stderr or ""}'
    if result.returncode == 0:
        return True, 'Conexión con Firebase OK.'

    return False, _mensaje_error_firebase(salida)


def deploy_olala_hosting():
    """Devuelve (ok, mensaje, detalle)."""
    try:
        cmd = _firebase_cmd_base() + [
            'deploy',
            '--only',
            'hosting:olala',
            '--project',
            'turigest-ja',
            '--non-interactive',
        ]
    except RuntimeError as exc:
        return False, str(exc), ''

    try:
        result = subprocess.run(
            cmd,
            cwd=str(_firebase_dir()),
            capture_output=True,
            text=True,
            timeout=600,
            env=_entorno_deploy(),
        )
    except FileNotFoundError:
        return False, 'Firebase CLI no encontrado.', ''
    except subprocess.TimeoutExpired:
        return False, 'El deploy tardó más de 5 minutos.', ''

    salida = f'{result.stdout or ""}{result.stderr or ""}'.strip()
    if result.returncode == 0:
        return True, 'Sitio publicado en https://olala-viajes.web.app', salida[-400:]

    return False, _mensaje_error_firebase(salida), salida[-400:]
