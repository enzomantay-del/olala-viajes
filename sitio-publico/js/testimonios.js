(function () {
  'use strict';

  const U = window.OlalaUtil;

  function estrellas(n) {
    const v = Math.min(5, Math.max(1, Number(n) || 5));
    return '★'.repeat(v) + '☆'.repeat(5 - v);
  }

  function cardHtml(t) {
    const img = t.foto_url
      ? `<img src="${U.escapeHtml(t.foto_url)}" alt="" class="testi-foto" loading="lazy">`
      : `<div class="testi-foto testi-foto-placeholder">${U.escapeHtml(t.emoji_destino || '✈️')}</div>`;
    return `
      <article class="testi-card">
        ${img}
        <div class="testi-body">
          <div class="testi-estrellas" aria-label="${t.estrellas || 5} estrellas">${estrellas(t.estrellas)}</div>
          <blockquote class="testi-texto">"${U.escapeHtml(t.texto)}"</blockquote>
          <footer class="testi-meta">
            <strong>${U.escapeHtml(t.nombre_cliente)}</strong>
            ${t.destino_label ? `<span> · ${U.escapeHtml(t.destino_label)}</span>` : ''}
            ${t.anio ? `<span class="testi-anio">${t.anio}</span>` : ''}
          </footer>
        </div>
      </article>`;
  }

  function renderLista(testimonios, contenedorId) {
    const el = document.getElementById(contenedorId);
    if (!el) return;
    if (!testimonios.length) {
      el.innerHTML = '<p class="testi-vacio">Pronto sumamos más experiencias de viajeros.</p>';
      return;
    }
    el.innerHTML = `<div class="testi-grid">${testimonios.map(cardHtml).join('')}</div>`;
  }

  async function cargar() {
    const client = window.getSupabaseClient && window.getSupabaseClient();
    if (!client) return;
    const { data, error } = await client
      .from('olala_testimonios')
      .select('*')
      .eq('visible', true)
      .order('orden', { ascending: true })
      .order('id', { ascending: true });
    if (error) {
      console.warn('Testimonios:', error.message);
      return;
    }
    window.OLALA_TESTIMONIOS = data || [];
    renderLista(window.OLALA_TESTIMONIOS, 'testimonios-grid');
    document.dispatchEvent(new CustomEvent('olala:testimonios-cargados', { detail: window.OLALA_TESTIMONIOS }));
  }

  function paraSalida(salidaId) {
    const todos = window.OLALA_TESTIMONIOS || [];
    const id = Number(salidaId);
    const delPaquete = todos.filter((t) => t.salida_id === id);
    if (delPaquete.length) return delPaquete;
    const salida = (window.OLALA_SALIDAS || []).find((s) => Number(s.id) === id);
    if (!salida) return [];
    const dest = (salida.nombre_paquete || '').toLowerCase();
    return todos.filter((t) => {
      const td = (t.destino_label || '').toLowerCase();
      return td && dest.includes(td) || dest.includes(td);
    }).slice(0, 3);
  }

  window.OlalaTestimonios = { paraSalida, cardHtml, renderLista };

  document.addEventListener('DOMContentLoaded', cargar);
})();
