(function () {
  'use strict';

  const API = (window.OLALA_COTIZAR_URL || '').replace(/\/$/, '');

  function qs(sel) { return document.querySelector(sel); }

  function agregarMenor(edad) {
    const lista = qs('#menores-lista');
    if (!lista) return;
    const fila = document.createElement('div');
    fila.className = 'menor-fila';
    fila.innerHTML = `
      <label>Edad del menor
        <input type="number" class="cotizar-input menor-edad" min="0" max="17" value="${edad || ''}" required>
      </label>
      <button type="button" class="btn-quitar-menor" title="Quitar">×</button>
    `;
    fila.querySelector('.btn-quitar-menor').addEventListener('click', () => fila.remove());
    lista.appendChild(fila);
  }

  function recolectarMenores() {
    return Array.from(document.querySelectorAll('.menor-edad'))
      .map((inp) => ({ edad: Number(inp.value) }))
      .filter((m) => !Number.isNaN(m.edad));
  }

  function mostrarEstado(msg, ok) {
    const el = qs('#cotizar-estado');
    if (!el) return;
    el.textContent = msg;
    el.className = 'cotizar-estado ' + (ok ? 'ok' : 'error');
    el.hidden = !msg;
  }

  async function enviar(e) {
    e.preventDefault();
    const btn = qs('#btn-enviar-cotizacion');
    const payload = {
      destino: qs('#cotizar-destino').value.trim(),
      fecha_salida: qs('#cotizar-fecha').value,
      noches: Number(qs('#cotizar-noches').value),
      categoria_hotel: qs('#cotizar-hotel').value,
      regimen: qs('#cotizar-regimen').value,
      adultos: Number(qs('#cotizar-adultos').value),
      menores: recolectarMenores(),
      aclaraciones: qs('#cotizar-aclaraciones').value.trim(),
      email: qs('#cotizar-email').value.trim(),
      whatsapp: qs('#cotizar-whatsapp').value.trim(),
    };

    if (!API) {
      mostrarEstado('Formulario no configurado. Escribinos por WhatsApp.', false);
      return;
    }

    btn.disabled = true;
    btn.textContent = 'Enviando…';
    mostrarEstado('', true);

    try {
      const res = await fetch(API, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok || !data.ok) {
        throw new Error(data.error || 'Error al enviar');
      }
      mostrarEstado('¡Listo! Recibimos tu solicitud. Te vamos a contactar para enviarte la cotización.', true);
      e.target.reset();
      qs('#menores-lista').innerHTML = '';
    } catch (err) {
      mostrarEstado(err.message || 'No se pudo enviar. Probá por WhatsApp.', false);
    } finally {
      btn.disabled = false;
      btn.textContent = 'Solicitar cotización';
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    const form = qs('#form-cotizar');
    const btnMenor = qs('#btn-agregar-menor');
    if (btnMenor) btnMenor.addEventListener('click', () => agregarMenor(''));
    if (form) form.addEventListener('submit', enviar);
  });
})();
