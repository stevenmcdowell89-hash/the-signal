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

// Broken-image fallback — hide any <img> that fails to load along with its
// caption/figure wrapper, so a fabricated or expired image URL doesn't
// render a broken-image icon. Capture-phase listener because img error
// events don't bubble. Belt to the Phase 7.6 check-image-urls.sh gate's
// braces.
(function() {
  document.addEventListener('error', function(e) {
    var t = e.target;
    if (!t || t.tagName !== 'IMG') return;
    t.style.display = 'none';
    var p = t.parentElement;
    if (!p) return;
    // Hide a sibling .caption (the common pattern) and any wrapping <figure>
    var next = t.nextElementSibling;
    if (next && next.classList && next.classList.contains('caption')) {
      next.style.display = 'none';
    }
    if (p.tagName === 'FIGURE') {
      p.style.display = 'none';
    }
  }, true);
})();

// Back to top button visibility + click handler
(function() {
  const btn = document.getElementById('backToTop') || document.getElementById('btt');
  if (!btn) return;
  window.addEventListener('scroll', function() {
    if (window.scrollY > 800) {
      btn.classList.add('visible');
    } else {
      btn.classList.remove('visible');
    }
  }, { passive: true });
  btn.addEventListener('click', function(e) {
    e.preventDefault();
    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
})();

// Enhancement 5: IntersectionObserver for .reveal elements
// Low threshold + rootMargin so tall elements on mobile still trigger.
// CSS makes .reveal visible by default below 601px as a belt-and-braces safety.
(function() {
  var els = document.querySelectorAll('.reveal');
  if (!els.length || !('IntersectionObserver' in window)) {
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
  }, { threshold: 0.02, rootMargin: '0px 0px 80px 0px' });
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
  }, { threshold: 0.02, rootMargin: '0px 0px 80px 0px' });
  els.forEach(function(el) { observer.observe(el); });
})();

// Enhancement 19C: Wax-stamp chapter numeral tracker.
// Counts every top-level <section>/<header> inside .mag and writes the
// roman numeral of the section currently centred in the viewport into
// #stampNumeral. Cover counts as I. No-op if the stamp isn't on the page.
(function() {
  var hub = document.getElementById('stampNumeral');
  if (!hub || !('IntersectionObserver' in window)) return;

  var mag = document.querySelector('.mag');
  if (!mag) return;
  var chapters = Array.prototype.slice.call(
    mag.querySelectorAll(':scope > section, :scope > header.cover')
  );
  if (!chapters.length) return;

  function toRoman(n) {
    var map = [
      [1000,'M'],[900,'CM'],[500,'D'],[400,'CD'],
      [100,'C'],[90,'XC'],[50,'L'],[40,'XL'],
      [10,'X'],[9,'IX'],[5,'V'],[4,'IV'],[1,'I']
    ];
    var s = '';
    for (var i = 0; i < map.length; i++) {
      while (n >= map[i][0]) { s += map[i][1]; n -= map[i][0]; }
    }
    return s;
  }

  chapters.forEach(function(el, i) { el.dataset.chapterNumeral = toRoman(i + 1); });

  var current = chapters[0].dataset.chapterNumeral;
  hub.textContent = current;

  var observer = new IntersectionObserver(function(entries) {
    // Pick the entry with the highest intersection ratio that's intersecting.
    var best = null;
    entries.forEach(function(e) {
      if (e.isIntersecting && (!best || e.intersectionRatio > best.intersectionRatio)) best = e;
    });
    if (best && best.target.dataset.chapterNumeral && best.target.dataset.chapterNumeral !== current) {
      current = best.target.dataset.chapterNumeral;
      hub.textContent = current;
    }
  }, { threshold: [0.25, 0.5, 0.75], rootMargin: '-35% 0px -35% 0px' });

  chapters.forEach(function(el) { observer.observe(el); });
})();
/* ============================================================
   UNIVERSAL — CHAPTER BEADS (v8.3+)
   Runs on every issue (standard weekly + special editions).
   Auto-discovers chapters:
     1. Prefer elements carrying [data-sp-chapter]
     2. Fall back to <section class="sec"> on standard editions
   Titles resolved in order:
     [data-sp-chapter-title] → first <h2> text → section id → "Chapter N"
   If no <aside class="sp-chapter-beads"> exists, component is inert.
   Shared rAF tick loop also exposes --sp-chapter-progress /
   --sp-next-ground so the special-edition sp-horizon can piggyback.
   ============================================================ */
(function () {
  var beads = document.querySelector('.sp-chapter-beads');
  if (!beads) return;

  var prefersReduced = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Discover chapters. Special editions usually carry data-sp-chapter.
  // Standard weekly falls back to <section class="sec"> which every
  // rotating/fixed section uses.
  var chapters = Array.prototype.slice.call(
    document.querySelectorAll('[data-sp-chapter]')
  );
  if (!chapters.length) {
    chapters = Array.prototype.slice.call(
      document.querySelectorAll('.mag > section.sec, .mag > section[class*="-section"]')
    );
  }
  if (!chapters.length) return;

  function titleOf(ch, i) {
    var t = ch.getAttribute('data-sp-chapter-title');
    if (t) return t;
    var h = ch.querySelector('h2');
    if (h && h.textContent) return h.textContent.trim();
    if (ch.id) return ch.id.replace(/[-_]/g, ' ').replace(/\b\w/g, function (c) { return c.toUpperCase(); });
    return 'Chapter ' + (i + 1);
  }

  // Build beads if container is empty
  if (!beads.children.length) {
    chapters.forEach(function (ch, i) {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'cb-bead';
      var label = titleOf(ch, i);
      b.setAttribute('aria-label', label);
      b.dataset.cIndex = i;
      var fill = document.createElement('span');
      fill.className = 'cb-fill';
      b.appendChild(fill);
      var tip = document.createElement('span');
      tip.className = 'cb-tip';
      tip.textContent = label;
      b.appendChild(tip);
      b.addEventListener('click', function () {
        ch.scrollIntoView({ behavior: prefersReduced ? 'auto' : 'smooth', block: 'start' });
      });
      beads.appendChild(b);
    });
  }

  // Activate after first scroll (graceful fade-in)
  var activated = false;
  function activate() {
    if (activated) return;
    activated = true;
    document.body.classList.add('sp-beads-ready');
  }
  window.addEventListener('scroll', activate, { once: true, passive: true });
  // Safety fallback — reveal after 1.8s even if no scroll fired
  setTimeout(activate, 1800);

  var beadEls = Array.prototype.slice.call(beads.querySelectorAll('.cb-bead'));
  var ticking = false;

  function tick() {
    ticking = false;
    var vh = window.innerHeight;
    var midY = vh * 0.4;
    var found = -1;
    var inProg = 0;
    for (var i = 0; i < chapters.length; i++) {
      var rect = chapters[i].getBoundingClientRect();
      if (rect.top <= midY && rect.bottom > midY) {
        found = i;
        var span = rect.height;
        var done = midY - rect.top;
        inProg = span > 0 ? Math.max(0, Math.min(1, done / span)) : 0;
        break;
      }
    }
    beadEls.forEach(function (b, i) {
      b.classList.toggle('passed', i < found);
      b.classList.toggle('active', i === found);
      var fill = b.querySelector('.cb-fill');
      if (fill) fill.style.setProperty('--cb-progress', i === found ? inProg.toFixed(3) : (i < found ? '1' : '0'));
    });
    document.documentElement.style.setProperty('--sp-chapter-progress', inProg.toFixed(3));
    var next = chapters[found + 1];
    if (next) {
      var ng = next.getAttribute('data-sp-ground-color');
      if (ng) {
        document.documentElement.style.setProperty('--sp-next-ground', ng);
        document.documentElement.style.setProperty('--sp-next-ground-fade', ng + '00');
      }
    }
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(tick); }
  }, { passive: true });
  window.addEventListener('resize', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(tick); }
  }, { passive: true });
  tick();
})();

/* ============================================================
   UNIVERSAL — STICKY PIN (v8.3)
   Drives the --spin-progress variable on .sp-sticky-pin as the
   reader scrolls past the pinned card's parent section. Enforces
   the "max one per issue" rule by removing extras after the first.
   Mobile (<= 820px) skips wiring — CSS collapses to inline figure.
   ============================================================ */
(function () {
  var pins = Array.prototype.slice.call(document.querySelectorAll('.sp-sticky-pin'));
  if (!pins.length) return;

  // Enforce: max one per issue. Demote the rest to plain inline figures.
  if (pins.length > 1) {
    pins.slice(1).forEach(function (p) { p.classList.add('sp-sticky-pin--demoted'); p.style.position = 'static'; p.style.float = 'none'; });
  }
  var pin = pins[0];
  if (window.matchMedia && window.matchMedia('(max-width: 820px)').matches) return;

  var host = pin.parentElement;
  if (!host) return;

  var ticking = false;
  function tick() {
    ticking = false;
    var rect = host.getBoundingClientRect();
    var vh = window.innerHeight;
    // Progress = how far the reader is through the host section
    // while the pin is stuck.
    var total = rect.height - vh;
    if (total <= 0) { pin.style.setProperty('--spin-progress', '0'); return; }
    var done = Math.max(0, Math.min(total, -rect.top));
    pin.style.setProperty('--spin-progress', (done / total).toFixed(3));
  }
  window.addEventListener('scroll', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(tick); }
  }, { passive: true });
  window.addEventListener('resize', function () {
    if (!ticking) { ticking = true; requestAnimationFrame(tick); }
  }, { passive: true });
  tick();
})();

/* ============================================================
   PORTRAIT SPREAD REPARENTER (v8.7.1)
   On portrait viewports (≤ 980px) the 3-column magazine spread
   switches from grid to float layout so prose can reclaim full
   reading width once the margin column ends. The authored HTML
   has .sp-margin as a DOM sibling of .sp-spread-body; we move it
   to be the first child of .sp-spread-body on portrait, and move
   it back on wider viewports where the grid takes over. Idempotent
   and safe under reduced-motion (pure layout, no animation).
   ============================================================ */
(function () {
  if (typeof window === 'undefined') return;
  var mq = window.matchMedia('(max-width: 980px)');
  function applyLayout() {
    var portrait = mq.matches;
    var spreads = document.querySelectorAll('.sp-spread');
    for (var i = 0; i < spreads.length; i++) {
      var sp = spreads[i];
      var body = sp.querySelector(':scope > .sp-spread-body');
      var margin = sp.querySelector('.sp-margin');
      if (!body || !margin) continue;
      if (portrait) {
        if (margin.parentElement !== body) {
          body.insertBefore(margin, body.firstChild);
        }
        sp.dataset.spreadPortraitLayout = 'on';
      } else {
        if (margin.parentElement === body) {
          sp.appendChild(margin);
        }
        if (sp.dataset.spreadPortraitLayout) delete sp.dataset.spreadPortraitLayout;
      }
    }
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', applyLayout);
  } else {
    applyLayout();
  }
  var rt;
  window.addEventListener('resize', function () {
    clearTimeout(rt);
    rt = setTimeout(applyLayout, 120);
  });
  if (mq.addEventListener) {
    mq.addEventListener('change', applyLayout);
  } else if (mq.addListener) {
    mq.addListener(applyLayout);
  }
})();

