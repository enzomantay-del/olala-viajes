from decimal import Decimal

from django.conf import settings as django_settings
from django.core.cache import cache
from django.db.models import Sum, F, DecimalField, Count, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta

from .models import Reserva


def agencia_sitio(request):
    """URLs públicas del sitio (Firebase), independientes del host del panel."""
    return {'public_web_url': django_settings.PUBLIC_WEB_BASE_URL}


def estado_publicacion_web(request):
    return {'estado_publicacion': None, 'publicacion_log': ''}


def estado_fotos_salidas(request):
    """Solo en pantallas de Salidas (evita trabajo en cada click del menú)."""
    if not request.user.is_authenticated:
        return {'estado_fotos': None}
    name = ''
    try:
        name = request.resolver_match.url_name or ''
    except Exception:
        pass
    if 'salida' not in name:
        return {'estado_fotos': None}
    from .fotos_utils import resumen_fotos_salidas
    try:
        return {'estado_fotos': resumen_fotos_salidas()}
    except Exception:
        return {'estado_fotos': None}


def alertas_globales(request):
    if not request.user.is_authenticated:
        return {'alertas_salidas': 0, 'alertas_saldos': 0}

    cache_key = 'agencia:alertas_globales_v2'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    hoy = timezone.now().date()
    proximos_dias = hoy + timedelta(days=7)

    try:
        salidas_proximas = Reserva.objects.filter(
            fecha_salida__gte=hoy,
            fecha_salida__lte=proximos_dias,
            estado__in=['PENDIENTE', 'CONFIRMADA'],
        ).count()

        # Consulta liviana: evita joins pesados en cada request del menú.
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
    except Exception:
        salidas_proximas = 0
        saldos_pendientes = 0

    data = {
        'alertas_salidas': salidas_proximas,
        'alertas_saldos': saldos_pendientes,
    }
    cache.set(cache_key, data, 120)
    return data
