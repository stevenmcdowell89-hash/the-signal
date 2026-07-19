/* mx-motion.js — WP-5 motion controller (Law 5). data-mx issues only; the
   stitcher swaps it in for legacy script.js on the mx path. JS-off = 100%
   content (initial-hidden CSS is gated on [data-mx-motion-ready], stamped
   only here); reduced-motion → no-op (CSS gate is belt #2); IO reveals add
   .is-in + data-mx-inview, stagger via --mx-i; no scroll-jacking; motion
   attaches to furniture, never prose. */
(function () {
  'use strict';
  var d = document, root = d.documentElement, rm = null;

  function $$(sel, ctx) {
    return Array.prototype.slice.call((ctx || d).querySelectorAll(sel));
  }
  function reduced() { return rm ? rm.matches : false; }

  function init() {
    var body = d.body;
    if (!body || !body.hasAttribute('data-mx')) return;
    var tier = body.getAttribute('data-motion');
    if (tier !== 'tier0' && tier !== 'tier1' && tier !== 'tier2') return;
    rm = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;
    if (reduced()) return;
    if (rm && rm.addEventListener) {
      rm.addEventListener('change', function (e) {
        if (e.matches) root.removeAttribute('data-mx-motion-ready');
      });
    }
    if (!('IntersectionObserver' in window)) return;

    var CHROME = '.mx-mast, .mx-footer, .mx-colophon, nav';
    var pending = [], scrollFns = [];

    function reveal(el) {
      el.classList.add('is-in');
      el.setAttribute('data-mx-inview', '');
      var i = pending.indexOf(el);
      if (i >= 0) pending.splice(i, 1);
    }
    var io = new IntersectionObserver(function (entries) {
      for (var i = 0; i < entries.length; i++) {
        if (entries[i].isIntersecting) {
          reveal(entries[i].target);
          io.unobserve(entries[i].target);
        }
      }
    }, { rootMargin: '0px 0px -9% 0px', threshold: 0.04 });

    function watch(el, cls) {
      if (el.closest && el.closest(CHROME)) return;
      if (cls) el.classList.add(cls);
      pending.push(el);
      io.observe(el);
    }
    function stagger(el) { /* index among animated siblings → CSS delay */
      var p = el.parentNode;
      if (p) { p.__mxn = p.__mxn || 0; el.style.setProperty('--mx-i', '' + p.__mxn++); }
    }

    if (tier === 'tier0') {
      /* tier0: hairline draw-ins + ghost parallax ONLY */
      $$('.mx-plate, .mx-actopen, .mx-pull, .mx-ledger, .mx-numbers, .mx-quote, .mx-sources')
        .forEach(function (el) { watch(el, 'mx-draw'); });
      var plates = $$('.mx-plate');
      scrollFns.push(function (vh) {
        for (var i = 0; i < plates.length; i++) {
          var r = plates[i].getBoundingClientRect();
          if (r.bottom < -120 || r.top > vh + 120) continue;
          var p = ((vh / 2) - (r.top + r.height / 2)) / vh;
          if (p > 1) p = 1; else if (p < -1) p = -1;
          plates[i].style.setProperty('--mx-par', p.toFixed(3));
        }
      });
    } else {
      /* tier1/tier2: rise-on-scroll + object settles */
      $$('.mx-card, .mx-ticket, .mx-coaster, .mx-note' + (tier === 'tier1' ? ', .mx-stamp' : ''))
        .forEach(function (el) { stagger(el); watch(el, 'mx-settle'); });
      $$('.mx-quote, .mx-pull, .mx-anchor, .mx-plate, .mx-actopen, .mx-zig__entry, .mx-chart')
        .forEach(function (el) { stagger(el); watch(el, 'mx-rise'); });
      if (tier === 'tier2') {
        $$('.mx-stamp').forEach(function (el) { stagger(el); watch(el, 'mx-slam'); });
      }
      $$('.mx-sig-stamp-slam').forEach(function (el) { watch(el, 'mx-slam'); });

      /* sequences: rows tick in order */
      [['.mx-ranked', '.mx-ranked__entry'],
       ['.mx-scorecard', 'tr'],
       ['.mx-numbers', '.mx-numbers__cell'],
       ['.mx-cheat', '.mx-cheat__col'],
       ['.mx-dontmiss', 'li'],
       ['.mx-countdown', '.mx-countdown__cell'],
       ['.mx-sig-rows-climb', 'tr, li, .mx-ranked__entry'],
       ['.mx-sig-cols-reveal', '.mx-cheat__col, .mx-col']
      ].forEach(function (pair) {
        $$(pair[0]).forEach(function (c) {
          if (c.classList.contains('mx-seq')) return;
          var rows = $$(pair[1], c).filter(function (r) { return r.closest(pair[0]) === c; });
          if (!rows.length) return;
          for (var i = 0; i < rows.length; i++) {
            rows[i].classList.add('mx-row');
            rows[i].style.setProperty('--mx-i', String(i));
          }
          watch(c, 'mx-seq');
        });
      });
      /* facts ledgers: dt+dd pairs share one index */
      $$('.mx-ledger').forEach(function (c) {
        var kids = $$('dl > dt, dl > dd', c), n = -1;
        if (!kids.length) return;
        for (var i = 0; i < kids.length; i++) {
          if (kids[i].tagName === 'DT') n++;
          kids[i].classList.add('mx-row');
          kids[i].style.setProperty('--mx-i', String(Math.max(0, n)));
        }
        watch(c, 'mx-seq');
      });

      if (tier === 'tier2') {
        /* act crossfade at transit seams (endpoint colors = act tokens) */
        var seams = [];
        $$('.mx-transit').forEach(function (t) {
          function seamEl(host, dir) {
            if (!host || !host.hasAttribute || !host.hasAttribute('data-act')) return null;
            if (getComputedStyle(host).position === 'static') host.style.position = 'relative';
            var s = d.createElement('div');
            s.className = 'mx-seam mx-seam--' + dir;
            s.setAttribute('aria-hidden', 'true');
            host.appendChild(s);
            return s;
          }
          seams.push({ t: t, a: seamEl(t.previousElementSibling, 'out'), b: seamEl(t.nextElementSibling, 'in') });
        });
        if (seams.length) {
          scrollFns.push(function (vh) {
            for (var i = 0; i < seams.length; i++) {
              var r = seams[i].t.getBoundingClientRect();
              var p = 1 - Math.abs(r.top + r.height / 2 - vh / 2) / (vh * 1.15);
              if (p < 0) p = 0; else if (p > 1) p = 1;
              var v = p.toFixed(3);
              if (seams[i].a) seams[i].a.style.setProperty('--mx-seam', v);
              if (seams[i].b) seams[i].b.style.setProperty('--mx-seam', v);
            }
          });
        }
        $$('.mx-countdown[data-mx-target]').forEach(bindCountdown);
      }
    }

    /* activate: only now may CSS hold start states */
    root.setAttribute('data-mx-motion-ready', '');

    /* safety reveal: pending-but-on-screen can never stay blank */
    scrollFns.push(function (vh) {
      for (var i = pending.length - 1; i >= 0; i--) {
        var r = pending[i].getBoundingClientRect();
        if (r.top < vh * 0.94 && r.bottom > 0) {
          io.unobserve(pending[i]);
          reveal(pending[i]);
        }
      }
    });
    var ticking = false;
    function onScroll() {
      if (ticking || reduced()) return;
      ticking = true;
      requestAnimationFrame(function () {
        ticking = false;
        var vh = window.innerHeight;
        for (var i = 0; i < scrollFns.length; i++) scrollFns[i](vh);
      });
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    onScroll();
    setTimeout(onScroll, 2500);
  }

  /* opt-in live countdown; numerals re-flip on change */
  function bindCountdown(box) {
    var target = Date.parse(box.getAttribute('data-mx-target'));
    if (isNaN(target)) return;
    var cells = {};
    $$('[data-cd]', box).forEach(function (el) { cells[el.getAttribute('data-cd')] = el; });
    function pad(n) { return n < 10 ? '0' + n : String(n); }
    function set(el, v) {
      if (!el || el.textContent === v) return;
      el.textContent = v;
      el.classList.remove('mx-flip-tick');
      void el.offsetWidth;
      el.classList.add('mx-flip-tick');
    }
    function tick() {
      var ms = target - Date.now();
      if (ms < 0) ms = 0;
      var s = Math.floor(ms / 1000);
      set(cells.days, pad(Math.floor(s / 86400)));
      set(cells.hours, pad(Math.floor(s / 3600) % 24));
      set(cells.mins, pad(Math.floor(s / 60) % 60));
      set(cells.secs, pad(s % 60));
      if (ms > 0 && !reduced()) setTimeout(tick, 1000);
    }
    tick();
  }

  if (d.readyState === 'loading') d.addEventListener('DOMContentLoaded', init);
  else init();
})();