/* ============================================================
   UNIVERSAL CHAPTER GATE (v8.5 — STICKY SCROLL MODEL)
   Auto-builds the black-panel opener for every .sp-chapter-gate
   element. Expected markup:
     <aside class="sp-chapter-gate"
            data-chapter-num="V"
            data-chapter-title="BEEKSE BERGEN"
            data-chapter-arc="Act III — the wild">
       <p class="scg-deck">...</p>
     </aside>
   Controller:
     1. Builds the .scg-strip panel (arc / numeral / title / deck).
     2. Adds body.sp-motion-ready so the CSS switches from static
        fallback to sticky-scroll model.
     3. On every frame while any gate is near the viewport, maps
        scroll progress through the gate's 150vh container to the
        --scg-progress CSS custom property (0..1). The CSS drives
        arc → numeral → title → deck reveal from that value.
     4. If IntersectionObserver / rAF / the progress loop fail,
        the static fallback CSS still shows a full-bleed black band
        with everything visible (safety net).
   ============================================================ */
(function () {
  var gates = document.querySelectorAll('.sp-chapter-gate');
  if (!gates.length) return;

  // Honour reduced motion: build DOM but skip the sticky progress driver.
  var prefersReducedGate = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Signal motion-ready so the CSS switches to the sticky model.
  document.body.classList.add('sp-motion-ready');

  gates.forEach(function (gate) {
    if (gate.querySelector('.scg-strip')) return; // idempotent

    var num   = gate.getAttribute('data-chapter-num')   || '';
    var title = gate.getAttribute('data-chapter-title') || '';
    var arc   = gate.getAttribute('data-chapter-arc')   || '';
    var deck  = gate.querySelector('.scg-deck');

    var strip = document.createElement('div');
    strip.className = 'scg-strip';

    if (arc) {
      var arcEl = document.createElement('p');
      arcEl.className = 'scg-arc';
      arcEl.textContent = arc;
      strip.appendChild(arcEl);
    }
    if (num) {
      var numEl = document.createElement('p');
      numEl.className = 'scg-numeral';
      numEl.textContent = num;
      strip.appendChild(numEl);
    }
    if (title) {
      var titleEl = document.createElement('p');
      titleEl.className = 'scg-title';
      titleEl.textContent = title;
      strip.appendChild(titleEl);
    }
    // Move the deck INSIDE the strip (v8.5 — deck now sits on the black panel)
    if (deck) {
      strip.appendChild(deck);
    }

    gate.appendChild(strip);

    // In reduced-motion mode, force progress = 1 so everything is visible
    // (CSS static fallback also handles this, this is belt-and-braces).
    if (prefersReducedGate) {
      gate.style.setProperty('--scg-progress', '1');
    }
  });

  if (prefersReducedGate) return;

  // --- Scroll progress driver ---
  // For each gate, the progress is how far we've scrolled through the
  // 160vh container, clamped so:
  //   before the top of the gate reaches the viewport top  → 0
  //   one viewport-height of scroll later                  → 1
  // This lines up with the sticky hold (100vh of the 160vh container).
  var visibleGates = new Set();
  var ticking = false;

  function updateProgress() {
    ticking = false;
    var vh = window.innerHeight || document.documentElement.clientHeight;
    visibleGates.forEach(function (gate) {
      var r = gate.getBoundingClientRect();
      // v8.10.2 — progress starts as the panel begins sliding into view, not
      // when its top reaches the viewport top. Otherwise on portrait the
      // sticky panel can fill the screen with progress still near 0, leaving
      // a long black-with-no-title moment. New mapping: progress = 0 when the
      // gate's top is 0.4*vh below the viewport top (~40% of the strip already
      // visible as it rises), progress = 1 when r.top = -0.6*vh (panel locked,
      // most of the hold consumed). Span = 1.0*vh.
      var scrolled = (vh * 0.4) + (-r.top);
      var p = scrolled / vh;
      if (p < 0) p = 0;
      else if (p > 1) p = 1;
      gate.style.setProperty('--scg-progress', p.toFixed(3));
    });
  }

  function requestUpdate() {
    if (ticking) return;
    ticking = true;
    window.requestAnimationFrame(updateProgress);
  }

  if ('IntersectionObserver' in window) {
    // Watch each gate with a generous rootMargin so we start updating
    // progress before the panel locks, and keep updating until it leaves.
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) visibleGates.add(e.target);
        else                  visibleGates.delete(e.target);
      });
      requestUpdate();
    }, { rootMargin: '50% 0px 50% 0px', threshold: 0 });
    gates.forEach(function (g) { io.observe(g); });
  } else {
    // Fallback: watch all gates every scroll event.
    gates.forEach(function (g) { visibleGates.add(g); });
  }

  window.addEventListener('scroll', requestUpdate, { passive: true });
  window.addEventListener('resize', requestUpdate, { passive: true });

  // Prime the progress once so initial-on-screen gates aren't invisible.
  requestUpdate();

  // Safety backstop — if after 2.5s any gate is still at progress 0
  // (observer never fired / layout weirdness), force it to 1 so the
  // user at least sees the chapter title.
  setTimeout(function () {
    gates.forEach(function (g) {
      var val = g.style.getPropertyValue('--scg-progress');
      if (!val || parseFloat(val) === 0) {
        var r = g.getBoundingClientRect();
        // Only force if it's currently off-screen above (already scrolled past)
        // or already near / in viewport — safe to reveal.
        if (r.bottom < 0 || r.top < (window.innerHeight || 800)) {
          g.style.setProperty('--scg-progress', '1');
        }
      }
    });
  }, 2500);
})();

/* ============================================================
   SPECIAL EDITION — MOTION CONTROLLER
   Activates only on body.is-special. Honours prefers-reduced-motion.
   All effects are additive — if this block fails, the issue still
   renders correctly.
   ============================================================ */
