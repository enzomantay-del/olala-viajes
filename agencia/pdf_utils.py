import os
from io import BytesIO
from decimal import Decimal
from datetime import date

from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from PIL import Image as PILImage

from django.conf import settings

TEAL = colors.HexColor('#0a6e7c')
TEAL_LIGHT = colors.HexColor('#e0f2f5')
ORANGE = colors.HexColor('#f08030')
GRIS = colors.HexColor('#666666')
GRIS_CLARO = colors.HexColor('#f5f5f5')
NEGRO = colors.HexColor('#222222')

SIMBOLOS = {'ARS': '$', 'USD': 'U$S', 'BRL': 'R$'}


def _get_logo():
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo.png')
    if os.path.exists(logo_path):
        with PILImage.open(logo_path) as img:
            orig_w, orig_h = img.size
        ancho = 4 * cm
        alto = ancho * orig_h / orig_w
        return Image(logo_path, width=ancho, height=alto)
    return None


def _estilos():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('TituloDoc', fontSize=18, textColor=TEAL, spaceAfter=4, leading=22))
    styles.add(ParagraphStyle('SubtituloDoc', fontSize=11, textColor=GRIS, spaceAfter=2))
    styles.add(ParagraphStyle('AgenciaNombre', fontSize=13, textColor=TEAL, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle('AgenciaInfo', fontSize=8, textColor=GRIS, leading=12))
    styles.add(ParagraphStyle('EtiquetaCampo', fontSize=8, textColor=GRIS, fontName='Helvetica'))
    styles.add(ParagraphStyle('ValorCampo', fontSize=9, textColor=NEGRO, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle('Total', fontSize=13, textColor=TEAL, fontName='Helvetica-Bold', alignment=TA_RIGHT))
    styles.add(ParagraphStyle('Footer', fontSize=7, textColor=GRIS, alignment=TA_CENTER))
    styles.add(ParagraphStyle('Centrado', alignment=TA_CENTER))
    return styles


def _get_qr_rnav():
    qr_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'qr_rnav.png')
    if os.path.exists(qr_path):
        size = 2.5 * cm
        return Image(qr_path, width=size, height=size)
    return None


def _header_table(styles, titulo, numero, fecha_str):
    logo = _get_logo()
    qr = _get_qr_rnav()

    agencia_info = [
        Paragraph('Olalá Viajes', styles['AgenciaNombre']),
        Paragraph(f'Leg. Nº{settings.AGENCIA_LEG}', styles['AgenciaInfo']),
    ]
    if settings.AGENCIA_TELEFONO:
        agencia_info.append(Paragraph(f'Tel: {settings.AGENCIA_TELEFONO}', styles['AgenciaInfo']))
    if settings.AGENCIA_EMAIL:
        agencia_info.append(Paragraph(settings.AGENCIA_EMAIL, styles['AgenciaInfo']))
    if settings.AGENCIA_DIRECCION:
        agencia_info.append(Paragraph(settings.AGENCIA_DIRECCION, styles['AgenciaInfo']))

    doc_info = [
        Paragraph(titulo, styles['TituloDoc']),
        Paragraph(f'<b>Nro. {numero}</b>', styles['SubtituloDoc']),
        Paragraph(f'Fecha: {fecha_str}', styles['SubtituloDoc']),
    ]

    logo_cell = logo if logo else Paragraph('', styles['Normal'])
    qr_cell = qr if qr else Paragraph('', styles['Normal'])

    rnav_style = ParagraphStyle('RNAV', fontSize=6, textColor=GRIS, alignment=TA_CENTER, leading=8)
    qr_block = [qr_cell, Paragraph('Verificar registro\nRNAV', rnav_style)]

    data = [[logo_cell, agencia_info, doc_info, qr_block]]
    t = Table(data, colWidths=[4 * cm, 6.5 * cm, 4 * cm, 2.5 * cm])
    t.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
        ('ALIGN', (3, 0), (3, 0), 'CENTER'),
    ]))
    return t


def _footer(styles):
    return Paragraph(
        f'Olalá Viajes — Leg. Nº{settings.AGENCIA_LEG} — Documento generado por el sistema de gestión',
        styles['Footer']
    )


