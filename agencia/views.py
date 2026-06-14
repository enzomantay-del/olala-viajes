from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from pathlib import Path
from django.utils import timezone
from django.db.models import Sum, Q
from datetime import timedelta, date
from decimal import Decimal

from django.conf import settings as django_settings

from .models import Cliente, Proveedor, Reserva, ServicioReserva, Cobro, PagoProveedor, Recibo, Voucher, Salida, SIMBOLOS_MONEDA
from .forms import ClienteForm, ProveedorForm, ReservaForm, ServicioFormSet, CobroForm, PagoProveedorForm, ReciboForm, VoucherForm, SalidaForm
from .pdf_utils import generar_recibo_pdf, generar_voucher_pdf, generar_salidas_pdf
from .salidas_utils import categorizar_salida, categorizar_salidas
from .og_catalogo import contexto_og_catalogo
from .web_publish import generar_sitio_web_estatico, preparar_salida_web, _contexto_agencia
from .flyer_utils import generar_flyer_salida
from .salidas_utils import categorizar_salida


def _reservas_activas_qs():
    return Reserva.objects.filter(
        estado__in=['PENDIENTE', 'CONFIRMADA', 'EN_CURSO']
    ).select_related('cliente').prefetch_related('cobros', 'servicios', 'pagos_proveedor')


def _salidas_qs(ver_todas=False):
    qs = Salida.objects.select_related('operadora')
    if not ver_todas:
        hoy = timezone.now().date()
        qs = qs.filter(fecha_salida__gte=hoy)
    return qs


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

def _calcular_ganancias(reservas_qs):
    """Calcula ganancias por moneda para un queryset de reservas."""
    ganancias = {}
    for r in reservas_qs.prefetch_related('servicios'):
        g = r.ganancia
        if g is not None:
            ganancias[r.moneda_venta] = ganancias.get(r.moneda_venta, Decimal('0')) + g
    return ganancias


def dashboard(request):
    hoy = timezone.now().date()
    proximos_7 = hoy + timedelta(days=7)

    salidas_proximas = Reserva.objects.filter(
        fecha_salida__gte=hoy,
        fecha_salida__lte=proximos_7,
        estado__in=['PENDIENTE', 'CONFIRMADA']
    ).order_by('fecha_salida')

    reservas_activas = list(_reservas_activas_qs())
    con_saldo_cliente = [r for r in reservas_activas if r.saldo_pendiente_cliente > 0]
    con_saldo_proveedor = [r for r in reservas_activas if r.saldo_pendiente_proveedor > 0]

    total_clientes = Cliente.objects.filter(activo=True).count()
    total_proveedores = Proveedor.objects.filter(activo=True).count()
    total_reservas = Reserva.objects.exclude(estado='CANCELADA').count()

    # Ganancias con filtro de período
    periodo = request.GET.get('periodo', 'mes')
    desde_custom = request.GET.get('desde', '')
    hasta_custom = request.GET.get('hasta', '')

    if periodo == 'hoy':
        desde_g, hasta_g = hoy, hoy
    elif periodo == 'semana':
        desde_g = hoy - timedelta(days=hoy.weekday())
        hasta_g = hoy
    elif periodo == 'mes':
        desde_g = hoy.replace(day=1)
        hasta_g = hoy
    elif periodo == 'anio':
        desde_g = hoy.replace(month=1, day=1)
        hasta_g = hoy
    elif periodo == 'custom' and desde_custom and hasta_custom:
        from datetime import datetime
        desde_g = datetime.strptime(desde_custom, '%Y-%m-%d').date()
        hasta_g = datetime.strptime(hasta_custom, '%Y-%m-%d').date()
    else:
        desde_g = hoy.replace(day=1)
        hasta_g = hoy
        periodo = 'mes'

    reservas_periodo = Reserva.objects.filter(
        created_at__date__gte=desde_g,
        created_at__date__lte=hasta_g,
        estado__in=['CONFIRMADA', 'EN_CURSO', 'COMPLETADA', 'PENDIENTE']
    )
    ganancias_periodo = _calcular_ganancias(reservas_periodo)

    context = {
        'salidas_proximas': salidas_proximas,
        'con_saldo_cliente': con_saldo_cliente[:10],
        'con_saldo_proveedor': con_saldo_proveedor[:10],
        'total_clientes': total_clientes,
        'total_proveedores': total_proveedores,
        'total_reservas': total_reservas,
        'hoy': hoy,
        'ganancias_periodo': ganancias_periodo,
        'periodo': periodo,
        'desde_custom': desde_custom,
        'hasta_custom': hasta_custom,
        'desde_g': desde_g,
        'hasta_g': hasta_g,
    }
    return render(request, 'dashboard.html', context)