(function() {
  if (!document.body.classList.contains('is-special')) return;

  var prefersReduced = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Pre-roll splash auto-cleanup */
  var splash = document.querySelector('.sp-splash');
  if (splash) {
    setTimeout(function() {
      if (splash && splash.parentNode) splash.parentNode.removeChild(splash);
    }, prefersReduced ? 100 : 2200);
  }

  if (prefersReduced) return;

  /* Layered parallax */
  (function() {
    var blocks = document.querySelectorAll('.sp-parallax');
    if (!blocks.length) return;

    var visible = new Set();
    var obs = new IntersectionObserver(function(entries) {
      entries.forEach(function(e) {
        if (e.isIntersecting) visible.add(e.target);
        else visible.delete(e.target);
      });
    }, { rootMargin: '20% 0px 20% 0px' });
    blocks.forEach(function(b) { obs.observe(b); });

    var ticking = false;
    function update() {
      ticking = false;
      var vh = window.innerHeight;
      visible.forEach(function(block) {
        var rect = block.getBoundingClientRect();
        var centre = rect.top + rect.height / 2;
        var progress = (centre - vh / 2) / vh;
        progress = Math.max(-1.4, Math.min(1.4, progress));

        var layers = block.querySelectorAll('.p-bg, .p-mid, .p-fg');
        layers.forEach(function(l) {
          var speed = parseFloat(getComputedStyle(l).getPropertyValue('--sp-speed')) || 0.5;
          var y = -progress * 40 * speed;
          l.style.setProperty('--sp-y', y.toFixed(1) + 'px');
        });
      });
    }
    window.addEventListener('scroll', function() {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    window.addEventListener('resize', update, { passive: true });
    update();
  })();

  /* Stagger reveal */
  (function() {
    var targets = document.querySelectorAll('.sp-stagger');
    if (!targets.length) return;

    targets.forEach(function(el) {
      if (el.dataset.staggered) return;
      el.dataset.staggered = '1';
      var txt = el.textContent.trim();
      if (!txt) return;
      var words = txt.split(/\s+/);
      var maxDelayCount = Math.min(words.length, 10);
      el.innerHTML = words.map(function(w, i) {
        var idx = Math.min(i, maxDelayCount - 1);
        return '<span class="sp-word" style="--sp-i:' + idx + '">' + w + '</span>';
      }).join(' ');
    });

    var obs = new IntersectionObserver(function(entries) {
      entries.forEach(function(e) {
        if (e.isIntersecting) {
          e.target.classList.add('sp-in');
          obs.unobserve(e.target);
        }
      });
    }, { threshold: 0.15, rootMargin: '0px 0px -10% 0px' });
    targets.forEach(function(t) { obs.observe(t); });
  })();

  /* Colour-wipe section transitions */
  (function() {
    var wipes = document.querySelectorAll('.sp-wipe');
    if (!wipes.length) return;

    wipes.forEach(function(w) {
      if (w.querySelector('.sp-wipe-layer')) return;
      w.innerHTML = '<span class="sp-wipe-layer l1"></span>' +
                    '<span class="sp-wipe-layer l2"></span>' +
                    '<span class="sp-wipe-layer l3"></span>';
    });

    var obs = new IntersectionObserver(function(entries) {
      entries.forEach(function(e) {
        if (e.isIntersecting) {
          e.target.classList.add('sp-in');
          obs.unobserve(e.target);
        }
      });
    }, { threshold: 0.1 });
    wipes.forEach(function(w) { obs.observe(w); });
  })();

  /* Countdown D-day badge: shows the AUTHORED days-until-event, fixed at publication.
     A magazine issue is a snapshot — the prose says "23 days to go" and the badge
     must agree, forever. The badge value is authored via data-dday-start on <body>.
     data-trip-date is used ONLY to compute an accurate value at generation time
     (handled by the authoring tool, not this runtime). At render time we just display
     the static authored value. Appears on scroll past hero, then stays. */
  (function() {
    if (document.body.getAttribute('data-special') !== 'countdown') return;
    var badge = document.querySelector('.sp-dday');
    if (!badge) return;
    var numEl = badge.querySelector('.sp-dday-num');
    var labelEl = badge.querySelector('.sp-dday-label');
    if (!numEl) return;

    var days = parseInt(document.body.getAttribute('data-dday-start') || numEl.textContent || '0', 10);
    if (isNaN(days) || days < 0) days = 0;

    if (days === 0) {
      numEl.textContent = '0';
      if (labelEl) labelEl.textContent = 'Today';
    } else if (days === 1) {
      numEl.textContent = '1';
      if (labelEl) labelEl.textContent = 'Day to go';
    } else {
      numEl.textContent = String(days);
      if (labelEl) labelEl.textContent = 'Days to go';
    }

    // Reveal on scroll past hero (first 8% of page). Stays visible after.
    var revealed = false;
    var ticking = false;
    function check() {
      ticking = false;
      if (revealed) return;
      var h = document.documentElement;
      var maxScroll = h.scrollHeight - h.clientHeight;
      if (maxScroll <= 0) return;
      var pct = h.scrollTop / maxScroll;
      if (pct > 0.06) {
        document.body.classList.add('sp-dday-visible');
        revealed = true;
        window.removeEventListener('scroll', onScroll);
      }
    }
    function onScroll() {
      if (!ticking) { ticking = true; requestAnimationFrame(check); }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    check();
  })();

  /* ============================================================
     TIER 4 — Body-embedded components (from 25-special-body.css).
     All components here are additive. If observers fail, content
     is still fully readable; CSS .sp-no-anim fallbacks kick in.
     ============================================================ */

  /* Generic IntersectionObserver reveal helper used by several components.
     Adds .sp-in when the element enters view, unobserves after. */
  function makeRevealer(selector, threshold, rootMargin) {
    var els = document.querySelectorAll(selector);
    if (!els.length) return null;
    if (!('IntersectionObserver' in window)) {
      els.forEach(function(el) { el.classList.add('sp-in'); });
      return null;
    }
    var obs = new IntersectionObserver(function(entries) {
      entries.forEach(function(e) {
        if (e.isIntersecting) {
          e.target.classList.add('sp-in');
          obs.unobserve(e.target);
        }
      });
    }, { threshold: threshold || 0.2, rootMargin: rootMargin || '0px 0px -10% 0px' });
    els.forEach(function(el) { obs.observe(el); });
    return obs;
  }

  /* Inline figure reveal — generous rootMargin so it triggers well before centre. */
  makeRevealer('.sp-inline-figure', 0.01, '200px 0px 200px 0px');
  /* Pull quote reveal */
  makeRevealer('.sp-pullquote-huge', 0.01, '200px 0px 200px 0px');
  /* Kicker (h3/h4) reveal — small elements, need very low threshold on mobile. */
  makeRevealer('.sp-kicker', 0.01, '200px 0px 200px 0px');
  /* Marginalia reveal */
  makeRevealer('.sp-marginalia', 0.01, '200px 0px 200px 0px');

  /* SP-SCROLL-IMAGE parallax — translate img inside frame based on
     how much of the frame is in view. Subtle: max 40px range.
     Honours reduced-motion (already returned above). */
  (function() {
    var figures = document.querySelectorAll('.sp-scroll-image');
    if (!figures.length) return;

    var items = [];
    figures.forEach(function(fig) {
      var img = fig.querySelector('img');
      if (img) items.push({ fig: fig, img: img, inView: false });
    });

    if ('IntersectionObserver' in window) {
      var obs = new IntersectionObserver(function(entries) {
        entries.forEach(function(e) {
          var item = items.filter(function(i) { return i.fig === e.target; })[0];
          if (item) item.inView = e.isIntersecting;
        });
      }, { threshold: [0, 0.1, 0.9, 1], rootMargin: '20% 0px 20% 0px' });
      items.forEach(function(i) { obs.observe(i.fig); });
    } else {
      items.forEach(function(i) { i.inView = true; });
    }

    var ticking = false;
    function update() {
      ticking = false;
      var vh = window.innerHeight;
      items.forEach(function(item) {
        if (!item.inView) return;
        var rect = item.fig.getBoundingClientRect();
        // Progress: 0 when element centre is at bottom of viewport, 1 when at top
        var centre = rect.top + rect.height / 2;
        var progress = 1 - (centre / vh);
        // Clamp
        if (progress < -0.2) progress = -0.2;
        if (progress > 1.2)  progress = 1.2;
        // Subtle translate: -20px to +20px
        var y = (progress - 0.5) * -40;
        item.img.style.setProperty('--sp-parallax-y', y.toFixed(1) + 'px');
      });
    }
    function onScroll() {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    update();
  })();

  /* SP-IMAGE-STRIP — horizontal drift as the page scrolls vertically.
     Translate the track by a calculated X based on vertical scroll
     progress through the strip's visible range. */
  (function() {
    var strips = document.querySelectorAll('.sp-image-strip');
    if (!strips.length) return;

    var items = [];
    strips.forEach(function(strip) {
      var track = strip.querySelector('.sp-strip-track');
      if (track) items.push({ strip: strip, track: track, inView: false });
    });

    if ('IntersectionObserver' in window) {
      var obs = new IntersectionObserver(function(entries) {
        entries.forEach(function(e) {
          var item = items.filter(function(i) { return i.strip === e.target; })[0];
          if (item) item.inView = e.isIntersecting;
        });
      }, { threshold: [0, 0.01, 0.99, 1], rootMargin: '10% 0px 10% 0px' });
      items.forEach(function(i) { obs.observe(i.strip); });
    } else {
      items.forEach(function(i) { i.inView = true; });
    }

    var ticking = false;
    function update() {
      ticking = false;
      var vh = window.innerHeight;
      items.forEach(function(item) {
        if (!item.inView) return;
        var stripRect = item.strip.getBoundingClientRect();
        var trackW = item.track.scrollWidth;
        var stripW = item.strip.clientWidth;
        var overflow = Math.max(0, trackW - stripW + 40); // +gutter
        // Progress: 0 when strip top hits bottom of viewport,
        //          1 when strip bottom hits top of viewport.
        var total = stripRect.height + vh;
        var travelled = vh - stripRect.top;
        var progress = Math.max(0, Math.min(1, travelled / total));
        // Translate negative X to pull the track left as we scroll down
        var x = -overflow * progress;
        item.track.style.setProperty('--sp-strip-x', x.toFixed(1) + 'px');
      });
    }
    function onScroll() {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll, { passive: true });
    update();
  })();

  /* SP-NUMBER count-up — both inline .sp-number and block .sp-number-huge.
     Uses data-to attribute; animates from 0 to target over ~1.2s
     when scrolled into view. Preserves any comma formatting from data-to. */
  (function() {
    var els = document.querySelectorAll('.sp-number[data-to], .sp-number-huge[data-to]');
    if (!els.length) return;
    if (!('IntersectionObserver' in window)) {
      els.forEach(function(el) { el.textContent = el.getAttribute('data-to'); });
      return;
    }

    function formatNumber(n, hasComma) {
      n = Math.round(n);
      if (!hasComma) return String(n);
      return n.toLocaleString('en-GB');
    }

    function animate(el) {
      var raw = el.getAttribute('data-to');
      var hasComma = raw.indexOf(',') !== -1;
      var target = parseFloat(raw.replace(/,/g, ''));
      if (isNaN(target)) return;
      var start = null;
      var duration = 1100;
      function step(ts) {
        if (start === null) start = ts;
        var t = Math.min(1, (ts - start) / duration);
        // Ease-out cubic
        var eased = 1 - Math.pow(1 - t, 3);
        el.textContent = formatNumber(target * eased, hasComma);
        if (t < 1) requestAnimationFrame(step);
      }
      requestAnimationFrame(step);
    }

    var obs = new IntersectionObserver(function(entries) {
      entries.forEach(function(e) {
        if (e.isIntersecting) {
          animate(e.target);
          obs.unobserve(e.target);
        }
      });
    }, { threshold: 0.6 });
    els.forEach(function(el) { obs.observe(el); });
  })();

  /* SP-CURTAIN transition — drop then retract. Reuse the wipe pattern
     but with a vertical scale and a post-drop retract phase. */
  (function() {
    var curtains = document.querySelectorAll('.sp-curtain');
    if (!curtains.length) return;
    if (!('IntersectionObserver' in window)) {
      curtains.forEach(function(c) { c.classList.add('sp-in'); });
      return;
    }
    var obs = new IntersectionObserver(function(entries) {
      entries.forEach(function(e) {
        if (!e.isIntersecting) return;
        e.target.classList.add('sp-in');
        // Retract after it has fully dropped
        setTimeout(function() {
          e.target.classList.add('sp-out');
        }, 700);
        obs.unobserve(e.target);
      });
    }, { threshold: 0.3 });
    curtains.forEach(function(c) { obs.observe(c); });
  })();

})();

/* ============================================================
   SPECIAL EDITION — TIER 5.5 EDITORIAL MOTION CONTROLLERS
   Pairs with 28-special-motion-editorial.css.
   Short-circuits unless body.is-special; honours reduced motion.
   ============================================================ */
(function() {
  if (typeof document === 'undefined') return;
  if (!document.body || !document.body.classList.contains('is-special')) return;
  var prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // Mark motion-ready so CSS-gated initial states (opacity:0) activate.
  // If this line never runs (JS disabled/error), content stays fully visible.
  document.body.classList.add('sp-motion-ready');

  /* Image-failure safety net.
     Auto-tag any .sp-scroll-image / .sp-inline-figure / .sp-image-quote
     whose <img> fails to load (404, 429 rate-limit, CORS, offline) so the
     CSS can collapse the empty frame. Runs for every existing image plus any
     inserted later. Without this, a broken Wikimedia thumbnail leaves a huge
     empty cream box on mobile. */
  function tagFailedFigure(img) {
    var fig = img.closest && (img.closest('.sp-scroll-image') || img.closest('.sp-inline-figure') || img.closest('.sp-image-quote'));
    if (fig) fig.classList.add('sp-img-failed');
  }
  function watchImg(img) {
    if (img.dataset.spImgWatched === '1') return;
    img.dataset.spImgWatched = '1';
    // If already finished loading with no dimensions, it failed.
    if (img.complete && (img.naturalWidth === 0 || img.naturalHeight === 0)) {
      tagFailedFigure(img);
      return;
    }
    img.addEventListener('error', function() { tagFailedFigure(img); });
    img.addEventListener('load', function() {
      if (img.naturalWidth === 0 || img.naturalHeight === 0) tagFailedFigure(img);
    });
  }
  document.querySelectorAll('.sp-scroll-image img, .sp-inline-figure img, .sp-image-quote img').forEach(watchImg);

  // Scroll-aware safety net: after the reader stops scrolling (idle 1.2s),
  // reveal anything at OR ABOVE the current viewport that still hasn't got
  // its -in class. Elements below the viewport stay hidden so their scroll-
  // triggered entrance animation still fires when the reader reaches them.
  // This catches observers that fail to fire on mobile (fast scroll, odd
  // thresholds, landing mid-page) without killing the staggered motion.
  var safetyMap = [
    ['.sp-band', 'sp-band-in'],
    ['.sp-chapter-chrome', 'sp-chr-in'],
    ['.sp-dash', 'sp-dash-in'],
    ['.sp-timeline', 'sp-tl-in'],
    ['.sp-hero-quote', 'sp-hq-in'],
    ['.sp-brief', 'sp-br-in'],
    ['.sp-pull-break', 'sp-pb-in'],
    ['.sp-bridger', 'sp-bg-in'],
    ['.sp-spread', 'sp-sp-in'],
    ['.sp-signoff', 'sp-so-in'],
    ['.sp-eyebrow', 'sp-eb-in'],
    ['.sp-caption-strip', 'sp-cs-in'],
    ['.sp-spine', 'sp-spine-in'],
    // Tier-4 reveal classes — all use generic .sp-in
    ['.sp-kicker', 'sp-in'],
    ['.sp-inline-figure', 'sp-in'],
    ['.sp-pullquote-huge', 'sp-in'],
    ['.sp-marginalia', 'sp-in']
  ];

  function catchUpAboveViewport() {
    var threshold = window.innerHeight + 200; // reveal anything whose top is within 200px below viewport
    safetyMap.forEach(function(pair) {
      document.querySelectorAll(pair[0]).forEach(function(el) {
        if (el.classList.contains(pair[1])) return;
        var rect = el.getBoundingClientRect();
        if (rect.top < threshold) el.classList.add(pair[1]);
      });
    });
  }

  // Run initial catch-up shortly after load (covers elements above the fold
  // when JS initialises late, or mid-page landings).
  setTimeout(catchUpAboveViewport, 600);

  // Throttled scroll-idle catch-up.
  var idleTimer = null;
  window.addEventListener('scroll', function() {
    if (idleTimer) clearTimeout(idleTimer);
    idleTimer = setTimeout(catchUpAboveViewport, 1200);
  }, { passive: true });

  // Final backstop: 8 seconds after load, force-reveal everything. No reader
  // should ever see an invisible element this long after the page loaded.
  setTimeout(function() {
    safetyMap.forEach(function(pair) {
      document.querySelectorAll(pair[0]).forEach(function(el) { el.classList.add(pair[1]); });
    });
  }, 8000);

  // Helper: lazy-create observer with options
  function makeObserver(threshold, cb, once) {
    if (!('IntersectionObserver' in window)) {
      return { observe: function(el) { cb({ target: el, isIntersecting: true }); } };
    }
    var obs = new IntersectionObserver(function(entries) {
      entries.forEach(function(e) {
        if (!e.isIntersecting) return;
        cb(e);
        if (once !== false) obs.unobserve(e.target);
      });
    }, { threshold: threshold || 0.01, rootMargin: '150px 0px 150px 0px' });
    return obs;
  }

  /* ----- 1. .sp-band — wipe-band reveal ----- */
  (function() {
    var bands = document.querySelectorAll('.sp-band');
    if (!bands.length) return;
    // Auto-wrap inner text into .sp-band-t (only if not already wrapped)
    bands.forEach(function(el) {
      if (el.querySelector('.sp-band-t')) return;
      var inner = document.createElement('span');
      inner.className = 'sp-band-t';
      while (el.firstChild) inner.appendChild(el.firstChild);
      el.appendChild(inner);
    });
    if (prefersReduced) {
      bands.forEach(function(el) { el.classList.add('sp-band-in'); });
      return;
    }
    var obs = makeObserver(0.01, function(e) { e.target.classList.add('sp-band-in'); });
    bands.forEach(function(el) { obs.observe(el); });
  })();

  /* ----- 2. .sp-chapter-chrome — sequenced wipe ----- */
  (function() {
    var chromes = document.querySelectorAll('.sp-chapter-chrome');
    if (!chromes.length) return;
    if (prefersReduced) {
      chromes.forEach(function(el) { el.classList.add('sp-chr-in'); });
      return;
    }
    var obs = makeObserver(0.01, function(e) { e.target.classList.add('sp-chr-in'); });
    chromes.forEach(function(el) { obs.observe(el); });
  })();

  /* ----- 3. .sp-folio — scroll drift via --sp-folio-y ----- */
  (function() {
    var folios = document.querySelectorAll('.sp-folio');
    if (!folios.length || prefersReduced) return;
    var ticking = false;
    function update() {
      ticking = false;
      var vh = window.innerHeight || 800;
      folios.forEach(function(el) {
        var r = el.getBoundingClientRect();
        // Centre of element vs centre of viewport, normalised to [-1, 1]
        var centre = (r.top + r.height / 2);
        var t = (centre - vh / 2) / vh;
        // Clamp + scale to ±60px
        t = Math.max(-1, Math.min(1, t));
        el.style.setProperty('--sp-folio-y', (t * -60).toFixed(1) + 'px');
      });
    }
    function onScroll() {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(update);
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', onScroll);
    update();
  })();

  /* ----- 4. .sp-dash — cell stagger ----- */
  (function() {
    var dashes = document.querySelectorAll('.sp-dash');
    if (!dashes.length) return;
    if (prefersReduced) {
      dashes.forEach(function(el) { el.classList.add('sp-dash-in'); });
      return;
    }
    var obs = makeObserver(0.01, function(e) { e.target.classList.add('sp-dash-in'); });
    dashes.forEach(function(el) { obs.observe(el); });
  })();

  /* ----- 5. .sp-timeline — row stagger with --sp-tl-i ----- */
  (function() {
    var tls = document.querySelectorAll('.sp-timeline');
    if (!tls.length) return;
    tls.forEach(function(tl) {
      var rows = tl.querySelectorAll('.sp-tl-row');
      rows.forEach(function(r, i) { r.style.setProperty('--sp-tl-i', i); });
    });
    if (prefersReduced) {
      tls.forEach(function(el) { el.classList.add('sp-tl-in'); });
      return;
    }
    var obs = makeObserver(0.01, function(e) { e.target.classList.add('sp-tl-in'); });
    tls.forEach(function(el) { obs.observe(el); });
  })();

  /* ----- 6. .sp-hero-quote — card lift ----- */
  (function() {
    var hqs = document.querySelectorAll('.sp-hero-quote');
    if (!hqs.length) return;
    if (prefersReduced) {
      hqs.forEach(function(el) { el.classList.add('sp-hq-in'); });
      return;
    }
    var obs = makeObserver(0.01, function(e) { e.target.classList.add('sp-hq-in'); });
    hqs.forEach(function(el) { obs.observe(el); });
  })();

  /* ----- 7. .sp-brief — slide-in ----- */
  (function() {
    var briefs = document.querySelectorAll('.sp-brief');
    if (!briefs.length) return;
    if (prefersReduced) {
      briefs.forEach(function(el) { el.classList.add('sp-br-in'); });
      return;
    }
    var obs = makeObserver(0.01, function(e) { e.target.classList.add('sp-br-in'); });
    briefs.forEach(function(el) { obs.observe(el); });
  })();

  /* ----- 8. .sp-pull-break — corner glyph reveal ----- */
  (function() {
    var pbs = document.querySelectorAll('.sp-pull-break');
    if (!pbs.length) return;
    if (prefersReduced) {
      pbs.forEach(function(el) { el.classList.add('sp-pb-in'); });
      return;
    }
    var obs = makeObserver(0.01, function(e) { e.target.classList.add('sp-pb-in'); });
    pbs.forEach(function(el) { obs.observe(el); });
  })();

  /* ----- 9. .sp-bridger — three-column stagger ----- */
  (function() {
    var bgs = document.querySelectorAll('.sp-bridger');
    if (!bgs.length) return;
    if (prefersReduced) {
      bgs.forEach(function(el) { el.classList.add('sp-bg-in'); });
      return;
    }
    var obs = makeObserver(0.01, function(e) { e.target.classList.add('sp-bg-in'); });
    bgs.forEach(function(el) { obs.observe(el); });
  })();

  /* ----- 10. .sp-spread — rail+margin slide-in ----- */
  (function() {
    var spreads = document.querySelectorAll('.sp-spread');
    if (!spreads.length) return;
    if (prefersReduced) {
      spreads.forEach(function(el) { el.classList.add('sp-sp-in'); });
      return;
    }
    var obs = makeObserver(0.01, function(e) { e.target.classList.add('sp-sp-in'); });
    spreads.forEach(function(el) { obs.observe(el); });
  })();

  /* ----- 11. .sp-signoff — scale-in finale ----- */
  (function() {
    var sos = document.querySelectorAll('.sp-signoff');
    if (!sos.length) return;
    if (prefersReduced) {
      sos.forEach(function(el) { el.classList.add('sp-so-in'); });
      return;
    }
    var obs = makeObserver(0.01, function(e) { e.target.classList.add('sp-so-in'); });
    sos.forEach(function(el) { obs.observe(el); });
  })();

  /* ----- 12. .sp-eyebrow — soft slide-up (skips bands) ----- */
  (function() {
    var ebs = document.querySelectorAll('.sp-eyebrow:not(.sp-band)');
    if (!ebs.length) return;
    if (prefersReduced) {
      ebs.forEach(function(el) { el.classList.add('sp-eb-in'); });
      return;
    }
    var obs = makeObserver(0.01, function(e) { e.target.classList.add('sp-eb-in'); });
    ebs.forEach(function(el) { obs.observe(el); });
  })();

  /* ----- 13. .sp-caption-strip — hairline draw ----- */
  (function() {
    var caps = document.querySelectorAll('.sp-caption-strip');
    if (!caps.length) return;
    if (prefersReduced) {
      caps.forEach(function(el) { el.classList.add('sp-cs-in'); });
      return;
    }
    var obs = makeObserver(0.01, function(e) { e.target.classList.add('sp-cs-in'); });
    caps.forEach(function(el) { obs.observe(el); });
  })();

  /* ----- 14. .sp-spine — SVG line draw via --sp-spine-len ----- */
  (function() {
    var spines = document.querySelectorAll('.sp-spine');
    if (!spines.length) return;
    spines.forEach(function(spine) {
      var path = spine.querySelector('path');
      if (!path) return;
      try {
        var len = path.getTotalLength();
        if (len && isFinite(len) && len > 0) {
          spine.style.setProperty('--sp-spine-len', len);
        }
      } catch (err) {
        // getTotalLength can throw on some path shapes — fall back to default
      }
    });
    if (prefersReduced) {
      spines.forEach(function(el) { el.classList.add('sp-spine-in'); });
      return;
    }
    var obs = makeObserver(0.01, function(e) { e.target.classList.add('sp-spine-in'); });
    spines.forEach(function(el) { obs.observe(el); });
  })();

})();

/* ============================================================
   SIGNATURE MOMENTS + TRANSITIONS + AMBIENT (skill v8.2)
   Per-format signature moments + format-agnostic chapter
   transitions and ambient layers. Vanilla JS, IO-driven,
   reduced-motion safe, mobile graceful.
   ============================================================ */
(function () {
  if (!document.body.classList.contains('is-special')) return;
  var prefersReduced = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function $(sel, root) { return (root || document).querySelector(sel); }
  function $$(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function makeIO(threshold, cb) {
    if (!('IntersectionObserver' in window)) {
      return { observe: function (el) { cb({ isIntersecting: true, target: el, intersectionRatio: 1 }); } };
    }
    return new IntersectionObserver(function (entries) { entries.forEach(cb); }, { threshold: threshold });
  }

  var format = document.body.getAttribute('data-special') || '';

  /* -------- Signature: sp-sand-clock (Countdown) -------- */
  if (format === 'countdown') (function () {
    var clock = $('.sp-sand-clock');
    if (!clock) return;
    // Set elapsed-fraction from data-total / data-remaining
    var total = parseFloat(clock.getAttribute('data-total') || '0');
    var rem = parseFloat(clock.getAttribute('data-remaining') || '0');
    if (total > 0 && rem >= 0 && rem <= total) {
      clock.style.setProperty('--elapsed-fraction', ((total - rem) / total).toFixed(3));
    }
    if (prefersReduced) return;
    var io = makeIO(0.35, function (e) {
      if (e.isIntersecting) { clock.classList.add('is-pouring'); io.disconnect && io.disconnect(); }
    });
    io.observe(clock);
  })();

  /* -------- Signature: sp-memory-wall (Rewind) -------- */
  if (format === 'rewind') (function () {
    var wall = $('.sp-memory-wall');
    if (!wall) return;
    document.body.classList.add('sp-mw-ready');
    var triggers = $$('[data-reveals]');
    if (!triggers.length) return;
    var io = makeIO(0.18, function (e) {
      if (!e.isIntersecting) return;
      var ids = (e.target.getAttribute('data-reveals') || '').split(',');
      ids.forEach(function (id) {
        var cell = wall.querySelector('[data-item-id="' + id.trim() + '"]');
        if (cell) cell.classList.add('lit');
      });
    });
    triggers.forEach(function (t) { io.observe(t); });
  })();

  /* -------- Signature: sp-fault-line (Versus) -------- */
  if (format === 'versus') (function () {
    var line = $('.sp-fault-line');
    if (!line) return;
    var max = parseFloat(line.getAttribute('data-max-shift') || '90');
    line.style.setProperty('--fl-max', max + 'px');
    if (prefersReduced) return;
    var paragraphs = $$('[data-lean]');
    if (!paragraphs.length) return;
    // sum of absolute leans = max possible score
    var maxScore = 0;
    paragraphs.forEach(function (p) {
      var v = parseFloat(p.getAttribute('data-lean') || '0');
      maxScore += Math.abs(v);
    });
    if (maxScore === 0) maxScore = 1;
    var seen = {};
    var score = 0;
    var io = makeIO(0.55, function (e) {
      var id = e.target.getAttribute('data-pid') || (e.target.dataset.pid = String(Math.random()));
      if (e.isIntersecting && !seen[id]) {
        seen[id] = true;
        score += parseFloat(e.target.getAttribute('data-lean') || '0');
        line.style.setProperty('--fl-shift', (score / maxScore * max).toFixed(2) + 'px');
      }
    });
    paragraphs.forEach(function (p) { io.observe(p); });
    // Verdict element (optional)
    var verdict = $('[data-verdict]');
    if (verdict) {
      var vIO = makeIO(0.4, function (e) {
        if (!e.isIntersecting) return;
        var v = verdict.getAttribute('data-verdict');
        if (v === 'a') line.classList.add('verdict-a');
        if (v === 'b') line.classList.add('verdict-b');
      });
      vIO.observe(verdict);
    }
  })();

  /* -------- Signature: sp-form-tape (Season Review) -------- */
  if (format === 'season-review') (function () {
    var tapes = $$('.sp-form-tape');
    if (!tapes.length) return;
    var chapters = $$('[data-results]');
    if (!chapters.length) return;
    chapters.forEach(function (chapter) {
      var io = makeIO(0.25, function (e) {
        if (!e.isIntersecting) return;
        var results = (chapter.getAttribute('data-results') || '').split(',');
        var startIndex = parseInt(chapter.getAttribute('data-result-from') || '0', 10);
        results.forEach(function (r, i) {
          tapes.forEach(function (tape) {
            var pill = tape.children[startIndex + i];
            if (pill && !pill.classList.contains('lit')) {
              pill.setAttribute('data-r', r.trim());
              pill.style.setProperty('--i', i);
              pill.classList.add('lit');
            }
          });
        });
        io.disconnect && io.disconnect();
      });
      io.observe(chapter);
    });
  })();

  /* -------- Signature: sp-thread-pull (Deep Dive) -------- */
  if (format === 'deep-dive') (function () {
    var thread = $('.sp-thread-pull');
    if (!thread) return;
    if (window.innerWidth < 1100) return; // CSS hides it but skip JS too
    document.body.classList.add('sp-tp-ready');
    var spine = thread.querySelector('.tp-spine');
    var markers = $$('.tp-marker', thread);
    var article = $('[data-tp-track]') || document.body;
    var ticking = false;
    function update() {
      ticking = false;
      var rect = article.getBoundingClientRect();
      var vh = window.innerHeight;
      var total = rect.height;
      var passed = Math.max(0, Math.min(total, -rect.top + vh * 0.5));
      var prog = total > 0 ? passed / total : 0;
      thread.style.setProperty('--tp-progress', prog.toFixed(3));
      // Mark each branch passed when crossed
      markers.forEach(function (m) {
        var at = parseFloat(m.getAttribute('data-at') || '0'); // 0..1
        if (prog >= at) m.classList.add('passed');
        else m.classList.remove('passed');
      });
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
    update();
  })();

  /* -------- Signature: sp-build-meter (Blueprint) -------- */
  if (format === 'blueprint') (function () {
    var meter = $('.sp-build-meter');
    if (!meter) return;
    var cells = $$('.bm-cell', meter);
    var phases = $$('[data-phase]');
    if (!phases.length || !cells.length) return;
    var io = makeIO(0.3, function (e) {
      if (!e.isIntersecting) return;
      var idx = parseInt(e.target.getAttribute('data-phase') || '0', 10);
      cells.forEach(function (c, i) {
        if (i <= idx) c.classList.add('active'); else c.classList.remove('active');
      });
    });
    phases.forEach(function (p) { io.observe(p); });
  })();

  /* -------- Signature: sp-cold-start (Starter Kit) -------- */
  if (format === 'starter-kit') (function () {
    var cs = $('.sp-cold-start');
    if (!cs) return;
    var letters = $$('.cs-letter', cs);
    letters.forEach(function (l, i) { l.style.setProperty('--i', i); });
    if (prefersReduced) {
      document.body.classList.add('sp-cs-started');
      return;
    }
    var last = letters[letters.length - 1];
    function open() { document.body.classList.add('sp-cs-started'); }
    if (last) last.addEventListener('animationend', open, { once: true });
    setTimeout(open, 1800); // safety
  })();

  /* -------- Signature: sp-deck-reveal (Shortlist) -------- */
  if (format === 'shortlist') (function () {
    var deck = $('.sp-deck');
    if (!deck) return;
    var cards = $$('.dk-card', deck);
    cards.forEach(function (c, i) { c.style.setProperty('--i', i); });
    if (prefersReduced) {
      // collapse to vertical stack — let CSS handle
      cards.forEach(function (c) { c.classList.add('static'); });
      return;
    }
    var pulses = $$('[data-deck-step]');
    if (!pulses.length) return;
    var step = 0;
    var io = makeIO(0.45, function (e) {
      if (!e.isIntersecting) return;
      var s = parseInt(e.target.getAttribute('data-deck-step') || '0', 10);
      if (s > step) {
        for (var i = step; i < s; i++) {
          if (cards[i]) cards[i].classList.add('peeled');
        }
        step = s;
      }
    });
    pulses.forEach(function (p) { io.observe(p); });
  })();

  /* -------- Signature: sp-pinboard (Field Guide) -------- */
  if (format === 'field-guide') (function () {
    var pb = $('.sp-pinboard');
    if (!pb) return;
    var pins = $$('.pb-pin', pb);
    var labels = $$('.pb-label', pb);
    pins.forEach(function (p, i) { p.style.setProperty('--i', i); });
    labels.forEach(function (l, i) { l.style.setProperty('--i', i); });
    var io = makeIO(0.25, function (e) {
      if (e.isIntersecting) { pb.classList.add('is-shown'); io.disconnect && io.disconnect(); }
    });
    io.observe(pb);
    // pulse on prose-section reference
    var refs = $$('[data-pin-id]');
    if (!refs.length) return;
    var pulseIO = makeIO(0.5, function (e) {
      if (!e.isIntersecting) return;
      var id = e.target.getAttribute('data-pin-id');
      var pin = pb.querySelector('[data-pin="' + id + '"]');
      if (!pin) return;
      pin.classList.remove('pulse');
      // restart animation
      void pin.offsetWidth;
      pin.classList.add('pulse');
    });
    refs.forEach(function (r) { pulseIO.observe(r); });
  })();

  /* ============================================================
     TRANSITIONS + AMBIENT (format-agnostic)
     ============================================================ */

  /* -------- T1. sp-stat-curtain -------- */
  (function () {
    var curtains = $$('.sp-stat-curtain');
    if (!curtains.length) return;
    curtains.forEach(function (curtain) {
      var trigger = document.querySelector('[data-curtain-for="' + curtain.id + '"]');
      if (!trigger) return;
      var raised = false;
      var io = makeIO(0.5, function (e) {
        if (e.isIntersecting && !raised) {
          raised = true;
          curtain.classList.add('is-rising');
          setTimeout(function () {
            curtain.classList.remove('is-rising');
            curtain.classList.add('is-retracting');
            setTimeout(function () { curtain.classList.remove('is-retracting'); }, 800);
          }, 1200);
        }
      });
      io.observe(trigger);
    });
  })();

  /* -------- T2. sp-page-fold -------- */
  (function () {
    var folds = $$('.sp-page-fold');
    if (!folds.length) return;
    var io = makeIO(0.4, function (e) {
      if (e.isIntersecting) { e.target.classList.add('is-folded'); }
    });
    folds.forEach(function (f) { io.observe(f); });
  })();

  /* -------- A1. sp-chapter-beads --------
     v8.3: beads are now wired by the UNIVERSAL base controller above
     (lines ~137–255). Short-circuit here to avoid duplicate wiring.
     Left in place as a guard so any legacy empty aside still inerts
     cleanly on older pre-rendered HTML. */
  (function () {
    return; // handled by universal base controller
    /* eslint-disable */
    var beads = $('.sp-chapter-beads');
    var chapters = $$('[data-sp-chapter]');
    if (!beads || !chapters.length) return;

    // Build beads if container is empty
    if (!beads.children.length) {
      chapters.forEach(function (ch, i) {
        var b = document.createElement('button');
        b.className = 'cb-bead';
        b.setAttribute('aria-label', ch.getAttribute('data-sp-chapter-title') || ('Chapter ' + (i + 1)));
        b.dataset.cIndex = i;
        var fill = document.createElement('span');
        fill.className = 'cb-fill';
        b.appendChild(fill);
        var tip = document.createElement('span');
        tip.className = 'cb-tip';
        tip.textContent = ch.getAttribute('data-sp-chapter-title') || ('Chapter ' + (i + 1));
        b.appendChild(tip);
        b.addEventListener('click', function () {
          ch.scrollIntoView({ behavior: prefersReduced ? 'auto' : 'smooth', block: 'start' });
        });
        beads.appendChild(b);
      });
    }

    // Activate after first scroll
    var activated = false;
    function activate() {
      if (activated) return;
      activated = true;
      document.body.classList.add('sp-beads-ready');
    }
    window.addEventListener('scroll', activate, { once: true, passive: true });

    var beadEls = $$('.cb-bead', beads);
    var current = -1;
    var ticking = false;

    function tick() {
      ticking = false;
      var vh = window.innerHeight;
      var midY = vh * 0.4;
      var found = -1;
      var inProg = 0;
      for (var i = 0; i < chapters.length; i++) {
        var rect = chapters[i].getBoundingClientRect();
        if (rect.top <= midY && rect.bottom > midY) {
          found = i;
          var span = rect.height;
          var done = midY - rect.top;
          inProg = span > 0 ? Math.max(0, Math.min(1, done / span)) : 0;
          break;
        } else if (rect.top > midY) {
          // we're before this chapter — the previous one (i-1) might be passing out
          break;
        }
      }
      // Update beads
      beadEls.forEach(function (b, i) {
        b.classList.toggle('passed', i < found);
        b.classList.toggle('active', i === found);
        var fill = b.querySelector('.cb-fill');
        if (fill) fill.style.setProperty('--cb-progress', i === found ? inProg.toFixed(3) : (i < found ? '1' : '0'));
      });
      // Expose chapter progress for sp-horizon
      document.documentElement.style.setProperty('--sp-chapter-progress', inProg.toFixed(3));
      // Expose next-ground colour for sp-horizon
      var next = chapters[found + 1];
      if (next) {
        var ng = next.getAttribute('data-sp-ground-color');
        if (ng) {
          document.documentElement.style.setProperty('--sp-next-ground', ng);
          document.documentElement.style.setProperty('--sp-next-ground-fade', ng + '00');
        }
      }
      if (found !== current) current = found;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(tick); }
    }, { passive: true });
    window.addEventListener('resize', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(tick); }
    }, { passive: true });
    tick();
  })();

  /* sp-horizon piggybacks on the beads tick (above) for its CSS vars.
     Nothing else to wire — CSS handles height/opacity from
     --sp-chapter-progress and --sp-next-ground. */

})();

/* ===================================================================
   HOLIDAY IDENTITY — live countdown controller (v8.12)
   Activates on body.is-special[data-special="countdown"] only.
   Field Guide uses the same .hol-countdown markup but typically displays
   a static target date; if Field Guide carries a live grid, this also
   drives it. Reads target from data-target ISO string on the wrapper.
   Reduced-motion guard: tick still runs (numbers update once on load),
   but the flip-pop animation is suppressed by CSS.
   =================================================================== */
(function () {
  if (!document.body.classList.contains('is-special')) return;
  var fmt = document.body.getAttribute('data-special');
  if (fmt !== 'countdown' && fmt !== 'field-guide') return;

  var grids = document.querySelectorAll('.hol-countdown');
  if (!grids.length) return;

  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function pad(n, w) { w = w || 2; n = String(n); while (n.length < w) n = '0' + n; return n; }

  function tickOne(grid) {
    var iso = grid.getAttribute('data-target');
    if (!iso) return;
    var target = new Date(iso);
    if (isNaN(target.getTime())) return;
    var diff = target - new Date();
    if (diff < 0) diff = 0;
    var s = Math.floor(diff / 1000);
    var d = Math.floor(s / 86400); s -= d * 86400;
    var h = Math.floor(s / 3600);  s -= h * 3600;
    var m = Math.floor(s / 60);    s -= m * 60;
    var cells = grid.querySelectorAll('[data-cd]');
    cells.forEach(function (el) {
      var k = el.getAttribute('data-cd');
      var newVal;
      if (k === 'days')  newVal = pad(d, d >= 100 ? 3 : 2);
      else if (k === 'hours') newVal = pad(h);
      else if (k === 'mins')  newVal = pad(m);
      else if (k === 'secs')  newVal = pad(s);
      if (newVal !== undefined && el.textContent !== newVal) {
        el.textContent = newVal;
        if (k === 'secs' && !reduceMotion) {
          el.classList.remove('is-flipping');
          void el.offsetWidth; // restart anim
          el.classList.add('is-flipping');
        }
      }
    });
  }

  function tick() { grids.forEach(tickOne); }
  tick();
  if (!reduceMotion) setInterval(tick, 1000);
})();

/* ===================================================================
   HOLIDAY MOTION CONTROLLER (v8.13.1)

   Adds scroll-driven motion to Countdown + Field Guide issues.
   Pairs with 38-holiday-motion.css. All work is gated behind
   body.is-special[data-special=countdown|field-guide], so this
   block is a no-op on every other format.

   What it does:
     1. Tags major .hol-* blocks with .hm-rise (and .from-left /
        .from-right where relevant) so writers don't need to touch
        existing HTML to opt in.
     2. IntersectionObserver fades each block in once it enters
        the viewport (.is-in).
     3. requestAnimationFrame scroll loop writes --hm-scroll on
        the .hol-cover only while the cover is in view, driving
        parallax on the back-num / back-script watermarks.
     4. Pointer/touch tap on hover-driven elements (polaroid,
        wonder, unmissable, anchor) adds .is-active for 1.2s so
        the photo unrotates without a mouse.
     5. Pauses .hol-marquee__track during active touchmove so the
        moving text doesn't fight the user's finger drag.
     6. Injects a sticky folio badge (Roman numeral I / II) and
        switches its label as the reader crosses from Half I to
        Half II.
     7. body.hol-motion-ready is added on init + a 2s safety
        backstop forces every .hm-rise to its visible state even
        if the observer pipeline fails.

   Reduced motion: every motion path short-circuits. Only the
   .hm-rise reveal is suppressed by setting all elements visible
   immediately (rest state); the folio badge is still positioned
   but its transitions are killed by CSS.
   =================================================================== */
(function () {
  if (!document.body.classList.contains('is-special')) return;
  var fmt = document.body.getAttribute('data-special');
  if (fmt !== 'countdown' && fmt !== 'field-guide') return;

  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ----- 1. Auto-tag major blocks with .hm-rise ------------------- */
  /* Each selector → blocks that should animate in. We mark them on
     init so the CSS opacity:0 / transform:translate kicks in before
     the IntersectionObserver wires up. */
  var RISE_SELECTORS = [
    '.hol-kicker-strip',
    '.hol-half__opener',
    '.hol-half__opener-tag',
    '.hol-half__opener-title',
    '.hol-half__opener-subtitle',
    '.hol-half__opener-pills',
    '.hol-anchor',
    '.hol-wonder',
    '.hol-unmissable',
    '.hol-dont-miss',
    '.hol-polaroid',
    '.hol-postcard',
    '.hol-stamp',
    '.hol-chalkboard',
    '.hol-transit',
    '.hol-meanwhile__title',
    '.hol-subscribe',
    '.hol-marquee'
  ];

  RISE_SELECTORS.forEach(function (sel) {
    var nodes = document.querySelectorAll(sel);
    Array.prototype.forEach.call(nodes, function (n) {
      n.classList.add('hm-rise');
    });
  });

  /* Stagger pieces inside .hol-half__opener so they cascade. */
  document.querySelectorAll('.hol-half__opener').forEach(function (opener) {
    var tag = opener.querySelector('.hol-half__opener-tag');
    var title = opener.querySelector('.hol-half__opener-title');
    var sub = opener.querySelector('.hol-half__opener-subtitle');
    var pills = opener.querySelector('.hol-half__opener-pills');
    if (tag)   tag.classList.add('delay-1');
    if (title) title.classList.add('delay-2');
    if (sub)   sub.classList.add('delay-3');
    if (pills) pills.classList.add('delay-3');
  });

  /* Side-direction hints for .hol-wonder / .hol-unmissable.
     Default is from-left for normal, from-right for --reverse. */
  document.querySelectorAll('.hol-marquee').forEach(function (m) {
    m.classList.add('from-left');
  });

  /* Body class so .hm-rise:not(.hol-motion-ready) safety guard
     releases. Without this class, CSS keeps every .hm-rise fully
     visible — no FOUC if JS fails. */
  document.body.classList.add('hol-motion-ready');

  /* Safety backstop — if anything below fails, every .hm-rise
     ends up .is-in within 2.4s so nothing stays hidden. */
  var safetyTimer = setTimeout(function () {
    document.querySelectorAll('.hm-rise').forEach(function (el) {
      el.classList.add('is-in');
    });
  }, 2400);

  /* If user prefers reduced motion: reveal everything immediately
     and skip the rest. */
  if (reduceMotion) {
    document.querySelectorAll('.hm-rise').forEach(function (el) {
      el.classList.add('is-in');
    });
    clearTimeout(safetyTimer);
    /* still install folio badge for context, but its transitions
       are killed by the reduced-motion CSS block. */
  }

  /* ----- 2. IntersectionObserver reveal --------------------------- */
  if (!reduceMotion && 'IntersectionObserver' in window) {
    var revealObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-in');
          revealObs.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.08,
      rootMargin: '0px 0px -8% 0px'
    });
    document.querySelectorAll('.hm-rise').forEach(function (el) {
      revealObs.observe(el);
    });
  }

  /* ----- 3. Cover parallax ---------------------------------------- */
  var cover = document.querySelector('.hol-cover');
  if (cover && !reduceMotion) {
    var coverInView = true;
    var ticking = false;
    var coverObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) { coverInView = e.isIntersecting; });
    }, { threshold: [0, 0.05, 0.95, 1] });
    coverObs.observe(cover);

    function updateCoverParallax() {
      ticking = false;
      if (!coverInView) {
        cover.style.removeProperty('--hm-scroll');
        return;
      }
      var rect = cover.getBoundingClientRect();
      /* Use a px value (capped) representing how far the cover has
         scrolled past the top of the viewport. */
      var y = Math.max(0, -rect.top);
      /* Cap at cover height so we never push the watermark too far. */
      var capped = Math.min(y, cover.offsetHeight);
      cover.style.setProperty('--hm-scroll', capped + 'px');
    }
    window.addEventListener('scroll', function () {
      if (!ticking) {
        requestAnimationFrame(updateCoverParallax);
        ticking = true;
      }
    }, { passive: true });
    updateCoverParallax();
  }

  /* ----- 4. Tap-to-unrotate for hover-driven elements ------------- */
  var TAPPABLE = ['.hol-polaroid', '.hol-wonder', '.hol-unmissable', '.hol-anchor'];
  TAPPABLE.forEach(function (sel) {
    document.querySelectorAll(sel).forEach(function (el) {
      el.addEventListener('pointerdown', function () {
        el.classList.add('is-active');
      }, { passive: true });
      el.addEventListener('pointerleave', function () {
        /* small delay so the user sees the unrotated state briefly */
        setTimeout(function () { el.classList.remove('is-active'); }, 1200);
      }, { passive: true });
      el.addEventListener('pointerup', function () {
        setTimeout(function () { el.classList.remove('is-active'); }, 1200);
      }, { passive: true });
    });
  });

  /* ----- 5. Pause marquee during touch drag ----------------------- */
  var marqueeTracks = document.querySelectorAll('.hol-marquee__track');
  if (marqueeTracks.length && !reduceMotion) {
    var pauseTimer = null;
    function pauseAll() {
      Array.prototype.forEach.call(marqueeTracks, function (t) {
        t.classList.add('hm-pause');
      });
      if (pauseTimer) clearTimeout(pauseTimer);
      pauseTimer = setTimeout(function () {
        Array.prototype.forEach.call(marqueeTracks, function (t) {
          t.classList.remove('hm-pause');
        });
      }, 280);
    }
    window.addEventListener('touchmove', pauseAll, { passive: true });
    window.addEventListener('touchstart', pauseAll, { passive: true });
  }

  /* ----- 6. Folio badge ------------------------------------------- */
  /* Inject a sticky badge that shows the current half. Tracks the
     most-intersecting .hol-half--one / .hol-half--two and updates
     its label + palette accordingly. */
  (function () {
    var halves = document.querySelectorAll('.hol-half--one, .hol-half--two');
    if (!halves.length) return;

    var badge = document.createElement('div');
    badge.className = 'hol-folio-badge';
    badge.setAttribute('aria-hidden', 'true');
    badge.textContent = 'I';
    document.body.appendChild(badge);

    if (!('IntersectionObserver' in window)) {
      badge.classList.add('is-on');
      return;
    }

    var visible = new Map();
    var folioObs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          visible.set(e.target, e.intersectionRatio);
        } else {
          visible.delete(e.target);
        }
      });
      /* Pick the half with the highest visibility ratio. */
      var best = null, bestRatio = 0;
      visible.forEach(function (ratio, el) {
        if (ratio > bestRatio) { bestRatio = ratio; best = el; }
      });
      if (best) {
        if (best.classList.contains('hol-half--two')) {
          badge.textContent = 'II';
          badge.setAttribute('data-half', '2');
        } else {
          badge.textContent = 'I';
          badge.setAttribute('data-half', '1');
        }
        badge.classList.add('is-on');
      } else {
        badge.classList.remove('is-on');
      }
    }, {
      threshold: [0, 0.2, 0.5, 0.8, 1]
    });
    halves.forEach(function (h) { folioObs.observe(h); });
  })();
})();

