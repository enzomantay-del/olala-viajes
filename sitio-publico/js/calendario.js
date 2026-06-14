(function () {
  'use strict';

  const U = window.OlalaUtil;
  const DIAS_SEM = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];

  let mesActual = new Date();
  mesActual.setDate(1);

  const wrap = () => document.getElementById('calendario-app');
  const salidas = () => {
    const todas = window.OLALA_SALIDAS || [];
    const cat = window.OLALA_FILTRO_ACTIVO || 'todos';
    if (cat === 'todos') return todas;
    return todas.filter((s) => (Array.isArray(s.cats) ? s.cats : []).includes(cat));
  };

  function salidasDelMes(ano, mes) {
    return salidas().filter((s) => {
      const p = String(s.fecha_salida).split('-');
      return Number(p[0]) === ano && Number(p[1]) === mes;
    });
  }

  function tituloMes(d) {
    return `${U.MESES[d.getMonth()]} ${d.getFullYear()}`;
  }

  function render() {
    const el = wrap();
    if (!el) return;
    const ano = mesActual.getFullYear();
    const mes = mesActual.getMonth() + 1;
    const eventos = salidasDelMes(ano, mes);
    const porDia = {};
    eventos.forEach((s) => {
      const dia = parseInt(String(s.fecha_salida).split('-')[2], 10);
      if (!porDia[dia]) porDia[dia] = [];
      porDia[dia].push(s);
    });

    const primerDia = new Date(ano, mes - 1, 1).getDay();
    const diasMes = new Date(ano, mes, 0).getDate();
    let celdas = '';
    for (let i = 0; i < primerDia; i += 1) {
      celdas += '<div class="cal-celda cal-vacia"></div>';
    }
    for (let d = 1; d <= diasMes; d += 1) {
      const evs = porDia[d] || [];
      const tiene = evs.length > 0;
      const clases = ['cal-celda', tiene ? 'cal-con-evento' : ''];
      const lista = evs.map((s) => {
        const urg = s.agotado ? 'agotado' : (s.cupos != null && s.cupos <= 5 ? 'urgente' : '');
        return `<button type="button" class="cal-evento ${urg}" data-id="${s.id}" title="${U.escapeHtml(s.nombre_paquete)}">
          <span class="cal-evento-emoji">${U.escapeHtml(s.emoji || '✈️')}</span>
          <span class="cal-evento-nombre">${U.escapeHtml(s.nombre_paquete)}</span>
        </button>`;
      }).join('');
      celdas += `
        <div class="${clases.join(' ')}">
          <span class="cal-dia-num">${d}</span>
          ${tiene ? `<div class="cal-eventos">${lista}</div>` : ''}
        </div>`;
    }

    const hoy = new Date();
    const puedeAtras = mesActual > new Date(hoy.getFullYear(), hoy.getMonth(), 1);

    el.innerHTML = `
      <div class="cal-nav">
        <button type="button" class="cal-nav-btn" data-cal="prev" ${puedeAtras ? '' : 'disabled'}>←</button>
        <h3 class="cal-titulo">${tituloMes(mesActual)}</h3>
        <button type="button" class="cal-nav-btn" data-cal="next">→</button>
      </div>
      <div class="cal-leyenda">
        <span><i class="cal-dot cal-dot-normal"></i> Salida programada</span>
        <span><i class="cal-dot cal-dot-urgente"></i> Pocos lugares</span>
        <span><i class="cal-dot cal-dot-agotado"></i> Agotado</span>
      </div>
      <div class="cal-semana">${DIAS_SEM.map((d) => `<span>${d}</span>`).join('')}</div>
      <div class="cal-grid">${celdas}</div>
      <p class="cal-hint">${eventos.length} salida${eventos.length !== 1 ? 's' : ''} en ${U.MESES[mes - 1]}</p>`;

    el.querySelector('[data-cal="prev"]')?.addEventListener('click', () => {
      mesActual = new Date(mesActual.getFullYear(), mesActual.getMonth() - 1, 1);
      render();
    });
    el.querySelector('[data-cal="next"]')?.addEventListener('click', () => {
      mesActual = new Date(mesActual.getFullYear(), mesActual.getMonth() + 1, 1);
      render();
    });
    el.querySelectorAll('.cal-evento').forEach((btn) => {
      btn.addEventListener('click', () => {
        const id = btn.dataset.id;
        const card = document.querySelector(`.paq-card[data-id="${id}"]`);
        if (card) {
          document.getElementById('vista-lista')?.click();
          card.scrollIntoView({ behavior: 'smooth', block: 'center' });
          card.classList.add('paq-highlight');
          setTimeout(() => card.classList.remove('paq-highlight'), 2000);
        } else {
          window.location.href = U.paqueteUrl(id);
        }
      });
    });
  }

  document.addEventListener('olala:salidas-cargadas', render);
  document.addEventListener('olala:filtro', render);
  if (window.OLALA_SALIDAS?.length) render();
})();
