from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Clientes
    path('clientes/', views.clientes_lista, name='clientes_lista'),
    path('clientes/nuevo/', views.cliente_nuevo, name='cliente_nuevo'),
    path('clientes/<int:pk>/', views.cliente_detalle, name='cliente_detalle'),
    path('clientes/<int:pk>/editar/', views.cliente_editar, name='cliente_editar'),
    path('clientes/<int:pk>/eliminar/', views.cliente_eliminar, name='cliente_eliminar'),

    # Proveedores
    path('proveedores/', views.proveedores_lista, name='proveedores_lista'),
    path('proveedores/nuevo/', views.proveedor_nuevo, name='proveedor_nuevo'),
    path('proveedores/<int:pk>/', views.proveedor_detalle, name='proveedor_detalle'),
    path('proveedores/<int:pk>/editar/', views.proveedor_editar, name='proveedor_editar'),
    path('proveedores/<int:pk>/eliminar/', views.proveedor_eliminar, name='proveedor_eliminar'),

    # Reservas
    path('reservas/', views.reservas_lista, name='reservas_lista'),
    path('reservas/nueva/', views.reserva_nueva, name='reserva_nueva'),
    path('reservas/<int:pk>/', views.reserva_detalle, name='reserva_detalle'),
    path('reservas/<int:pk>/editar/', views.reserva_editar, name='reserva_editar'),
    path('reservas/<int:pk>/eliminar/', views.reserva_eliminar, name='reserva_eliminar'),
    path('reservas/<int:pk>/estado/', views.reserva_cambiar_estado, name='reserva_cambiar_estado'),

    # Cobros
    path('cobros/', views.cobros_lista, name='cobros_lista'),
    path('cobros/nuevo/<int:reserva_pk>/', views.cobro_nuevo, name='cobro_nuevo'),
    path('cobros/<int:pk>/editar/', views.cobro_editar, name='cobro_editar'),
    path('cobros/<int:pk>/eliminar/', views.cobro_eliminar, name='cobro_eliminar'),

    # Pagos a proveedores
    path('pagos-proveedor/', views.pagos_proveedor_lista, name='pagos_proveedor_lista'),
    path('pagos-proveedor/nuevo/<int:reserva_pk>/', views.pago_proveedor_nuevo, name='pago_proveedor_nuevo'),
    path('pagos-proveedor/<int:pk>/eliminar/', views.pago_proveedor_eliminar, name='pago_proveedor_eliminar'),

    # Recibos
    path('recibos/', views.recibos_lista, name='recibos_lista'),
    path('recibos/nuevo/<int:reserva_pk>/', views.recibo_nuevo, name='recibo_nuevo'),
    path('recibos/<int:pk>/', views.recibo_detalle, name='recibo_detalle'),
    path('recibos/<int:pk>/pdf/', views.recibo_pdf, name='recibo_pdf'),
    path('recibos/<int:pk>/eliminar/', views.recibo_eliminar, name='recibo_eliminar'),

    # Vouchers
    path('vouchers/', views.vouchers_lista, name='vouchers_lista'),
    path('vouchers/nuevo/<int:reserva_pk>/', views.voucher_nuevo, name='voucher_nuevo'),
    path('vouchers/<int:pk>/', views.voucher_detalle, name='voucher_detalle'),
    path('vouchers/<int:pk>/pdf/', views.voucher_pdf, name='voucher_pdf'),
    path('vouchers/<int:pk>/eliminar/', views.voucher_eliminar, name='voucher_eliminar'),

    # Reportes
    path('reportes/', views.reportes, name='reportes'),
    path('reportes/saldos/', views.reporte_saldos, name='reporte_saldos'),
    path('reportes/cobros/', views.reporte_cobros, name='reporte_cobros'),
    path('reportes/pagos/', views.reporte_pagos, name='reporte_pagos'),

    # Salidas
    path('salidas/', views.salidas_lista, name='salidas_lista'),
    path('salidas/pdf/', views.salidas_pdf, name='salidas_pdf'),
    path('salidas/whatsapp/', views.salidas_whatsapp, name='salidas_whatsapp'),
    path('salidas/nueva/', views.salida_nueva, name='salida_nueva'),
    path('salidas/<int:pk>/editar/', views.salida_editar, name='salida_editar'),
    path('salidas/<int:pk>/eliminar/', views.salida_eliminar, name='salida_eliminar'),
]
