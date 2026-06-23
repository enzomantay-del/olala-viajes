"""Alertas de destino: registro y notificación cuando hay salidas coincidentes."""



import json

import re

import unicodedata

from datetime import datetime



from django.conf import settings

from django.core.mail import send_mail



from .salidas_utils import CATEGORIAS_WEB



CATEGORIAS_VALIDAS = set(CATEGORIAS_WEB.keys())





def _normalizar(texto):

    texto = unicodedata.normalize('NFKD', texto or '')

    texto = texto.encode('ascii', 'ignore').decode('ascii')

    return texto.lower().strip()





def _validar_payload(data):

    destino = (data.get('destino') or '').strip()

    categoria = (data.get('categoria') or '').strip()

    if categoria and categoria not in CATEGORIAS_VALIDAS:

        raise ValueError('Categoría inválida.')

    fecha_desde = (data.get('fecha_desde') or '').strip() or None

    fecha_hasta = (data.get('fecha_hasta') or '').strip() or None

    for campo, valor in (('fecha_desde', fecha_desde), ('fecha_hasta', fecha_hasta)):

        if valor:

            try:

                datetime.strptime(valor, '%Y-%m-%d')

            except ValueError as exc:

                raise ValueError(f'{campo} inválida.') from exc

    if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:

        raise ValueError('La fecha desde no puede ser posterior a la fecha hasta.')

    if not destino and not categoria:

        raise ValueError('Indicá un destino o una categoría.')

    email = (data.get('email') or '').strip()

    whatsapp = (data.get('whatsapp') or '').strip()

    if not email and not whatsapp:

        raise ValueError('Indicá email o WhatsApp para avisarte.')

    return {

        'destino': destino,

        'categoria': categoria,

        'fecha_desde': fecha_desde,

        'fecha_hasta': fecha_hasta,

        'email': email,

        'whatsapp': whatsapp,

    }





def _guardar_supabase(payload):

    from .supabase_sync import supabase_configurado, _request



    if not supabase_configurado():

        raise ValueError('Supabase no configurado en el servidor. Contactá a la agencia.')

    row = {**payload, 'estado': 'activa', 'salidas_avisadas': []}

    try:

        result = _request(

            'POST',

            '/rest/v1/olala_alertas',

            data=row,

            extra_headers={'Prefer': 'return=representation'},

        )

    except Exception as exc:

        raise ValueError(f'No se pudo guardar la alerta: {exc}') from exc

    if isinstance(result, list) and result:

        return result[0].get('id')

    return True





def _enviar_email_agencia(payload, alerta_id):

    destinatario = getattr(settings, 'COTIZACION_EMAIL', settings.AGENCIA_EMAIL)

    cat_label = CATEGORIAS_WEB.get(payload['categoria'], ('', ''))[1] if payload['categoria'] else '—'

    cuerpo = f"""Nueva alerta de destino en el catálogo web



Destino buscado: {payload['destino'] or '—'}

Categoría: {cat_label}

Fecha desde: {payload['fecha_desde'] or '—'}

Fecha hasta: {payload['fecha_hasta'] or '—'}



Contacto email: {payload['email'] or '—'}

Contacto WhatsApp: {payload['whatsapp'] or '—'}



ID alerta: {alerta_id or '—'}



—

Olalá Viajes · Catálogo web

"""

    send_mail(

        f'[Olalá Viajes] Nueva alerta: {payload["destino"] or cat_label}',

        cuerpo,

        getattr(settings, 'DEFAULT_FROM_EMAIL', settings.AGENCIA_EMAIL),

        [destinatario],

        fail_silently=True,

    )





def procesar_alerta(data):

    payload = _validar_payload(data)

    alerta_id = _guardar_supabase(payload)

    try:

        if getattr(settings, 'EMAIL_HOST_USER', ''):

            _enviar_email_agencia(payload, alerta_id)

    except Exception:

        pass

    return {'ok': True, 'id': alerta_id if alerta_id is not True else None}





def _coincide_destino(destino_busqueda, salida):

    if not destino_busqueda:

        return True

    texto = _normalizar(

        f"{salida.get('nombre_paquete', '')} {salida.get('descripcion', '')} "

        f"{salida.get('lugar_salida', '')}"

    )

    busqueda = _normalizar(destino_busqueda)

    if busqueda in texto:

        return True

    palabras = [p for p in re.split(r'\s+', busqueda) if len(p) >= 3]

    return any(p in texto for p in palabras)





