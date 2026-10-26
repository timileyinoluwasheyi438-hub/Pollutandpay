(function () {
  var els = document.querySelectorAll('[data-a]');
  var reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce || !('IntersectionObserver' in window)) { els.forEach(function (e) { e.classList.add('in'); }); }
  else {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (x) { if (x.isIntersecting) { x.target.classList.add('in'); io.unobserve(x.target); } });
    }, { threshold: 0.12 });
    els.forEach(function (e) { io.observe(e); });
  }
  var rt = document.getElementById('rates'), cat = document.getElementById('id_category'), qty = document.getElementById('id_quantity'), out = document.getElementById('levy');
  if (rt && cat && qty && out && rt.tagName === 'SCRIPT') {
    var rates = JSON.parse(rt.textContent);
    var calc = function () {
      var v = (rates[cat.value] || 0) * (parseFloat(qty.value) || 0);
      out.textContent = '₦' + v.toLocaleString('en-NG', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    };
    cat.addEventListener('change', calc); qty.addEventListener('input', calc); calc();
  }
  var sl = document.querySelectorAll('.rv blockquote'), i = 0;
  document.querySelectorAll('[data-rv]').forEach(function (b) { b.addEventListener('click', function () {
    sl[i].classList.remove('on'); i = (i + +b.dataset.rv + sl.length) % sl.length; sl[i].classList.add('on'); }); });
  document.querySelectorAll('nav a').forEach(function (a) { a.addEventListener('click', function () { document.body.classList.remove('open'); }); });
})();