/* ===================================================================
   HOLIDAY MOTION EXTRAS (v8.13.2)

   Eight extra behaviours layered on top of the tier-13 controller.
   Each one is wrapped in its own block so any single behaviour can
   be commented out without affecting the others.

   Behaviours implemented here:
     01 · Half edge crossfade driver (--hm-edge custom property)
     02 · Countdown count-up on first viewport entry
     03 · Anchor photo ken-burns scroll driver (--hm-progress)
     04 · Polaroid weight-drop tape twitch (.hm-landed flag)
     05 · Don't Miss numeral count-up (data-num + .is-counting)
     06 · Marquee on-entry burst (.hm-burst for 900ms)
     07 · Cover dek typewriter (character-wrap + .hm-typewriter)
     14 · Half ground parallax (--hm-half-scroll custom property)

   Gating: body.is-special[data-special="countdown"|"field-guide"]
   and prefers-reduced-motion checked at IIFE top.
   =================================================================== */
(function () {
  if (!document.body.classList.contains('is-special')) return;
  var fmt = document.body.getAttribute('data-special');
  if (fmt !== 'countdown' && fmt !== 'field-guide') return;

  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ─────────────────────────────────────────────────────────
     07 · COVER DEK TYPEWRITER
     Wrap each visible character of the dek in a <span class="hm-typed">,
     set --hm-char-index for the staggered CSS animation-delay, and
     add a .hm-typed-done flag once typing completes (to hide caret).
     Skipped if reduced-motion.
     ───────────────────────────────────────────────────────── */
  if (!reduceMotion) {
    var dek = document.querySelector('.hol-cover__dek');
    if (dek && !dek.classList.contains('hm-typewriter')) {
      var text = dek.textContent || '';
      // Wrap each char in a span. Preserve whitespace by wrapping
      // spaces too — they still animate, just look identical.
      var frag = document.createDocumentFragment();
      var idx = 0;
      for (var i = 0; i < text.length; i++) {
        var ch = text.charAt(i);
        var span = document.createElement('span');
        span.className = 'hm-typed';
        span.textContent = ch;
        span.style.setProperty('--hm-char-index', idx);
        frag.appendChild(span);
        idx++;
      }
      dek.textContent = '';
      dek.appendChild(frag);
      dek.classList.add('hm-typewriter');
      // Hide caret once last character has revealed.
      var totalMs = 200 + (idx * 18) + 400;
      setTimeout(function () { dek.classList.add('hm-typed-done'); }, totalMs);
    }
  }

  /* ─────────────────────────────────────────────────────────
     02 · COUNTDOWN COUNT-UP ON FIRST VIEW
     The tier-12 controller writes the live tick every second. We
     intercept the FIRST render only — animate from 0 up to the
     starting value over ~900ms, then let the live tick take over.
     We detect first render by checking a one-shot flag on the grid.
     ───────────────────────────────────────────────────────── */
  if (!reduceMotion && 'IntersectionObserver' in window) {
    var grids = document.querySelectorAll('.hol-countdown');
    if (grids.length) {
      var coObs = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          var grid = e.target;
          if (grid.dataset.hmCounted === '1') return;
          grid.dataset.hmCounted = '1';
          var cells = grid.querySelectorAll('[data-cd]');
          cells.forEach(function (cell) {
            var target = parseInt(cell.textContent, 10);
            if (isNaN(target) || target < 0) return;
            var pad = cell.textContent.length;
            var start = performance.now();
            var dur = 900;
            function pad0(n, w) { n = String(n); while (n.length < w) n = '0' + n; return n; }
            function step(now) {
              var p = Math.min((now - start) / dur, 1);
              var eased = 1 - Math.pow(1 - p, 3);
              cell.textContent = pad0(Math.floor(target * eased), pad);
              if (p < 1) requestAnimationFrame(step);
              else cell.textContent = pad0(target, pad);
            }
            cell.textContent = pad0(0, pad);
            requestAnimationFrame(step);
          });
          coObs.unobserve(grid);
        });
      }, { threshold: 0.4 });
      grids.forEach(function (g) { coObs.observe(g); });
    }
  }

  /* ─────────────────────────────────────────────────────────
     05 · DON'T MISS NUMERAL COUNT-UP
     Switch to attr-driven numerals so we can write data-num
     during the count-up animation. The CSS in tier 39 has the
     .is-counting flag that picks up data-num via attr().
     ───────────────────────────────────────────────────────── */
  if (!reduceMotion && 'IntersectionObserver' in window) {
    var dms = document.querySelectorAll('.hol-dont-miss');
    if (dms.length) {
      var dmObs = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          var dm = e.target;
          if (dm.dataset.hmCounted === '1') return;
          dm.dataset.hmCounted = '1';
          var items = dm.querySelectorAll('.hol-dont-miss__list li');
          dm.classList.add('is-counting');
          items.forEach(function (li, i) {
            var target = i + 1;
            li.setAttribute('data-num', '00');
            // Stagger start matches the tier-13 list-item entry delays
            // (320ms for #1, +80ms per subsequent item).
            var startDelay = 320 + (i * 80);
            setTimeout(function () {
              var start = performance.now();
              var dur = 480;
              function pad0(n) { n = String(n); return n.length < 2 ? '0' + n : n; }
              function step(now) {
                var p = Math.min((now - start) / dur, 1);
                var eased = 1 - Math.pow(1 - p, 3);
                // For small targets (1..N), use ceil with a small
                // floor guard so the counter climbs visibly through
                // intermediate values rather than sitting at 0 until
                // the last frame.
                var raw = target * eased;
                var shown = raw < 0.05 ? 0 : Math.max(1, Math.ceil(raw));
                li.setAttribute('data-num', pad0(shown));
                if (p < 1) requestAnimationFrame(step);
                else li.setAttribute('data-num', pad0(target));
              }
              requestAnimationFrame(step);
            }, startDelay);
          });
          dmObs.unobserve(dm);
        });
      }, { threshold: 0.25 });
      dms.forEach(function (dm) { dmObs.observe(dm); });
    }
  }

  /* ─────────────────────────────────────────────────────────
     06 · MARQUEE ON-ENTRY BURST
     Add .hm-burst to the track for 900ms on first viewport entry
     so the loop briefly runs at 3x speed, then settles.
     ───────────────────────────────────────────────────────── */
  if (!reduceMotion && 'IntersectionObserver' in window) {
    var tracks = document.querySelectorAll('.hol-marquee__track');
    if (tracks.length) {
      var mObs = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          var track = e.target;
          if (track.dataset.hmBursted === '1') return;
          track.dataset.hmBursted = '1';
          track.classList.add('hm-burst');
          setTimeout(function () {
            track.classList.remove('hm-burst');
          }, 900);
          mObs.unobserve(track);
        });
      }, { threshold: 0.2 });
      tracks.forEach(function (t) { mObs.observe(t); });
    }
  }

  /* ─────────────────────────────────────────────────────────
     04 · POLAROID WEIGHT-DROP / TAPE TWITCH
     After the tier-13 entry transition lands (~640ms), add
     .hm-landed to fire the tape-twitch keyframe in tier 39.
     ───────────────────────────────────────────────────────── */
  if (!reduceMotion && 'IntersectionObserver' in window) {
    var pls = document.querySelectorAll('.hol-polaroid');
    if (pls.length) {
      var plObs = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          var pl = e.target;
          if (pl.dataset.hmLanded === '1') return;
          pl.dataset.hmLanded = '1';
          // Tier-13 entry transition runs 720ms by default. Fire tape
          // twitch at the tail of the transition.
          setTimeout(function () { pl.classList.add('hm-landed'); }, 640);
          plObs.unobserve(pl);
        });
      }, { threshold: 0.3 });
      pls.forEach(function (pl) { plObs.observe(pl); });
    }
  }

  /* ─────────────────────────────────────────────────────────
     03 · ANCHOR KEN-BURNS SCROLL DRIVER
     For each .hol-anchor in view, write --hm-progress on its
     .hol-anchor__photo based on the photo's normalised position
     in the viewport. Driven by a single rAF loop bound to scroll.
     ───────────────────────────────────────────────────────── */
  var anchors = Array.prototype.slice.call(document.querySelectorAll('.hol-anchor'));
  if (!reduceMotion && anchors.length) {
    var anchorsInView = new Set();
    if ('IntersectionObserver' in window) {
      var aObs = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) anchorsInView.add(e.target);
          else anchorsInView.delete(e.target);
        });
      }, { rootMargin: '20% 0px 20% 0px' });
      anchors.forEach(function (a) { aObs.observe(a); });
    } else {
      anchors.forEach(function (a) { anchorsInView.add(a); });
    }

    var anchorTicking = false;
    function updateAnchors() {
      anchorTicking = false;
      var vh = window.innerHeight || document.documentElement.clientHeight;
      anchorsInView.forEach(function (a) {
        var photo = a.querySelector('.hol-anchor__photo');
        if (!photo) return;
        var rect = photo.getBoundingClientRect();
        var centre = rect.top + rect.height / 2;
        // 0 when centre is at top of viewport, 1 when at bottom.
        var progress = centre / vh;
        // Clamp to [0,1] so we don't push transforms out of range.
        progress = Math.max(0, Math.min(1, progress));
        photo.style.setProperty('--hm-progress', progress.toFixed(3));
      });
    }
    window.addEventListener('scroll', function () {
      if (!anchorTicking) {
        requestAnimationFrame(updateAnchors);
        anchorTicking = true;
      }
    }, { passive: true });
    updateAnchors();
  }

  /* ─────────────────────────────────────────────────────────
     14 · HALF GROUND PARALLAX
     For each .hol-half in view, write --hm-half-scroll based on
     how far the half has scrolled past the top of the viewport.
     Values clamp at the half's own height so the parallax never
     pushes the ground further than the half itself.

     01 · EDGE CROSSFADE
     For each .hol-half, write --hm-edge based on how close its
     bottom/top edge is to the transit centre. 0 when far away,
     1 when the edge is at the viewport centre.

     Combined into a single rAF loop with the anchor pass for
     efficiency — fewer scroll listeners, fewer rAF schedules.
     ───────────────────────────────────────────────────────── */
  var halves = Array.prototype.slice.call(document.querySelectorAll('.hol-half'));
  if (!reduceMotion && halves.length) {
    /* Inject .hm-edge-overlay element into each half. Tier 39 CSS
       paints the crossfade tint on this overlay with mix-blend-mode
       so the warm/cool tint passes through content cards (not just
       the dark gutters). Empty div, position:absolute via CSS. */
    halves.forEach(function (h) {
      if (!h.querySelector(':scope > .hm-edge-overlay')) {
        var ov = document.createElement('div');
        ov.className = 'hm-edge-overlay';
        ov.setAttribute('aria-hidden', 'true');
        h.appendChild(ov);
      }
    });
    var halvesInView = new Set();
    if ('IntersectionObserver' in window) {
      var hObs = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (e.isIntersecting) halvesInView.add(e.target);
          else halvesInView.delete(e.target);
        });
      }, { rootMargin: '50% 0px 50% 0px' });
      halves.forEach(function (h) { hObs.observe(h); });
    } else {
      halves.forEach(function (h) { halvesInView.add(h); });
    }

    var halvesTicking = false;
    function updateHalves() {
      halvesTicking = false;
      var vh = window.innerHeight || document.documentElement.clientHeight;
      halvesInView.forEach(function (h) {
        var rect = h.getBoundingClientRect();
        // 14 · Parallax: distance the half has scrolled past top of viewport
        var pastTop = -rect.top;
        // Clamp to half height so parallax doesn't accelerate forever.
        pastTop = Math.max(0, Math.min(pastTop, rect.height));
        h.style.setProperty('--hm-half-scroll', pastTop + 'px');

        // 01 · Edge crossfade:
        // For Half I, edge intensity ramps up as bottom approaches
        // viewport (last 480px of the half).
        // For Half II, edge intensity ramps down as top moves past
        // viewport (first 480px after the transit).
        // 520px ramp matches the CSS gradient extent in tier 39.
        var edge = 0;
        if (h.classList.contains('hol-half--one')) {
          var distFromBottom = rect.bottom - vh;
          if (distFromBottom <= 0) edge = 1;
          else if (distFromBottom < 520) edge = 1 - (distFromBottom / 520);
          else edge = 0;
        } else if (h.classList.contains('hol-half--two')) {
          var topPast = -rect.top;
          if (topPast < 0) edge = 0;
          else if (topPast < 520) edge = 1 - (topPast / 520);
          else edge = 0;
        }
        h.style.setProperty('--hm-edge', edge.toFixed(3));
      });
    }
    window.addEventListener('scroll', function () {
      if (!halvesTicking) {
        requestAnimationFrame(updateHalves);
        halvesTicking = true;
      }
    }, { passive: true });
    updateHalves();
  }

})();

