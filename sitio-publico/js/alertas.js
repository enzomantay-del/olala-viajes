(function () {
  'use strict';

  const CATEGORIAS_VALIDAS = new Set([
    '', 'argentina', 'brasil', 'termas', 'playas', 'caribe', 'europa', 'mundo', 'naturaleza',
  ]);

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

  function validar(destino, categoria, email, whatsapp, fechaDesde, fechaHasta) {
    if (!destino && !categoria) {
      return 'Indicá un destino o una categoría.';
    }
    if (categoria && !CATEGORIAS_VALIDAS.has(categoria)) {
      return 'Categoría inválida.';
    }
    if (!email && !whatsapp) {
      return 'Indicá email o WhatsApp para avisarte.';
    }
    if (fechaDesde && fechaHasta && fechaDesde > fechaHasta) {
      return 'La fecha desde no puede ser posterior a la fecha hasta.';
    }
    return null;
  }

  async function guardarEnSupabase(datos) {
    const client = window.getSupabaseClient && window.getSupabaseClient();
    if (!client) {
      throw new Error('Error de configuración. Recargá la página.');
    }
    const row = {
      destino: datos.destino,
      categoria: datos.categoria,
      fecha_desde: datos.fecha_desde || null,
      fecha_hasta: datos.fecha_hasta || null,
      email: datos.email,
      whatsapp: datos.whatsapp,
      estado: 'activa',
      salidas_avisadas: [],
    };
    const { error } = await client
      .from('olala_alertas')
      .insert(row);
    if (error) {
      if (error.code === '42501' || error.message.includes('policy')) {
        throw new Error(
          'Falta configurar Supabase. Ejecutá olala_alertas_politica_insert.sql en el SQL Editor.'
        );
      }
      throw new Error(error.message || 'No se pudo guardar la alerta.');
    }
    return true;
  }

  async function enviar(e) {
    e.preventDefault();
    const destino = (document.getElementById('alerta-destino')?.value || '').trim();
    const categoria = document.getElementById('alerta-categoria')?.value || '';
    const fechaDesde = document.getElementById('alerta-desde')?.value || '';
    const fechaHasta = document.getElementById('alerta-hasta')?.value || '';
    const email = (document.getElementById('alerta-email')?.value || '').trim();
    const whatsapp = (document.getElementById('alerta-whatsapp')?.value || '').trim();

    const errorVal = validar(destino, categoria, email, whatsapp, fechaDesde, fechaHasta);
    if (errorVal) {
      mostrarEstado(errorVal, false);
      return;
    }

    const btn = document.getElementById('btn-enviar-alerta');
    if (btn) { btn.disabled = true; btn.textContent = 'Guardando…'; }

    try {
      await guardarEnSupabase({
        destino,
        categoria,
        fecha_desde: fechaDesde || null,
        fecha_hasta: fechaHasta || null,
        email,
        whatsapp,
      });
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