def generar_recibo_pdf(recibo):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=1.5 * cm, bottomMargin=2 * cm,
        leftMargin=2 * cm, rightMargin=2 * cm
    )
    styles = _estilos()
    elements = []

    # Header
    fecha_str = recibo.fecha.strftime('%d/%m/%Y')
    elements.append(_header_table(styles, 'RECIBO', recibo.numero, fecha_str))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(HRFlowable(width='100%', thickness=2, color=TEAL))
    elements.append(Spacer(1, 0.4 * cm))

    # Datos del cliente
    cliente = recibo.cliente
    client_data = [
        [Paragraph('DATOS DEL CLIENTE', ParagraphStyle('H', fontSize=9, textColor=TEAL, fontName='Helvetica-Bold')), '', ''],
        [
            Paragraph(f'<b>{cliente.apellido}, {cliente.nombre}</b>', styles['ValorCampo']),
            Paragraph(f'{cliente.tipo_doc}: {cliente.nro_doc}', styles['ValorCampo']),
            Paragraph(cliente.telefono or '', styles['ValorCampo']),
        ]
    ]
    t_cliente = Table(client_data, colWidths=[7 * cm, 5 * cm, 5 * cm])
    t_cliente.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TEAL_LIGHT),
        ('SPAN', (0, 0), (-1, 0)),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.append(t_cliente)
    elements.append(Spacer(1, 0.5 * cm))

    # Tabla de cobros
    elements.append(Paragraph('DETALLE DE COBROS', ParagraphStyle('H2', fontSize=9, textColor=TEAL, fontName='Helvetica-Bold', spaceAfter=4)))

    cobros_data = [['Fecha', 'Reserva / Servicio', 'Forma de pago', 'Moneda', 'Monto']]
    cell_style_rec = ParagraphStyle('CeldaRec', fontSize=8, textColor=NEGRO, fontName='Helvetica', leading=10)
    for cobro in recibo.cobros.all():
        simbolo = SIMBOLOS.get(cobro.moneda, cobro.moneda)
        cobros_data.append([
            cobro.fecha.strftime('%d/%m/%Y'),
            Paragraph(f"{cobro.reserva.numero} — {cobro.reserva.destino}", cell_style_rec),
            cobro.get_forma_pago_display(),
            cobro.moneda,
            f"{simbolo} {cobro.monto:,.2f}",
        ])

    t_cobros = Table(cobros_data, colWidths=[2.5 * cm, 6.5 * cm, 3.5 * cm, 1.8 * cm, 2.7 * cm])
    t_cobros.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TEAL),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (4, 0), (4, -1), 'RIGHT'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, GRIS_CLARO]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(t_cobros)
    elements.append(Spacer(1, 0.5 * cm))

    # Totales por moneda
    totales = recibo.total_por_moneda
    for moneda, total in totales.items():
        simbolo = SIMBOLOS.get(moneda, moneda)
        elements.append(Paragraph(
            f'TOTAL {moneda}: {simbolo} {total:,.2f}',
            styles['Total']
        ))

    elements.append(Spacer(1, 1 * cm))

    # Notas
    if recibo.notas:
        elements.append(Paragraph(f'<i>Notas: {recibo.notas}</i>', styles['AgenciaInfo']))
        elements.append(Spacer(1, 0.5 * cm))

    # Leyenda legal
    elements.append(Spacer(1, 0.4 * cm))
    leyenda_style = ParagraphStyle('Leyenda', fontSize=7, textColor=GRIS, alignment=TA_CENTER,
                                   borderPad=4, borderColor=GRIS, borderWidth=0.5, borderRadius=3)
    elements.append(Paragraph('DOCUMENTO NO VÁLIDO COMO FACTURA', leyenda_style))
    elements.append(Spacer(1, 0.3 * cm))

    # Footer
    elements.append(HRFlowable(width='100%', thickness=0.5, color=GRIS))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(_footer(styles))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generar_voucher_pdf(voucher):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=1.5 * cm, bottomMargin=2 * cm,
        leftMargin=2 * cm, rightMargin=2 * cm
    )
    styles = _estilos()
    elements = []
    reserva = voucher.reserva

    # Header
    fecha_str = voucher.fecha.strftime('%d/%m/%Y')
    elements.append(_header_table(styles, 'VOUCHER DE SERVICIO', voucher.numero, fecha_str))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(HRFlowable(width='100%', thickness=2, color=ORANGE))
    elements.append(Spacer(1, 0.4 * cm))

    # Datos del pasajero titular
    cliente = reserva.cliente
    elements.append(Paragraph('PASAJERO TITULAR', ParagraphStyle('H', fontSize=9, textColor=TEAL, fontName='Helvetica-Bold', spaceAfter=3)))

    pasajero_data = [[
        Paragraph(f'<b>{cliente.apellido}, {cliente.nombre}</b>', styles['ValorCampo']),
        Paragraph(f'{cliente.tipo_doc}: {cliente.nro_doc}', styles['ValorCampo']),
        Paragraph(cliente.telefono or '', styles['ValorCampo']),
    ]]
    t_pas = Table(pasajero_data, colWidths=[7 * cm, 5 * cm, 5 * cm])
    t_pas.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), TEAL_LIGHT),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.append(t_pas)

    # Pasajeros adicionales
    adicionales = reserva.pasajeros_adicionales.all()
    if adicionales:
        elements.append(Spacer(1, 0.3 * cm))
        elements.append(Paragraph('PASAJEROS ADICIONALES', ParagraphStyle('H', fontSize=9, textColor=TEAL, fontName='Helvetica-Bold', spaceAfter=3)))
        adic_data = [[Paragraph(f'{p.apellido}, {p.nombre} — {p.tipo_doc}: {p.nro_doc}', styles['ValorCampo'])] for p in adicionales]
        t_adic = Table(adic_data, colWidths=[17 * cm])
        t_adic.setStyle(TableStyle([
            ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, GRIS_CLARO]),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ]))
        elements.append(t_adic)

    elements.append(Spacer(1, 0.5 * cm))

    # Datos del servicio
    elements.append(Paragraph('DETALLE DEL SERVICIO', ParagraphStyle('H', fontSize=9, textColor=TEAL, fontName='Helvetica-Bold', spaceAfter=3)))

    salida_str = reserva.fecha_salida.strftime('%d/%m/%Y')
    regreso_str = reserva.fecha_regreso.strftime('%d/%m/%Y') if reserva.fecha_regreso else '—'

    cell_style = ParagraphStyle('CeldaServ', fontSize=9, textColor=NEGRO, fontName='Helvetica', leading=11)
    servicio_data = [
        ['Tipo de servicio', Paragraph(reserva.get_tipo_servicio_display(), cell_style), 'Proveedor', Paragraph(reserva.proveedor.nombre, cell_style)],
        ['Destino', Paragraph(reserva.destino, cell_style), 'Nro. reserva proveedor', Paragraph(reserva.nro_reserva_proveedor or '—', cell_style)],
        ['Fecha de salida', Paragraph(salida_str, cell_style), 'Fecha de regreso', Paragraph(regreso_str, cell_style)],
    ]
    t_serv = Table(servicio_data, colWidths=[4 * cm, 4.5 * cm, 4 * cm, 4.5 * cm])
    t_serv.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('TEXTCOLOR', (0, 0), (0, -1), TEAL),
        ('TEXTCOLOR', (2, 0), (2, -1), TEAL),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [GRIS_CLARO, colors.white]),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
    ]))
    elements.append(t_serv)
    elements.append(Spacer(1, 0.4 * cm))

    # Descripción
    elements.append(Paragraph('DESCRIPCIÓN', ParagraphStyle('H', fontSize=9, textColor=TEAL, fontName='Helvetica-Bold', spaceAfter=3)))
    desc_data = [[Paragraph(reserva.descripcion, styles['Normal'])]]
    t_desc = Table(desc_data, colWidths=[17 * cm])
    t_desc.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), GRIS_CLARO),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
    ]))
    elements.append(t_desc)

    # Notas del voucher
    if voucher.notas_voucher:
        elements.append(Spacer(1, 0.4 * cm))
        elements.append(Paragraph('NOTAS', ParagraphStyle('H', fontSize=9, textColor=TEAL, fontName='Helvetica-Bold', spaceAfter=3)))
        notas_data = [[Paragraph(voucher.notas_voucher, styles['Normal'])]]
        t_notas = Table(notas_data, colWidths=[17 * cm])
        t_notas.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#fff8f0')),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('LINEBELOW', (0, 0), (-1, -1), 1, ORANGE),
        ]))
        elements.append(t_notas)

    elements.append(Spacer(1, 1 * cm))
    elements.append(HRFlowable(width='100%', thickness=0.5, color=GRIS))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(_footer(styles))

    doc.build(elements)
    buffer.seek(0)
    return buffer


