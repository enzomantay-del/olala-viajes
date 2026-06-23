from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('agencia', '0015_testimonio'),
    ]

    operations = [
        migrations.CreateModel(
            name='Popup',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titulo', models.CharField(max_length=200, verbose_name='Título')),
                ('mensaje', models.TextField(help_text='Texto del aviso. Podés usar varias líneas.', verbose_name='Mensaje')),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='popups/', verbose_name='Imagen (opcional)')),
                ('fecha_desde', models.DateField(default=django.utils.timezone.now, help_text='Fecha en la que empieza a mostrarse.', verbose_name='Visible desde')),
                ('fecha_hasta', models.DateField(help_text='Después de esta fecha el aviso deja de mostrarse automáticamente.', verbose_name='Visible hasta')),
                ('enlace_url', models.URLField(blank=True, help_text='Ej: WhatsApp, landing o paquete.', verbose_name='Enlace (opcional)')),
                ('enlace_texto', models.CharField(blank=True, default='Ver más', max_length=80, verbose_name='Texto del botón')),
                ('activo', models.BooleanField(default=True, verbose_name='Activo en la web')),
                ('orden', models.PositiveIntegerField(default=0, help_text='Si hay varios avisos vigentes, se muestra el de menor número (0 = primero).', verbose_name='Prioridad')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Popup',
                'verbose_name_plural': 'Popups',
                'ordering': ['orden', '-fecha_desde', '-created_at'],
            },
        ),
    ]
