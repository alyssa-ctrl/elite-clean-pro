const toggle=document.querySelector('.menu-toggle'),nav=document.querySelector('#nav');
function closeMenu(){nav?.classList.remove('open');toggle?.setAttribute('aria-expanded','false')}
toggle?.addEventListener('click',()=>{const open=toggle.getAttribute('aria-expanded')!=='true';toggle.setAttribute('aria-expanded',String(open));nav.classList.toggle('open',open)});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){closeMenu();toggle?.focus()}});
nav?.querySelectorAll('a').forEach(a=>a.addEventListener('click',closeMenu));
const form=document.querySelector('#quote-form');
if(form){let step=0;const panels=[...form.querySelectorAll('fieldset')],steps=[...document.querySelectorAll('.stepper span')],error=document.querySelector('#form-error');
function show(n){step=n;panels.forEach((p,i)=>p.hidden=i!==n);steps.forEach((p,i)=>{p.classList.toggle('active',i===n);if(i===n)p.setAttribute('aria-current','step');else p.removeAttribute('aria-current')});document.querySelector('#back').hidden=n===0;document.querySelector('#next').textContent=n===panels.length-1?(form.dataset.bookingEnabled==='true'?'Review my request':'Preview my request'):'Continue';error.textContent='';panels[n].querySelector('input,select,textarea')?.focus()}
document.querySelector('#back').addEventListener('click',()=>show(Math.max(0,step-1)));
document.querySelector('#service').addEventListener('change',e=>{document.querySelector('#move-date-field').hidden=e.target.value!=='Move-out cleaning'});
document.querySelector('#next').addEventListener('click',()=>{for(const el of panels[step].querySelectorAll('input,select,textarea')){if(!el.checkValidity()){el.reportValidity();error.textContent=el.validationMessage||'Please complete the required details before continuing.';return}}if(step<panels.length-1){show(step+1);return}const data=new FormData(form),out=document.querySelector('#request-summary');out.replaceChildren();for(const [k,v]of data){if(['form-name','email','website','Request reference'].includes(k)||!v)continue;const row=document.createElement('div');row.className='sample-row';const a=document.createElement('span'),b=document.createElement('span');a.textContent=k;b.textContent=v;row.append(a,b);out.append(row)}document.querySelector('#form-entry').hidden=true;document.querySelector('#form-success').hidden=false;document.querySelector('#success-heading').focus()});
document.querySelector('#edit-request').addEventListener('click',()=>{document.querySelector('#form-entry').hidden=false;document.querySelector('#form-success').hidden=true;show(0)});
form.addEventListener('booking-time-invalid',e=>{document.querySelector('#form-entry').hidden=false;document.querySelector('#form-success').hidden=true;const date=document.querySelector('#preferred-date');show(panels.findIndex(panel=>panel.contains(date)));error.textContent=e.detail;const field=date.validationMessage?date:document.querySelector('#preferred-time');field.focus();});
form.addEventListener('submit',e=>e.preventDefault());
}

const cleanerForm=document.querySelector('#cleaner-form');cleanerForm?.addEventListener('submit',e=>{e.preventDefault();const output=document.querySelector('#cleaner-result');output.hidden=false;output.textContent='Preview introduction prepared. No application has been sent. At launch, this would enter the dedicated recruitment queue for review.';});

// One-time reveals respect the visitor's motion preference.
if('IntersectionObserver' in window&&!window.matchMedia('(prefers-reduced-motion: reduce)').matches){
 const observer=new IntersectionObserver(entries=>{for(const entry of entries){if(entry.isIntersecting){entry.target.classList.add('in-view');observer.unobserve(entry.target)}}},{threshold:0.08});
 document.querySelectorAll('.section-head,.service-card,.cards .card,.home-moment,.founder,.closing,.about-story,.standards-block,.about-detail,.route-hero-image .route-image').forEach((el,i)=>{el.style.setProperty('--reveal-delay',el.matches('.card,.service-card')?'0ms':'0ms');el.classList.add('motion-ready');observer.observe(el)});
}

