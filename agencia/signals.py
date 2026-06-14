import threading



from django.db.models.signals import post_delete, post_save

from django.dispatch import receiver



from .models import Salida





def _sync_en_segundo_plano(salida_pk, rapido=True):

    from .models import Salida

    from .supabase_sync import sincronizar_salida, supabase_configurado



    if not supabase_configurado():

        return

    try:

        salida = Salida.objects.select_related('operadora').get(pk=salida_pk)

        sincronizar_salida(salida, rapido=rapido)

    except Exception:

        pass





@receiver(post_save, sender=Salida)

def salida_guardada_sync_supabase(sender, instance, **kwargs):

    from .supabase_sync import supabase_configurado



    if not supabase_configurado():

        return

    threading.Thread(

        target=_sync_en_segundo_plano,

        args=(instance.pk,),

        kwargs={'rapido': True},

        daemon=True,

    ).start()





@receiver(post_delete, sender=Salida)

def salida_eliminada_sync_supabase(sender, instance, **kwargs):

    from .supabase_sync import ocultar_salida, supabase_configurado



    if not supabase_configurado():

        return

    try:

        ocultar_salida(instance.pk)

    except Exception:

        pass


