// Reading progress bar
(function() {
  const bar = document.getElementById('progressBar');
  if (!bar) return;
  window.addEventListener('scroll', function() {
    const h = document.documentElement;
    const pct = (h.scrollTop / (h.scrollHeight - h.clientHeight)) * 100;
    bar.style.width = Math.min(pct, 100) + '%';
  }, { passive: true });
})();

// Back to top button visibility
(function() {
  const btn = document.getElementById('backToTop');
  if (!btn) return;
  window.addEventListener('scroll', function() {
    if (window.scrollY > 800) {
      btn.classList.add('visible');
    } else {
      btn.classList.remove('visible');
    }
  }, { passive: true });
})();

// Enhancement 5: IntersectionObserver for .reveal elements
(function() {
  var els = document.querySelectorAll('.reveal');
  if (!els.length || !('IntersectionObserver' in window)) {
    // Fallback: make everything visible if IntersectionObserver not supported
    els.forEach(function(el) { el.classList.add('visible'); });
    return;
  }
  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });
  els.forEach(function(el) { observer.observe(el); });
})();

// Enhancement 5: Count-up animation for .count-up elements
(function() {
  var els = document.querySelectorAll('.count-up');
  if (!els.length || !('IntersectionObserver' in window)) return;

  function animateCount(el) {
    var target = el.getAttribute('data-target');
    if (!target) return;
    // Parse number — handle percentages, commas, decimals
    var raw = target.replace(/[^0-9.\-]/g, '');
    var num = parseFloat(raw);
    if (isNaN(num)) return;
    var prefix = target.match(/^[^0-9.\-]*/)[0] || '';
    var suffix = target.match(/[^0-9.\-]*$/)[0] || '';
    var isInt = num === Math.floor(num);
    var duration = 800;
    var start = performance.now();

    function step(now) {
      var progress = Math.min((now - start) / duration, 1);
      // Ease-out cubic
      var ease = 1 - Math.pow(1 - progress, 3);
      var current = num * ease;
      el.textContent = prefix + (isInt ? Math.floor(current).toLocaleString() : current.toFixed(1)) + suffix;
      if (progress < 1) requestAnimationFrame(step);
    }
    el.textContent = prefix + '0' + suffix;
    requestAnimationFrame(step);
  }

  var observer = new IntersectionObserver(function(entries) {
    entries.forEach(function(entry) {
      if (entry.isIntersecting) {
        animateCount(entry.target);
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });
  els.forEach(function(el) { observer.observe(el); });
})();