const serviceSelect=document.querySelector('#service');
if(serviceSelect){
 const preferred=document.querySelector('#preferred-date'),handover=document.querySelector('[name="Handover deadline"]');
 const now=new Date(),today=`${now.getFullYear()}-${String(now.getMonth()+1).padStart(2,'0')}-${String(now.getDate()).padStart(2,'0')}`;
 [preferred,handover].forEach(el=>{if(el)el.min=today});
 function syncService(){const moving=serviceSelect.value==='Move-out cleaning';const frequency=document.querySelector('#frequency-field');frequency.hidden=moving;frequency.querySelector('select').disabled=moving;document.querySelector('#move-date-field').hidden=!moving;handover.disabled=!moving;const scopeNote=document.querySelector('#extras-scope-note');if(scopeNote)scopeNote.textContent=moving?'Oven, fridge and empty cabinet interiors are included in the move-out estimate. Use the checkboxes to highlight priorities. Interior windows and other requests need review. Your written quote confirms the work.':'These are requests, not automatic inclusions. Your written quote confirms the work.';}
 serviceSelect.addEventListener('change',syncService);
 const options={regular:'Regular cleaning',deep:'Deep cleaning',moveout:'Move-out cleaning'};
 const requested=options[new URLSearchParams(location.search).get('service')];if(requested)serviceSelect.value=requested;syncService();
}

const estimator=document.querySelector('#estimate-form');
const estimateFields=['service','band','full','half','condition','basement','frequency','established','oven','fridge','cabinets','hair','windows'];
function estimateValues(params){const v={};for(const key of estimateFields)v[key]=['established','oven','fridge','cabinets','hair'].includes(key)?params.get(key)==='1':params.get(key);return v;}
function money(n){return new Intl.NumberFormat('en-CA',{style:'currency',currency:'CAD',maximumFractionDigits:0}).format(n);}
if(estimator){
 function renderEstimate(){
  const v={};for(const key of estimateFields){const el=estimator.elements.namedItem(key);v[key]=el.type==='checkbox'?el.checked:el.value;}
  const moving=v.service==='moveout',regular=v.service==='regular';
  for(const key of ['oven','fridge','cabinets']){const el=estimator.elements.namedItem(key);el.disabled=moving;el.closest('label').classList.toggle('included-extra',moving);}
  document.querySelector('#estimate-frequency').hidden=!regular;document.querySelector('#estimate-established').hidden=!regular;
  const result=EliteEstimate.calculate(v),total=document.querySelector('#estimate-total'),lines=document.querySelector('#estimate-lines');lines.replaceChildren();
  total.textContent=result.manual?'Let’s review your space':`${money(result.low)}–${money(result.high)}`;
  if(result.manual){const p=document.createElement('p');p.textContent='Size, condition or scope needs a personal estimate. Send these details for review.';lines.append(p);}else{for(const line of result.lines){const row=document.createElement('div');row.className='sample-row';const label=document.createElement('span'),amount=document.createElement('span');label.textContent=line.label;amount.textContent=line.amount===0?'Included':money(line.amount);row.append(label,amount);lines.append(row);}const note=document.createElement('p');note.className='quiet';note.textContent='Base estimate rounded up to $5; upper range allows 15% for scope variation. The final quote may differ after review.';lines.append(note);}
  const params=new URLSearchParams();for(const key of estimateFields)params.set(key,typeof v[key]==='boolean'?(v[key]?'1':'0'):v[key]);params.set('estimate','1');document.querySelector('#estimate-continue').href='/book/?'+params.toString();
 }
 estimator.addEventListener('input',renderEstimate);estimator.addEventListener('change',renderEstimate);estimator.addEventListener('submit',e=>e.preventDefault());renderEstimate();
}
if(form&&new URLSearchParams(location.search).get('estimate')==='1'){
 const params=new URLSearchParams(location.search),v=estimateValues(params),result=EliteEstimate.calculate(v);
 const names={regular:'Regular cleaning',deep:'Deep cleaning',moveout:'Move-out cleaning'};
 if(names[v.service])serviceSelect.value=names[v.service];serviceSelect.dispatchEvent(new Event('change'));
 const size=form.elements.namedItem('Approximate size');size.value=EliteEstimate.config.bands[Number(v.band)]||'2,500+ sq. ft.';
 form.elements.namedItem('Full bathrooms').value=String(v.full);form.elements.namedItem('Half bathrooms').value=String(v.half);
 const freq={once:'One-time',weekly:'Weekly',biweekly:'Bi-weekly',monthly:'Monthly'};form.elements.namedItem('Frequency').value=freq[v.frequency]||'One-time';
 const condition={typical:'Maintained / regular cleaning',moderate:'First clean / needs a reset',heavy:'Unsure — please discuss',unsure:'Unsure — please discuss'};form.elements.namedItem('Condition').value=condition[v.condition]||'Unsure — please discuss';if(v.service==='moveout'&&v.condition==='typical')form.elements.namedItem('Condition').value='Vacant after moving out';
 const extras={oven:'Inside oven',fridge:'Inside fridge',cabinets:'Inside cabinets'};for(const [key,value]of Object.entries(extras)){const box=[...form.querySelectorAll('[name="Requested extras"]')].find(x=>x.value===value);if(box)box.checked=Boolean(v[key]||v.service==='moveout');}
 const details=`Basement: ${v.basement||'review'}. Interior window panes: ${v.windows||0}. Extra pet-hair removal: ${v.hair?'yes':'no'}. Established maintenance schedule: ${v.established?'yes':'no'}.`;
 form.elements.namedItem('Priorities').value=details;
 const banner=document.querySelector('#carried-estimate'),hidden=document.querySelector('#estimate-summary-field');banner.hidden=false;
 const summary=result.manual?'Personal estimate needed':`${money(result.low)}–${money(result.high)} CAD before any applicable tax`;
 banner.textContent='Your calculator details are filled below. '+summary+'. Final scope and price require review.';hidden.value=summary+'; '+details;
 form.addEventListener('change',e=>{if(['Name','Email','Phone','Preferred date','Preferred time','Handover deadline','Flexible dates'].includes(e.target.name))return;hidden.value='Details changed after calculator — revised estimate required';banner.textContent='Your details have changed. We’ll prepare a revised estimate from this request.';});
}

