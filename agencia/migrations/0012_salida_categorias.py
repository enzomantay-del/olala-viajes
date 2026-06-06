from django.db import migrations, models


def asignar_categorias_iniciales(apps, schema_editor):
    Salida = apps.get_model('agencia', 'Salida')
    from agencia.salidas_utils import inferir_categorias

    for salida in Salida.objects.all():
        salida.categorias = inferir_categorias(salida)
        salida.save(update_fields=['categorias'])


class Migration(migrations.Migration):

    dependencies = [
        ('agencia', '0011_add_vacaciones_invierno_to_salida'),
    ]

    operations = [
        migrations.AddField(
            model_name='salida',
            name='categorias',
            field=models.JSONField(
                blank=True,
                default=list,
                help_text='Una o más categorías para los filtros de la web pública.',
                verbose_name='Categorías web',
            ),
        ),
        migrations.RunPython(asignar_categorias_iniciales, migrations.RunPython.noop),
    ]
