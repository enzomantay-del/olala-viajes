(function () {
  'use strict';

  const URL = window.OLALA_ALERTA_URL || '';

  const CATEGORIAS = [
    { value: '', label: 'Cualquier categoría' },
    { value: 'argentina', label: '🇦🇷 Argentina' },
    { value: 'brasil', label: '🇧🇷 Brasil' },
    { value: 'termas', label: '♨️ Termas' },
    { value: 'playas', label: '🏖️ Playas' },
    { value: 'caribe', label: '🏝️ Caribe' },
    { value: 'europa', label: '🇪🇺 Europa' },
    { value: 'mundo', label: '🌍 Mundo' },
    { value: 'naturaleza', label: '🦭 Naturaleza' },
  ];

  function mostrarEstado(msg, ok) {
    const el = document.getElementById('alerta-estado');
    if (!el) return;
    el.hidden = false;
    el.textContent = msg;
    el.className = 'cotizar-estado ' + (ok ? 'ok' : 'error');
  }

  async function enviar(e) {
    e.preventDefault();
    const destino = (document.getElementById('alerta-destino')?.value || '').trim();
    const categoria = document.getElementById('alerta-categoria')?.value || '';
    const fechaDesde = document.getElementById('alerta-desde')?.value || '';
    const fechaHasta = document.getElementById('alerta-hasta')?.value || '';
    const email = (document.getElementById('alerta-email')?.value || '').trim();
    const whatsapp = (document.getElementById('alerta-whatsapp')?.value || '').trim();

    if (!destino && !categoria) {
      mostrarEstado('Indicá un destino o una categoría.', false);
      return;
    }
    if (!email && !whatsapp) {
      mostrarEstado('Indicá email o WhatsApp para avisarte.', false);
      return;
    }
    if (!URL) {
      mostrarEstado('Servicio no disponible. Escribinos por WhatsApp.', false);
      return;
    }

    const btn = document.getElementById('btn-enviar-alerta');
    if (btn) { btn.disabled = true; btn.textContent = 'Guardando…'; }

    try {
      const res = await fetch(URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          destino,
          categoria,
          fecha_desde: fechaDesde || null,
          fecha_hasta: fechaHasta || null,
          email,
          whatsapp,
        }),
      });
      const data = await res.json();
      if (!res.ok || !data.ok) {
        throw new Error(data.error || 'Error al guardar');
      }
      mostrarEstado('¡Listo! Te avisaremos cuando haya una salida que coincida.', true);
      document.getElementById('form-alerta')?.reset();
    } catch (err) {
      mostrarEstado(err.message || 'No pudimos guardar la alerta.', false);
    } finally {
      if (btn) { btn.disabled = false; btn.textContent = 'Activar alerta'; }
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    const sel = document.getElementById('alerta-categoria');
    if (sel) {
      sel.innerHTML = CATEGORIAS.map((c) =>
        `<option value="${c.value}">${c.label}</option>`
      ).join('');
    }
    document.getElementById('form-alerta')?.addEventListener('submit', enviar);
  });
})();