if(form){
 const dateField=document.querySelector('#preferred-date'),timeField=document.querySelector('#preferred-time'),notice=document.querySelector('#booking-notice');
 function updateNotice(){
  const now=Date.now(),first=EliteBookingTime.nextStart([...timeField.options].map(option=>option.value),now);
  const earliest=first?new Intl.DateTimeFormat('en-CA',{timeZone:EliteBookingTime.ZONE,weekday:'long',month:'long',day:'numeric',hour:'numeric',minute:'2-digit',timeZoneName:'short'}).format(new Date(first.ms)):'';
  const help='We need at least 72 hours to arrange your cleaner. '+(earliest?'The earliest time you can request is '+earliest+'.':'Please choose a later date and time.');
  dateField.min=EliteBookingTime.localParts(now+EliteBookingTime.NOTICE).date;
  // Preserve the chosen time so an invalid selection can be explained, never silently cleared.
  for(const option of timeField.options)option.disabled=false;
  const earlyDate=Boolean(dateField.value&&dateField.value<dateField.min);
  const earlyTime=Boolean(!earlyDate&&dateField.value&&timeField.value&&!EliteBookingTime.validate(dateField.value,timeField.value,now));
  dateField.setCustomValidity(earlyDate?help:'');timeField.setCustomValidity(earlyTime?help:'');
  dateField.setAttribute('aria-invalid',String(earlyDate));timeField.setAttribute('aria-invalid',String(earlyTime));
  notice.textContent=(earlyDate||earlyTime?'That date or time is too soon. ':'')+help+' Your preferred time is subject to availability.';
  notice.classList.toggle('error',earlyDate||earlyTime);
  const error=document.querySelector('#form-error');if(error.dataset.bookingNotice==='true'&&!earlyDate&&!earlyTime){error.textContent='';delete error.dataset.bookingNotice;}
  return {valid:!earlyDate&&!earlyTime,message:help};
 }
 dateField.addEventListener('input',updateNotice);timeField.addEventListener('change',updateNotice);dateField.addEventListener('change',updateNotice);
 document.querySelector('#next').addEventListener('click',()=>{const result=updateNotice();if(!result.valid){const error=document.querySelector('#form-error');error.dataset.bookingNotice='true';}},true);
 form.addEventListener('refresh-booking-notice',updateNotice);updateNotice();
}