def generar_salidas_pdf(salidas, filtros=None):
    """PDF con el listado de salidas de operadoras (A4 apaisado)."""
    salidas = list(salidas)
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(A4),
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm
    )
    styles = _estilos()
    elements = []

    # ── Encabezado ──────────────────────────────────────────────────────────
    logo = _get_logo()
    logo_cell = logo if logo else Paragraph('', styles['Normal'])

    from django.conf import settings as dj_settings
    hoy_str = date.today().strftime('%d/%m/%Y')
    header_data = [[
        logo_cell,
        [Paragraph('Olalá Viajes', styles['AgenciaNombre']),
         Paragraph(f'Leg. Nº{dj_settings.AGENCIA_LEG}', styles['AgenciaInfo'])],
        [Paragraph('SALIDAS DE OPERADORAS', ParagraphStyle('TitPDF', fontSize=16, textColor=TEAL, fontName='Helvetica-Bold', spaceAfter=2)),
         Paragraph(f'Generado: {hoy_str}', ParagraphStyle('SubPDF', fontSize=8, textColor=GRIS, alignment=TA_RIGHT))],
    ]]
    t_header = Table(header_data, colWidths=[3.5 * cm, 7 * cm, 17.2 * cm])
    t_header.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (2, 0), (2, 0), 'RIGHT'),
    ]))
    elements.append(t_header)
    elements.append(HRFlowable(width='100%', thickness=2, color=TEAL))
    elements.append(Spacer(1, 0.3 * cm))

    # ── Filtros aplicados ────────────────────────────────────────────────────
    if filtros:
        partes = []
        if filtros.get('q'):
            partes.append(f'Búsqueda: "{filtros["q"]}"')
        if filtros.get('solo_jardin'):
            partes.append('Solo Jardín América')
        if filtros.get('orden'):
            etiquetas = {
                'fecha_salida': 'Fecha ↑', '-fecha_salida': 'Fecha ↓',
                'operadora__nombre': 'Operadora A-Z', '-operadora__nombre': 'Operadora Z-A',
                'lugar_salida': 'Lugar A-Z', 'nombre_paquete': 'Paquete A-Z',
            }
            partes.append(f'Orden: {etiquetas.get(filtros["orden"], filtros["orden"])}')
        if partes:
            elements.append(Paragraph(
                'Filtros: ' + '  |  '.join(partes),
                ParagraphStyle('FiltPDF', fontSize=7, textColor=GRIS, fontName='Helvetica-Oblique')
            ))
            elements.append(Spacer(1, 0.2 * cm))

    # ── Tabla de salidas ─────────────────────────────────────────────────────
    cell_s = ParagraphStyle('CS', fontSize=8, textColor=NEGRO, fontName='Helvetica', leading=10)
    cell_bold = ParagraphStyle('CB', fontSize=8, textColor=NEGRO, fontName='Helvetica-Bold', leading=10)
    cell_muted = ParagraphStyle('CM', fontSize=7, textColor=GRIS, fontName='Helvetica', leading=9)

    data = [['Paquete', 'Operadora', 'Fecha salida', 'Días', 'Lugar de salida', 'Jardín Amér.', 'Precio', 'Lugares']]

    hoy = date.today()
    for s in salidas:
        dias = (s.fecha_salida - hoy).days
        if dias == 0:
            dias_str = 'Hoy'
        elif dias == 1:
            dias_str = 'Mañana'
        else:
            dias_str = f'{dias} días'

        precio_str = '—'
        if s.precio:
            simbolo = SIMBOLOS.get(s.moneda, s.moneda)
            precio_str = f'{simbolo} {s.precio:,.0f}'

        nombre_cell = [Paragraph(s.nombre_paquete, cell_bold)]
        if s.descripcion:
            nombre_cell.append(Paragraph(s.descripcion[:80] + ('…' if len(s.descripcion) > 80 else ''), cell_muted))

        data.append([
            nombre_cell,
            Paragraph(s.operadora.nombre if s.operadora else '—', cell_s),
            Paragraph(s.fecha_salida.strftime('%d/%m/%Y'), cell_s),
            Paragraph(dias_str, cell_s),
            Paragraph(s.lugar_salida, cell_s),
            Paragraph('Sí' if s.pasa_por_jardin_america else '—', cell_s),
            Paragraph(precio_str, cell_s),
            Paragraph(str(s.cupos) if s.cupos is not None else '—', cell_s),
        ])

    col_widths = [6.5 * cm, 4.5 * cm, 2.5 * cm, 2 * cm, 4.5 * cm, 2.2 * cm, 3 * cm, 2.5 * cm]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), TEAL),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, GRIS_CLARO]),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#cccccc')),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (2, 1), (3, -1), 'CENTER'),
        ('ALIGN', (5, 1), (5, -1), 'CENTER'),
        ('ALIGN', (6, 1), (7, -1), 'RIGHT'),
    ]))

    for i, s in enumerate(salidas, start=1):
        if s.pasa_por_jardin_america:
            t.setStyle(TableStyle([
                ('TEXTCOLOR', (5, i), (5, i), colors.HexColor('#198754')),
                ('FONTNAME', (5, i), (5, i), 'Helvetica-Bold'),
            ]))

    elements.append(t)

    if not salidas:
        elements.append(Spacer(1, 0.5 * cm))
        elements.append(Paragraph(
            'No hay salidas para mostrar.',
            ParagraphStyle('Vacio', fontSize=10, textColor=GRIS, alignment=TA_CENTER)
        ))

    # ── Total y footer ───────────────────────────────────────────────────────
    elements.append(Spacer(1, 0.4 * cm))
    elements.append(Paragraph(
        f'Total: {len(salidas)} salida{"s" if len(salidas) != 1 else ""}',
        ParagraphStyle('Tot', fontSize=8, textColor=GRIS, alignment=TA_RIGHT)
    ))
    elements.append(Spacer(1, 0.3 * cm))
    elements.append(HRFlowable(width='100%', thickness=0.5, color=GRIS))
    elements.append(Spacer(1, 0.2 * cm))
    elements.append(_footer(styles))

    doc.build(elements)
    buffer.seek(0)
    return buffer
