(function(){
  const D=JSON.parse(document.getElementById('lc-data').textContent||'{}');
  const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
  const store={get(k,d){try{const v=localStorage.getItem(k);return v?JSON.parse(v):d}catch(e){return d}},set(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}}};
  const toast=m=>{const t=$('#toast');t.textContent=m;t.classList.add('show');clearTimeout(toast.t);toast.t=setTimeout(()=>t.classList.remove('show'),1800)};

  // mobile menu
  const nav=$('#nav'),mb=$('#menuBtn');
  mb.addEventListener('click',()=>{const o=nav.classList.toggle('open');mb.setAttribute('aria-expanded',o)});
  nav.addEventListener('click',e=>{if(e.target.tagName==='A'){nav.classList.remove('open');mb.setAttribute('aria-expanded',false)}});

  // office status from Configuracion Sitio (Puerto Rico time)
  const now=new Date(new Date().toLocaleString('en-US',{timeZone:'America/Puerto_Rico'}));
  const hr=now.getHours()+now.getMinutes()/60;
  const open=(D.horario||[]).some(x=>x.d===now.getDay()&&hr>=x.a&&hr<x.b);
  $('#officeStatus').textContent = open ? 'abierta para pagos ahora' : (D.diasPago ? 'pagos '+D.diasPago : 'ver horario en Cuotas');

  // report categories (from Categoria Reporte)
  const CATS=D.categorias||[];
  function pick(k){
    const c=CATS[k];if(!c)return;$$('.cat').forEach(b=>b.setAttribute('aria-pressed',b.dataset.cat===String(k)));
    $('#tkEyebrow').textContent=c.n;$('#tkTitle').textContent=c.t||c.n;$('#tkPrio').textContent=c.p||'';$('#tkPrio').hidden=!c.p;
    const esc2=s=>String(s).replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]));
    $('#tkList').innerHTML=(c.l||[]).map(x=>'<li>'+esc2(x)+'</li>').join('');
    $('#tkGo').href='/reportar?categoria='+encodeURIComponent(c.n);
  }
  $$('.cat').forEach(b=>b.addEventListener('click',()=>pick(+b.dataset.cat)));
  if(CATS.length)pick(0);else{const tk=document.querySelector('.ticket');if(tk)tk.hidden=true;}

  // bulletin filters
  $$('.filters button').forEach(b=>b.addEventListener('click',()=>{
    const f=b.dataset.f;$$('.filters button').forEach(x=>x.setAttribute('aria-pressed',x===b));
    $$('#board .post').forEach(p=>p.hidden=!(f==='todos'||p.dataset.k===f||(p.classList.contains('lead')&&f==='comunidad')));
  }));

  // events
  const EV=(D.eventos||[]).map(e=>[e.f,e.t,e.s]);
  const M=['ene','feb','mar','abr','may','jun','jul','ago','sep','oct','nov','dic'];
  const today=new Date(now.getFullYear(),now.getMonth(),now.getDate());
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  $('#events').innerHTML=EV.length?'':'<li class="empty">No hay fechas programadas.</li>';
  if(EV.length)$('#events').innerHTML=EV.map(([d,t,s])=>{
    const [y,m,dd]=d.split('-').map(Number),dt=new Date(y,m-1,dd),n=Math.round((dt-today)/864e5);
    const w=n<0?'Pasó':n===0?'Hoy':n===1?'Mañana':'En '+n+' días';
    return `<li class="ev${n<0?' past':''}"><span class="date"><span>${M[m-1]}</span><b>${dd}</b></span><div><h4>${esc(t)}</h4><p>${esc(s)}</p></div><span class="when${n>=0&&n<=7?' soon':''}">${w}</span></li>`;
  }).join('');

  // dues
  const day=now.getDate(),last=new Date(now.getFullYear(),now.getMonth()+1,0).getDate();
  const box=$('#duesBox');let head,body,cls;
  const mes=now.toLocaleString('es-PR',{month:'long'});
  const L=D.limite||16;
  if(day<L){head=`Te quedan ${L-day} días sin recargo`;body=`El pago de ${mes} se acepta sin penalidad hasta el ${L}.`;cls=L-day<=4?'warn':'ok'}
  else if(day===L){head='Hoy es el último día sin recargo';body=`Paga la cuota de ${mes} hoy para evitar la penalidad.`;cls='warn'}
  else{head='Pago con recargo';body=`Desde el ${L+1} de ${mes} aplica recargo. Comunícate con la Oficina si necesitas un plan de pago.`;cls='bad'}
  box.className='dues-status '+cls;$('#duesHead').textContent=head;$('#duesBody').textContent=body;
  $('#duesBar').style.width=(day/last*100)+'%';$('#duesEnd').textContent='Día '+last;

  // hurricane checklist
  const PREP=[
    ['Agua','Un galón por persona por día, para al menos 3 días'],
    ['Alimentos','No perecederos para 3 días y un abrelatas manual'],
    ['Medicinas','Suficientes para 3 semanas, con copia de las recetas'],
    ['Higiene y botiquín','Desinfectante, jabón, pañales, mascarillas y primeros auxilios'],
    ['Radio y linternas','De baterías, con baterías adicionales'],
    ['Documentos','En bolsa sellada, con una lista impresa de contactos'],
    ['Efectivo','Los cajeros y tarjetas pueden fallar sin electricidad'],
    ['Prepara tu apartamento','Asegura objetos del balcón y revisa las ventanas']
  ];
  const done=store.get('lc-prep',{});
  $('#prepList').innerHTML=PREP.map(([t,s],i)=>`<label class="chk" for="prep${i}"><input type="checkbox" id="prep${i}" ${done[i]?'checked':''}><span><b>${t}</b><small>${s}</small></span></label>`).join('');
  function meter(){const c=$$('#prepList input').filter(x=>x.checked).length,p=Math.round(c/PREP.length*100);$('#prepBar').style.width=p+'%';$('#prepPct').textContent=p+'%'}
  $('#prepList').addEventListener('change',e=>{const i=e.target.id.slice(4);done[i]=e.target.checked;store.set('lc-prep',done);meter();if($$('#prepList input').every(x=>x.checked))toast('Plan familiar completo')});
  meter();

  // copy
  $$('[data-copy]').forEach(b=>b.addEventListener('click',()=>{
    const el=document.getElementById(b.dataset.copy),txt=el.textContent;
    const sel=()=>{const r=document.createRange();r.selectNodeContents(el);const s=getSelection();s.removeAllRanges();s.addRange(r);toast('Texto seleccionado')};
    try{navigator.clipboard.writeText(txt).then(()=>toast('Copiado'),sel)}catch(e){sel()}
  }));

  // home tiles: live snippets
  const nextEv=EV.find(([d])=>{const [y,m,dd]=d.split('-').map(Number);return new Date(y,m-1,dd)>=today});
  if(nextEv){const [y,m,dd]=nextEv[0].split('-').map(Number);$('#tileEvent').textContent='Próximo: '+nextEv[1]+' · '+dd+' '+M[m-1]}
  else $('#tileEvent').textContent='Sin fechas programadas';
  $('#tileDues').textContent=head;
  const prepTile=()=>{const c=$$('#prepList input').filter(x=>x.checked).length;$('#tilePrep').textContent=c?('Tu plan: '+Math.round(c/PREP.length*100)+'% listo'):'Lista de preparación familiar'};
  prepTile();$('#prepList').addEventListener('change',prepTile);

  // router: each menu button shows only its own view
  const views=$$('.view'),ids=views.map(v=>v.id);
  function show(){
    let id=(location.hash||'').slice(1);if(!ids.includes(id))id='inicio';
    views.forEach(v=>v.hidden=v.id!==id);
    $$('.nav a').forEach(a=>{const on=a.getAttribute('href')==='#'+id;a.classList.toggle('on',on);on?a.setAttribute('aria-current','page'):a.removeAttribute('aria-current')});
    document.title=(id==='inicio'?'':document.getElementById(id).dataset.title+' · ')+'Condominio Los Cedros';
    window.scrollTo(0,0);
  }
  window.addEventListener('hashchange',show);show();
})();
