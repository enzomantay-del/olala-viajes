from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Salida


@receiver(post_save, sender=Salida)
def salida_guardada_sync_supabase(sender, instance, **kwargs):
    from .supabase_sync import sincronizar_salida, supabase_configurado

    if not supabase_configurado():
        return
    try:
        sincronizar_salida(instance)
    except Exception:
        pass


@receiver(post_delete, sender=Salida)
def salida_eliminada_sync_supabase(sender, instance, **kwargs):
    from .supabase_sync import ocultar_salida, supabase_configurado

    if not supabase_configurado():
        return
    try:
        ocultar_salida(instance.pk)
    except Exception:
        pass
