from decimal import Decimal

from django.conf import settings as django_settings
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta

from .models import Reserva


def agencia_sitio(request):
    """URLs públicas del sitio (Firebase), independientes del host del panel."""
    return {'public_web_url': django_settings.PUBLIC_WEB_BASE_URL}


def estado_publicacion_web(request):
    if not request.user.is_authenticated:
        return {'estado_publicacion': None, 'publicacion_log': ''}
    from .publish_status import leer_estado, leer_log_publicacion
    estado = leer_estado()
    log = leer_log_publicacion() if estado and estado.get('state') == 'running' else ''
    return {'estado_publicacion': estado, 'publicacion_log': log}


def estado_fotos_salidas(request):
    if not request.user.is_authenticated:
        return {'estado_fotos': None}
    from .fotos_utils import resumen_fotos_salidas
    return {'estado_fotos': resumen_fotos_salidas()}


def alertas_globales(request):
    if not request.user.is_authenticated:
        return {'alertas_salidas': 0, 'alertas_saldos': 0}

    hoy = timezone.now().date()
    proximos_dias = hoy + timedelta(days=7)

    salidas_proximas = Reserva.objects.filter(
        fecha_salida__gte=hoy,
        fecha_salida__lte=proximos_dias,
        estado__in=['PENDIENTE', 'CONFIRMADA'],
    ).count()

    saldos_pendientes = (
        Reserva.objects.filter(estado__in=['PENDIENTE', 'CONFIRMADA', 'EN_CURSO'])
        .annotate(
            total_cobrado=Coalesce(
                Sum('cobros__monto'),
                Decimal('0'),
                output_field=DecimalField(max_digits=12, decimal_places=2),
            )
        )
        .filter(precio_venta__gt=F('total_cobrado'))
        .count()
    )

    return {
        'alertas_salidas': salidas_proximas,
        'alertas_saldos': saldos_pendientes,
    }
