(function () {
  'use strict';

  const U = window.OlalaUtil;
  const WA = window.OLALA_WHATSAPP || '5493743483429';

  const TIPOS_VIAJE = [
    { id: 'playa', label: '🏖️ Playa y sol', cats: ['playas', 'caribe', 'brasil'] },
    { id: 'ciudad', label: '🏙️ Ciudad y cultura', cats: ['europa', 'mundo', 'argentina'] },
    { id: 'naturaleza', label: '🦭 Naturaleza', cats: ['naturaleza', 'argentina'] },
    { id: 'termas', label: '♨️ Termas', cats: ['termas'] },
    { id: 'europa', label: '🇪🇺 Europa', cats: ['europa'] },
    { id: 'cualquiera', label: '✨ Me da igual', cats: [] },
  ];

  const GRUPOS = [
    { id: 'solo', label: 'Viajo solo/a' },
    { id: 'pareja', label: 'En pareja' },
    { id: 'familia', label: 'En familia' },
    { id: 'amigos', label: 'Con amigos' },
  ];

  const MESES_OPTS = U.MESES.map((m, i) => ({ num: i + 1, label: m }));

  let paso = 0;
  let prefs = { tipo: '', mes: null, presupuesto: '', moneda: 'ARS', grupo: '' };
  let resultados = [];

  const root = () => document.getElementById('asistente-app');
  const salidas = () => window.OLALA_SALIDAS || [];

  function puntuar(s, p) {
    let score = 0;
    const tipo = TIPOS_VIAJE.find((t) => t.id === p.tipo);
    const cats = Array.isArray(s.cats) ? s.cats : [];
    if (tipo && tipo.cats.length) {
      if (cats.some((c) => tipo.cats.includes(c))) score += 45;
      else if (tipo.id !== 'cualquiera') score -= 10;
    }
    if (p.mes) {
      const mesSalida = parseInt(String(s.fecha_salida).split('-')[1], 10);
      const diff = Math.min(Math.abs(mesSalida - p.mes), 12 - Math.abs(mesSalida - p.mes));
      if (diff === 0) score += 35;
      else if (diff === 1) score += 20;
      else if (diff === 2) score += 8;
    }
    if (p.presupuesto && s.precio) {
      const max = Number(p.presupuesto);
      const precio = Number(s.precio);
      if (p.moneda === s.moneda) {
        if (precio <= max) score += 30;
        else if (precio <= max * 1.15) score += 12;
        else score -= 15;
      }
    }
    if (p.grupo === 'familia' && s.cupos && s.cupos >= 4) score += 5;
    if (s.salida_confirmada) score += 8;
    if (s.agotado) score -= 80;
    else if (s.cupos != null && s.cupos <= 5) score += 5;
    return score;
  }

  function recomendar() {
    const lista = salidas().filter((s) => !s.agotado);
    resultados = lista
      .map((s) => ({ s, score: puntuar(s, prefs) }))
      .filter((r) => r.score > 0)
      .sort((a, b) => b.score - a.score)
      .slice(0, 3);
    return resultados;
  }

  function renderPaso() {
    const el = root();
    if (!el) return;
    const pasos = [
      renderTipo,
      renderMes,
      renderPresupuesto,
      renderGrupo,
      renderResultados,
    ];
    el.innerHTML = pasos[paso]();
    bindPaso();
  }

  function navBtns(atras, siguiente, siguienteLabel) {
    return `
      <div class="asistente-nav">
        ${atras ? '<button type="button" class="btn-ghost-asistente" data-accion="atras">← Atrás</button>' : '<span></span>'}
        <button type="button" class="btn-naranja btn-asistente-next" data-accion="siguiente">${siguienteLabel || 'Siguiente →'}</button>
      </div>`;
  }

  function renderTipo() {
    const opts = TIPOS_VIAJE.map((t) =>
      `<button type="button" class="asistente-opcion${prefs.tipo === t.id ? ' sel' : ''}" data-tipo="${t.id}">${t.label}</button>`
    ).join('');
    return `
      <div class="asistente-paso">
        <p class="asistente-pregunta">¿Qué tipo de viaje buscás?</p>
        <div class="asistente-opciones">${opts}</div>
        ${navBtns(false, true, 'Siguiente →')}
      </div>`;
  }

  function renderMes() {
    const opts = MESES_OPTS.map((m) =>
      `<button type="button" class="asistente-opcion asistente-opcion-sm${prefs.mes === m.num ? ' sel' : ''}" data-mes="${m.num}">${m.label}</button>`
    ).join('');
    return `
      <div class="asistente-paso">
        <p class="asistente-pregunta">¿En qué mes te gustaría viajar?</p>
        <div class="asistente-opciones asistente-opciones-grid">${opts}
          <button type="button" class="asistente-opcion asistente-opcion-sm${prefs.mes === null ? ' sel' : ''}" data-mes="">Flexible</button>
        </div>
        ${navBtns(true, true)}
      </div>`;
  }

  function renderPresupuesto() {
    return `
      <div class="asistente-paso">
        <p class="asistente-pregunta">¿Cuál es tu presupuesto aproximado por persona?</p>
        <div class="asistente-presupuesto">
          <select id="asistente-moneda" class="cotizar-input">
            <option value="ARS" ${prefs.moneda === 'ARS' ? 'selected' : ''}>ARS ($)</option>
            <option value="USD" ${prefs.moneda === 'USD' ? 'selected' : ''}>USD (U$S)</option>
            <option value="BRL" ${prefs.moneda === 'BRL' ? 'selected' : ''}>BRL (R$)</option>
          </select>
          <input type="number" id="asistente-presupuesto" class="cotizar-input" min="0" step="1000"
            placeholder="Ej: 500000" value="${prefs.presupuesto || ''}">
        </div>
        <p class="asistente-hint">Podés dejarlo vacío si preferís ver todas las opciones.</p>
        ${navBtns(true, true, 'Siguiente →')}
      </div>`;
  }

  function renderGrupo() {
    const opts = GRUPOS.map((g) =>
      `<button type="button" class="asistente-opcion${prefs.grupo === g.id ? ' sel' : ''}" data-grupo="${g.id}">${g.label}</button>`
    ).join('');
    return `
      <div class="asistente-paso">
        <p class="asistente-pregunta">¿Con quién viajás?</p>
        <div class="asistente-opciones">${opts}</div>
        ${navBtns(true, true, 'Ver recomendaciones →')}
      </div>`;
  }

  function cardMini(s) {
    const sim = U.SIMBOLO[s.moneda] || s.moneda;
    const urgencia = U.estadoUrgenciaTexto(s);
    return `
      <article class="asistente-resultado">
        <div class="asistente-resultado-img cat-${U.escapeHtml(s.cat || 'argentina')}">
          ${s.imagen_url
            ? `<img src="${U.escapeHtml(s.imagen_url)}" alt="" loading="lazy">`
            : `<span class="emoji-bg">${U.escapeHtml(s.emoji || '✈️')}</span>`}
        </div>
        <div class="asistente-resultado-body">
          <h4>${U.escapeHtml(s.nombre_paquete)}</h4>
          <p class="asistente-resultado-meta">📅 ${U.fechaLegible(s.fecha_salida)}</p>
          ${urgencia ? `<p class="asistente-resultado-urgencia">${U.escapeHtml(urgencia)}</p>` : ''}
          ${s.precio ? `<p class="asistente-resultado-precio">Desde ${sim} ${Number(s.precio).toLocaleString('es-AR')}</p>` : ''}
          <div class="asistente-resultado-btns">
            <a href="${U.paqueteUrl(s.id)}" class="btn-ghost-asistente">Ver paquete</a>
            <button type="button" class="btn-naranja btn-asistente-wa" data-id="${s.id}">Consultar</button>
          </div>
        </div>
      </article>`;
  }

  function renderResultados() {
    recomendar();
    const tipoLabel = TIPOS_VIAJE.find((t) => t.id === prefs.tipo)?.label || '';
    let contenido;
    if (!resultados.length) {
      contenido = `
        <p class="asistente-sin-match">No encontramos paquetes exactos con esos criterios.</p>
        <p class="asistente-hint">Probá con otro mes o tipo de viaje, o escribinos y te armamos algo a medida.</p>
        <a href="#alertas" class="btn-naranja" data-accion="alertas">Avisame cuando salga</a>`;
    } else {
      contenido = `
        <p class="asistente-hint">Según ${tipoLabel ? tipoLabel.toLowerCase() + ' y ' : ''}tus preferencias, te recomendamos:</p>
        <div class="asistente-resultados">${resultados.map((r) => cardMini(r.s)).join('')}</div>
        <button type="button" class="btn-naranja btn-asistente-wa-todos" data-accion="wa-todos">Consultar por WhatsApp</button>`;
    }
    return `
      <div class="asistente-paso">
        <p class="asistente-pregunta">Estos viajes van con vos ✈️</p>
        ${contenido}
        ${navBtns(true, false)}
        <button type="button" class="btn-link-asistente" data-accion="reiniciar">Empezar de nuevo</button>
      </div>`;
  }

  function mensajeWaTodos() {
    const lineas = ['Hola! Usé el asistente de Olalá Viajes y me interesan estos paquetes:', ''];
    resultados.forEach((r, i) => {
      lineas.push(`${i + 1}. *${r.s.nombre_paquete}* (${U.fechaLegible(r.s.fecha_salida)})`);
      lineas.push(`   ${U.paqueteUrl(r.s.id)}`);
    });
    lineas.push('', '¿Podés contarme disponibilidad y precio actualizado?');
    return lineas.join('\n');
  }

  function bindPaso() {
    const el = root();
    if (!el) return;

    el.querySelectorAll('[data-tipo]').forEach((btn) => {
      btn.addEventListener('click', () => {
        prefs.tipo = btn.dataset.tipo;
        el.querySelectorAll('[data-tipo]').forEach((b) => b.classList.toggle('sel', b === btn));
      });
    });
    el.querySelectorAll('[data-mes]').forEach((btn) => {
      btn.addEventListener('click', () => {
        prefs.mes = btn.dataset.mes ? parseInt(btn.dataset.mes, 10) : null;
        el.querySelectorAll('[data-mes]').forEach((b) => b.classList.toggle('sel', b === btn));
      });
    });
    el.querySelectorAll('[data-grupo]').forEach((btn) => {
      btn.addEventListener('click', () => {
        prefs.grupo = btn.dataset.grupo;
        el.querySelectorAll('[data-grupo]').forEach((b) => b.classList.toggle('sel', b === btn));
      });
    });

    el.querySelector('[data-accion="atras"]')?.addEventListener('click', () => {
      if (paso > 0) { paso -= 1; renderPaso(); }
    });
    el.querySelector('[data-accion="siguiente"]')?.addEventListener('click', () => {
      if (paso === 0 && !prefs.tipo) return;
      if (paso === 3) { paso = 4; renderPaso(); return; }
      if (paso === 2) {
        const mon = el.querySelector('#asistente-moneda');
        const pre = el.querySelector('#asistente-presupuesto');
        if (mon) prefs.moneda = mon.value;
        if (pre) prefs.presupuesto = pre.value.trim();
      }
      if (paso < 4) { paso += 1; renderPaso(); }
    });
    el.querySelector('[data-accion="reiniciar"]')?.addEventListener('click', () => {
      paso = 0;
      prefs = { tipo: '', mes: null, presupuesto: '', moneda: 'ARS', grupo: '' };
      renderPaso();
    });
    el.querySelector('[data-accion="wa-todos"]')?.addEventListener('click', () => {
      window.open(`https://wa.me/${WA}?text=${encodeURIComponent(mensajeWaTodos())}`, '_blank');
    });
    el.querySelector('[data-accion="alertas"]')?.addEventListener('click', () => {
      document.getElementById('alertas')?.scrollIntoView({ behavior: 'smooth' });
    });
    el.querySelectorAll('.btn-asistente-wa').forEach((btn) => {
      btn.addEventListener('click', () => {
        const s = salidas().find((x) => String(x.id) === btn.dataset.id);
        if (!s) return;
        const msg = `Hola! Me interesa el paquete *${s.nombre_paquete}* (${U.fechaLegible(s.fecha_salida)}).\n${U.paqueteUrl(s.id)}`;
        window.open(`https://wa.me/${WA}?text=${encodeURIComponent(msg)}`, '_blank');
      });
    });
  }

  function iniciar() {
    if (!root()) return;
    renderPaso();
  }

  document.addEventListener('olala:salidas-cargadas', iniciar);
  if (window.OLALA_SALIDAS?.length) iniciar();
})();
