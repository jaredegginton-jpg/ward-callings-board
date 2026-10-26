// Run in the LCR Organizations page (https://lcr.churchofjesuschrist.org/mlt/orgs?lang=eng)
// after it has fully loaded. Produces one line per calling:
//   Organization|Group|Calling|Last, First|Sustained date
// It then replaces the page's <main> with the lines so the page text can be read in one go
// (reload the page afterwards).
const nodes=[...document.querySelectorAll('main h2, main h3, main h4, main table')];
let h2='',h3='',h4='';const rows=[];
for(const n of nodes){const tg=n.tagName;
 if(tg==='H2'){h2=n.textContent.trim();h3='';h4='';continue}
 if(tg==='H3'){h3=n.textContent.trim();h4='';continue}
 if(tg==='H4'){h4=n.textContent.trim();continue}
 for(const tr of n.querySelectorAll('tbody tr')){const td=[...tr.querySelectorAll('td')].map(c=>c.innerText.replace(/\s+/g,' ').trim());
  if(td.length<2)continue;
  let calling=td[0].replace(/ Custom Calling$/,'');let name=td[1]||'';let sus=td[2]||'';
  if(/Calling Vacant/.test(td[0]+' '+name)){name='';sus='';calling=calling.replace(/ ?Calling Vacant/,'')}
  rows.push([h2,[h3,h4].filter(Boolean).join(' › '),calling,name,sus]);}}
const m=document.querySelector('main');m.innerHTML='';const p=document.createElement('pre');
p.textContent='ROWSTART\n'+rows.map(r=>r.join('|')).join('\n')+'\nROWEND';m.appendChild(p);
rows.length