def _coincide_fecha(fecha_desde, fecha_hasta, fecha_salida):

    if not fecha_salida:

        return True

    if fecha_desde and fecha_salida < fecha_desde:

        return False

    if fecha_hasta and fecha_salida > fecha_hasta:

        return False

    return True





def _coincide_categoria(categoria, salida):

    if not categoria:

        return True

    cats = salida.get('cats') or salida.get('categorias') or []

    return categoria in cats





def alerta_coincide_salida(alerta, salida):

    if alerta.get('estado') != 'activa':

        return False

    if not _coincide_destino(alerta.get('destino', ''), salida):

        return False

    if not _coincide_categoria(alerta.get('categoria', ''), salida):

        return False

    if not _coincide_fecha(

        alerta.get('fecha_desde'),

        alerta.get('fecha_hasta'),

        salida.get('fecha_salida'),

    ):

        return False

    salida_id = int(salida.get('id', 0))

    avisadas = alerta.get('salidas_avisadas') or []

    if salida_id in avisadas:

        return False

    return True





def _enviar_match_usuario(alerta, salida):

    email = (alerta.get('email') or '').strip()

    if not email or not getattr(settings, 'EMAIL_HOST_USER', ''):

        return False

    base = getattr(settings, 'PUBLIC_WEB_BASE_URL', 'https://olala-viajes.web.app').rstrip('/')

    url = f"{base}/paquete.html?id={salida['id']}"

    cuerpo = f"""¡Hay una salida que coincide con tu alerta!



Paquete: {salida.get('nombre_paquete', '')}

Fecha de salida: {salida.get('fecha_salida', '')}

{f"Desde: {salida.get('lugar_salida')}" if salida.get('lugar_salida') else ""}



Ver paquete: {url}



Si ya no te interesa, ignorá este mensaje.



—

Olalá Viajes

"""

    send_mail(

        f"¡Nueva salida para vos! {salida.get('nombre_paquete', '')}",

        cuerpo,

        getattr(settings, 'DEFAULT_FROM_EMAIL', settings.AGENCIA_EMAIL),

        [email],

        fail_silently=True,

    )

    return True





def _enviar_match_agencia(alerta, salida):

    if not getattr(settings, 'EMAIL_HOST_USER', ''):

        return

    destinatario = getattr(settings, 'COTIZACION_EMAIL', settings.AGENCIA_EMAIL)

    cuerpo = f"""Coincidencia alerta → salida



Alerta #{alerta.get('id')}

Buscaba: {alerta.get('destino') or alerta.get('categoria') or '—'}

Contacto: {alerta.get('email') or '—'} / {alerta.get('whatsapp') or '—'}



Salida: {salida.get('nombre_paquete')} ({salida.get('fecha_salida')})



—

Olalá Viajes

"""

    send_mail(

        f"[Olalá] Alerta #{alerta.get('id')} → {salida.get('nombre_paquete')}",

        cuerpo,

        getattr(settings, 'DEFAULT_FROM_EMAIL', settings.AGENCIA_EMAIL),

        [destinatario],

        fail_silently=True,

    )





def _marcar_avisada(alerta_id, salida_id):

    from .supabase_sync import supabase_configurado, _request



    if not supabase_configurado():

        return

    rows = _request('GET', f'/rest/v1/olala_alertas?id=eq.{alerta_id}&select=salidas_avisadas') or []

    if not rows:

        return

    avisadas = list(rows[0].get('salidas_avisadas') or [])

    if salida_id not in avisadas:

        avisadas.append(salida_id)

    _request(

        'PATCH',

        f'/rest/v1/olala_alertas?id=eq.{alerta_id}',

        data={

            'salidas_avisadas': avisadas,

            'notificado_en': datetime.utcnow().isoformat() + 'Z',

        },

    )





def verificar_alertas_para_salida(salida_payload):

    from .supabase_sync import supabase_configurado, _request



    if not supabase_configurado():

        return

    try:

        alertas = _request(

            'GET',

            '/rest/v1/olala_alertas?estado=eq.activa&select=*',

        ) or []

    except Exception:

        return

    salida_id = int(salida_payload.get('id', 0))

    for alerta in alertas:

        if not alerta_coincide_salida(alerta, salida_payload):

            continue

        _enviar_match_usuario(alerta, salida_payload)

        _enviar_match_agencia(alerta, salida_payload)

        _marcar_avisada(alerta['id'], salida_id)


