/* Portal de Residentes · Los Cedros (/reportar y /mis-reportes) */
(function () {
  const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
  let D = {};
  try { D = JSON.parse(($('#lc-data') || {}).textContent || '{}'); } catch (e) { D = {}; }
  const esc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const plain = h => { const d = document.createElement('div'); d.innerHTML = h; return (d.textContent || '').trim(); };

  // ---- menu (mobile)
  const nav = $('#nav'), mb = $('#menuBtn');
  if (nav && mb) {
    mb.addEventListener('click', () => { const o = nav.classList.toggle('open'); mb.setAttribute('aria-expanded', o); });
  }

  // ---- POST to a whitelisted method with Frappe's CSRF token
  function serverError(j, status) {
    if (status === 429) return 'Enviaste demasiados mensajes en poco tiempo. Intenta de nuevo en una hora.';
    if (j && j.exc_type === 'CSRFTokenError') return 'Tu sesión expiró. Recarga la página e intenta de nuevo.';
    if (status === 403 || status === 401) return 'Tu sesión terminó. Vuelve a iniciar sesión.';
    try {
      if (j && j._server_messages) {
        const m = JSON.parse(j._server_messages);
        const x = JSON.parse(m[m.length - 1]);
        if (x && x.message) return plain(x.message);
      }
    } catch (e) { /* ignore */ }
    return 'No se pudo enviar. Revisa tu conexión e intenta de nuevo.';
  }
  async function post(method, fd) {
    let res;
    try {
      res = await fetch('/api/method/' + method, {
        method: 'POST', body: fd, credentials: 'same-origin',
        headers: { 'X-Frappe-CSRF-Token': D.csrf || '', 'Accept': 'application/json' }
      });
    } catch (e) { throw new Error('No hay conexión con el servidor. Intenta de nuevo.'); }
    let j = {};
    try { j = await res.json(); } catch (e) { j = {}; }
    if (!res.ok || j.exc_type) throw new Error(serverError(j, res.status));
    return j.message;
  }
  function showErr(el, msg) { el.textContent = msg; el.hidden = !msg; if (msg) el.scrollIntoView({ block: 'center', behavior: 'smooth' }); }

  // =====================================================================
  // /reportar
  // =====================================================================
  const form = $('#form');
  if (form && Array.isArray(D.categorias)) {
    const CATS = D.categorias, R = D.residente || {};
    let actual = -1;
    const fotos = []; // {blob, name, url}

    const step = n => ['#st1', '#st2', '#st3'].forEach((s, i) => { const el = $(s); el.classList.toggle('on', i === n - 1); el.classList.toggle('done', i < n - 1); });

    // building / apartment / contact from the resident profile
    $('#edificio').value = R.edificio || '';
    $('#apartamento').value = R.apartamento || '';
    $('#telefono').value = R.telefono || '';
    if (R.verificado) { $('#edificio').readOnly = true; $('#apartamento').readOnly = true; $('#verif').hidden = false; }
    const radio = $$('input[name="contacto"]').find(r => r.value === R.contacto);
    if (radio) radio.checked = true;
    const syncTel = () => {
      const tel = $('input[name="contacto"]:checked').value === 'Teléfono';
      $('#telReq').hidden = !tel; $('#telefono').required = tel;
    };
    $$('input[name="contacto"]').forEach(r => r.addEventListener('change', syncTel)); syncTel();

    // extra fields of the chosen category
    function renderExtras(c) {
      const box = $('#extras');
      box.innerHTML = (c.campos || []).map((f, i) => {
        const id = 'x' + i, req = f.req ? ' <span class="req">*</span>' : '';
        if (f.tipo === 'Sí/No') {
          return `<div class="field"><span class="lbl" id="${id}l">${esc(f.e)}${req}</span>
            <div class="pills" role="radiogroup" aria-labelledby="${id}l" data-x="${i}">
              <label><input type="radio" name="${id}" value="Sí"> Sí</label>
              <label><input type="radio" name="${id}" value="No"> No</label></div></div>`;
        }
        if (f.tipo === 'Opciones') {
          return `<div class="field"><label for="${id}">${esc(f.e)}${req}</label>
            <select id="${id}" data-x="${i}"><option value="">Escoge una opción</option>
            ${(f.ops || []).map(o => `<option>${esc(o)}</option>`).join('')}</select></div>`;
        }
        return `<div class="field"><label for="${id}">${esc(f.e)}${req}</label>
          <input id="${id}" data-x="${i}" maxlength="300" autocomplete="off"></div>`;
      }).join('');
    }
    function extraValues(c) {
      return (c.campos || []).map((f, i) => {
        if (f.tipo === 'Sí/No') { const r = $(`input[name="x${i}"]:checked`); return r ? r.value : ''; }
        const el = $('#x' + i); return el ? el.value.trim() : '';
      });
    }

    function choose(i) {
      const c = CATS[i]; if (!c) return;
      actual = i;
      $('#selIcon').innerHTML = c.i || '';
      $('#selName').textContent = c.n;
      $('#selTime').textContent = c.p || '';
      $('#selTime').hidden = !c.p;
      $('#tips').innerHTML = (c.l || []).map(x => `<li>${esc(x)}</li>`).join('');
      $('#tipsBox').hidden = !(c.l || []).length;
      $('#aviso').textContent = c.a || ''; $('#aviso').hidden = !c.a;
      renderExtras(c);
      $('#paso1').hidden = true; form.hidden = false; step(2);
      showErr($('#formErr'), '');
      try { history.replaceState(null, '', '/reportar?categoria=' + encodeURIComponent(c.n)); } catch (e) { /* ignore */ }
      window.scrollTo({ top: 0, behavior: 'smooth' });
      const first = $('#extras input, #extras select') || $('#descripcion');
      setTimeout(() => first && first.focus({ preventScroll: true }), 250);
    }
    $$('.rcat').forEach(b => b.addEventListener('click', () => choose(+b.dataset.i)));
    $('#cambiar').addEventListener('click', () => { form.hidden = true; $('#paso1').hidden = false; step(1); });
    if (D.inicial >= 0) choose(D.inicial);

    // description counter
    const desc = $('#descripcion');
    desc.addEventListener('input', () => { $('#dcount').textContent = desc.value.length; });

    // photos: downscale to 1600px JPEG (also drops EXIF/GPS) before upload
    async function prepare(file) {
      if (!/^image\//.test(file.type) && !/\.(heic|heif)$/i.test(file.name)) throw new Error('Solo se aceptan fotos.');
      try {
        const bmp = await createImageBitmap(file, { imageOrientation: 'from-image' });
        const s = Math.min(1, 1600 / Math.max(bmp.width, bmp.height));
        const cv = document.createElement('canvas');
        cv.width = Math.round(bmp.width * s); cv.height = Math.round(bmp.height * s);
        cv.getContext('2d').drawImage(bmp, 0, 0, cv.width, cv.height);
        const blob = await new Promise(r => cv.toBlob(r, 'image/jpeg', 0.82));
        if (blob) return { blob, name: 'foto.jpg', url: URL.createObjectURL(blob) };
      } catch (e) { /* the browser can't decode it (e.g. HEIC): send the original */ }
      if (file.size > 8 * 1024 * 1024) throw new Error('Cada foto debe pesar menos de 8 MB.');
      return { blob: file, name: file.name, url: URL.createObjectURL(file) };
    }
    function renderFotos() {
      $$('#fotos .foto').forEach(n => n.remove());
      const add = $('#fotos .foto-add');
      fotos.forEach((f, i) => {
        const el = document.createElement('div');
        el.className = 'foto';
        el.innerHTML = `<img alt="Foto ${i + 1}"><button type="button" aria-label="Quitar foto ${i + 1}">×</button>`;
        const img = el.querySelector('img');
        img.src = f.url;
        img.onerror = () => { el.classList.add('noimg'); el.insertAdjacentHTML('afterbegin', `<span>${esc(f.name)}</span>`); img.remove(); };
        el.querySelector('button').addEventListener('click', () => { URL.revokeObjectURL(f.url); fotos.splice(i, 1); renderFotos(); });
        add.before(el);
      });
      add.hidden = fotos.length >= 3;
    }
    $('#fotoInput').addEventListener('change', async e => {
      const files = [...e.target.files]; e.target.value = '';
      showErr($('#formErr'), '');
      for (const f of files) {
        if (fotos.length >= 3) { showErr($('#formErr'), 'Puedes adjuntar hasta 3 fotos.'); break; }
        try { fotos.push(await prepare(f)); } catch (err) { showErr($('#formErr'), err.message); }
      }
      renderFotos();
    });

    // submit
    form.addEventListener('submit', async e => {
      e.preventDefault();
      const c = CATS[actual]; const err = $('#formErr');
      if (!c) { showErr(err, 'Escoge una categoría.'); return; }
      const vals = extraValues(c);
      const falta = (c.campos || []).findIndex((f, i) => f.req && !vals[i]);
      if (falta >= 0) { showErr(err, 'Completa el campo: ' + c.campos[falta].e); return; }
      if (desc.value.trim().length < 10) { showErr(err, 'Describe la situación con al menos 10 caracteres.'); desc.focus(); return; }
      if (!$('#edificio').value.trim() || !$('#apartamento').value.trim()) { showErr(err, 'Indica tu edificio y apartamento.'); return; }
      const contacto = $('input[name="contacto"]:checked').value;
      const tel = $('#telefono').value.trim();
      if (contacto === 'Teléfono' && tel.replace(/\D/g, '').length < 7) { showErr(err, 'Escribe un teléfono válido para que te llamen.'); $('#telefono').focus(); return; }

      const fd = new FormData();
      fd.append('categoria', c.n);
      fd.append('descripcion', desc.value.trim());
      fd.append('edificio', $('#edificio').value.trim());
      fd.append('apartamento', $('#apartamento').value.trim());
      fd.append('extras', JSON.stringify(vals));
      fd.append('contacto', contacto);
      fd.append('telefono', tel);
      fotos.forEach((f, i) => fd.append('fotos', f.blob, f.name || ('foto' + (i + 1) + '.jpg')));

      const btn = $('#enviar'); btn.disabled = true; $('#enviando').hidden = false; showErr(err, '');
      try {
        const r = await post('los_cedros.api.crear_reporte', fd);
        const caso = r && r.caso;
        $('#casoNum').textContent = '#' + caso;
        $('#verCaso').href = '/mis-reportes?caso=' + encodeURIComponent(caso);
        form.hidden = true; $('#exito').hidden = false; step(3);
        try { history.replaceState(null, '', '/reportar'); } catch (x) { /* ignore */ }
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } catch (x) {
        showErr(err, x.message);
      } finally {
        btn.disabled = false; $('#enviando').hidden = true;
      }
    });
  }

  // =====================================================================
  // /mis-reportes?caso=N
  // =====================================================================
  const reply = $('#reply');
  if (reply && D.caso) {
    const ta = $('#mensaje');
    ta.addEventListener('input', () => { $('#mcount').textContent = ta.value.length; });
    reply.addEventListener('submit', async e => {
      e.preventDefault();
      const err = $('#replyErr');
      if (ta.value.trim().length < 2) { showErr(err, 'Escribe tu mensaje.'); ta.focus(); return; }
      const fd = new FormData(); fd.append('caso', D.caso); fd.append('mensaje', ta.value.trim());
      const btn = $('#replyBtn'); btn.disabled = true; btn.textContent = 'Enviando…';
      try { await post('los_cedros.api.responder', fd); location.reload(); }
      catch (x) { showErr(err, x.message); btn.disabled = false; btn.textContent = 'Enviar respuesta'; }
    });
  }
})();
