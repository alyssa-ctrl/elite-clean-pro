(function(root){
const config={bands:['Under 1,000 sq. ft.','1,000–1,499 sq. ft.','1,500–1,999 sq. ft.','2,000–2,499 sq. ft.'],base:{regular:[150,190,230,280],deep:[220,280,340,410],moveout:[300,360,420,500]},bath:{regular:[25,15],deep:[35,20],moveout:[40,25]},extras:{oven:40,fridge:35,cabinets:45,windows:10,hair:25}};
function calculate(v){
 const service=v.service,band=Number(v.band),full=Number(v.full),half=Number(v.half),windows=Number(v.windows||0);
 if(!config.base[service]||v.band===''||!Number.isInteger(band)||band<0||band>3||!Number.isInteger(full)||full<1||full>4||!Number.isInteger(half)||half<0||half>3||!Number.isInteger(windows)||windows<0||windows>20||!['typical','moderate'].includes(v.condition)||v.basement==='excluded')return {manual:true};
 const lines=[{label:config.bands[band]+' · '+({regular:'regular',deep:'deep',moveout:'move-out'}[service]),amount:config.base[service][band]}];
 if(full>1)lines.push({label:`${full-1} additional full bathroom(s)`,amount:(full-1)*config.bath[service][0]});
 if(half)lines.push({label:`${half} half bathroom(s)`,amount:half*config.bath[service][1]});
 const labor=lines.reduce((n,l)=>n+l.amount,0);
 if(v.condition==='moderate')lines.push({label:'Extra buildup allowance (20% of base + bathrooms)',amount:labor*.2});
 if(service==='regular'&&v.established&&['weekly','biweekly'].includes(v.frequency)){const rate=v.frequency==='weekly'?.1:.05;lines.push({label:'Established '+v.frequency+' schedule adjustment',amount:-labor*rate});}
 for(const key of ['oven','fridge','cabinets'])if(v[key]&&service!=='moveout')lines.push({label:({oven:'Inside oven',fridge:'Inside fridge',cabinets:'Empty kitchen cabinet interiors'})[key],amount:config.extras[key]});
 if(service==='moveout')lines.push({label:'One oven + one fridge + empty kitchen cabinet interiors',amount:0});
 if(windows)lines.push({label:`${windows} accessible interior window pane(s)`,amount:windows*config.extras.windows});
 if(v.hair)lines.push({label:'Significant pet-hair removal allowance',amount:config.extras.hair});
 const subtotal=Math.ceil(lines.reduce((n,l)=>n+l.amount,0)/5)*5;
 return {manual:false,subtotal,low:subtotal,high:Math.ceil(subtotal*1.15/5)*5,lines};
}
root.EliteEstimate={config,calculate};if(typeof module!=='undefined')module.exports=root.EliteEstimate;
})(typeof window!=='undefined'?window:globalThis);
