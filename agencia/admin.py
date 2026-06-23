from django.contrib import admin
from .models import Cliente, Proveedor, Reserva, Cobro, PagoProveedor, Recibo, Voucher, Salida, Testimonio, Popup


@admin.register(Popup)
class PopupAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'fecha_desde', 'fecha_hasta', 'activo', 'orden')
    list_filter = ('activo',)
    search_fields = ('titulo', 'mensaje')
    ordering = ('orden', '-fecha_desde')


@admin.register(Testimonio)
class TestimonioAdmin(admin.ModelAdmin):
    list_display = ('nombre_cliente', 'destino_label', 'salida', 'estrellas', 'visible', 'orden')
    list_filter = ('visible', 'estrellas')
    search_fields = ('nombre_cliente', 'destino_label', 'texto')
    ordering = ('orden', '-created_at')


@admin.register(Salida)
class SalidaAdmin(admin.ModelAdmin):
    list_display = ('nombre_paquete', 'fecha_salida', 'categorias', 'operadora', 'precio', 'agotado')
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
