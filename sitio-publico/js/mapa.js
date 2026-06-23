(function () {
  'use strict';

  const U = window.OlalaUtil;

  const DESTINOS = [
    { keys: ['bariloche', 'patagonia', 'san carlos'], lat: -41.13, lng: -71.31, label: 'Bariloche' },
    { keys: ['madryn', 'valdes', 'pinguin', 'ballena'], lat: -42.77, lng: -65.04, label: 'Puerto Madryn' },
    { keys: ['punta cana', 'bavaro', 'dominicana'], lat: 18.56, lng: -68.37, label: 'Punta Cana' },
    { keys: ['cancun', 'riviera maya', 'caribe mex'], lat: 21.16, lng: -86.85, label: 'Cancún' },
    { keys: ['europa', 'paris', 'roma', 'madrid', 'barcelona', 'venecia', 'grecia', 'atenas', 'mikonos', 'santorini'], lat: 48.86, lng: 2.35, label: 'Europa' },
    { keys: ['porto de galinhas', 'porto galinhas', 'pernambuco'], lat: -8.51, lng: -35.0, label: 'Porto de Galinhas' },
    { keys: ['fortaleza', 'cumbuco', 'jericoacoara'], lat: -3.73, lng: -38.52, label: 'Fortaleza' },
    { keys: ['gramado', 'canela', 'snowland'], lat: -29.37, lng: -50.87, label: 'Gramado / Canela' },
    { keys: ['termas', 'rio hondo', 'federacion', 'colon entre'], lat: -30.01, lng: -57.81, label: 'Termas' },
    { keys: ['iguazu', 'cataratas', 'foz'], lat: -25.69, lng: -54.44, label: 'Cataratas' },
    { keys: ['salta', 'cafayate', 'jujuy', 'purmamarca'], lat: -24.78, lng: -65.41, label: 'Noroeste' },
    { keys: ['mendoza', 'uco', 'wine'], lat: -32.89, lng: -68.83, label: 'Mendoza' },
    { keys: ['china', 'pekin', 'beijing', 'shanghai'], lat: 39.90, lng: 116.40, label: 'China' },
    { keys: ['turquia', 'estambul', 'capadocia'], lat: 41.01, lng: 28.98, label: 'Turquía' },
    { keys: ['calafate', 'glaciar', 'ushuaia', 'tierra del fuego'], lat: -50.34, lng: -72.27, label: 'Patagonia sur' },
    { keys: ['camboriu', 'florianopolis', 'santa catarina'], lat: -26.99, lng: -48.63, label: 'Santa Catarina' },
    { keys: ['buenos aires', 'capital federal'], lat: -34.60, lng: -58.38, label: 'Buenos Aires' },
    { keys: ['misiones', 'posadas', 'jardin america'], lat: -27.04, lng: -55.23, label: 'Misiones' },
  ];

  const CAT_FALLBACK = {
    argentina: { lat: -34.60, lng: -58.38, label: 'Argentina' },
    brasil: { lat: -15.79, lng: -47.88, label: 'Brasil' },
    termas: { lat: -30.01, lng: -57.81, label: 'Termas' },
    playas: { lat: -8.51, lng: -35.0, label: 'Playas' },
    caribe: { lat: 18.56, lng: -68.37, label: 'Caribe' },
    europa: { lat: 48.86, lng: 2.35, label: 'Europa' },
    mundo: { lat: 20.0, lng: 0.0, label: 'Mundo' },
    naturaleza: { lat: -42.77, lng: -65.04, label: 'Naturaleza' },
  };

  let mapa = null;
  let capaMarcadores = null;
  let inicializado = false;

  function panelVisible() {
    const panel = document.getElementById('vista-mapa-panel');
    return panel && !panel.hidden;
  }

  function normalizar(t) {
    return (t || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  }

  function coordsSalida(s) {
    const texto = normalizar(`${s.nombre_paquete} ${s.descripcion || ''} ${s.lugar_salida || ''}`);
    for (const d of DESTINOS) {
      if (d.keys.some((k) => texto.includes(normalizar(k)))) {
        return { lat: d.lat, lng: d.lng, label: d.label };
      }
    }
    const cat = s.cat || (Array.isArray(s.cats) ? s.cats[0] : 'argentina');
    const fb = CAT_FALLBACK[cat] || CAT_FALLBACK.argentina;
    return { lat: fb.lat, lng: fb.lng, label: fb.label };
  }

  function salidasFiltradas() {
    const todas = window.OLALA_SALIDAS || [];
    const cat = window.OLALA_FILTRO_ACTIVO || 'todos';
    if (cat === 'todos') return todas;
    return todas.filter((s) => (Array.isArray(s.cats) ? s.cats : []).includes(cat));
  }

  function iconoHtml(emoji) {
    return `<div class="mapa-pin">${emoji || '✈️'}</div>`;
  }

  function asegurarMapa() {
    const el = document.getElementById('mapa-app');
    if (!el) return false;
    if (typeof L === 'undefined') {
      el.innerHTML = '<p class="mapa-error">No se pudo cargar el mapa. Recargá la página (Ctrl+F5).</p>';
      return false;
    }
    if (!inicializado) {
      el.innerHTML = '<div id="mapa-leaflet" class="mapa-leaflet"></div><div id="mapa-lista" class="mapa-lista"></div>';
      mapa = L.map('mapa-leaflet', { scrollWheelZoom: false }).setView([-15, -55], 3);
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap',
        maxZoom: 18,
      }).addTo(mapa);
      capaMarcadores = L.layerGroup().addTo(mapa);
      inicializado = true;
      mapa.on('click', () => mapa.scrollWheelZoom.enable());
      mapa.on('mouseout', () => mapa.scrollWheelZoom.disable());
    }
    return true;
  }

  function render() {
    if (!panelVisible()) return;
    const el = document.getElementById('mapa-app');
    if (!el) return;
    if (!asegurarMapa()) return;

    const lista = salidasFiltradas();
    capaMarcadores.clearLayers();
    const bounds = [];
    const porZona = {};

    lista.forEach((s) => {
      const c = coordsSalida(s);
      const key = `${c.lat.toFixed(2)}_${c.lng.toFixed(2)}`;
      if (!porZona[key]) porZona[key] = 0;
      const offset = porZona[key]++;
      const lat = c.lat + offset * 0.15;
      const lng = c.lng + offset * 0.12;
      const marker = L.marker([lat, lng], {
        icon: L.divIcon({
          className: 'mapa-marker-wrap',
          html: iconoHtml(s.emoji),
          iconSize: [36, 36],
          iconAnchor: [18, 36],
        }),
      });
      const precio = s.precio
        ? `Desde ${U.SIMBOLO[s.moneda] || ''} ${Number(s.precio).toLocaleString('es-AR')}`
        : 'Consultar precio';
      marker.bindPopup(`
        <div class="mapa-popup">
          <strong>${U.escapeHtml(s.nombre_paquete)}</strong>
          <p>📅 ${U.fechaLegible(s.fecha_salida)}</p>
          <p>${U.escapeHtml(precio)}</p>
          <a href="${U.paqueteUrl(s.id)}">Ver paquete →</a>
        </div>
      `);
      marker.on('click', () => {
        const card = document.querySelector(`.paq-card[data-id="${s.id}"]`);
        if (card) {
          document.getElementById('vista-lista')?.click();
          setTimeout(() => {
            card.scrollIntoView({ behavior: 'smooth', block: 'center' });
            card.classList.add('paq-highlight');
            setTimeout(() => card.classList.remove('paq-highlight'), 2000);
          }, 300);
        }
      });
      capaMarcadores.addLayer(marker);
      bounds.push([lat, lng]);
    });

    if (bounds.length) {
      mapa.fitBounds(bounds, { padding: [40, 40], maxZoom: 6 });
    } else {
      mapa.setView([-15, -55], 3);
    }

    const listaEl = document.getElementById('mapa-lista');
    if (listaEl) {
      listaEl.innerHTML = lista.length
        ? `<p class="mapa-hint">${lista.length} salida${lista.length !== 1 ? 's' : ''} en el mapa · Tocá un pin para ver detalle</p>`
        : '<p class="mapa-hint">No hay paquetes en esta categoría.</p>';
    }

    setTimeout(() => {
      mapa.invalidateSize();
      if (bounds.length) mapa.fitBounds(bounds, { padding: [40, 40], maxZoom: 6 });
    }, 150);
  }

  document.addEventListener('olala:vista-mapa', render);
  document.addEventListener('olala:filtro', () => { if (inicializado && panelVisible()) render(); });
  document.addEventListener('olala:salidas-cargadas', () => { if (panelVisible()) render(); });
})();
