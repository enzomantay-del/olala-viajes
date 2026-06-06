"""Tarea de publicación del sitio web estático."""


def ejecutar_publicacion_web():
    from django.db import connections

    from .firebase_deploy import deploy_olala_hosting
    from .fotos_cloudinary import sincronizar_todas_las_fotos
    from .publish_status import actualizar_progreso, finalizar_publicacion
    from .web_publish import generar_sitio_web_estatico

    connections.close_all()
    log_path = None
    try:
        from django.conf import settings

        log_path = settings.BASE_DIR / '.publish_log.txt'
        log_path.write_text('Iniciando publicación…\n', encoding='utf-8')
    except Exception:
        pass

    def log(msg):
        if log_path:
            try:
                with open(log_path, 'a', encoding='utf-8') as f:
                    f.write(f'{msg}\n')
            except OSError:
                pass

    try:
        actualizar_progreso('Sincronizando fotos en la nube…')
        log('Sincronizando fotos…')
        sincronizar_todas_las_fotos()

        actualizar_progreso('Generando sitio web…')
        log('Generando sitio…')
        _dest, num_salidas, num_flyers = generar_sitio_web_estatico(request=None)
        log(f'Sitio generado: {num_salidas} paquetes')

        from .firebase_deploy import verificar_firebase_auth

        actualizar_progreso('Verificando Firebase…')
        log('Verificando Firebase…')
        auth_ok, auth_msg = verificar_firebase_auth()
        if not auth_ok:
            finalizar_publicacion(False, auth_msg, '')
            return

        actualizar_progreso('Subiendo a olala-viajes.web.app…')
        log('Subiendo a Firebase…')
        deploy_ok, deploy_msg, detalle = deploy_olala_hosting()
        log(deploy_msg)

        if deploy_ok:
            finalizar_publicacion(
                True,
                f'Listo: {num_salidas} paquetes en olala-viajes.web.app',
                detalle,
            )
        else:
            finalizar_publicacion(False, deploy_msg, detalle)
    except Exception as exc:
        log(f'Error: {exc}')
        finalizar_publicacion(False, f'Error: {exc}', '')
