from django.utils import timezone
from datetime import timedelta
from .models import Reserva

def alertas_globales(request):
    hoy = timezone.now().date()
    proximos_dias = hoy + timedelta(days=7)

    salidas_proximas = Reserva.objects.filter(
        fecha_salida__gte=hoy,
        fecha_salida__lte=proximos_dias,
        estado__in=['PENDIENTE', 'CONFIRMADA']
    ).count()

    saldos_pendientes = Reserva.objects.filter(
        estado__in=['PENDIENTE', 'CONFIRMADA', 'EN_CURSO']
    ).count()

    return {
        'alertas_salidas': salidas_proximas,
        'alertas_saldos': saldos_pendientes,
    }
