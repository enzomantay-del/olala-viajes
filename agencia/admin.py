from django.contrib import admin
from .models import Cliente, Proveedor, Reserva, Cobro, PagoProveedor, Recibo, Voucher, Salida


@admin.register(Salida)
class SalidaAdmin(admin.ModelAdmin):
    list_display = ('nombre_paquete', 'fecha_salida', 'operadora', 'precio', 'agotado', 'pasa_por_jardin_america')
    list_filter = ('agotado', 'vacaciones_invierno', 'pasa_por_jardin_america', 'moneda')
    search_fields = ('nombre_paquete', 'lugar_salida')
    date_hierarchy = 'fecha_salida'


admin.site.register(Cliente)
admin.site.register(Proveedor)
admin.site.register(Reserva)
admin.site.register(Cobro)
admin.site.register(PagoProveedor)
admin.site.register(Recibo)
admin.site.register(Voucher)