if(form?.dataset.bookingEnabled==='true'){
 const send=document.querySelector('#send-request'),status=document.querySelector('#send-status');const requestId=crypto.randomUUID();let pending=false;document.querySelector('#request-reference').value=requestId;
 send?.addEventListener('click',async()=>{if(pending)return;
 const date=form.elements.namedItem('Preferred date').value,time=form.elements.namedItem('Preferred time').value;
 if(!EliteBookingTime.validate(date,time)){form.dispatchEvent(new Event('refresh-booking-notice'));form.dispatchEvent(new CustomEvent('booking-time-invalid',{detail:document.querySelector('#booking-notice').textContent}));return;}
 pending=true;send.disabled=true;status.textContent='Sending your request…';document.querySelector('#notification-email').value=form.elements.namedItem('Email').value;
 const data=new FormData(form),extras=data.getAll('Requested extras');data.delete('Requested extras');if(extras.length)data.set('Requested extras',extras.join(', '));
 try{const response=await fetch('/',{method:'POST',headers:{'Content-Type':'application/x-www-form-urlencoded'},body:new URLSearchParams(data).toString()});if(!response.ok)throw new Error('We could not confirm delivery. Please contact us before resubmitting.');
 document.querySelector('#success-heading').textContent='Thanks for trusting Elite Clean Pro!';document.querySelector('.form-success > .quiet').textContent='Your request is in. We review your scope and cleaner availability, then send a written quote for you to accept. Your appointment is confirmed separately. Check your email for next steps.';document.querySelector('#request-summary').hidden=true;status.replaceChildren();const help=document.createElement('p');help.append('Have questions? Email ');const emailLink=document.createElement('a');emailLink.href='mailto:hello@elitecleanpro.ca';emailLink.textContent='hello@elitecleanpro.ca';help.append(emailLink,'.');const reference=document.createElement('p');reference.className='quiet';reference.textContent='Your request reference: '+requestId;status.append(help,reference);send.hidden=true;document.querySelector('#edit-request').hidden=true;document.querySelector('.form-success .review-tag').textContent='REQUEST RECEIVED';document.querySelector('#success-heading').focus();}
 catch(error){status.textContent=error.message+' Reference: '+requestId+' · hello@elitecleanpro.ca';send.disabled=false;pending=false;}
 });
}

// Keep the mobile booking action available after the hero, without covering the final CTA.
const stickyBooking=document.querySelector('.mobile-booking'),bookingHero=document.querySelector('#booking-hero');
if(stickyBooking&&bookingHero&&'IntersectionObserver' in window){
 let pastHero=false,atClosing=false;
 const syncSticky=()=>{stickyBooking.hidden=!pastHero||atClosing;document.body.classList.toggle('has-mobile-booking',!stickyBooking.hidden)};
 const stickyObserver=new IntersectionObserver(entries=>{for(const entry of entries){if(entry.target===bookingHero)pastHero=!entry.isIntersecting&&entry.boundingClientRect.bottom<=0;else atClosing=entry.isIntersecting;}syncSticky();});
 stickyObserver.observe(bookingHero);const closing=document.querySelector('.closing');if(closing)stickyObserver.observe(closing);
}
