(function () {
  'use strict';

  const MESES = [
    'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
  ];
  const SIMBOLO = { ARS: '$', USD: 'U$S', BRL: 'R$' };
  const WA = window.OLALA_WHATSAPP || '5493743483429';
  const BASE = window.location.origin;
  const PANEL_FLYER = (window.OLALA_PANEL_URL || 'https://olala-viajes.onrender.com').replace(/\/accounts\/login\/?$/, '');

  const SVG_WA = '<svg viewBox="0 0 32 32" width="18" height="18" fill="currentColor"><path d="M16 2C8.268 2 2 8.268 2 16c0 2.493.651 4.835 1.787 6.865L2 30l7.353-1.768A13.94 13.94 0 0016 30c7.732 0 14-6.268 14-14S23.732 2 16 2zm6.29 19.383c-.344-.172-2.036-1.004-2.352-1.118-.316-.115-.546-.172-.775.172-.229.344-.888 1.118-1.089 1.347-.2.23-.4.258-.745.086-.344-.172-1.453-.536-2.768-1.708-1.023-.913-1.713-2.04-1.913-2.384-.2-.344-.021-.53.15-.701.155-.154.344-.402.516-.603.172-.2.229-.344.344-.573.115-.229.057-.43-.029-.602-.086-.172-.775-1.869-1.062-2.56-.28-.672-.564-.58-.775-.591l-.66-.011c-.229 0-.602.086-.917.43-.315.344-1.204 1.176-1.204 2.867s1.233 3.327 1.405 3.556c.172.23 2.427 3.706 5.88 5.196.823.355 1.465.567 1.965.726.826.263 1.578.226 2.172.137.663-.099 2.036-.832 2.323-1.635.287-.803.287-1.49.2-1.634-.086-.143-.315-.23-.66-.402z"/></svg>';
  const SVG_FB = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>';
  const SVG_IG = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z"/></svg>';
  const SVG_COPY = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>';
  const SVG_FLYER = '<svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 16H5V5h14v14zm-4-8l-4 4-4-4h3V7h2v4h3z"/></svg>';

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

  function paqueteUrl(id) {
    return `${BASE}/paquete.html?id=${id}`;
  }

  function flyerUrl(s) {
    if (s.flyer_url) return s.flyer_url;
    return `${PANEL_FLYER}/web/flyer/${s.id}/`;
  }

  function limpiarLineaServicio(ln) {
    return ln.replace(/^[\u2713\u2714\u2717✓✔•\-]\s*/, '').trim();
  }

  function mensajeWhatsapp(s) {
    const url = paqueteUrl(s.id);
    const lineas = [
      `🗺️ *${s.nombre_paquete}*`,
      `📅 Salida: ${fechaLegible(s.fecha_salida)}`,
    ];
    if (s.lugar_salida) lineas.push(`📍 Desde: ${s.lugar_salida}`);
    if (s.servicios_incluidos) {
      lineas.push('', '*Incluye:*');
      s.servicios_incluidos.split('\n').forEach((ln) => {
        const t = limpiarLineaServicio(ln);
        if (t) lineas.push(`✓ ${t}`);
      });
    }
    if (s.precio) {
      const sim = SIMBOLO[s.moneda] || s.moneda;
      lineas.push(`💰 Desde ${sim} ${Number(s.precio).toLocaleString('es-AR')} (${s.moneda})`);
    }
    lineas.push('', `👉 Ver paquete: ${url}`, '', 'Consultá disponibilidad con Olalá Viajes ✈️');
    return lineas.join('\n');
  }

  function serviciosHtml(texto) {
    const lineas = (texto || '').split('\n').map(limpiarLineaServicio).filter(Boolean);
    if (!lineas.length) return '';
    const items = lineas.map((ln, i) =>
      `<li${i >= 6 ? ' class="servicio-extra"' : ''}>${escapeHtml(ln)}</li>`
    ).join('');
    return `<div class="paq-servicios"><div class="paq-servicios-titulo">Incluye</div><ul>${items}</ul></div>`;
  }

  function shareHtml(s) {
    const payload = encodeURIComponent(JSON.stringify({
      url: paqueteUrl(s.id),
      text: mensajeWhatsapp(s),
      title: s.nombre_paquete,
    }));
    const flyer = flyerUrl(s);
    return `
      <div class="paq-share" data-share="${payload}">
        <span class="paq-share-label">Compartir</span>
        <div class="paq-share-btns">
          <button type="button" class="btn-share btn-share-wa" title="WhatsApp" aria-label="WhatsApp">${SVG_WA}</button>
          <button type="button" class="btn-share btn-share-fb" title="Facebook" aria-label="Facebook">${SVG_FB}</button>
          <button type="button" class="btn-share btn-share-ig" title="Instagram" aria-label="Instagram">${SVG_IG}</button>
          <button type="button" class="btn-share btn-share-copy" title="Copiar enlace" aria-label="Copiar enlace">${SVG_COPY}</button>
          <a href="${escapeHtml(flyer)}" class="btn-share btn-share-flyer" title="Descargar flyer JPG (9:16)" download target="_blank" rel="noopener">${SVG_FLYER}</a>
        </div>
      </div>`;
  }

  function cardHtml(s) {
    const cats = Array.isArray(s.cats) ? s.cats.join(',') : '';
    const cat = s.cat || 'argentina';
    const img = s.imagen_url
      ? `<img src="${escapeHtml(s.imagen_url)}" alt="${escapeHtml(s.nombre_paquete)}" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='block'"><span class="emoji-bg" style="display:none">${escapeHtml(s.emoji || '✈️')}</span>`
      : `<span class="emoji-bg">${escapeHtml(s.emoji || '✈️')}</span>`;
    const precio = s.precio
      ? `<div class="paq-precio"><div class="paq-precio-desde">desde</div><div class="paq-precio-valor">${SIMBOLO[s.moneda] || ''} ${Number(s.precio).toLocaleString('es-AR')}</div><div class="paq-precio-moneda">por persona · ${escapeHtml(s.moneda)}</div></div>`
      : '<div></div>';
    const cuposBadge = s.agotado
      ? '<div class="paq-agotado-overlay"><span class="paq-agotado-texto">¡AGOTADO!</span></div>'
      : s.cupos
        ? (s.cupos < 10
          ? `<span class="paq-badge-urgente">¡Últimos ${s.cupos} lugares!</span>`
          : `<span class="paq-badge-lugares">${s.cupos} lugares</span>`)
        : '';
    return `
      <div class="paq-card fade${s.agotado ? ' agotado' : ''}" data-cats="${escapeHtml(cats)}">
        <div class="paq-visual cat-${escapeHtml(cat)}">
          ${img}
          ${s.pasa_por_jardin_america ? '<span class="paq-badge-ja">Pasa por Jardín América</span>' : ''}
          ${s.vacaciones_invierno ? '<span class="paq-badge-invierno">❄️ Vacaciones de Invierno</span>' : ''}
          ${cuposBadge}
        </div>
        <div class="paq-body">
          <div class="paq-cat">${escapeHtml(s.cat_label || '')}</div>
          <div class="paq-nombre"><a href="${paqueteUrl(s.id)}" class="paq-nombre-link">${escapeHtml(s.nombre_paquete)}</a></div>
          <div class="paq-meta">
            <span class="paq-chip">📅 ${fechaLegible(s.fecha_salida)}</span>
            ${s.lugar_salida ? `<span class="paq-chip">📍 Sale de ${escapeHtml(s.lugar_salida)}</span>` : ''}
          </div>
          ${s.descripcion ? `<div class="paq-descripcion">${escapeHtml(s.descripcion)}</div>` : ''}
          ${serviciosHtml(s.servicios_incluidos)}
          <button class="btn-ver-mas" type="button">↓ Ver más</button>
          ${shareHtml(s)}
          <div class="paq-spacer"></div>
          <div class="paq-footer">
            ${precio}
            <button class="btn-consultar" type="button" data-consulta="${escapeHtml(s.nombre_paquete)} — ${fechaLegible(s.fecha_salida)}">Consultar</button>
          </div>
        </div>
      </div>`;
  }

  function filtrar(cat, btn) {
    document.querySelectorAll('.filtro-btn').forEach((b) => b.classList.remove('active'));
    if (btn) btn.classList.add('active');
    let visible = 0;
    document.querySelectorAll('.paq-card').forEach((c) => {
      const cats = (c.dataset.cats || '').split(',').filter(Boolean);
      const mostrar = cat === 'todos' || cats.includes(cat);
      c.classList.toggle('oculto', !mostrar);
      if (mostrar) visible += 1;
    });
    const count = document.getElementById('resultado-count');
    if (count) count.textContent = `${visible} paquete${visible !== 1 ? 's' : ''}`;
    const sin = document.getElementById('sin-resultados');
    if (sin) sin.classList.toggle('visible', visible === 0);
  }

  window.filtrar = filtrar;

  function showToast(msg) {
    const t = document.getElementById('share-toast');
    if (!t) return;
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2500);
  }

  function consultar(texto) {
    const msg = encodeURIComponent(`Hola! Quiero consultar sobre el paquete:\n*${texto}*\n\n¿Tiene disponibilidad?`);
    window.open(`https://wa.me/${WA}?text=${msg}`, '_blank');
  }

  function bindCards() {
    document.querySelectorAll('.btn-consultar').forEach((btn) => {
      btn.addEventListener('click', () => consultar(btn.dataset.consulta || ''));
    });
    document.querySelectorAll('.paq-share').forEach((box) => {
      if (!box.dataset.share) return;
      const data = JSON.parse(decodeURIComponent(box.dataset.share));
      box.querySelector('.btn-share-wa')?.addEventListener('click', () => {
        window.open(`https://wa.me/${WA}?text=${encodeURIComponent(data.text)}`, '_blank');
      });
      box.querySelector('.btn-share-fb')?.addEventListener('click', () => {
        window.open('https://www.facebook.com/sharer/sharer.php?u=' + encodeURIComponent(data.url), '_blank', 'width=600,height=500');
      });
      box.querySelector('.btn-share-ig')?.addEventListener('click', async () => {
        if (navigator.share) {
          try {
            await navigator.share({ title: data.title, text: data.text, url: data.url });
            return;
          } catch (e) {
            if (e.name === 'AbortError') return;
          }
        }
        try {
          await navigator.clipboard.writeText(data.url);
          showToast('Enlace copiado. Pegalo en Instagram.');
        } catch (_e) {
          prompt('Copiá este enlace para Instagram:', data.url);
        }
      });
      box.querySelector('.btn-share-copy')?.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(data.url);
          showToast('Enlace del paquete copiado');
        } catch (_e) {
          prompt('Copiá este enlace:', data.url);
        }
      });
    });
    document.querySelectorAll('.paq-card').forEach((card) => {
      const extras = card.querySelectorAll('.servicio-extra');
      const btn = card.querySelector('.btn-ver-mas');
      if (!btn || !extras.length) return;
      btn.classList.add('visible');
      btn.addEventListener('click', () => {
        const open = card.classList.toggle('expandida');
        btn.textContent = open ? '↑ Ver menos' : '↓ Ver más';
      });
    });
  }

  async function cargarCatalogo() {
    const grilla = document.getElementById('grilla');
    const loading = document.getElementById('loading-msg');
    const client = window.getSupabaseClient && window.getSupabaseClient();
    if (!client) {
      if (loading) loading.textContent = 'Error de configuración Supabase.';
      return;
    }
    const { data, error } = await client
      .from('olala_salidas')
      .select('*')
      .eq('visible', true)
      .gte('fecha_salida', hoyIso())
      .order('fecha_salida', { ascending: true });
    if (error) {
      if (loading) loading.textContent = 'No se pudieron cargar los paquetes. ' + error.message;
      return;
    }
    const salidas = data || [];
    if (loading) loading.remove();
    document.getElementById('stat-salidas').textContent = String(salidas.length);
    if (grilla) {
      grilla.innerHTML = salidas.map(cardHtml).join('');
      bindCards();
      filtrar('todos', document.querySelector('.filtro-btn.active'));
    }
    const shareBtn = document.getElementById('btn-compartir-catalogo');
    if (shareBtn) {
      shareBtn.addEventListener('click', () => {
        const texto = `✈️ *Olalá Viajes*\n\nIngresá y conocé todos los paquetes 👇\n\n${BASE}/`;
        window.open('https://wa.me/?text=' + encodeURIComponent(texto), '_blank');
      });
    }
  }

  document.addEventListener('DOMContentLoaded', cargarCatalogo);
})();
