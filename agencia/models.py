from django.db import models
from django.utils import timezone
from decimal import Decimal
import unicodedata
import re
import os


def _sanitizar_nombre_foto(instance, filename):
    """Sanitiza el nombre del archivo: elimina tildes y caracteres especiales."""
    nombre, ext = os.path.splitext(filename)
    # Normalizar unicode y eliminar acentos
    nombre = unicodedata.normalize('NFKD', nombre)
    nombre = nombre.encode('ascii', 'ignore').decode('ascii')
    # Reemplazar espacios y chars no alfanuméricos por guión bajo
    nombre = re.sub(r'[^\w\-]', '_', nombre)
    nombre = re.sub(r'_+', '_', nombre).strip('_')
    return f'salidas/{nombre}{ext.lower()}'

MONEDAS = [
    ('ARS', 'Pesos (ARS)'),
    ('USD', 'Dólares (USD)'),
    ('BRL', 'Reales (BRL)'),
]


FORMAS_PAGO = [
    ('EFECTIVO', 'Efectivo'),
    ('TRANSFERENCIA', 'Transferencia Bancaria'),
    ('TARJETA_DEB', 'Tarjeta de Débito'),
    ('TARJETA_CRED', 'Tarjeta de Crédito'),
    ('CHEQUE', 'Cheque'),
    ('MERCADOPAGO', 'MercadoPago'),
    ('DEPOSITO', 'Depósito Bancario'),
    ('OTRO', 'Otro'),
]

TIPOS_SERVICIO = [
    ('VUELO', 'Vuelo'),
    ('HOTEL', 'Hotel'),
    ('PAQUETE', 'Paquete Turístico'),
    ('CRUCERO', 'Crucero'),
    ('TRASLADO', 'Traslado'),
    ('SEGURO', 'Seguro de Viaje'),
    ('EXCURSION', 'Excursión'),
    ('OTRO', 'Otro'),
]

SIMBOLOS_MONEDA = {'ARS': '$', 'USD': 'U$S', 'BRL': 'R$'}


class Cliente(models.Model):
    TIPOS_DOC = [
        ('DNI', 'DNI'),
        ('PASAPORTE', 'Pasaporte'),
        ('LC', 'L.C.'),
        ('LE', 'L.E.'),
        ('CUIT', 'CUIT'),
    ]
    nombre = models.CharField('Nombre', max_length=100)
    apellido = models.CharField('Apellido', max_length=100)
    tipo_doc = models.CharField('Tipo de documento', max_length=20, choices=TIPOS_DOC, default='DNI')
    nro_doc = models.CharField('Nro. de documento', max_length=50, blank=True)
    email = models.EmailField('Email', blank=True)
    telefono = models.CharField('Teléfono', max_length=50, blank=True)
    direccion = models.CharField('Dirección', max_length=300, blank=True)
    fecha_nacimiento = models.DateField('Fecha de nacimiento', null=True, blank=True)
    notas = models.TextField('Notas', blank=True)
    foto_dni = models.FileField('Foto DNI', upload_to='dni/', blank=True, null=True)
    activo = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['apellido', 'nombre']

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"


