(function(root){
const ZONE='America/Edmonton',NOTICE=72*60*60*1000;
function localParts(ms){const parts=new Intl.DateTimeFormat('en-CA',{timeZone:ZONE,year:'numeric',month:'2-digit',day:'2-digit',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).formatToParts(new Date(ms));const p=Object.fromEntries(parts.map(x=>[x.type,x.value]));return {date:`${p.year}-${p.month}-${p.day}`,time:`${p.hour}:${p.minute}`};}
function utcFor(date,time){if(!/^\d{4}-\d{2}-\d{2}$/.test(date)||!/^\d{2}:\d{2}$/.test(time))return null;const guess=Date.parse(`${date}T${time}:00Z`);if(!Number.isFinite(guess))return null;for(let offset=5;offset<=8;offset++){const ms=guess+offset*3600000,p=localParts(ms);if(p.date===date&&p.time===time)return ms;}return null;}
function validate(date,time,now=Date.now()){const ms=utcFor(date,time);return ms!==null&&ms>=now+NOTICE;}
root.EliteBookingTime={ZONE,NOTICE,localParts,utcFor,validate};if(typeof module!=='undefined')module.exports=root.EliteBookingTime;
})(typeof window!=='undefined'?window:globalThis);
