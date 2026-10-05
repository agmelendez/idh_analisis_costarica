// Pestañas internas accesibles (ARIA) con sincronización de hash.
(function(){
  document.querySelectorAll('[data-tabs]').forEach(function(root){
    var tabs=[].slice.call(root.querySelectorAll('[role=tab]'));
    function show(id,push){
      tabs.forEach(function(t){var on=t.getAttribute('aria-controls')===id;t.setAttribute('aria-selected',on);t.tabIndex=on?0:-1;
        var p=document.getElementById(t.getAttribute('aria-controls'));if(p)p.hidden=!on;});
      if(push&&history.replaceState)history.replaceState(null,'','#'+id);
    }
    tabs.forEach(function(t,i){
      t.addEventListener('click',function(){show(t.getAttribute('aria-controls'),true)});
      t.addEventListener('keydown',function(e){
        var j=null;if(e.key==='ArrowRight')j=(i+1)%tabs.length;if(e.key==='ArrowLeft')j=(i-1+tabs.length)%tabs.length;
        if(j!==null){e.preventDefault();tabs[j].focus();show(tabs[j].getAttribute('aria-controls'),true)}
      });
    });
    var h=location.hash.slice(1);var ids=tabs.map(function(t){return t.getAttribute('aria-controls')});
    show(ids.indexOf(h)>=0?h:ids[0],false);
  });
})();