# ─── CLIENTES ─────────────────────────────────────────────────────────────────

def clientes_lista(request):
    q = request.GET.get('q', '')
    clientes = Cliente.objects.all()
    if q:
        clientes = clientes.filter(
            Q(nombre__icontains=q) | Q(apellido__icontains=q) |
            Q(nro_doc__icontains=q) | Q(email__icontains=q) |
            Q(telefono__icontains=q)
        )
    return render(request, 'clientes/lista.html', {'clientes': clientes, 'q': q})


def cliente_nuevo(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            cliente = form.save()
            messages.success(request, f'Cliente {cliente.nombre_completo} creado correctamente.')
            return redirect('cliente_detalle', pk=cliente.pk)
    else:
        form = ClienteForm()
    return render(request, 'clientes/formulario.html', {'form': form, 'titulo': 'Nuevo Cliente'})


def cliente_detalle(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    reservas = cliente.reservas.all().order_by('-fecha_salida')
    return render(request, 'clientes/detalle.html', {'cliente': cliente, 'reservas': reservas})


def cliente_editar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado correctamente.')
            return redirect('cliente_detalle', pk=pk)
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/formulario.html', {'form': form, 'titulo': 'Editar Cliente', 'cliente': cliente})


def cliente_eliminar(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        try:
            nombre = cliente.nombre_completo
            cliente.delete()
            messages.success(request, f'Cliente {nombre} eliminado.')
        except Exception:
            messages.error(request, 'No se puede eliminar el cliente porque tiene reservas asociadas.')
        return redirect('clientes_lista')
    return render(request, 'confirmar_eliminar.html', {'objeto': cliente, 'tipo': 'cliente'})


# ─── PROVEEDORES ──────────────────────────────────────────────────────────────

def proveedores_lista(request):
    q = request.GET.get('q', '')
    proveedores = Proveedor.objects.all()
    if q:
        proveedores = proveedores.filter(
            Q(nombre__icontains=q) | Q(contacto__icontains=q) | Q(email__icontains=q)
        )
    return render(request, 'proveedores/lista.html', {'proveedores': proveedores, 'q': q})


def proveedor_nuevo(request):
    if request.method == 'POST':
        form = ProveedorForm(request.POST)
        if form.is_valid():
            proveedor = form.save()
            messages.success(request, f'Proveedor {proveedor.nombre} creado correctamente.')
            return redirect('proveedor_detalle', pk=proveedor.pk)
    else:
        form = ProveedorForm()
    return render(request, 'proveedores/formulario.html', {'form': form, 'titulo': 'Nuevo Proveedor'})


def proveedor_detalle(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    reservas = Reserva.objects.filter(
        servicios__proveedor=proveedor
    ).distinct().prefetch_related('servicios__proveedor').order_by('-fecha_salida')
    return render(request, 'proveedores/detalle.html', {'proveedor': proveedor, 'reservas': reservas})


def proveedor_editar(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        form = ProveedorForm(request.POST, instance=proveedor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Proveedor actualizado correctamente.')
            return redirect('proveedor_detalle', pk=pk)
    else:
        form = ProveedorForm(instance=proveedor)
    return render(request, 'proveedores/formulario.html', {'form': form, 'titulo': 'Editar Proveedor', 'proveedor': proveedor})


def proveedor_eliminar(request, pk):
    proveedor = get_object_or_404(Proveedor, pk=pk)
    if request.method == 'POST':
        try:
            nombre = proveedor.nombre
            proveedor.delete()
            messages.success(request, f'Proveedor {nombre} eliminado.')
        except Exception:
            messages.error(request, 'No se puede eliminar el proveedor porque tiene reservas asociadas.')
        return redirect('proveedores_lista')
    return render(request, 'confirmar_eliminar.html', {'objeto': proveedor, 'tipo': 'proveedor'})


# ─── RESERVAS ─────────────────────────────────────────────────────────────────

def reservas_lista(request):
    q = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    reservas = Reserva.objects.select_related('cliente').prefetch_related('servicios__proveedor').all()
    if q:
        reservas = reservas.filter(
            Q(numero__icontains=q) | Q(cliente__nombre__icontains=q) |
            Q(cliente__apellido__icontains=q) | Q(destino__icontains=q) |
            Q(servicios__nro_reserva_proveedor__icontains=q) |
            Q(servicios__proveedor__nombre__icontains=q)
        ).distinct()
    if estado:
        reservas = reservas.filter(estado=estado)
    estados = Reserva.ESTADOS
    return render(request, 'reservas/lista.html', {'reservas': reservas, 'q': q, 'estado': estado, 'estados': estados})


def reserva_nueva(request):
    cliente_pk = request.GET.get('cliente')
    initial = {}
    if cliente_pk:
        initial['cliente'] = cliente_pk
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        formset = ServicioFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            reserva = form.save()
            formset.instance = reserva
            formset.save()
            messages.success(request, f'Reserva {reserva.numero} creada correctamente.')
            return redirect('reserva_detalle', pk=reserva.pk)
    else:
        form = ReservaForm(initial=initial)
        formset = ServicioFormSet()
    return render(request, 'reservas/formulario.html', {
        'form': form,
        'formset': formset,
        'titulo': 'Nueva Reserva',
        'proveedores_comisiones': Proveedor.objects.filter(activo=True),
    })


def reserva_detalle(request, pk):
    reserva = get_object_or_404(Reserva.objects.prefetch_related('servicios__proveedor'), pk=pk)
    cobros = reserva.cobros.all()
    pagos = reserva.pagos_proveedor.all()
    recibos = Recibo.objects.filter(cobros__reserva=reserva).distinct()
    vouchers = reserva.voucher_set.all()
    return render(request, 'reservas/detalle.html', {
        'reserva': reserva,
        'servicios': reserva.servicios.select_related('proveedor').all(),
        'cobros': cobros,
        'pagos': pagos,
        'recibos': recibos,
        'vouchers': vouchers,
        'simbolos': SIMBOLOS_MONEDA,
    })


def reserva_editar(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        formset = ServicioFormSet(request.POST, instance=reserva)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Reserva actualizada correctamente.')
            return redirect('reserva_detalle', pk=pk)
    else:
        form = ReservaForm(instance=reserva)
        formset = ServicioFormSet(instance=reserva)
    return render(request, 'reservas/formulario.html', {
        'form': form,
        'formset': formset,
        'titulo': 'Editar Reserva',
        'reserva': reserva,
        'proveedores_comisiones': Proveedor.objects.filter(activo=True),
    })


def reserva_eliminar(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        try:
            numero = reserva.numero
            reserva.delete()
            messages.success(request, f'Reserva {numero} eliminada.')
        except Exception:
            messages.error(request, 'No se puede eliminar la reserva porque tiene cobros o pagos asociados.')
        return redirect('reservas_lista')
    return render(request, 'confirmar_eliminar.html', {'objeto': reserva, 'tipo': 'reserva'})


def reserva_cambiar_estado(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        estados_validos = [e[0] for e in Reserva.ESTADOS]
        if nuevo_estado in estados_validos:
            reserva.estado = nuevo_estado
            reserva.save()
            messages.success(request, f'Estado actualizado a: {reserva.get_estado_display()}')
    return redirect('reserva_detalle', pk=pk)


# ─── COBROS ───────────────────────────────────────────────────────────────────

def cobros_lista(request):
    cobros = Cobro.objects.select_related('reserva__cliente').all()
    return render(request, 'cobros/lista.html', {'cobros': cobros})


def cobro_nuevo(request, reserva_pk):
    reserva = get_object_or_404(Reserva, pk=reserva_pk)
    if request.method == 'POST':
        form = CobroForm(request.POST)
        if form.is_valid():
            cobro = form.save(commit=False)
            cobro.reserva = reserva
            cobro.save()
            messages.success(request, 'Cobro registrado correctamente.')
            return redirect('reserva_detalle', pk=reserva_pk)
    else:
        form = CobroForm(initial={'moneda': reserva.moneda_venta})
    return render(request, 'cobros/formulario.html', {'form': form, 'reserva': reserva})


def cobro_editar(request, pk):
    cobro = get_object_or_404(Cobro, pk=pk)
    reserva = cobro.reserva
    if request.method == 'POST':
        form = CobroForm(request.POST, instance=cobro)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cobro actualizado correctamente.')
            return redirect('reserva_detalle', pk=reserva.pk)
    else:
        form = CobroForm(instance=cobro)
    return render(request, 'cobros/formulario.html', {'form': form, 'reserva': reserva, 'editando': True})


def cobro_eliminar(request, pk):
    cobro = get_object_or_404(Cobro, pk=pk)
    reserva_pk = cobro.reserva.pk
    if request.method == 'POST':
        cobro.delete()
        messages.success(request, 'Cobro eliminado.')
    return redirect('reserva_detalle', pk=reserva_pk)


# ─── PAGOS A PROVEEDORES ──────────────────────────────────────────────────────

def pagos_proveedor_lista(request):
    pagos = PagoProveedor.objects.select_related('reserva__cliente').prefetch_related('reserva__servicios__proveedor').all()
    return render(request, 'pagos_proveedor/lista.html', {'pagos': pagos})


def pago_proveedor_nuevo(request, reserva_pk):
    reserva = get_object_or_404(Reserva.objects.prefetch_related('servicios__proveedor'), pk=reserva_pk)
    if request.method == 'POST':
        form = PagoProveedorForm(request.POST, request.FILES)
        if form.is_valid():
            pago = form.save(commit=False)
            pago.reserva = reserva
            pago.save()
            messages.success(request, 'Pago a proveedor registrado correctamente.')
            return redirect('reserva_detalle', pk=reserva_pk)
    else:
        form = PagoProveedorForm(initial={'moneda': 'ARS'})
    return render(request, 'pagos_proveedor/formulario.html', {'form': form, 'reserva': reserva})


def pago_proveedor_eliminar(request, pk):
    pago = get_object_or_404(PagoProveedor, pk=pk)
    reserva_pk = pago.reserva.pk
    if request.method == 'POST':
        pago.delete()
        messages.success(request, 'Pago eliminado.')
    return redirect('reserva_detalle', pk=reserva_pk)


# ─── RECIBOS ──────────────────────────────────────────────────────────────────

def recibos_lista(request):
    recibos = Recibo.objects.select_related('cliente').all()
    return render(request, 'documentos/recibos_lista.html', {'recibos': recibos})


def recibo_nuevo(request, reserva_pk):
    reserva = get_object_or_404(Reserva, pk=reserva_pk)
    cobros_disponibles = reserva.cobros.all()

    if request.method == 'POST':
        form = ReciboForm(request.POST)
        cobros_ids = request.POST.getlist('cobros')
        if form.is_valid() and cobros_ids:
            recibo = form.save(commit=False)
            recibo.cliente = reserva.cliente
            recibo.save()
            recibo.cobros.set(Cobro.objects.filter(pk__in=cobros_ids))
            messages.success(request, f'Recibo {recibo.numero} generado correctamente.')
            return redirect('recibo_detalle', pk=recibo.pk)
        elif not cobros_ids:
            messages.error(request, 'Debe seleccionar al menos un cobro.')
    else:
        form = ReciboForm()

    return render(request, 'documentos/recibo_nuevo.html', {
        'form': form, 'reserva': reserva, 'cobros_disponibles': cobros_disponibles
    })


def recibo_detalle(request, pk):
    recibo = get_object_or_404(Recibo, pk=pk)
    return render(request, 'documentos/recibo_detalle.html', {'recibo': recibo, 'simbolos': SIMBOLOS_MONEDA})


def recibo_pdf(request, pk):
    recibo = get_object_or_404(Recibo, pk=pk)
    buffer = generar_recibo_pdf(recibo)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recibo_{recibo.numero}.pdf"'
    return response


def recibo_eliminar(request, pk):
    recibo = get_object_or_404(Recibo, pk=pk)
    if request.method == 'POST':
        recibo.delete()
        messages.success(request, 'Recibo eliminado.')
        return redirect('recibos_lista')
    return render(request, 'confirmar_eliminar.html', {'objeto': recibo, 'tipo': 'recibo'})


# ─── VOUCHERS ─────────────────────────────────────────────────────────────────

def vouchers_lista(request):
    vouchers = Voucher.objects.select_related('reserva__cliente').all()
    return render(request, 'documentos/vouchers_lista.html', {'vouchers': vouchers})


def voucher_nuevo(request, reserva_pk):
    reserva = get_object_or_404(Reserva, pk=reserva_pk)
    if request.method == 'POST':
        form = VoucherForm(request.POST)
        if form.is_valid():
            voucher = form.save(commit=False)
            voucher.reserva = reserva
            voucher.save()
            messages.success(request, f'Voucher {voucher.numero} generado correctamente.')
            return redirect('voucher_detalle', pk=voucher.pk)
    else:
        form = VoucherForm()
    return render(request, 'documentos/voucher_nuevo.html', {'form': form, 'reserva': reserva})


def voucher_detalle(request, pk):
    voucher = get_object_or_404(Voucher, pk=pk)
    return render(request, 'documentos/voucher_detalle.html', {'voucher': voucher, 'simbolos': SIMBOLOS_MONEDA})


def voucher_pdf(request, pk):
    voucher = get_object_or_404(Voucher, pk=pk)
    buffer = generar_voucher_pdf(voucher)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="voucher_{voucher.numero}.pdf"'
    return response


def voucher_eliminar(request, pk):
    voucher = get_object_or_404(Voucher, pk=pk)
    if request.method == 'POST':
        voucher.delete()
        messages.success(request, 'Voucher eliminado.')
        return redirect('vouchers_lista')
    return render(request, 'confirmar_eliminar.html', {'objeto': voucher, 'tipo': 'voucher'})


# ─── REPORTES ─────────────────────────────────────────────────────────────────

def reportes(request):
    return render(request, 'reportes/index.html')


def reporte_saldos(request):
    reservas = list(_reservas_activas_qs())

    con_saldo_cliente = [r for r in reservas if r.saldo_pendiente_cliente > 0]
    con_saldo_proveedor = [r for r in reservas if r.saldo_pendiente_proveedor > 0]

    totales_cliente = {}
    for r in con_saldo_cliente:
        moneda = r.moneda_venta
        totales_cliente[moneda] = totales_cliente.get(moneda, Decimal('0')) + r.saldo_pendiente_cliente

    totales_proveedor = {}
    for r in con_saldo_proveedor:
        for moneda, costo in r.costo_total_por_moneda.items():
            totales_proveedor[moneda] = totales_proveedor.get(moneda, Decimal('0')) + costo

    return render(request, 'reportes/saldos.html', {
        'con_saldo_cliente': con_saldo_cliente,
        'con_saldo_proveedor': con_saldo_proveedor,
        'totales_cliente': totales_cliente,
        'totales_proveedor': totales_proveedor,
        'simbolos': SIMBOLOS_MONEDA,
    })


def reporte_cobros(request):
    desde = request.GET.get('desde', '')
    hasta = request.GET.get('hasta', '')
    cobros = Cobro.objects.select_related('reserva__cliente').all()

    if desde:
        cobros = cobros.filter(fecha__gte=desde)
    if hasta:
        cobros = cobros.filter(fecha__lte=hasta)

    totales = {}
    for c in cobros:
        totales[c.moneda] = totales.get(c.moneda, Decimal('0')) + c.monto

    return render(request, 'reportes/cobros.html', {
        'cobros': cobros,
        'totales': totales,
        'desde': desde,
        'hasta': hasta,
        'simbolos': SIMBOLOS_MONEDA,
    })


def reporte_pagos(request):
    desde = request.GET.get('desde', '')
    hasta = request.GET.get('hasta', '')
    pagos = PagoProveedor.objects.select_related('reserva__cliente').prefetch_related('reserva__servicios__proveedor').all()

    if desde:
        pagos = pagos.filter(fecha__gte=desde)
    if hasta:
        pagos = pagos.filter(fecha__lte=hasta)

    totales = {}
    for p in pagos:
        totales[p.moneda] = totales.get(p.moneda, Decimal('0')) + p.monto

    return render(request, 'reportes/pagos.html', {
        'pagos': pagos,
        'totales': totales,
        'desde': desde,
        'hasta': hasta,
        'simbolos': SIMBOLOS_MONEDA,
    })


# ─── SALIDAS ──────────────────────────────────────────────────────────────────

ORDENES_VALIDOS_SALIDAS = {
    'fecha_salida', '-fecha_salida',
    'operadora__nombre', '-operadora__nombre',
    'lugar_salida', '-lugar_salida',
    'nombre_paquete', '-nombre_paquete',
}


def salidas_lista(request):
    orden = request.GET.get('orden', 'fecha_salida')
    if orden not in ORDENES_VALIDOS_SALIDAS:
        orden = 'fecha_salida'
    q = request.GET.get('q', '')
    solo_jardin = request.GET.get('jardin', '')
    ver_todas = request.GET.get('todas', '') == '1'

    salidas = _salidas_qs(ver_todas=ver_todas)
    if q:
        salidas = salidas.filter(
            Q(nombre_paquete__icontains=q) |
            Q(lugar_salida__icontains=q) |
            Q(operadora__nombre__icontains=q)
        )
    if solo_jardin == '1':
        salidas = salidas.filter(pasa_por_jardin_america=True)

    salidas = list(salidas.order_by(orden))

    import json as _json
    SIMBOLOS = {'ARS': '$', 'USD': 'U$S', 'BRL': 'R$'}
    salidas_json = _json.dumps([{
        'pk': s.pk,
        'nombre': s.nombre_paquete,
        'fecha': s.fecha_salida.isoformat(),
        'lugar': s.lugar_salida,
        'jardin': s.pasa_por_jardin_america,
        'precio': float(s.precio) if s.precio else None,
        'simbolo': SIMBOLOS.get(s.moneda, s.moneda),
        'cupos': s.cupos,
        'agotado': s.agotado,
        'descripcion': s.descripcion,
    } for s in salidas], ensure_ascii=False)

    return render(request, 'salidas/lista.html', {
        'salidas': salidas,
        'salidas_json': salidas_json,
        'q': q,
        'orden': orden,
        'solo_jardin': solo_jardin,
        'ver_todas': ver_todas,
    })


def salida_nueva(request):
    if request.method == 'POST':
        form = SalidaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salida cargada correctamente.')
            return redirect('salidas_lista')
    else:
        form = SalidaForm()
    return render(request, 'salidas/formulario.html', {'form': form, 'titulo': 'Nueva salida'})


def salida_editar(request, pk):
    salida = get_object_or_404(Salida, pk=pk)
    if request.method == 'POST':
        form = SalidaForm(request.POST, request.FILES, instance=salida)
        if form.is_valid():
            form.save()
            messages.success(request, 'Salida actualizada correctamente.')
            return redirect('salidas_lista')
    else:
        form = SalidaForm(instance=salida)
    return render(request, 'salidas/formulario.html', {'form': form, 'titulo': 'Editar salida', 'salida': salida})


def web_publica(request):
    hoy = timezone.now().date()
    salidas = list(Salida.objects.filter(fecha_salida__gte=hoy).order_by('fecha_salida'))
    categorizar_salidas(salidas)
    base_url = django_settings.PUBLIC_WEB_BASE_URL
    for s in salidas:
        preparar_salida_web(s, base_url, modo='django')
    context = {
        'salidas': salidas,
        'es_estatico': False,
        'web_base_url': base_url,
        **_contexto_agencia(request),
        **contexto_og_catalogo(base_url),
    }
    return render(request, 'web_publica.html', context)


def web_publica_paquete(request, pk):
    salida = get_object_or_404(Salida, pk=pk)
    categorizar_salida(salida)
    base_url = django_settings.PUBLIC_WEB_BASE_URL
    preparar_salida_web(salida, base_url, modo='django')
    context = {
        'salida': salida,
        's': salida,
        'es_estatico': False,
        'web_base_url': base_url,
        **_contexto_agencia(request),
    }
    return render(request, 'web_publica_paquete.html', context)


def _flyer_response(salida, as_attachment=False):
    from django.conf import settings

    categorizar_salida(salida)
    ruta = Path(settings.MEDIA_ROOT) / 'flyers' / f'{salida.pk}.jpg'
    if not ruta.exists():
        generar_flyer_salida(salida, ruta)
    kwargs = {'content_type': 'image/jpeg'}
    if as_attachment:
        nombre = f'olala-{salida.pk}-{salida.nombre_paquete[:30].replace(" ", "-")}.jpg'
        kwargs.update(as_attachment=True, filename=nombre)
    return FileResponse(ruta.open('rb'), **kwargs)


def salida_flyer(request, pk):
    """Descarga o genera el flyer JPG 9:16 del paquete."""
    salida = get_object_or_404(Salida.objects.select_related('operadora'), pk=pk)
    return _flyer_response(salida, as_attachment=True)


def web_publica_flyer(request, pk):
    """Flyer público (sin login) para compartir en redes."""
    salida = get_object_or_404(Salida.objects.select_related('operadora'), pk=pk)
    return _flyer_response(salida, as_attachment=False)


def web_og_catalogo(request):
    """Imagen Open Graph del catálogo (WhatsApp / redes)."""
    from django.conf import settings

    from .og_catalogo import generar_og_catalogo

    dest = Path(settings.MEDIA_ROOT)
    dest.mkdir(parents=True, exist_ok=True)
    ruta = dest / 'og-catalogo.jpg'
    if not ruta.exists() or ruta.stat().st_size == 0:
        generar_og_catalogo(dest)
    return FileResponse(ruta.open('rb'), content_type='image/jpeg')


def _cors_web_publica(response, request):
    origen = request.headers.get('Origin', '')
    permitidos = {
        django_settings.PUBLIC_WEB_BASE_URL.rstrip('/'),
        'https://olala-viajes.web.app',
        'http://127.0.0.1:5500',
        'http://localhost:5500',
    }
    if origen in permitidos or origen.endswith('.web.app'):
        response['Access-Control-Allow-Origin'] = origen
    response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response['Access-Control-Allow-Headers'] = 'Content-Type'
    return response


def _cors_cotizacion_response(response, request):
    return _cors_web_publica(response, request)


@csrf_exempt
def web_cotizacion(request):
    """Recibe solicitudes de cotización desde el catálogo público (Firebase)."""
    import json as _json

    from django.http import JsonResponse

    from .cotizaciones import procesar_cotizacion

    if request.method == 'OPTIONS':
        return _cors_cotizacion_response(HttpResponse(status=204), request)

    if request.method != 'POST':
        resp = JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)
        return _cors_cotizacion_response(resp, request)
    try:
        data = _json.loads(request.body.decode('utf-8'))
    except _json.JSONDecodeError:
        resp = JsonResponse({'ok': False, 'error': 'Datos inválidos'}, status=400)
        return _cors_cotizacion_response(resp, request)
    try:
        resultado = procesar_cotizacion(data)
        resp = JsonResponse(resultado)
        return _cors_cotizacion_response(resp, request)
    except ValueError as exc:
        resp = JsonResponse({'ok': False, 'error': str(exc)}, status=400)
        return _cors_cotizacion_response(resp, request)
    except Exception:
        resp = JsonResponse(
            {'ok': False, 'error': 'No pudimos enviar la solicitud. Escribinos por WhatsApp.'},
            status=500,
        )
        return _cors_cotizacion_response(resp, request)


@csrf_exempt
def web_alerta(request):
    """Recibe alertas de destino desde el catálogo público (Firebase)."""
    import json as _json

    from django.http import JsonResponse

    from .alertas import procesar_alerta

    if request.method == 'OPTIONS':
        return _cors_web_publica(HttpResponse(status=204), request)

    if request.method != 'POST':
        resp = JsonResponse({'ok': False, 'error': 'Método no permitido'}, status=405)
        return _cors_web_publica(resp, request)
    try:
        data = _json.loads(request.body.decode('utf-8'))
    except _json.JSONDecodeError:
        resp = JsonResponse({'ok': False, 'error': 'Datos inválidos'}, status=400)
        return _cors_web_publica(resp, request)
    try:
        resultado = procesar_alerta(data)
        resp = JsonResponse(resultado)
        return _cors_web_publica(resp, request)
    except ValueError as exc:
        resp = JsonResponse({'ok': False, 'error': str(exc)}, status=400)
        return _cors_web_publica(resp, request)
    except Exception:
        resp = JsonResponse(
            {'ok': False, 'error': 'No pudimos registrar la alerta. Escribinos por WhatsApp.'},
            status=500,
        )
        return _cors_web_publica(resp, request)


def salida_eliminar(request, pk):
    salida = get_object_or_404(Salida, pk=pk)
    if request.method == 'POST':
        salida.delete()
        messages.success(request, 'Salida eliminada.')
        return redirect('salidas_lista')
    return render(request, 'salidas/confirmar_eliminar.html', {'salida': salida})


def salidas_whatsapp(request):
    import json as _json

    pks = request.GET.getlist('pk')
    if pks:
        salidas = list(
            Salida.objects.select_related('operadora').filter(pk__in=pks).order_by('fecha_salida')
        )
    else:
        salidas = list(_salidas_qs(ver_todas=False).order_by('fecha_salida'))

    MESES = ['enero','febrero','marzo','abril','mayo','junio',
             'julio','agosto','septiembre','octubre','noviembre','diciembre']

    def fecha_bonita(d):
        return f'{d.day} de {MESES[d.month - 1]} de {d.year}'

    separador = '─────────────────'

    bloques = []
    for s in salidas:
        lineas = [f'🗺️ *{s.nombre_paquete}*']
        lineas.append(f'📅 Salida: {fecha_bonita(s.fecha_salida)}')
        lineas.append(f'📍 Desde: {s.lugar_salida}')
        if s.pasa_por_jardin_america:
            lineas.append('🌿 Pasa por Jardín América')
        if s.precio:
            simbolo = {'ARS': '$', 'USD': 'U$S', 'BRL': 'R$'}.get(s.moneda, s.moneda)
            lineas.append(f'💰 Precio: {simbolo} {s.precio:,.0f}')
        if s.cupos:
            if s.cupos < 10:
                lineas.append(f'🔥 *¡ÚLTIMOS {s.cupos} LUGARES DISPONIBLES!*')
            else:
                lineas.append(f'🪑 Lugares disponibles: {s.cupos}')
        if s.descripcion:
            lineas.append(f'📝 {s.descripcion[:150]}')
        bloques.append('\n'.join(lineas))

    cuerpo = f'\n{separador}\n\n'.join(bloques) if bloques else '_(Sin salidas seleccionadas)_'

    mensaje = (
        '👋 ¡Hola! Te escribimos desde *Olalá Viajes* para contarte sobre nuestras próximas salidas. ✈️🌍\n\n'
        'Tenemos opciones increíbles esperándote:\n\n'
        f'{separador}\n\n'
        f'{cuerpo}\n\n'
        f'{separador}\n\n'
        '🔥 ¡Los lugares son *limitados*! No dejes pasar esta oportunidad.\n\n'
        '📲 Respondé este mensaje o escribínos para reservar tu lugar. ¡Con gusto te asesoramos! 😊'
    )

    # encodeURIComponent en JS maneja emojis correctamente (Python quote() no)
    mensaje_json = _json.dumps(mensaje)
    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Abriendo WhatsApp...</title></head>
<body>
<script>
var msg = {mensaje_json};
window.location.href = "https://wa.me/?text=" + encodeURIComponent(msg);
</script>
<p>Redirigiendo a WhatsApp...</p>
</body></html>"""
    return HttpResponse(html)


def publicar_web(request):
    """Sincroniza salidas y fotos a Supabase (catálogo en olala-viajes.web.app)."""
    from .fotos_utils import puede_publicar_seguro
    from .supabase_sync import sincronizar_todas_las_salidas, supabase_configurado

    if not supabase_configurado():
        messages.error(
            request,
            'Falta Supabase en .env: SUPABASE_URL y SUPABASE_SERVICE_KEY '
            '(Supabase → Settings → API → service_role).',
        )
        return redirect('salidas_lista')

    ok_fotos, msg_fotos = puede_publicar_seguro()
    if not ok_fotos:
        messages.error(request, msg_fotos)
        return redirect('salidas_lista')

    try:
        n, omitidas = sincronizar_todas_las_salidas()
    except Exception as exc:
        messages.error(request, f'Error al sincronizar: {exc}')
        return redirect('salidas_lista')

    web_url = django_settings.PUBLIC_WEB_BASE_URL.rstrip('/') + '/'
    extra = f' ({omitidas} sin cambios)' if omitidas else ''
    messages.success(request, f'{n} paquetes en Supabase{extra}. Catálogo: {web_url}')
    return redirect('salidas_lista')


def reiniciar_publicacion_web(request):
    """Cancela un estado de publicación colgado."""
    from .publish_status import reiniciar_publicacion

    reiniciar_publicacion()
    messages.success(request, 'Estado de publicación reiniciado. Podés publicar de nuevo.')
    return redirect('salidas_lista')


def salidas_pdf(request):
    orden = request.GET.get('orden', 'fecha_salida')
    if orden not in ORDENES_VALIDOS_SALIDAS:
        orden = 'fecha_salida'
    q = request.GET.get('q', '')
    solo_jardin = request.GET.get('jardin', '')
    ver_todas = request.GET.get('todas', '') == '1'

    salidas = _salidas_qs(ver_todas=ver_todas)
    if q:
        salidas = salidas.filter(
            Q(nombre_paquete__icontains=q) |
            Q(lugar_salida__icontains=q) |
            Q(operadora__nombre__icontains=q)
        )
    if solo_jardin == '1':
        salidas = salidas.filter(pasa_por_jardin_america=True)
    salidas = salidas.order_by(orden)

    filtros = {'q': q, 'solo_jardin': solo_jardin == '1', 'orden': orden}
    buffer = generar_salidas_pdf(salidas, filtros=filtros)
    return HttpResponse(buffer, content_type='application/pdf',
                        headers={'Content-Disposition': 'inline; filename="salidas.pdf"'})
