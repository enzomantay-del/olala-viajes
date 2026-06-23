from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agencia', '0014_salida_confirmada'),
    ]

    operations = [
        migrations.CreateModel(
            name='Testimonio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre_cliente', models.CharField(max_length=100, verbose_name='Nombre del viajero')),
                ('destino_label', models.CharField(blank=True, help_text='Ej: Europa, Bariloche. Se usa si no hay paquete vinculado.', max_length=100, verbose_name='Destino (etiqueta)')),
                ('texto', models.TextField(verbose_name='Comentario')),
                ('foto', models.ImageField(blank=True, null=True, upload_to='testimonios/', verbose_name='Foto del viaje')),
                ('emoji_destino', models.CharField(blank=True, default='✈️', max_length=8, verbose_name='Emoji')),
                ('estrellas', models.PositiveSmallIntegerField(default=5, verbose_name='Estrellas')),
                ('anio', models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Año del viaje')),
                ('orden', models.PositiveIntegerField(default=0, verbose_name='Orden en la web')),
                ('visible', models.BooleanField(default=True, verbose_name='Visible en la web')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('salida', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='testimonios', to='agencia.salida', verbose_name='Paquete vinculado')),
            ],
            options={
                'verbose_name': 'Testimonio',
                'verbose_name_plural': 'Testimonios',
                'ordering': ['orden', '-created_at'],
            },
        ),
    ]
