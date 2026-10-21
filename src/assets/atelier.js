// Enhance the crawlable service content only when JavaScript is available.
const choices=[...document.querySelectorAll('[data-service]')];
function chooseService(key){
 choices.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.service===key)));
 document.querySelectorAll('.service-panel').forEach(p=>p.hidden=p.id!=='panel-'+key);
 document.querySelectorAll('.hero-copy .button,.closing .button,.mobile-booking .button,.header .button,.footer a[href^="/book/"]').forEach(a=>a.href='/book/?service='+key);
 document.querySelectorAll('.service-price,.hero-copy .text-link').forEach(a=>a.href='/pricing/?service='+key);
}
choices.forEach((b,i)=>{b.addEventListener('click',()=>chooseService(b.dataset.service));b.addEventListener('keydown',e=>{if(['ArrowDown','ArrowRight','ArrowUp','ArrowLeft','Home','End'].includes(e.key)){e.preventDefault();const n=e.key==='Home'?0:e.key==='End'?2:(i+(['ArrowDown','ArrowRight'].includes(e.key)?1:2))%3;choices[n].focus();chooseService(choices[n].dataset.service)}})});
const priceService=document.querySelector('#estimate-form [name="service"]');
if(priceService){const value=new URLSearchParams(location.search).get('service');if(['regular','deep','moveout'].includes(value)){priceService.value=value;priceService.dispatchEvent(new Event('change',{bubbles:true}))}}
// Keep the keyboard focus on the changed content when moving through form steps.
if(form&&!form.dataset.bookingEnabled.includes('true')){
 const review=document.querySelector('#form-success');
 const test=document.createElement('button');test.type='button';test.className='button';test.textContent='Test request delivery';
 const state=document.createElement('p');state.setAttribute('role','status');state.className='quiet';
 const fail=document.createElement('label');fail.className='checkbox-line';fail.innerHTML='<input type="checkbox"> Simulate a delivery failure';
 review.append(fail,test,state);
 test.addEventListener('click',()=>{test.disabled=true;state.textContent='Sending test request…';setTimeout(()=>{test.disabled=false;state.textContent=fail.querySelector('input').checked?'Test delivery failed. Your details are kept here. Try again or email hello@elitecleanpro.ca. No request was sent.':'Test complete. In the live flow, your request would now be received for review. This preview sent nothing and did not book an appointment.'},350)});
}