class Proveedor(models.Model):
    TIPOS = [
        ('AEROLINEA', 'Aerolínea'),
        ('HOTEL', 'Hotel'),
        ('CRUCERO', 'Crucero'),
        ('AGENCIA', 'Agencia Mayorista'),
        ('OPERADOR', 'Operador Mayorista'),
        ('TRASLADO', 'Traslado'),
        ('SEGURO', 'Seguro de Viaje'),
        ('EXCURSION', 'Excursión'),
        ('OTRO', 'Otro'),
    ]
    nombre = models.CharField('Nombre', max_length=200)
    tipo = models.CharField('Tipo', max_length=20, choices=TIPOS, default='OTRO')
    comision_porcentaje = models.DecimalField('Comisión (%)', max_digits=5, decimal_places=2, default=0)
    contacto = models.CharField('Contacto', max_length=100, blank=True)
    email = models.EmailField('Email', blank=True)
    telefono = models.CharField('Teléfono', max_length=50, blank=True)
    notas = models.TextField('Notas', blank=True)
    activo = models.BooleanField('Activo', default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Reserva(models.Model):
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('CONFIRMADA', 'Confirmada'),
        ('EN_CURSO', 'En curso'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]

    numero = models.CharField('Nro. Reserva', max_length=20, unique=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, verbose_name='Cliente titular', related_name='reservas')
    descripcion = models.TextField('Descripción / Observaciones', blank=True)
    destino = models.CharField('Destino', max_length=200)
    fecha_salida = models.DateField('Fecha de salida')
    fecha_regreso = models.DateField('Fecha de regreso', null=True, blank=True)
    pasajeros_adicionales = models.ManyToManyField(
        Cliente, related_name='reservas_como_pasajero',
        blank=True, verbose_name='Pasajeros adicionales'
    )
    precio_venta = models.DecimalField('Precio de venta', max_digits=12, decimal_places=2, default=0)
    moneda_venta = models.CharField('Moneda venta', max_length=3, choices=MONEDAS, default='ARS')
    comision_porcentaje = models.DecimalField('Comisión (%)', max_digits=5, decimal_places=2, default=0)
    estado = models.CharField('Estado', max_length=20, choices=ESTADOS, default='PENDIENTE')
    notas = models.TextField('Notas internas', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        ordering = ['fecha_salida']

    def __str__(self):
        return f"{self.numero} - {self.cliente} - {self.destino}"

    def save(self, *args, **kwargs):
        if not self.numero:
            super().save(*args, **kwargs)
            self.numero = f"R{str(self.id).zfill(5)}"
            Reserva.objects.filter(pk=self.pk).update(numero=self.numero)
        else:
            super().save(*args, **kwargs)

    @property
    def costo_total_por_moneda(self):
        """Sumatoria de costos de todos los servicios, agrupada por moneda."""
        totales = {}
        for s in self.servicios.all():
            totales[s.moneda_costo] = totales.get(s.moneda_costo, Decimal('0')) + s.precio_costo
        return totales

    @property
    def precio_costo_total(self):
        """Suma de todos los costos de servicios (independientemente de la moneda)."""
        return sum((s.precio_costo for s in self.servicios.all()), Decimal('0'))

    @property
    def total_cobrado(self):
        return sum(c.monto for c in self.cobros.all())

    @property
    def saldo_pendiente_cliente(self):
        return self.precio_venta - self.total_cobrado

    @property
    def total_pagado_proveedor(self):
        return sum(p.monto for p in self.pagos_proveedor.all())

    @property
    def saldo_pendiente_proveedor(self):
        return self.precio_costo_total - self.total_pagado_proveedor

    @property
    def comision_monto(self):
        if self.comision_porcentaje and self.precio_venta:
            return (self.precio_venta * self.comision_porcentaje / 100).quantize(Decimal('0.01'))
        return Decimal('0')

    @property
    def ganancia(self):
        costos = self.costo_total_por_moneda
        if len(costos) == 1:
            moneda_costo = list(costos.keys())[0]
            if moneda_costo == self.moneda_venta:
                return self.precio_venta - costos[moneda_costo]
        elif len(costos) == 0:
            return self.precio_venta
        return None

    def get_estado_badge(self):
        colores = {
            'PENDIENTE': 'warning',
            'CONFIRMADA': 'info',
            'EN_CURSO': 'primary',
            'COMPLETADA': 'success',
            'CANCELADA': 'danger',
        }
        return colores.get(self.estado, 'secondary')


class ServicioReserva(models.Model):
    """Un servicio individual dentro de una reserva (puede haber varios por reserva)."""
    reserva = models.ForeignKey(Reserva, on_delete=models.CASCADE, related_name='servicios', verbose_name='Reserva')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT, verbose_name='Proveedor')
    tipo_servicio = models.CharField('Tipo', max_length=20, choices=TIPOS_SERVICIO, default='PAQUETE')
    descripcion = models.CharField('Descripción del servicio', max_length=500, blank=True)
    precio_costo = models.DecimalField('Costo', max_digits=12, decimal_places=2, default=0)
    moneda_costo = models.CharField('Moneda', max_length=3, choices=MONEDAS, default='ARS')
    nro_reserva_proveedor = models.CharField('Nro. reserva proveedor', max_length=100, blank=True)

    class Meta:
        verbose_name = 'Servicio'
        verbose_name_plural = 'Servicios'

    def __str__(self):
        return f"{self.get_tipo_servicio_display()} — {self.proveedor}"


class Cobro(models.Model):
    """Cobro realizado al cliente por una reserva"""
    reserva = models.ForeignKey(Reserva, on_delete=models.PROTECT, related_name='cobros', verbose_name='Reserva')
    fecha = models.DateField('Fecha')
    monto = models.DecimalField('Monto', max_digits=12, decimal_places=2)
    moneda = models.CharField('Moneda', max_length=3, choices=MONEDAS, default='ARS')
    forma_pago = models.CharField('Forma de pago', max_length=20, choices=FORMAS_PAGO)
    referencia = models.CharField('Referencia / Nro. comprobante', max_length=200, blank=True)
    notas = models.TextField('Notas', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cobro'
        verbose_name_plural = 'Cobros'
        ordering = ['-fecha']

    def __str__(self):
        simbolo = SIMBOLOS_MONEDA.get(self.moneda, self.moneda)
        return f"{simbolo} {self.monto} - {self.reserva.cliente}"


class PagoProveedor(models.Model):
    """Pago realizado a un proveedor por una reserva"""
    reserva = models.ForeignKey(Reserva, on_delete=models.PROTECT, related_name='pagos_proveedor', verbose_name='Reserva')
    fecha = models.DateField('Fecha')
    monto = models.DecimalField('Monto', max_digits=12, decimal_places=2)
    moneda = models.CharField('Moneda', max_length=3, choices=MONEDAS, default='ARS')
    forma_pago = models.CharField('Forma de pago', max_length=20, choices=FORMAS_PAGO)
    referencia = models.CharField('Referencia / Nro. comprobante', max_length=200, blank=True)
    notas = models.TextField('Notas', blank=True)
    comprobante = models.FileField('Comprobante', upload_to='comprobantes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pago a Proveedor'
        verbose_name_plural = 'Pagos a Proveedores'
        ordering = ['-fecha']

    def __str__(self):
        simbolo = SIMBOLOS_MONEDA.get(self.moneda, self.moneda)
        return f"{simbolo} {self.monto} - Reserva {self.reserva.numero}"


class Recibo(models.Model):
    """Recibo de cobro emitido al cliente"""
    numero = models.CharField('Nro. Recibo', max_length=20, unique=True, blank=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, verbose_name='Cliente')
    cobros = models.ManyToManyField(Cobro, verbose_name='Cobros incluidos')
    fecha = models.DateField('Fecha', default=timezone.now)
    notas = models.TextField('Notas', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Recibo'
        verbose_name_plural = 'Recibos'
        ordering = ['-created_at']

    def __str__(self):
        return f"Recibo Nro. {self.numero}"

    def save(self, *args, **kwargs):
        if not self.numero:
            super().save(*args, **kwargs)
            self.numero = str(self.id + 1099).zfill(6)
            Recibo.objects.filter(pk=self.pk).update(numero=self.numero)
        else:
            super().save(*args, **kwargs)

    @property
    def total_por_moneda(self):
        totales = {}
        for cobro in self.cobros.all():
            key = cobro.moneda
            totales[key] = totales.get(key, Decimal('0')) + cobro.monto
        return totales


class Salida(models.Model):
    """Salida de una agencia operadora (paquete turístico grupal)."""
    operadora = models.ForeignKey(
        Proveedor, on_delete=models.SET_NULL, null=True, blank=True,
        verbose_name='Operadora', related_name='salidas',
        limit_choices_to={'activo': True}
    )
    nombre_paquete = models.CharField('Nombre del paquete', max_length=200)
    fecha_salida = models.DateField('Fecha de salida')
    lugar_salida = models.CharField('Lugar de salida', max_length=200)
    pasa_por_jardin_america = models.BooleanField('Pasa por Jardín América', default=False)
    descripcion = models.TextField('Descripción / Itinerario', blank=True)
    servicios_incluidos = models.TextField('Servicios incluidos', blank=True, help_text='Un servicio por línea. Ej: Traslado de ida y vuelta\nAlojamiento en hotel 3 estrellas\nDesayuno incluido')
    foto = models.ImageField('Foto del paquete', upload_to=_sanitizar_nombre_foto, blank=True, null=True)
    precio = models.DecimalField('Precio', max_digits=12, decimal_places=2, null=True, blank=True)
    moneda = models.CharField('Moneda', max_length=3, choices=MONEDAS, default='ARS')
    cupos = models.PositiveIntegerField('Lugares disponibles', null=True, blank=True)
    vacaciones_invierno = models.BooleanField('Vacaciones de invierno', default=False)
    agotado = models.BooleanField('Agotado', default=False)
    salida_confirmada = models.BooleanField('Salida confirmada', default=False)
    categorias = models.JSONField(
        'Categorías web',
        default=list,
        blank=True,
        help_text='Una o más categorías para los filtros de la web pública.',
    )
    notas = models.TextField('Notas internas', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Salida'
        verbose_name_plural = 'Salidas'
        ordering = ['fecha_salida']

    def __str__(self):
        return f"{self.nombre_paquete} — {self.fecha_salida}"

    def dias_restantes(self):
        from django.utils import timezone
        hoy = timezone.now().date()
        return (self.fecha_salida - hoy).days

    def get_categorias_slugs(self):
        from .salidas_utils import CATEGORIAS_WEB

        if not isinstance(self.categorias, list):
            return []
        validas = set(CATEGORIAS_WEB.keys())
        return [c for c in self.categorias if c in validas]


class Voucher(models.Model):
    """Voucher de servicio emitido para una reserva"""
    numero = models.CharField('Nro. Voucher', max_length=20, unique=True, blank=True)
    reserva = models.ForeignKey(Reserva, on_delete=models.PROTECT, verbose_name='Reserva')
    fecha = models.DateField('Fecha de emisión', default=timezone.now)
    notas_voucher = models.TextField('Notas en el voucher', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Voucher'
        verbose_name_plural = 'Vouchers'
        ordering = ['-created_at']

    def __str__(self):
        return f"Voucher Nro. {self.numero}"

    def save(self, *args, **kwargs):
        if not self.numero:
            super().save(*args, **kwargs)
            self.numero = str(self.id).zfill(6)
            Voucher.objects.filter(pk=self.pk).update(numero=self.numero)
        else:
            super().save(*args, **kwargs)
