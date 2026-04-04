from django.contrib import admin
from .models import Cliente, Proveedor, Reserva, Cobro, PagoProveedor, Recibo, Voucher

admin.site.register(Cliente)
admin.site.register(Proveedor)
admin.site.register(Reserva)
admin.site.register(Cobro)
admin.site.register(PagoProveedor)
admin.site.register(Recibo)
admin.site.register(Voucher)
