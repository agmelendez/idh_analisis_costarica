// Explorador cantonal: mapa coroplético, tabla ordenable y dispersión (Spearman). Sin dependencias externas.
(function(){
  var VARS=[ // [clave, etiqueta, tipo, grupo, estudio]
    ['IDH_2024','IDH (2024)','num','Desarrollo humano (PNUD)'],['IDHD_2024','IDH ajustado por desigualdad (2024)','num','Desarrollo humano (PNUD)'],
    ['IDG_2024','IDG (2024; 1 = paridad)','num','Desarrollo humano (PNUD)'],['IPM_2024','IPM (2024)','num','Desarrollo humano (PNUD)'],
    ['ISC_2025','ISC (2025)','num','Seguridad (PNUD)'],['IVDAC_2024','IVDAC (2024)','num','Seguridad (PNUD)'],
    ['ICC_2024','ICC (2024)','num','Competitividad (UCR)'],['Pilar_Economico','ICC · pilar Económico','num','Competitividad (UCR)'],['Pilar_Gobierno','ICC · pilar Gobierno','num','Competitividad (UCR)'],
    ['Pilar_Empresarial','ICC · pilar Empresarial','num','Competitividad (UCR)'],['Pilar_Infraestructura','ICC · pilar Infraestructura','num','Competitividad (UCR)'],['Pilar_Laboral','ICC · pilar Laboral','num','Competitividad (UCR)'],
    ['Pilar_Innovacion','ICC · pilar Innovación','num','Competitividad (UCR)'],['Pilar_CalidadVida','ICC · pilar Calidad de vida','num','Competitividad (UCR)'],
    ['PIB_percapita_2022','PIB per cápita (2022; mill. ₡)','num','Producción y empresas (BCCR)'],['UJ_por_1000hab_2024','Unidades jurídicas por 1.000 hab. (2024)','num','Producción y empresas (BCCR)'],
    ['pob_2024','Población (2024)','num','Demografía y territorio'],['area_km2','Área (km²)','num','Demografía y territorio'],
    ['E','Eje económico-empresarial (informe, puntaje rotado)','num','Resultados derivados'],['S','Eje de seguridad (informe, puntaje rotado)','num','Resultados derivados'],
    ['Q_informe','Cuadrante — informe v3 (escala original)','cat','Resultados derivados'],['Q_articulo','Cuadrante — artículo (logaritmos)','cat','Resultados derivados'],
    ['K3','Conglomerado K-means k=3 — artículo','cat','Resultados derivados'],['IDH_cat','Categoría IDH, 5 rangos de Jenks — artículo','cat','Resultados derivados'],
    ['provincia','Provincia','cat','Territorio'],['region_bccr','Región BCCR','cat','Territorio']
  ];
  var CATLAB={IDH_cat:{0:'Muy Bajo',1:'Bajo',2:'Medio',3:'Alto',4:'Muy Alto'}};
  var OKABE=['#0072B2','#009E73','#D55E00','#E69F00','#CC79A7','#56B4E9','#F0E442','#999999'];
  var BLUES=['#DCE9F7','#A9C8EC','#6FA3DA','#3A78BE','#12468A']; // secuencial, orden creciente
  var data,geo,byCod={},cur='IDH_2024',selCod=null,sortKey='canton',sortAsc=true;
  var $=function(id){return document.getElementById(id)};
  var fmt=function(v,k){if(v===null||v===undefined||v===''||(typeof v==='number'&&isNaN(v)))return '—';
    if(typeof v==='number'){var a=Math.abs(v);return v.toLocaleString('es-CR',{maximumFractionDigits:a>=1000?0:(a>=100?1:3)})}return v};
  var meta=function(k){return VARS.filter(function(v){return v[0]===k})[0]};
  var lab=function(k,v){if(v===null||v===undefined)return '—';return CATLAB[k]?CATLAB[k][v]:String(v)};

  Promise.resolve(window.__CANTONES&&window.__GEO?[window.__CANTONES,window.__GEO]:Promise.all([fetch('assets/data/cantones.json').then(function(r){return r.json()}),fetch('data/geo/cri_cantones_simplificado.geojson').then(function(r){return r.json()})])).then(function(r){
    data=r[0];geo=r[1];data.forEach(function(d){byCod[String(d.cod_canton)]=d});init();
  }).catch(function(e){$('map').outerHTML='<p class="note warn">No se pudieron cargar los datos del explorador ('+e+'). Si abre el archivo directamente desde el disco, sírvalo con un servidor local: <code>python -m http.server</code>.</p>'});

  function opts(sel,onlyNum){
    var g={};VARS.forEach(function(v){if(onlyNum&&v[2]!=='num')return;(g[v[3]]=g[v[3]]||[]).push(v)});
    sel.innerHTML=Object.keys(g).map(function(k){return '<optgroup label="'+k+'">'+g[k].map(function(v){return '<option value="'+v[0]+'">'+v[1]+'</option>'}).join('')+'</optgroup>'}).join('');
  }
  function init(){
    opts($('var'),false);opts($('xv'),true);opts($('yv'),true);$('var').value=cur;$('xv').value='ICC_2024';$('yv').value='IDH_2024';
    $('var').onchange=function(){cur=this.value;draw()};$('xv').onchange=$('yv').onchange=scatter;
    $('q').oninput=table;
    drawMap();draw();scatter();
  }
  // Proyección equirrectangular con corrección por latitud
  var P={};
  function bounds(){var xs=[],ys=[];geo.features.forEach(function(f){rings(f).forEach(function(rg){rg.forEach(function(c){xs.push(c[0]);ys.push(c[1])})})});
    var x0=Math.min.apply(null,xs),x1=Math.max.apply(null,xs),y0=Math.min.apply(null,ys),y1=Math.max.apply(null,ys),k=Math.cos(((y0+y1)/2)*Math.PI/180);
    P={x0:x0,y0:y0,k:k,w:(x1-x0)*k,h:y1-y0};}
  function polys(f){var g=f.geometry,a=g.type==='Polygon'?[g.coordinates]:g.coordinates;return a.filter(function(pl){return pl[0][0][0]>-86.6})} // excluye la Isla del Coco
  function rings(f){return [].concat.apply([],polys(f))}
  function path(f){return polys(f).map(function(poly){return poly.map(function(rg){return 'M'+rg.map(function(c){return ((c[0]-P.x0)*P.k).toFixed(4)+','+((P.h-(c[1]-P.y0))).toFixed(4)}).join('L')+'Z'}).join('')}).join('')}
  function drawMap(){bounds();var s=$('map');s.setAttribute('viewBox','-0.05 -0.05 '+(P.w+0.1).toFixed(3)+' '+(P.h+0.1).toFixed(3));
    s.innerHTML=geo.features.map(function(f){var c=String(f.properties.cod_canton);
      return '<path data-c="'+c+'" d="'+path(f)+'" tabindex="0" role="img" aria-label="'+f.properties.canton+'"></path>'}).join('');
    var tip=$('tip');
    [].forEach.call(s.querySelectorAll('path'),function(p){
      p.addEventListener('mousemove',function(e){var d=byCod[p.dataset.c];tip.style.display='block';tip.style.left=(e.clientX+14)+'px';tip.style.top=(e.clientY+14)+'px';
        tip.innerHTML='<b>'+(d?d.canton:p.getAttribute('aria-label'))+'</b><br>'+meta(cur)[1]+': '+(d?(meta(cur)[2]==='cat'?lab(cur,d[cur]):fmt(d[cur])):'—')});
      p.addEventListener('mouseleave',function(){tip.style.display='none'});
      p.addEventListener('click',function(){select(p.dataset.c)});
      p.addEventListener('keydown',function(e){if(e.key==='Enter'||e.key===' '){e.preventDefault();select(p.dataset.c)}});
    });
  }
  function colors(){ // devuelve {cod:color}, leyenda
    var m=meta(cur),out={},leg=[];
    if(m[2]==='cat'){var cats=[];data.forEach(function(d){var v=d[cur];if(v!==null&&v!==undefined&&cats.indexOf(v)<0)cats.push(v)});cats.sort(function(a,b){return String(a)<String(b)?-1:1});
      cats.forEach(function(c,i){leg.push([OKABE[i%OKABE.length],lab(cur,c)]);data.forEach(function(d){if(d[cur]===c)out[String(d.cod_canton)]=OKABE[i%OKABE.length]})});}
    else{var v=data.map(function(d){return d[cur]}).filter(function(x){return typeof x==='number'&&!isNaN(x)}).sort(function(a,b){return a-b});
      var q=[1,2,3,4].map(function(i){return v[Math.min(v.length-1,Math.floor(i*v.length/5))]});
      data.forEach(function(d){var x=d[cur];if(typeof x!=='number'||isNaN(x))return;var k=0;while(k<4&&x>=q[k])k++;out[String(d.cod_canton)]=BLUES[k]});
      var lo=v[0],hi=v[v.length-1],e=[lo].concat(q,[hi]);for(var i=0;i<5;i++)leg.push([BLUES[i],fmt(e[i])+' – '+fmt(e[i+1])]);
      leg.push(['#F2F2F2','n='+v.length+' (quintiles)']);}
    return {c:out,leg:leg};
  }
  function draw(){var r=colors();
    [].forEach.call($('map').querySelectorAll('path'),function(p){p.setAttribute('fill',r.c[p.dataset.c]||'#F2F2F2');var on=p.dataset.c===selCod;p.classList.toggle('sel',on);if(on)p.parentNode.appendChild(p)});
    $('legend').innerHTML=r.leg.map(function(l){return '<span><i style="background:'+l[0]+'"></i>'+l[1]+'</span>'}).join('')+'<span><i style="background:#F2F2F2"></i>sin dato</span>';
    $('maptitle').textContent=meta(cur)[1];table();}
  function select(c){selCod=c;var d=byCod[c];draw();
    if(!d){$('detail').innerHTML='Sin datos para este cantón.';return}
    var keys=['IDH_2024','IDHD_2024','IPM_2024','ICC_2024','PIB_percapita_2022','UJ_por_1000hab_2024','ISC_2025','IVDAC_2024','Q_informe','Q_articulo','K3'];
    $('detail').innerHTML='<b style="font-size:1.05rem">'+d.canton+'</b> <span class="badge">'+d.provincia+'</span><br>'+
      keys.map(function(k){var m=meta(k);return m[1]+': <b>'+(m[2]==='cat'?lab(k,d[k]):fmt(d[k]))+'</b>'}).join(' · ');
    scatter();}
  function table(){
    var q=($('q').value||'').toLowerCase(),m=meta(cur);
    var rows=data.filter(function(d){return !q||(d.canton+' '+d.provincia).toLowerCase().indexOf(q)>=0});
    rows.sort(function(a,b){var x=a[sortKey],y=b[sortKey];if(x===null||x===undefined)return 1;if(y===null||y===undefined)return -1;var c=(typeof x==='number')?x-y:String(x).localeCompare(String(y),'es');return sortAsc?c:-c});
    var cols=[['canton','Cantón'],['provincia','Provincia'],[cur,m[1]]];
    $('tbl').innerHTML='<thead><tr>'+cols.map(function(c){return '<th scope="col" '+(c[0]===cur?'class="num"':'')+' aria-sort="'+(sortKey===c[0]?(sortAsc?'ascending':'descending'):'none')+'"><button type="button" data-k="'+c[0]+'">'+c[1]+(sortKey===c[0]?(sortAsc?' ▲':' ▼'):'')+'</button></th>'}).join('')+'</tr></thead><tbody>'+
      rows.map(function(d){return '<tr data-c="'+d.cod_canton+'"><td>'+d.canton+'</td><td>'+d.provincia+'</td><td class="num">'+(m[2]==='cat'?lab(cur,d[cur]):fmt(d[cur]))+'</td></tr>'}).join('')+'</tbody>';
    [].forEach.call($('tbl').querySelectorAll('th button'),function(b){b.onclick=function(){if(sortKey===b.dataset.k)sortAsc=!sortAsc;else{sortKey=b.dataset.k;sortAsc=true}table()}});
    [].forEach.call($('tbl').querySelectorAll('tbody tr'),function(t){t.style.cursor='pointer';t.onclick=function(){select(t.dataset.c)}});
    $('count').textContent=rows.length+' de '+data.length+' cantones';
  }
  // Spearman con rangos promedio
  function ranks(a){var idx=a.map(function(v,i){return [v,i]}).sort(function(x,y){return x[0]-y[0]}),r=new Array(a.length),i=0;
    while(i<idx.length){var j=i;while(j+1<idx.length&&idx[j+1][0]===idx[i][0])j++;var avg=(i+j)/2+1;for(var k=i;k<=j;k++)r[idx[k][1]]=avg;i=j+1}return r}
  function pearson(x,y){var n=x.length,mx=x.reduce(function(a,b){return a+b},0)/n,my=y.reduce(function(a,b){return a+b},0)/n,sxy=0,sxx=0,syy=0;
    for(var i=0;i<n;i++){sxy+=(x[i]-mx)*(y[i]-my);sxx+=Math.pow(x[i]-mx,2);syy+=Math.pow(y[i]-my,2)}return sxy/Math.sqrt(sxx*syy)}
  function scatter(){
    var xk=$('xv').value,yk=$('yv').value,pts=data.filter(function(d){return typeof d[xk]==='number'&&typeof d[yk]==='number'&&!isNaN(d[xk])&&!isNaN(d[yk])});
    var W=520,H=380,m={l:56,r:26,t:14,b:44},xs=pts.map(function(d){return d[xk]}),ys=pts.map(function(d){return d[yk]});
    var x0=Math.min.apply(null,xs),x1=Math.max.apply(null,xs),y0=Math.min.apply(null,ys),y1=Math.max.apply(null,ys);
    var px=function(v){return m.l+(v-x0)/(x1-x0||1)*(W-m.l-m.r)},py=function(v){return H-m.b-(v-y0)/(y1-y0||1)*(H-m.t-m.b)};
    var rho=pearson(ranks(xs),ranks(ys)),g='';
    for(var i=0;i<=4;i++){var vx=x0+(x1-x0)*i/4,vy=y0+(y1-y0)*i/4;
      g+='<line x1="'+px(vx)+'" x2="'+px(vx)+'" y1="'+m.t+'" y2="'+(H-m.b)+'" stroke="#8883" /><text x="'+px(vx)+'" y="'+(H-m.b+16)+'" font-size="10" text-anchor="middle" fill="currentColor">'+fmt(vx)+'</text>';
      g+='<line y1="'+py(vy)+'" y2="'+py(vy)+'" x1="'+m.l+'" x2="'+(W-m.r)+'" stroke="#8883" /><text x="'+(m.l-6)+'" y="'+(py(vy)+3)+'" font-size="10" text-anchor="end" fill="currentColor">'+fmt(vy)+'</text>';}
    var dots=pts.map(function(d){var c=String(d.cod_canton),s=c===selCod;return '<circle cx="'+px(d[xk]).toFixed(1)+'" cy="'+py(d[yk]).toFixed(1)+'" r="'+(s?7:4.2)+'" fill="'+(s?'#FF944E':'#4169E1')+'" fill-opacity="'+(s?1:.7)+'" stroke="'+(s?'#1F3864':'#fff')+'" stroke-width="'+(s?2:.6)+'" data-c="'+c+'"><title>'+d.canton+'</title></circle>'}).join('');
    $('scatter').setAttribute('viewBox','0 0 '+W+' '+H);
    $('scatter').innerHTML=g+dots+'<text x="'+(W/2)+'" y="'+(H-6)+'" font-size="11" text-anchor="middle" fill="currentColor">'+meta(xk)[1]+'</text><text transform="rotate(-90)" x="'+(-H/2)+'" y="13" font-size="11" text-anchor="middle" fill="currentColor">'+meta(yk)[1]+'</text>';
    [].forEach.call($('scatter').querySelectorAll('circle'),function(c){c.style.cursor='pointer';c.onclick=function(){select(c.dataset.c)}});
    $('rho').innerHTML='Spearman ρ = <b>'+rho.toFixed(3).replace('.',',')+'</b> · n = '+pts.length+' cantones con ambos datos. <small>Descriptivo: los 84 cantones son un censo, no una muestra; ρ no se acompaña de inferencia ni implica causalidad.</small>';
  }
})();
