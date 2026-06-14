from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agencia', '0013_corregir_categorias_internacionales'),
    ]

    operations = [
        migrations.AddField(
            model_name='salida',
            name='salida_confirmada',
            field=models.BooleanField(default=False, verbose_name='Salida confirmada'),
        ),
    ]
