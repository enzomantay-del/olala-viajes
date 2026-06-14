(function () {
  'use strict';

  const MESES = [
    'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
  ];
  const MESES_CORTO = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct', 'nov', 'dic'];
  const SIMBOLO = { ARS: '$', USD: 'U$S', BRL: 'R$' };
  const DIAS_RESERVA_URGENTE = 14;
  const CUPOS_URGENTE = 5;
  const CUPOS_ATENCION = 10;

  function escapeHtml(str) {
    return String(str || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;');
  }

  function fechaLegible(iso) {
    if (!iso) return '';
    const p = iso.split('-');
    const d = new Date(Number(p[0]), Number(p[1]) - 1, Number(p[2]));
    return `${d.getDate()} de ${MESES[d.getMonth()]} de ${d.getFullYear()}`;
  }

  function hoyIso() {
    const d = new Date();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${d.getFullYear()}-${m}-${day}`;
  }

  function diasHasta(iso) {
    if (!iso) return null;
    const p = iso.split('-');
    const destino = new Date(Number(p[0]), Number(p[1]) - 1, Number(p[2]));
    const hoy = new Date();
    hoy.setHours(0, 0, 0, 0);
    return Math.round((destino - hoy) / 86400000);
  }

  function paqueteUrl(id) {
    return `${window.location.origin}/paquete.html?id=${id}`;
  }

  function badgesUrgenciaHtml(s) {
    if (s.agotado) {
      return '<div class="paq-agotado-overlay"><span class="paq-agotado-texto">¡AGOTADO!</span></div>';
    }
    const badges = [];
    if (s.salida_confirmada) {
      badges.push('<span class="paq-badge-confirmada">✓ Salida confirmada</span>');
    }
    const dias = diasHasta(s.fecha_salida);
    if (dias !== null && dias >= 0 && dias <= DIAS_RESERVA_URGENTE) {
      const txt = dias === 0 ? '¡Sale hoy!' : dias === 1 ? '¡Sale mañana!' : `¡${dias} días para reservar!`;
      badges.push(`<span class="paq-badge-plazo">${txt}</span>`);
    }
    if (s.cupos != null && s.cupos > 0) {
      if (s.cupos <= CUPOS_URGENTE) {
        badges.push(`<span class="paq-badge-urgente">¡Quedan ${s.cupos} lugares!</span>`);
      } else if (s.cupos < CUPOS_ATENCION) {
        badges.push(`<span class="paq-badge-urgente">¡Últimos ${s.cupos} lugares!</span>`);
      } else {
        badges.push(`<span class="paq-badge-lugares">${s.cupos} lugares</span>`);
      }
    }
    if (!badges.length) return '';
    return `<div class="paq-badges-stack">${badges.join('')}</div>`;
  }

  function estadoUrgenciaTexto(s) {
    if (s.agotado) return 'Agotado';
    const partes = [];
    if (s.salida_confirmada) partes.push('Salida confirmada');
    const dias = diasHasta(s.fecha_salida);
    if (dias !== null && dias >= 0 && dias <= DIAS_RESERVA_URGENTE) {
      partes.push(dias === 0 ? 'Sale hoy' : `${dias} días para reservar`);
    }
    if (s.cupos != null && s.cupos > 0 && s.cupos <= CUPOS_ATENCION) {
      partes.push(`Quedan ${s.cupos} lugares`);
    }
    return partes.join(' · ');
  }

  window.OlalaUtil = {
    MESES,
    MESES_CORTO,
    SIMBOLO,
    escapeHtml,
    fechaLegible,
    hoyIso,
    diasHasta,
    paqueteUrl,
    badgesUrgenciaHtml,
    estadoUrgenciaTexto,
  };
})();