/* ============================================================
   v8.24.5 — Non-holiday special editions: scroll-reveal + count-up.
   (1) Reveals content blocks on entry with a gentle rise, staggered within
       groups (stat cells, Keep Digging cards), and a sideways slide for gutter
       marginalia. (2) Counts stat numbers up when a stat row enters view.
   Self-contained; does not touch the universal .reveal observer. Off under
   reduced-motion; a 2.6s safety timeout force-reveals everything if observers
   never fire.
   ============================================================ */
(function () {
  var b = document.body;
  if (!b || !b.classList.contains('is-special')) return;
  var ds = b.getAttribute('data-special');
  if (ds === 'countdown' || ds === 'field-guide') return;
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---- 1. Reveal on scroll (incl. body flair) ----
  // Figures fade in (opacity only) so the parallax transform isn't overwritten.
  [].slice.call(document.querySelectorAll('.chapter figure, .foreword figure'))
    .forEach(function (el) { el.classList.add('sp-fade'); });
  // Body paragraphs ease up as they enter — flair through the prose itself.
  [].slice.call(document.querySelectorAll('.chapter-body > p, .foreword-body > p, .argument-stance > p'))
    .forEach(function (el) { el.classList.add('sp-rise', 'sp-rise--soft'); });
  // Other blocks rise; marginalia slides from the right; sub-labels from the left.
  [].slice.call(document.querySelectorAll('.chapter blockquote.pullquote, .chapter .bignum-row, .chapter .argument, .argument, .chapter table, .chapter-body > .is-wide:not(figure), .keep-digging .kd-item, .chapter .chapter-head, .chapter .marginalia, .chapter .sp-kicker'))
    .forEach(function (el) {
      el.classList.add('sp-rise');
      if (el.classList.contains('marginalia')) el.classList.add('sp-rise--right');
    });
  // Stagger cascade within groups (Keep Digging cards, stat cells).
  [['.keep-digging', '.kd-item'], ['.bignum-row', '.bignum']].forEach(function (g) {
    [].slice.call(document.querySelectorAll(g[0])).forEach(function (group) {
      [].slice.call(group.querySelectorAll(g[1])).forEach(function (item, i) {
        item.classList.add('sp-rise');
        item.style.transitionDelay = (i * 80) + 'ms';
      });
    });
  });

  function showAll() {
    document.querySelectorAll('.sp-rise').forEach(function (el) { el.classList.add('sp-rise--in'); });
    document.querySelectorAll('.sp-fade').forEach(function (el) { el.classList.add('sp-fade--in'); });
  }

  if (reduce || !('IntersectionObserver' in window)) {
    showAll();
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (!e.isIntersecting) return;
        e.target.classList.add(e.target.classList.contains('sp-fade') ? 'sp-fade--in' : 'sp-rise--in');
        io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -7% 0px', threshold: 0.06 });
    document.querySelectorAll('.sp-rise, .sp-fade').forEach(function (el) { io.observe(el); });
    setTimeout(showAll, 2600);

    // ---- 2. Count-up on stat numbers ----
    var nums = [].slice.call(document.querySelectorAll('.bignum-value'));
    if (nums.length) {
      var cio = new IntersectionObserver(function (entries) {
        entries.forEach(function (e) {
          if (!e.isIntersecting) return;
          var el = e.target; cio.unobserve(el);
          var txt = (el.getAttribute('data-target') || el.textContent).trim();
          var raw = txt.replace(/[^0-9.]/g, '');
          var num = parseFloat(raw);
          if (isNaN(num)) return;
          var pre = txt.match(/^[^0-9.]*/)[0] || '';
          var suf = txt.match(/[^0-9.]*$/)[0] || '';
          var isInt = num === Math.floor(num);
          var t0 = performance.now();
          (function step(now) {
            var p = Math.min((now - t0) / 900, 1);
            var c = num * (1 - Math.pow(1 - p, 3));
            el.textContent = pre + (isInt ? Math.round(c).toLocaleString() : c.toFixed(1)) + suf;
            if (p < 1) requestAnimationFrame(step); else el.textContent = txt;
          })(performance.now());
        });
      }, { threshold: 0.2 });
      nums.forEach(function (el) { cio.observe(el); });
    }
  }
})();

