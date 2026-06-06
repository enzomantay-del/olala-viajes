"""Tarea de publicación del sitio web estático."""


def ejecutar_publicacion_web():
    from .firebase_deploy import deploy_olala_hosting
    from .publish_status import finalizar_publicacion
    from .web_publish import generar_sitio_web_estatico

    try:
        _dest, num_salidas, num_flyers = generar_sitio_web_estatico(request=None)
        deploy_ok, deploy_msg, detalle = deploy_olala_hosting()
        if deploy_ok:
            finalizar_publicacion(
                True,
                f'Listo: {num_salidas} paquetes y {num_flyers} flyers en olala-viajes.web.app',
                detalle,
            )
        else:
            finalizar_publicacion(False, deploy_msg, detalle)
    except Exception as exc:
        finalizar_publicacion(False, f'Error inesperado: {exc}', '')
