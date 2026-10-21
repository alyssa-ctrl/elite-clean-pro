const fs=require('node:fs');
if(process.env.SITE_MODE==='live'){
 if(process.env.BOOKING_ENABLED!=='true')throw new Error('Live release requires a working, tested booking connection.');
 fs.rmSync('_site/review',{recursive:true,force:true});
 fs.writeFileSync('_site/robots.txt','User-agent: *\nAllow: /\nDisallow: /review/\nSitemap: https://elitecleanpro.ca/sitemap.xml\n');
 const pages=['index.html','book/index.html','pricing/index.html','privacy/index.html'];
 for(const file of pages){const html=fs.readFileSync('_site/'+file,'utf8');if(html.includes('REVIEW PREVIEW')||html.includes('noindex,nofollow'))throw new Error('Preview markers found in '+file);}
}
