(function(){
  var m=document.getElementById('burger'),mn=document.getElementById('menu');
  if(m&&mn){
    var closeMenu=function(){
      mn.classList.remove('open');
      m.setAttribute('aria-expanded','false');
      m.setAttribute('aria-label','Abrir menu de navegação');
    };
    m.addEventListener('click',function(){
      var open=mn.classList.toggle('open');
      m.setAttribute('aria-expanded',open?'true':'false');
      m.setAttribute('aria-label',open?'Fechar menu de navegação':'Abrir menu de navegação');
    });
    mn.addEventListener('click',function(e){
      if(e.target.closest('a'))closeMenu();
    });
    document.addEventListener('keydown',function(e){
      if(e.key==='Escape'&&mn.classList.contains('open')){closeMenu();m.focus();}
    });
    document.addEventListener('click',function(e){
      if(mn.classList.contains('open')&&!mn.contains(e.target)&&!m.contains(e.target))closeMenu();
    });
  }

  // Fluxo de autoridade: cinco abas acessíveis, com painel de detalhes correspondente.
  var flowTabs=Array.prototype.slice.call(document.querySelectorAll('[data-flow-tab]'));
  if(flowTabs.length){
    var selectFlow=function(index,focus){
      flowTabs.forEach(function(tab,i){
        var current=i===index;
        tab.classList.toggle('active',current);
        tab.setAttribute('aria-selected',current?'true':'false');
        tab.setAttribute('tabindex',current?'0':'-1');
        var panel=document.getElementById(tab.getAttribute('aria-controls'));
        if(panel)panel.hidden=!current;
      });
      if(focus)flowTabs[index].focus();
    };
    flowTabs.forEach(function(tab,i){
      tab.addEventListener('click',function(){selectFlow(i,false);});
      tab.addEventListener('keydown',function(e){
        var n=i;
        if(e.key==='ArrowRight'||e.key==='ArrowDown')n=(i+1)%flowTabs.length;
        else if(e.key==='ArrowLeft'||e.key==='ArrowUp')n=(i+flowTabs.length-1)%flowTabs.length;
        else if(e.key==='Home')n=0;
        else if(e.key==='End')n=flowTabs.length-1;
        else return;
        e.preventDefault();
        selectFlow(n,true);
      });
    });
  }

  // Contagem regressiva (guia da reforma tributária). Sem JavaScript, fica só o texto com a data.
  var cd=document.getElementById('cd');
  if(cd){
    var to=new Date(cd.getAttribute('data-to')).getTime(),n=cd.querySelector('.cd-n'),
        set=function(u,v){var e=cd.querySelector('[data-u='+u+']');if(e)e.textContent=v};
    var tick=function(){
      var s=Math.max(0,Math.floor((to-Date.now())/1000));
      if(!s){n.hidden=true;cd.querySelector('.cd-l').textContent='A CBS já está em vigor.';return false}
      set('d',Math.floor(s/86400));set('h',Math.floor(s%86400/3600));set('m',Math.floor(s%3600/60));return true;
    };
    if(!isNaN(to)&&tick()){n.hidden=false;setInterval(tick,30000)}
  }

  // Filtro dos materiais por público. Sem JavaScript, todos aparecem.
  var chips=document.querySelectorAll('.chips button');
  if(chips.length)chips.forEach(function(b){
    b.addEventListener('click',function(){
      var f=b.getAttribute('data-f');
      chips.forEach(function(x){x.setAttribute('aria-pressed',x===b?'true':'false')});
      document.querySelectorAll('.mat').forEach(function(c){
        c.hidden=!(f==='todos'||(c.getAttribute('data-a')||'').split(' ').indexOf(f)>-1);
      });
    });
  });
})();