/* ============================================================
   v8.24.6 — Subtle parallax for non-holiday special editions.
   Floated portraits/coins + image-quotes drift vertically within their
   overflow clip as they cross the viewport; the cover content drifts and
   fades as you scroll past it. Wide maps/charts/diagrams are NOT selected,
   so nothing with edge labels gets cropped. rAF + passive scroll; fully off
   under reduced-motion (the CSS crop/scale only applies once this adds
   .sp-parallax-ready, so reduced-motion / no-JS readers see static images).
   ============================================================ */
(function () {
  var b = document.body;
  if (!b || !b.classList.contains('is-special')) return;
  var ds = b.getAttribute('data-special');
  if (ds === 'countdown' || ds === 'field-guide') return;
  if (window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;

  // Parallax only FULL-WIDTH figures (no text beside them), so the drift can be
  // bold and never reads as a floated image misaligned against wrapping text.
  // The whole figure moves (image stays correctly framed — no crop). Plus the cover.
  var figs = [].slice.call(document.querySelectorAll('.chapter figure.is-wide, .chapter figure.is-fullbleed'));
  var cover = document.querySelector('header.cover .cover-body');
  if (!figs.length && !cover) return;

  b.classList.add('sp-parallax-ready');

  var ticking = false;
  function update() {
    ticking = false;
    var vh = window.innerHeight || document.documentElement.clientHeight;
    for (var i = 0; i < figs.length; i++) {
      var f = figs[i];
      var r = f.getBoundingClientRect();
      if (r.bottom < -160 || r.top > vh + 160) continue;
      var ratio = ((r.top + r.height / 2) - vh / 2) / vh;   // -0.5 .. 0.5
      var px = Math.max(-22, Math.min(22, -ratio * 44));
      f.style.transform = 'translateY(' + px.toFixed(1) + 'px)';
    }
    if (cover) {
      var sy = window.pageYOffset || document.documentElement.scrollTop || 0;
      cover.style.transform = 'translateY(' + Math.min(sy * 0.22, 160).toFixed(1) + 'px)';
      cover.style.opacity = String(Math.max(0, 1 - sy / 680));
    }
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(update); } }
  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });
  update();
})();
