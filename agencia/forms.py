from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone
from .models import Cliente, Proveedor, Reserva, ServicioReserva, Cobro, PagoProveedor, Recibo, Voucher, Salida, MONEDAS


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'tipo_doc', 'nro_doc', 'email', 'telefono', 'direccion', 'fecha_nacimiento', 'notas', 'foto_dni', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'apellido': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_doc': forms.Select(attrs={'class': 'form-select'}),
            'nro_doc': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'direccion': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'foto_dni': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*,.pdf'}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['nombre', 'tipo', 'comision_porcentaje', 'contacto', 'email', 'telefono', 'notas', 'activo']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo': forms.Select(attrs={'class': 'form-select'}),
            'comision_porcentaje': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}),
            'contacto': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'activo': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = [
            'cliente', 'descripcion', 'destino',
            'fecha_salida', 'fecha_regreso', 'pasajeros_adicionales',
            'precio_venta', 'moneda_venta',
            'comision_porcentaje',
            'estado', 'notas'
        ]
        widgets = {
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'destino': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_salida': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'fecha_regreso': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'pasajeros_adicionales': forms.SelectMultiple(attrs={'class': 'form-select', 'size': '5'}),
            'precio_venta': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'moneda_venta': forms.Select(attrs={'class': 'form-select'}),
            'comision_porcentaje': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100', 'id': 'id_comision_porcentaje'}),
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ServicioReservaForm(forms.ModelForm):
    class Meta:
        model = ServicioReserva
        fields = ['proveedor', 'tipo_servicio', 'descripcion', 'precio_costo', 'moneda_costo', 'nro_reserva_proveedor']
        widgets = {
            'proveedor': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'tipo_servicio': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Ej: vuelo GRU-EZE, hotel 3 noches...'}),
            'precio_costo': forms.NumberInput(attrs={'class': 'form-control form-control-sm costo-input', 'step': '0.01', 'min': '0', 'placeholder': '0.00'}),
            'moneda_costo': forms.Select(attrs={'class': 'form-select form-select-sm moneda-select'}),
            'nro_reserva_proveedor': forms.TextInput(attrs={'class': 'form-control form-control-sm', 'placeholder': 'Nro. reserva (opcional)'}),
        }


ServicioFormSet = inlineformset_factory(
    Reserva,
    ServicioReserva,
    form=ServicioReservaForm,
    extra=1,
    can_delete=True,
    min_num=0,
)


class CobroForm(forms.ModelForm):
    class Meta:
        model = Cobro
        fields = ['fecha', 'monto', 'moneda', 'forma_pago', 'referencia', 'notas']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'moneda': forms.Select(attrs={'class': 'form-select'}),
            'forma_pago': forms.Select(attrs={'class': 'form-select'}),
            'referencia': forms.TextInput(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha'].initial = timezone.now().date()


class PagoProveedorForm(forms.ModelForm):
    class Meta:
        model = PagoProveedor
        fields = ['fecha', 'monto', 'moneda', 'forma_pago', 'referencia', 'notas', 'comprobante']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'monto': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'moneda': forms.Select(attrs={'class': 'form-select'}),
            'forma_pago': forms.Select(attrs={'class': 'form-select'}),
            'referencia': forms.TextInput(attrs={'class': 'form-control'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'comprobante': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*,.pdf'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha'].initial = timezone.now().date()


class ReciboForm(forms.ModelForm):
    class Meta:
        model = Recibo
        fields = ['fecha', 'notas']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha'].initial = timezone.now().date()


class VoucherForm(forms.ModelForm):
    class Meta:
        model = Voucher
        fields = ['fecha', 'notas_voucher']
        widgets = {
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'notas_voucher': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fecha'].initial = timezone.now().date()


class SalidaForm(forms.ModelForm):
    class Meta:
        model = Salida
        fields = [
            'operadora', 'nombre_paquete', 'fecha_salida', 'lugar_salida',
            'pasa_por_jardin_america', 'descripcion', 'servicios_incluidos',
            'foto', 'precio', 'moneda', 'cupos', 'vacaciones_invierno', 'agotado', 'notas'
        ]
        widgets = {
            'operadora': forms.Select(attrs={'class': 'form-select'}),
            'nombre_paquete': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_salida': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'lugar_salida': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: Posadas, Puerto Iguazú...'}),
            'pasa_por_jardin_america': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción del paquete para mostrar en la web...'}),
            'servicios_incluidos': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Un servicio por línea:\nTraslado de ida y vuelta\nAlojamiento en hotel 3 estrellas\nDesayuno incluido\n...'}),
            'foto': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}),
            'moneda': forms.Select(attrs={'class': 'form-select'}),
            'cupos': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'vacaciones_invierno': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'agotado': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notas': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
