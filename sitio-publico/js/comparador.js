(function () {
  'use strict';

  const U = window.OlalaUtil;
  const MAX = 3;
  let seleccionados = [];

  function salidas() {
    return window.OLALA_SALIDAS || [];
  }

  function porId(id) {
    return salidas().find((s) => String(s.id) === String(id));
  }

  function actualizarDock() {
    const dock = document.getElementById('comparador-dock');
    if (!dock) return;
    const n = seleccionados.length;
    dock.hidden = n === 0;
    dock.classList.toggle('comparador-dock-listo', n >= 2);
    const lbl = document.getElementById('comparador-dock-count');
    if (lbl) lbl.textContent = String(n);
    const btn = document.getElementById('btn-abrir-comparador');
    if (btn) {
      btn.disabled = n < 2;
      btn.textContent = n < 2 ? 'Elegí al menos 2' : `Comparar ${n} paquetes`;
    }
    document.querySelectorAll('.btn-comparar').forEach((b) => {
      const id = b.dataset.id;
      const sel = seleccionados.includes(id);
      b.classList.toggle('activo', sel);
      b.textContent = sel ? '✓ En comparación' : '+ Comparar';
      b.setAttribute('aria-pressed', sel ? 'true' : 'false');
    });
  }

  function toggle(id) {
    const sid = String(id);
    const idx = seleccionados.indexOf(sid);
    if (idx >= 0) {
      seleccionados.splice(idx, 1);
    } else {
      if (seleccionados.length >= MAX) {
        showToast(`Podés comparar hasta ${MAX} paquetes`);
        return;
      }
      seleccionados.push(sid);
    }
    actualizarDock();
  }

  function showToast(msg) {
    const t = document.getElementById('share-toast');
    if (!t) return;
    t.textContent = msg;
    t.classList.add('show');
    setTimeout(() => t.classList.remove('show'), 2500);
  }

  function serviciosLista(texto, max) {
    return (texto || '')
      .split('\n')
      .map((l) => l.replace(/^[\u2713\u2714✓✔•\-]\s*/, '').trim())
      .filter(Boolean)
      .slice(0, max || 8);
  }

  function celdaValor(s, campo) {
    if (!s) return '—';
    switch (campo) {
      case 'precio':
        if (!s.precio) return 'Consultar';
        return `${U.SIMBOLO[s.moneda] || ''} ${Number(s.precio).toLocaleString('es-AR')} (${s.moneda})`;
      case 'fecha':
        return U.fechaLegible(s.fecha_salida);
      case 'cupos':
        if (s.agotado) return 'Agotado';
        if (s.cupos != null) return `${s.cupos} lugares`;
        return 'Consultar';
      case 'estado':
        return U.estadoUrgenciaTexto(s) || 'Disponible';
      case 'servicios': {
        const items = serviciosLista(s.servicios_incluidos, 6);
        return items.length
          ? `<ul class="cmp-servicios">${items.map((i) => `<li>${U.escapeHtml(i)}</li>`).join('')}</ul>`
          : '—';
      }
      default:
        return U.escapeHtml(s[campo] || '—');
    }
  }

  function abrirModal() {
    if (seleccionados.length < 2) return;
    const modal = document.getElementById('comparador-modal');
    const body = document.getElementById('comparador-modal-body');
    if (!modal || !body) return;
    const paqs = seleccionados.map(porId).filter(Boolean);
    const filas = [
      ['Paquete', 'nombre_paquete'],
      ['Categoría', 'cat_label'],
      ['Fecha salida', 'fecha'],
      ['Sale desde', 'lugar_salida'],
      ['Precio', 'precio'],
      ['Cupos', 'cupos'],
      ['Estado', 'estado'],
      ['Incluye', 'servicios'],
    ];
    let html = '<div class="cmp-tabla-wrap"><table class="cmp-tabla"><thead><tr><th></th>';
    paqs.forEach((p) => {
      html += `<th>
        <div class="cmp-th-nombre">${U.escapeHtml(p.nombre_paquete)}</div>
        <a href="${U.paqueteUrl(p.id)}" class="cmp-th-link">Ver paquete →</a>
      </th>`;
    });
    html += '</tr></thead><tbody>';
    filas.forEach(([label, campo]) => {
      html += `<tr><th class="cmp-row-label">${label}</th>`;
      paqs.forEach((p) => {
        const val = celdaValor(p, campo === 'nombre_paquete' ? 'nombre_paquete' : campo);
        html += `<td>${campo === 'nombre_paquete' ? U.escapeHtml(p.nombre_paquete) : val}</td>`;
      });
      html += '</tr>';
    });
    html += '</tbody></table></div>';
    body.innerHTML = html;
    modal.hidden = false;
    document.body.style.overflow = 'hidden';
  }

  function cerrarModal() {
    const modal = document.getElementById('comparador-modal');
    if (modal) modal.hidden = true;
    document.body.style.overflow = '';
  }

  function limpiar() {
    seleccionados = [];
    actualizarDock();
    cerrarModal();
  }

  function bindGlobal() {
    document.getElementById('btn-abrir-comparador')?.addEventListener('click', abrirModal);
    document.getElementById('btn-cerrar-comparador')?.addEventListener('click', cerrarModal);
    document.getElementById('btn-limpiar-comparador')?.addEventListener('click', limpiar);
    document.getElementById('comparador-modal')?.addEventListener('click', (e) => {
      if (e.target.id === 'comparador-modal') cerrarModal();
    });
  }

  window.OlalaComparador = { toggle, actualizarDock };

  document.addEventListener('DOMContentLoaded', bindGlobal);
  document.addEventListener('olala:salidas-cargadas', actualizarDock);
})();
