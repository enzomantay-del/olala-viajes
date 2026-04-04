from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agencia', '0003_comprobante_pago_proveedor'),
    ]

    operations = [
        # Hacer nullable los campos que se van a mover a ServicioReserva
        migrations.AlterField(
            model_name='reserva',
            name='proveedor',
            field=models.ForeignKey(
                null=True, blank=True,
                on_delete=django.db.models.deletion.PROTECT,
                verbose_name='Proveedor',
                to='agencia.proveedor',
            ),
        ),
        migrations.AlterField(
            model_name='reserva',
            name='precio_costo',
            field=models.DecimalField('Precio de costo', max_digits=12, decimal_places=2, default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='reserva',
            name='moneda_costo',
            field=models.CharField('Moneda costo', max_length=3, null=True, blank=True,
                choices=[('ARS', 'Pesos (ARS)'), ('USD', 'Dólares (USD)'), ('BRL', 'Reales (BRL)')]),
        ),
        migrations.AlterField(
            model_name='reserva',
            name='tipo_servicio',
            field=models.CharField('Tipo de servicio', max_length=20, null=True, blank=True,
                choices=[('VUELO', 'Vuelo'), ('HOTEL', 'Hotel'), ('PAQUETE', 'Paquete Turístico'),
                         ('CRUCERO', 'Crucero'), ('TRASLADO', 'Traslado'), ('SEGURO', 'Seguro de Viaje'),
                         ('EXCURSION', 'Excursión'), ('OTRO', 'Otro')]),
        ),
        migrations.AlterField(
            model_name='reserva',
            name='descripcion',
            field=models.TextField('Descripción / Observaciones', blank=True),
        ),
        # Crear el nuevo modelo ServicioReserva
        migrations.CreateModel(
            name='ServicioReserva',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tipo_servicio', models.CharField(
                    choices=[('VUELO', 'Vuelo'), ('HOTEL', 'Hotel'), ('PAQUETE', 'Paquete Turístico'),
                             ('CRUCERO', 'Crucero'), ('TRASLADO', 'Traslado'), ('SEGURO', 'Seguro de Viaje'),
                             ('EXCURSION', 'Excursión'), ('OTRO', 'Otro')],
                    default='PAQUETE', max_length=20, verbose_name='Tipo')),
                ('descripcion', models.CharField(blank=True, max_length=500, verbose_name='Descripción del servicio')),
                ('precio_costo', models.DecimalField(decimal_places=2, default=0, max_digits=12, verbose_name='Costo')),
                ('moneda_costo', models.CharField(
                    choices=[('ARS', 'Pesos (ARS)'), ('USD', 'Dólares (USD)'), ('BRL', 'Reales (BRL)')],
                    default='ARS', max_length=3, verbose_name='Moneda')),
                ('nro_reserva_proveedor', models.CharField(blank=True, max_length=100, verbose_name='Nro. reserva proveedor')),
                ('proveedor', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    to='agencia.proveedor', verbose_name='Proveedor')),
                ('reserva', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='servicios', to='agencia.reserva', verbose_name='Reserva')),
            ],
            options={
                'verbose_name': 'Servicio',
                'verbose_name_plural': 'Servicios',
            },
        ),
    ]
