"""Solicitudes de cotización desde el catálogo público."""

import json
from datetime import datetime

from django.conf import settings
from django.core.mail import send_mail

REGIMENES = (
    'sin_regimen',
    'desayuno',
    'media_pension',
    'pension_completa',
    'all_inclusive',
)
REGIMEN_LABELS = {
    'sin_regimen': 'Sin régimen',
    'desayuno': 'Desayuno',
    'media_pension': 'Media pensión',
    'pension_completa': 'Pensión completa',
    'all_inclusive': 'All inclusive',
}
HOTEL_CATEGORIAS = (
    'sin_preferencia',
    'economico',
    'estandar_3',
    'superior_4',
    'lujo_5',
)
HOTEL_LABELS = {
    'sin_preferencia': 'Sin preferencia',
    'economico': 'Económico (2*)',
    'estandar_3': 'Estándar (3*)',
    'superior_4': 'Superior (4*)',
    'lujo_5': 'Lujo (5*)',
}


def _validar_payload(data):
    destino = (data.get('destino') or '').strip()
    if not destino:
        raise ValueError('Indicá el destino.')
    fecha = (data.get('fecha_salida') or '').strip()
    try:
        datetime.strptime(fecha, '%Y-%m-%d')
    except ValueError as exc:
        raise ValueError('Fecha de salida inválida.') from exc
    try:
        noches = int(data.get('noches') or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError('Cantidad de noches inválida.') from exc
    if noches < 1:
        raise ValueError('Las noches deben ser al menos 1.')
    categoria = (data.get('categoria_hotel') or 'sin_preferencia').strip()
    if categoria not in HOTEL_LABELS:
        raise ValueError('Categoría de hotel inválida.')
    regimen = (data.get('regimen') or 'sin_regimen').strip()
    if regimen not in REGIMEN_LABELS:
        raise ValueError('Régimen alimenticio inválido.')
    try:
        adultos = int(data.get('adultos') or 0)
    except (TypeError, ValueError) as exc:
        raise ValueError('Cantidad de adultos inválida.') from exc
    if adultos < 1:
        raise ValueError('Debe haber al menos 1 adulto.')
    menores = data.get('menores') or []
    if not isinstance(menores, list):
        raise ValueError('Datos de menores inválidos.')
    menores_ok = []
    for m in menores:
        try:
            edad = int(m.get('edad') if isinstance(m, dict) else m)
        except (TypeError, ValueError, AttributeError) as exc:
            raise ValueError('Edad de menor inválida.') from exc
        if edad < 0 or edad > 17:
            raise ValueError('La edad del menor debe ser entre 0 y 17.')
        menores_ok.append({'edad': edad})
    email = (data.get('email') or '').strip()
    whatsapp = (data.get('whatsapp') or '').strip()
    if not email and not whatsapp:
        raise ValueError('Indicá email o WhatsApp para responderte.')
    return {
        'destino': destino,
        'fecha_salida': fecha,
        'noches': noches,
        'categoria_hotel': categoria,
        'regimen': regimen,
        'adultos': adultos,
        'menores': menores_ok,
        'aclaraciones': (data.get('aclaraciones') or '').strip(),
        'email': email,
        'whatsapp': whatsapp,
    }


def _guardar_supabase(payload):
    from .supabase_sync import supabase_configurado, _request

    if not supabase_configurado():
        return None
    row = {
        **payload,
        'menores': payload['menores'],
        'estado': 'pendiente',
    }
    result = _request('POST', '/rest/v1/olala_cotizaciones', data=row)
    if isinstance(result, list) and result:
        return result[0].get('id')
    return None


def _texto_menores(menores):
    if not menores:
        return 'Sin menores'
    return ', '.join(f'{m["edad"]} años' for m in menores)


def _enviar_email(payload):
    destinatario = getattr(settings, 'COTIZACION_EMAIL', settings.AGENCIA_EMAIL)
    asunto = f'[Olalá Viajes] Cotización: {payload["destino"]}'
    cuerpo = f"""Nueva solicitud de cotización desde el catálogo web

Destino: {payload['destino']}
Fecha de salida: {payload['fecha_salida']}
Noches en destino: {payload['noches']}
Categoría de hotel: {HOTEL_LABELS[payload['categoria_hotel']]}
Régimen: {REGIMEN_LABELS[payload['regimen']]}
Adultos: {payload['adultos']}
Menores: {_texto_menores(payload['menores'])}

Contacto email: {payload['email'] or '—'}
Contacto WhatsApp: {payload['whatsapp'] or '—'}

Aclaraciones:
{payload['aclaraciones'] or '—'}

—
Olalá Viajes · Catálogo web
"""
    send_mail(
        asunto,
        cuerpo,
        getattr(settings, 'DEFAULT_FROM_EMAIL', settings.AGENCIA_EMAIL),
        [destinatario],
        fail_silently=False,
    )


def procesar_cotizacion(data):
    payload = _validar_payload(data)
    registro_id = _guardar_supabase(payload)
    email_enviado = False
    try:
        if getattr(settings, 'EMAIL_HOST_USER', ''):
            _enviar_email(payload)
            email_enviado = True
    except Exception:
        if not registro_id:
            raise
    return {
        'ok': True,
        'id': registro_id,
        'email_enviado': email_enviado,
    }
