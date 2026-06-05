from django.urls import path
from django.contrib.auth.decorators import login_required
from . import views

urlpatterns = [
    # Dashboard
    path('', login_required(views.dashboard), name='dashboard'),

    # Clientes
    path('clientes/', login_required(views.clientes_lista), name='clientes_lista'),
    path('clientes/nuevo/', login_required(views.cliente_nuevo), name='cliente_nuevo'),
    path('clientes/<int:pk>/', login_required(views.cliente_detalle), name='cliente_detalle'),
    path('clientes/<int:pk>/editar/', login_required(views.cliente_editar), name='cliente_editar'),
    path('clientes/<int:pk>/eliminar/', login_required(views.cliente_eliminar), name='cliente_eliminar'),

    # Proveedores
    path('proveedores/', login_required(views.proveedores_lista), name='proveedores_lista'),
    path('proveedores/nuevo/', login_required(views.proveedor_nuevo), name='proveedor_nuevo'),
    path('proveedores/<int:pk>/', login_required(views.proveedor_detalle), name='proveedor_detalle'),
    path('proveedores/<int:pk>/editar/', login_required(views.proveedor_editar), name='proveedor_editar'),
    path('proveedores/<int:pk>/eliminar/', login_required(views.proveedor_eliminar), name='proveedor_eliminar'),

    # Reservas
    path('reservas/', login_required(views.reservas_lista), name='reservas_lista'),
    path('reservas/nueva/', login_required(views.reserva_nueva), name='reserva_nueva'),
    path('reservas/<int:pk>/', login_required(views.reserva_detalle), name='reserva_detalle'),
    path('reservas/<int:pk>/editar/', login_required(views.reserva_editar), name='reserva_editar'),
    path('reservas/<int:pk>/eliminar/', login_required(views.reserva_eliminar), name='reserva_eliminar'),
    path('reservas/<int:pk>/estado/', login_required(views.reserva_cambiar_estado), name='reserva_cambiar_estado'),

    # Cobros
    path('cobros/', login_required(views.cobros_lista), name='cobros_lista'),
    path('cobros/nuevo/<int:reserva_pk>/', login_required(views.cobro_nuevo), name='cobro_nuevo'),
    path('cobros/<int:pk>/editar/', login_required(views.cobro_editar), name='cobro_editar'),
    path('cobros/<int:pk>/eliminar/', login_required(views.cobro_eliminar), name='cobro_eliminar'),

    # Pagos a proveedores
    path('pagos-proveedor/', login_required(views.pagos_proveedor_lista), name='pagos_proveedor_lista'),
    path('pagos-proveedor/nuevo/<int:reserva_pk>/', login_required(views.pago_proveedor_nuevo), name='pago_proveedor_nuevo'),
    path('pagos-proveedor/<int:pk>/eliminar/', login_required(views.pago_proveedor_eliminar), name='pago_proveedor_eliminar'),

    # Recibos
    path('recibos/', login_required(views.recibos_lista), name='recibos_lista'),
    path('recibos/nuevo/<int:reserva_pk>/', login_required(views.recibo_nuevo), name='recibo_nuevo'),
    path('recibos/<int:pk>/', login_required(views.recibo_detalle), name='recibo_detalle'),
    path('recibos/<int:pk>/pdf/', login_required(views.recibo_pdf), name='recibo_pdf'),
    path('recibos/<int:pk>/eliminar/', login_required(views.recibo_eliminar), name='recibo_eliminar'),

    # Vouchers
    path('vouchers/', login_required(views.vouchers_lista), name='vouchers_lista'),
    path('vouchers/nuevo/<int:reserva_pk>/', login_required(views.voucher_nuevo), name='voucher_nuevo'),
    path('vouchers/<int:pk>/', login_required(views.voucher_detalle), name='voucher_detalle'),
    path('vouchers/<int:pk>/pdf/', login_required(views.voucher_pdf), name='voucher_pdf'),
    path('vouchers/<int:pk>/eliminar/', login_required(views.voucher_eliminar), name='voucher_eliminar'),

    # Reportes
    path('reportes/', login_required(views.reportes), name='reportes'),
    path('reportes/saldos/', login_required(views.reporte_saldos), name='reporte_saldos'),
    path('reportes/cobros/', login_required(views.reporte_cobros), name='reporte_cobros'),
    path('reportes/pagos/', login_required(views.reporte_pagos), name='reporte_pagos'),

    # Web pública (sin autenticación)
    path('web/', views.web_publica, name='web_publica'),
    path('web/paquete/<int:pk>/', views.web_publica_paquete, name='web_publica_paquete'),

    # Salidas
    path('salidas/', login_required(views.salidas_lista), name='salidas_lista'),
    path('salidas/pdf/', login_required(views.salidas_pdf), name='salidas_pdf'),
    path('salidas/publicar-web/', login_required(views.publicar_web), name='publicar_web'),
    path('salidas/whatsapp/', login_required(views.salidas_whatsapp), name='salidas_whatsapp'),
    path('salidas/nueva/', login_required(views.salida_nueva), name='salida_nueva'),
    path('salidas/<int:pk>/editar/', login_required(views.salida_editar), name='salida_editar'),
    path('salidas/<int:pk>/flyer/', login_required(views.salida_flyer), name='salida_flyer'),
    path('salidas/<int:pk>/eliminar/', login_required(views.salida_eliminar), name='salida_eliminar'),
]
