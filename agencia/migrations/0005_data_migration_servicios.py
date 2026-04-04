from django.db import migrations


def migrar_servicios(apps, schema_editor):
    """Crea un ServicioReserva por cada Reserva existente que tenga proveedor."""
    Reserva = apps.get_model('agencia', 'Reserva')
    ServicioReserva = apps.get_model('agencia', 'ServicioReserva')

    for reserva in Reserva.objects.filter(proveedor__isnull=False):
        ServicioReserva.objects.create(
            reserva=reserva,
            proveedor=reserva.proveedor,
            tipo_servicio=reserva.tipo_servicio or 'PAQUETE',
            descripcion=reserva.descripcion or '',
            precio_costo=reserva.precio_costo or 0,
            moneda_costo=reserva.moneda_costo or 'ARS',
            nro_reserva_proveedor=reserva.nro_reserva_proveedor or '',
        )


def revertir_servicios(apps, schema_editor):
    ServicioReserva = apps.get_model('agencia', 'ServicioReserva')
    ServicioReserva.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('agencia', '0004_add_servicioreserva'),
    ]

    operations = [
        migrations.RunPython(migrar_servicios, revertir_servicios),
    ]
