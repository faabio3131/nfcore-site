(function(){
  var m=document.getElementById('burger'),mn=document.getElementById('menu');
  if(m)m.addEventListener('click',function(){mn.classList.toggle('open')});

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
