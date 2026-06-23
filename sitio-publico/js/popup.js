(function () {
  'use strict';

  const U = window.OlalaUtil;

  function hoyIso() {
    const d = new Date();
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${d.getFullYear()}-${m}-${day}`;
  }

  function dentroDeVigencia(p) {
    const hoy = hoyIso();
    return p.fecha_desde <= hoy && p.fecha_hasta >= hoy;
  }

  function elegirPopup(popups) {
    const vigentes = (popups || []).filter(dentroDeVigencia);
    if (!vigentes.length) return null;
    vigentes.sort((a, b) => {
      const oa = Number(a.orden) || 0;
      const ob = Number(b.orden) || 0;
      if (oa !== ob) return oa - ob;
      return Number(b.id) - Number(a.id);
    });
    return vigentes[0];
  }

  function mensajeHtml(texto) {
    return U.escapeHtml(texto || '').replace(/\n/g, '<br>');
  }

  function renderPopup(p) {
    const modal = document.getElementById('aviso-popup');
    const contenido = document.getElementById('aviso-popup-contenido');
    if (!modal || !contenido) return;

    const img = p.imagen_url
      ? `<img src="${U.escapeHtml(p.imagen_url)}" alt="" class="aviso-popup-img" loading="eager">`
      : '';
    const boton = p.enlace_url
      ? `<a href="${U.escapeHtml(p.enlace_url)}" class="aviso-popup-btn" target="_blank" rel="noopener">${U.escapeHtml(p.enlace_texto || 'Ver más')}</a>`
      : '';

    contenido.innerHTML = `
      ${img}
      <h2 class="aviso-popup-titulo" id="aviso-popup-titulo">${U.escapeHtml(p.titulo)}</h2>
      <div class="aviso-popup-mensaje">${mensajeHtml(p.mensaje)}</div>
      ${boton ? `<div class="aviso-popup-acciones">${boton}</div>` : ''}`;

    modal.hidden = false;
    document.body.style.overflow = 'hidden';
  }

  function cerrarPopup() {
    const modal = document.getElementById('aviso-popup');
    if (!modal) return;
    modal.hidden = true;
    document.body.style.overflow = '';
  }

  async function cargar() {
    const client = window.getSupabaseClient && window.getSupabaseClient();
    if (!client) return;

    const { data, error } = await client
      .from('olala_popups')
      .select('*')
      .eq('activo', true)
      .order('orden', { ascending: true })
      .order('id', { ascending: false });

    if (error) {
      console.warn('Popup:', error.message);
      return;
    }

    const popup = elegirPopup(data);
    if (popup) renderPopup(popup);
  }

  function init() {
    document.getElementById('aviso-popup-cerrar')?.addEventListener('click', cerrarPopup);
    document.getElementById('aviso-popup')?.addEventListener('click', (e) => {
      if (e.target.id === 'aviso-popup') cerrarPopup();
    });
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') cerrarPopup();
    });
    cargar();
  }

  window.OlalaPopup = { cerrarPopup };

  document.addEventListener('DOMContentLoaded', init);
})();
