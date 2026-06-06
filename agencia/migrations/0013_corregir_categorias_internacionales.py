from django.db import migrations


def corregir_categorias(apps, schema_editor):
    Salida = apps.get_model('agencia', 'Salida')
    from agencia.salidas_utils import inferir_categorias

    for salida in Salida.objects.all():
        salida.categorias = inferir_categorias(salida)
        salida.save(update_fields=['categorias'])


class Migration(migrations.Migration):

    dependencies = [
        ('agencia', '0012_salida_categorias'),
    ]

    operations = [
        migrations.RunPython(corregir_categorias, migrations.RunPython.noop),
    ]
