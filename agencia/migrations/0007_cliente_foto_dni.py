from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agencia', '0006_remove_reserva_old_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='foto_dni',
            field=models.FileField(blank=True, null=True, upload_to='dni/', verbose_name='Foto DNI'),
        ),
    ]
