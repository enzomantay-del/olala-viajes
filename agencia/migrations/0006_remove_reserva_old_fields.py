from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('agencia', '0005_data_migration_servicios'),
    ]

    operations = [
        migrations.RemoveField(model_name='reserva', name='proveedor'),
        migrations.RemoveField(model_name='reserva', name='precio_costo'),
        migrations.RemoveField(model_name='reserva', name='moneda_costo'),
        migrations.RemoveField(model_name='reserva', name='tipo_servicio'),
        migrations.RemoveField(model_name='reserva', name='nro_reserva_proveedor'),
    ]
