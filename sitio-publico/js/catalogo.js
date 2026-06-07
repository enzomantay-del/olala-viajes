(function () {
  'use strict';

  const MESES = [
    'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
    'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
  ];
  const SIMBOLO = { ARS: '$', USD: 'U$S', BRL: 'R$' };
  const WA = window.OLALA_WHATSAPP || '5493743483429';
  const BASE = window.location.origin;

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
        const t = ln.trim();
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
    const lineas = (texto || '').split('\n').map((l) => l.trim()).filter(Boolean);
    if (!lineas.length) return '';
    const items = lineas.map((ln, i) =>
      `<li${i >= 6 ? ' class="servicio-extra"' : ''}>${escapeHtml(ln)}</li>`
    ).join('');
    return `<div class="paq-servicios"><div class="paq-servicios-titulo">Incluye</div><ul>${items}</ul></div>`;
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
    const sharePayload = encodeURIComponent(JSON.stringify({
      url: paqueteUrl(s.id),
      text: mensajeWhatsapp(s),
      title: s.nombre_paquete,
    }));
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
          <div class="paq-share" data-share="${sharePayload}">
            <span class="paq-share-label">Compartir</span>
            <div class="paq-share-btns">
              <button class="btn-share btn-share-wa" type="button" title="WhatsApp">WA</button>
              <button class="btn-share btn-share-copy" type="button" title="Copiar enlace">⧉</button>
            </div>
          </div>
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
      box.querySelector('.btn-share-copy')?.addEventListener('click', async () => {
        try {
          await navigator.clipboard.writeText(data.url);
          alert('Enlace copiado');
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
