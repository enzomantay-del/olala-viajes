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


from .models import Testimonio


@receiver(post_save, sender=Testimonio)
def testimonio_guardado_sync(sender, instance, **kwargs):
    from .testimonios_sync import sincronizar_testimonio, supabase_configurado

    if not supabase_configurado():
        return

    def _sync():
        try:
            sincronizar_testimonio(instance)
        except Exception:
            pass

    threading.Thread(target=_sync, daemon=True).start()


@receiver(post_delete, sender=Testimonio)
def testimonio_eliminado_sync(sender, instance, **kwargs):
    from .testimonios_sync import ocultar_testimonio, supabase_configurado

    if not supabase_configurado():
        return
    try:
        ocultar_testimonio(instance.pk)
    except Exception:
        pass


from .models import Popup


def _sync_popup_en_segundo_plano(popup_pk):
    from .models import Popup
    from .popups_sync import sincronizar_popup, supabase_configurado

    if not supabase_configurado():
        return
    try:
        popup = Popup.objects.get(pk=popup_pk)
        sincronizar_popup(popup)
    except Exception:
        pass


@receiver(post_save, sender=Popup)
def popup_guardado_sync(sender, instance, **kwargs):
    from .popups_sync import supabase_configurado

    if not supabase_configurado():
        return
    threading.Thread(
        target=_sync_popup_en_segundo_plano,
        args=(instance.pk,),
        daemon=True,
    ).start()


@receiver(post_delete, sender=Popup)
def popup_eliminado_sync(sender, instance, **kwargs):
    from .popups_sync import eliminar_popup, supabase_configurado

    if not supabase_configurado():
        return
    try:
        eliminar_popup(instance.pk)
    except Exception:
        pass

