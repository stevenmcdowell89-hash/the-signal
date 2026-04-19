/* ============================================================
   THE SIGNAL — Motion & Scroll Behaviour
   Implements §5 from visual-language.md.

   §5.1 Continuous scroll-linked motion:
     - Parallax on hero portraits
     - Section-to-section colour flood
     - Sticky images with scrolling captions (CSS-driven, JS unsticks)
     - Count-up numerals
     - Colour-adaptive masthead
     - Footer rising card
     - Image progressive reveal (object-position pan)
     - Cover photo scale-down

   §5.2 Discrete entry motion:
     - Line-by-line head entry
     - Dropcap settle
     - .reveal fade-ups

   §5.3 Load state (Signal's own): body opacity 0 → fade in order
   §5.4 Reduced motion: respected throughout
   ============================================================ */

(function () {
  'use strict';

  const prefersReduced =
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const docEl = document.documentElement;
  const body = document.body;

  /* ------------------------------------------------------------
     §5.3 LOAD STATE — fade body, stagger cover
     ------------------------------------------------------------ */

  function orchestrateLoad() {
    // Masthead + seal draw in first (150ms)
    requestAnimationFrame(() => {
      body.classList.add('loaded');

      // Cover photo fades in (400ms)
      setTimeout(() => {
        const coverImg = document.querySelector('.cover__hero img');
        if (coverImg) {
          coverImg.style.transition = 'opacity 400ms ease-out, transform 0.5s ease-out';
          coverImg.style.opacity = '1';
        }
      }, 150);

      // Cover headline lines stagger (60ms each)
      setTimeout(() => {
        const coverHead = document.querySelector('.cover__headline.ln');
        if (coverHead) {
          coverHead.classList.add('in');
          const lines = coverHead.querySelectorAll(':scope > span');
          lines.forEach((line, i) => {
            line.style.transitionDelay = i * 60 + 'ms';
          });
        }
      }, 550);
    });
  }

  /* ------------------------------------------------------------
     §5.2 LINE-BY-LINE HEAD ENTRY
     Splits .ln heads into span-per-line on IntersectionObserver(25%)
     ------------------------------------------------------------ */

  function splitLines(el) {
    if (el.dataset.split === 'true') return;
    // If already has <span> children from template, leave it alone
    if (el.querySelector(':scope > span')) {
      el.dataset.split = 'true';
      return;
    }
    const text = el.textContent.trim();
    // Split by <br> wouldn't apply here; simpler: split by explicit breaks
    // Since our heads typically use <br> we first convert <br> to splits.
    const htmlParts = el.innerHTML.split(/<br\s*\/?>/i);
    if (htmlParts.length > 1) {
      el.innerHTML = htmlParts
        .map((part) => '<span>' + part.trim() + '</span>')
        .join('');
    } else {
      // No <br>: wrap whole thing in single span
      el.innerHTML = '<span>' + el.innerHTML + '</span>';
    }
    el.dataset.split = 'true';
  }

  function setupHeadEntry() {
    const heads = document.querySelectorAll('.ln');
    heads.forEach(splitLines);

    if (!('IntersectionObserver' in window)) {
      heads.forEach((h) => h.classList.add('in'));
      return;
    }

    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const el = entry.target;
            el.classList.add('in');
            const spans = el.querySelectorAll(':scope > span');
            spans.forEach((s, i) => {
              s.style.transitionDelay = i * 60 + 'ms';
            });
            io.unobserve(el);
          }
        });
      },
      { threshold: 0.25 }
    );

    heads.forEach((h) => {
      // Skip cover headline (handled in load orchestrator)
      if (!h.classList.contains('cover__headline')) {
        io.observe(h);
      }
    });
  }

  /* ------------------------------------------------------------
     §5.2 DROPCAP SETTLE & GENERIC REVEAL
     ------------------------------------------------------------ */

  function setupReveal() {
    const targets = document.querySelectorAll('.dropcap, .reveal');
    if (!('IntersectionObserver' in window)) {
      targets.forEach((el) => el.classList.add('in'));
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add('in');
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.2 }
    );
    targets.forEach((t) => io.observe(t));
  }

  /* ------------------------------------------------------------
     §5.1 COUNT-UP NUMERALS
     Trigger at 30% visible. 800ms. Respect reduced motion.
     Elements: .count-up[data-target]
     ------------------------------------------------------------ */

  function countUp(el) {
    const target = parseFloat(el.dataset.target);
    if (isNaN(target)) return;
    if (prefersReduced) {
      el.textContent = formatNumber(target, el.dataset);
      return;
    }
    const duration = 800;
    const start = performance.now();
    const from = 0;
    const suffix = el.dataset.suffix || '';
    const prefix = el.dataset.prefix || '';
    const decimals = parseInt(el.dataset.decimals || '0', 10);

    function tick(now) {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      const val = from + (target - from) * eased;
      el.textContent = prefix + val.toFixed(decimals) + suffix;
      if (t < 1) requestAnimationFrame(tick);
      else el.textContent = prefix + target.toFixed(decimals) + suffix;
    }
    requestAnimationFrame(tick);
  }

  function formatNumber(n, data) {
    const decimals = parseInt((data && data.decimals) || '0', 10);
    return (data.prefix || '') + n.toFixed(decimals) + (data.suffix || '');
  }

  function setupCountUp() {
    const nums = document.querySelectorAll('.count-up');
    if (!('IntersectionObserver' in window)) {
      nums.forEach(countUp);
      return;
    }
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            countUp(entry.target);
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.3 }
    );
    nums.forEach((n) => io.observe(n));
  }

  /* ------------------------------------------------------------
     §5.1 PARALLAX (hero portraits 0.6×) + COVER SCALE-DOWN
     + IMAGE PROGRESSIVE REVEAL (.pan object-position)
     All driven from a single rAF scroll loop.
     ------------------------------------------------------------ */

  const parallaxEls = [];
  const panEls = [];
  let coverImg = null;

  function collectParallax() {
    document.querySelectorAll('.parallax').forEach((el) => {
      parallaxEls.push(el);
    });
    document.querySelectorAll('.pan').forEach((el) => {
      panEls.push(el);
    });
    coverImg = document.querySelector('.cover__hero img');
  }

  function scrollTick() {
    const scrollY = window.scrollY || window.pageYOffset;
    const vh = window.innerHeight;

    // Cover scale-down 1.08 → 1 over 0..30vh
    if (coverImg) {
      const prog = Math.min(1, scrollY / (vh * 0.3));
      const scale = 1.08 - 0.08 * prog;
      coverImg.style.transform = 'scale(' + scale.toFixed(3) + ')';
    }

    if (prefersReduced) return;

    // Parallax 0.6× for each element
    parallaxEls.forEach((el) => {
      const rect = el.getBoundingClientRect();
      const elTop = rect.top + scrollY;
      const offset = (scrollY - elTop) * 0.4; // parallax lag = 0.4 of scroll diff
      el.style.transform = 'translate3d(0, ' + offset.toFixed(1) + 'px, 0)';
    });

    // Image progressive reveal: object-position 0% → 100% as scrolled
    panEls.forEach((el) => {
      const rect = el.getBoundingClientRect();
      const total = rect.height + vh;
      const passed = vh - rect.top;
      const pct = Math.max(0, Math.min(100, (passed / total) * 100));
      el.style.objectPosition = '50% ' + pct.toFixed(1) + '%';
    });
  }

  let scrollRAF = null;

  function onScroll() {
    if (scrollRAF) return;
    scrollRAF = requestAnimationFrame(() => {
      scrollTick();
      updateProgress();
      updateColourFlood();
      updateBackToTop();
      updateColophonRise();
      scrollRAF = null;
    });
  }

  /* ------------------------------------------------------------
     §5.1 SECTION-TO-SECTION COLOUR FLOOD
     A fixed ::before layer with clip-path(inset) driven by scroll.
     The next section's bg colour takes over progressively.
     ------------------------------------------------------------ */

  let sections = [];
  let flood = null;

  function collectSections() {
    sections = Array.from(document.querySelectorAll('.sec, .cover'));
    flood = document.querySelector('.colour-flood');
  }

  function sectionBG(sec) {
    // Read computed bg color from the section. If paper class, use --paper, else bg.
    const styles = getComputedStyle(sec);
    if (sec.classList.contains('paper')) {
      return styles.getPropertyValue('--paper').trim() || styles.backgroundColor;
    }
    if (sec.classList.contains('dark') || sec.classList.contains('cover')) {
      return styles.getPropertyValue('--bg').trim() || styles.backgroundColor;
    }
    return styles.backgroundColor;
  }

  function updateColourFlood() {
    if (!flood || !sections.length) return;
    const vh = window.innerHeight;
    const scrollY = window.scrollY;
    // Find current section (at 50vh line) and next
    let current = sections[0];
    let next = sections[1];
    for (let i = 0; i < sections.length; i++) {
      const rect = sections[i].getBoundingClientRect();
      if (rect.top <= vh * 0.5 && rect.bottom > vh * 0.5) {
        current = sections[i];
        next = sections[i + 1] || null;
        break;
      }
    }
    if (!next) {
      flood.style.clipPath = 'inset(100% 0 0 0)';
      return;
    }
    const nextRect = next.getBoundingClientRect();
    // Progress: from nextRect.top == vh (0) to nextRect.top == 0 (1)
    const progress = Math.max(0, Math.min(1, 1 - nextRect.top / vh));
    if (prefersReduced) {
      // Instant swap at boundary
      if (progress >= 1) {
        flood.style.background = sectionBG(next);
        flood.style.clipPath = 'inset(0 0 0 0)';
      } else {
        flood.style.clipPath = 'inset(100% 0 0 0)';
      }
      return;
    }
    flood.style.background = sectionBG(next);
    flood.style.clipPath = 'inset(' + ((1 - progress) * 100).toFixed(2) + '% 0 0 0)';

    // When fully flooded, reset by moving to next boundary (handled by natural scroll)
    if (progress >= 1) {
      flood.style.clipPath = 'inset(100% 0 0 0)';
    }
  }

  /* ------------------------------------------------------------
     §5.1 COLOUR-ADAPTIVE MASTHEAD
     IntersectionObserver tags body with data-ground="dark"|"paper"
     based on which section is at 50vh.
     ------------------------------------------------------------ */

  function setupGroundObserver() {
    if (!('IntersectionObserver' in window)) return;
    const secs = document.querySelectorAll('.sec, .cover');
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const el = entry.target;
            if (el.classList.contains('paper')) {
              body.dataset.ground = 'paper';
            } else {
              body.dataset.ground = 'dark';
            }
            // Sync seal colour if present
            const seal = el.querySelector('.dispatch-seal');
            if (seal) seal.style.color = getComputedStyle(el).color;
          }
        });
      },
      { rootMargin: '-50% 0px -50% 0px', threshold: 0 }
    );
    secs.forEach((s) => io.observe(s));
  }

  /* ------------------------------------------------------------
     PROGRESS BAR — scroll through document
     ------------------------------------------------------------ */

  function updateProgress() {
    const bar = document.querySelector('.progress-bar');
    if (!bar) return;
    const total = docEl.scrollHeight - window.innerHeight;
    const pct = total > 0 ? (window.scrollY / total) * 100 : 0;
    bar.style.width = pct.toFixed(2) + '%';
  }

  /* ------------------------------------------------------------
     BACK-TO-TOP
     ------------------------------------------------------------ */

  function updateBackToTop() {
    const btn = document.querySelector('.back-to-top');
    if (!btn) return;
    if (window.scrollY > window.innerHeight * 1.5) {
      btn.classList.add('visible');
    } else {
      btn.classList.remove('visible');
    }
  }

  function setupBackToTop() {
    const btn = document.querySelector('.back-to-top');
    if (!btn) return;
    btn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: prefersReduced ? 'auto' : 'smooth' });
    });
  }

  /* ------------------------------------------------------------
     §5.1 COLOPHON RISING CARD
     Colophon translateY driven by approach.
     ------------------------------------------------------------ */

  function updateColophonRise() {
    const colo = document.querySelector('.colophon');
    if (!colo) return;
    if (prefersReduced) {
      colo.classList.add('rise');
      return;
    }
    const rect = colo.getBoundingClientRect();
    const vh = window.innerHeight;
    if (rect.top < vh * 0.9) {
      colo.classList.add('rise');
    }
  }

  /* ------------------------------------------------------------
     DISPATCH SEAL — arc text render
     Takes elements with .dispatch-seal and fills them with the SVG.
     Data comes from data-num / data-month / data-year.
     ------------------------------------------------------------ */

  function renderSeals() {
    const seals = document.querySelectorAll('.dispatch-seal');
    seals.forEach((seal) => {
      if (seal.dataset.rendered === 'true') return;
      const num = seal.dataset.num || '47';
      const month = seal.dataset.month || 'APRIL';
      const year = seal.dataset.year || 'MMXXVI';
      const arcText =
        '· THE SIGNAL · SUNDAY MAGAZINE · NO. ' +
        num +
        ' · ' +
        month +
        ' ' +
        year +
        ' ';
      const repeated = arcText + arcText; // long enough for circumference
      const svgNS = 'http://www.w3.org/2000/svg';
      seal.innerHTML = ''; // clear
      const ring = document.createElementNS(svgNS, 'svg');
      ring.classList.add('dispatch-seal__ring');
      ring.setAttribute('viewBox', '0 0 200 200');
      ring.setAttribute('aria-hidden', 'true');
      const defs = document.createElementNS(svgNS, 'defs');
      const path = document.createElementNS(svgNS, 'path');
      path.setAttribute('id', seal.dataset.pathId || 'seal-path-' + Math.random().toString(36).slice(2, 7));
      path.setAttribute(
        'd',
        'M 100,100 m -82,0 a 82,82 0 1,1 164,0 a 82,82 0 1,1 -164,0'
      );
      path.setAttribute('fill', 'none');
      defs.appendChild(path);
      ring.appendChild(defs);

      // Outer hairline circles
      const circleOuter = document.createElementNS(svgNS, 'circle');
      circleOuter.setAttribute('cx', '100');
      circleOuter.setAttribute('cy', '100');
      circleOuter.setAttribute('r', '96');
      circleOuter.setAttribute('fill', 'none');
      circleOuter.setAttribute('stroke', 'currentColor');
      circleOuter.setAttribute('stroke-width', '0.5');
      circleOuter.setAttribute('opacity', '0.6');
      ring.appendChild(circleOuter);
      const circleInner = document.createElementNS(svgNS, 'circle');
      circleInner.setAttribute('cx', '100');
      circleInner.setAttribute('cy', '100');
      circleInner.setAttribute('r', '68');
      circleInner.setAttribute('fill', 'none');
      circleInner.setAttribute('stroke', 'currentColor');
      circleInner.setAttribute('stroke-width', '0.5');
      circleInner.setAttribute('opacity', '0.4');
      ring.appendChild(circleInner);

      // Arc text
      const textEl = document.createElementNS(svgNS, 'text');
      textEl.classList.add('dispatch-seal__arc-text');
      const textPath = document.createElementNS(svgNS, 'textPath');
      textPath.setAttributeNS(
        'http://www.w3.org/1999/xlink',
        'href',
        '#' + path.id
      );
      textPath.setAttribute('href', '#' + path.id);
      textPath.setAttribute('startOffset', '0');
      textPath.textContent = repeated;
      textEl.appendChild(textPath);
      ring.appendChild(textEl);

      seal.appendChild(ring);

      const hub = document.createElement('div');
      hub.className = 'dispatch-seal__hub';
      hub.textContent = '№ ' + num;
      seal.appendChild(hub);

      seal.dataset.rendered = 'true';
    });
  }

  /* ------------------------------------------------------------
     RIBBON — duplicate track content for seamless loop
     ------------------------------------------------------------ */

  function setupRibbons() {
    document.querySelectorAll('.ribbon__track').forEach((track) => {
      if (track.dataset.doubled === 'true') return;
      track.innerHTML = track.innerHTML + track.innerHTML;
      track.dataset.doubled = 'true';
    });
  }

  /* ------------------------------------------------------------
     INIT
     ------------------------------------------------------------ */

  function init() {
    renderSeals();
    setupRibbons();
    splitAllHeads();
    setupHeadEntry();
    setupReveal();
    setupCountUp();
    collectParallax();
    collectSections();
    setupGroundObserver();
    setupBackToTop();
    orchestrateLoad();
    // Initial tick
    scrollTick();
    updateProgress();
    updateColourFlood();
    updateColophonRise();
  }

  function splitAllHeads() {
    document.querySelectorAll('.ln').forEach(splitLines);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });
})();