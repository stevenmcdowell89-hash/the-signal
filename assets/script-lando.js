(function () {
  'use strict';

  var prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var hasFineHover = window.matchMedia && window.matchMedia('(hover: hover) and (pointer: fine)').matches;

  function onReady(fn) {
    if (document.readyState !== 'loading') fn();
    else document.addEventListener('DOMContentLoaded', fn);
  }

  // ─── Progress bar ───
  function setupProgress() {
    var bar = document.getElementById('progressBar');
    if (!bar) return;
    var ticking = false;
    function update() {
      var h = document.documentElement;
      var pct = (h.scrollTop / Math.max(1, h.scrollHeight - h.clientHeight)) * 100;
      bar.style.width = Math.min(pct, 100) + '%';
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
    update();
  }

  // ─── Back to top ───
  function setupBackToTop() {
    var btn = document.getElementById('backToTop') || document.getElementById('btt');
    if (!btn) return;
    window.addEventListener('scroll', function () {
      if (window.scrollY > 600) btn.classList.add('visible');
      else btn.classList.remove('visible');
    }, { passive: true });
    btn.addEventListener('click', function (e) {
      e.preventDefault();
      if (window.lenis) window.lenis.scrollTo(0, { duration: 1.2 });
      else window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  // ─── Reveals (fade + translate, staggered) ───
  function setupReveals() {
    var els = document.querySelectorAll('.reveal, .sec > h2, .sec > h3, .sec img, .pull-quote, .entry-stat, .entry-question, .entry-bullets, .stat-bar, .workout-card, .result-card, .angle, .dyk, .compare-panel, .shelf-item, .nav-card, .radar-row, .also-card, .compact-take, .breather-stat, .results-strip, .longshelf-grid, .league-table, .marquee, .opener-band');
    if (!els.length) return;
    if (prefersReduced || !('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.classList.add('visible'); });
      return;
    }
    els.forEach(function (el) { el.classList.add('reveal'); });
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry, i) {
        if (entry.isIntersecting) {
          var el = entry.target;
          var delay = Math.min(i * 60, 240);
          setTimeout(function () { el.classList.add('visible'); }, delay);
          observer.unobserve(el);
        }
      });
    }, { threshold: 0.08, rootMargin: '0px 0px -40px 0px' });
    els.forEach(function (el) { observer.observe(el); });
  }

  // ─── Count-up ───
  function setupCountUp() {
    var els = document.querySelectorAll('.count-up, .breather-stat, .stat-num');
    if (!els.length || prefersReduced || !('IntersectionObserver' in window)) return;
    function animate(el) {
      var target = el.getAttribute('data-target') || el.textContent.trim();
      if (!target) return;
      var num = parseFloat(target.replace(/[^0-9.\-]/g, ''));
      if (isNaN(num)) return;
      var prefix = (target.match(/^[^0-9.\-]*/) || [''])[0];
      var suffix = (target.match(/[^0-9.\-]*$/) || [''])[0];
      var isInt = num === Math.floor(num);
      var dur = 1200, start = performance.now();
      function step(now) {
        var p = Math.min((now - start) / dur, 1);
        var e = 1 - Math.pow(1 - p, 3);
        var cur = num * e;
        el.textContent = prefix + (isInt ? Math.floor(cur).toLocaleString() : cur.toFixed(1)) + suffix;
        if (p < 1) requestAnimationFrame(step);
      }
      el.textContent = prefix + '0' + suffix;
      requestAnimationFrame(step);
    }
    var obs = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { animate(e.target); obs.unobserve(e.target); }
      });
    }, { threshold: 0.3 });
    els.forEach(function (el) { obs.observe(el); });
  }

  // ─── Scroll-linked parallax ───
  function setupParallax() {
    if (prefersReduced) return;
    var items = [];
    document.querySelectorAll('.hero-img, .sec img').forEach(function (el) {
      items.push({ el: el, rate: 0.12 });
    });
    document.querySelectorAll('.sec-watermark').forEach(function (el) {
      items.push({ el: el, rate: -0.2 });
    });
    document.querySelectorAll('.breather-stat').forEach(function (el) {
      items.push({ el: el, rate: -0.18 });
    });
    if (!items.length) return;
    var ticking = false;
    function update() {
      var vh = window.innerHeight;
      items.forEach(function (item) {
        var r = item.el.getBoundingClientRect();
        var mid = r.top + r.height / 2;
        var offset = (mid - vh / 2) * item.rate;
        item.el.style.transform = 'translate3d(0,' + offset.toFixed(1) + 'px,0)';
      });
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) { requestAnimationFrame(update); ticking = true; }
    }, { passive: true });
    window.addEventListener('resize', update);
    update();
  }

  // ─── Nav-card wipe on scroll-in + tap ───
  function setupNavCardFlash() {
    if (prefersReduced) return;
    var cards = document.querySelectorAll('.nav-card');
    if (!cards.length) return;

    if ('IntersectionObserver' in window) {
      var obs = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry, i) {
          if (entry.isIntersecting) {
            var c = entry.target;
            setTimeout(function () {
              c.classList.add('flash');
              setTimeout(function () { c.classList.remove('flash'); }, 720);
            }, 100 + i * 80);
            obs.unobserve(c);
          }
        });
      }, { threshold: 0.4 });
      cards.forEach(function (c) { obs.observe(c); });
    }

    cards.forEach(function (c) {
      c.addEventListener('touchstart', function () { c.classList.add('pressed'); }, { passive: true });
      c.addEventListener('touchend', function () {
        setTimeout(function () { c.classList.remove('pressed'); }, 180);
      });
      c.addEventListener('touchcancel', function () { c.classList.remove('pressed'); });
    });
  }

  // ─── Magnetic hover (desktop only) ───
  function setupMagnetic() {
    if (prefersReduced || !hasFineHover) return;
    var targets = document.querySelectorAll('.nav-card, .back-to-top, .tag');
    targets.forEach(function (el) {
      var strength = el.classList.contains('nav-card') ? 0.12 : 0.3;
      el.addEventListener('mousemove', function (e) {
        var rect = el.getBoundingClientRect();
        var x = e.clientX - rect.left - rect.width / 2;
        var y = e.clientY - rect.top - rect.height / 2;
        el.style.transform = 'translate(' + (x * strength).toFixed(1) + 'px,' + (y * strength).toFixed(1) + 'px)';
      });
      el.addEventListener('mouseleave', function () { el.style.transform = ''; });
    });
  }

  // ─── Device tilt parallax (tablet-friendly) ───
  function setupTilt() {
    if (prefersReduced || hasFineHover) return;
    if (!window.DeviceOrientationEvent) return;
    var cover = document.querySelector('.cover');
    if (!cover) return;
    var brand = cover.querySelector('.cover-brand');
    var headline = cover.querySelector('.cover-headline');
    function onTilt(e) {
      var gx = Math.max(-20, Math.min(20, e.gamma || 0)) / 20;
      var gy = Math.max(-20, Math.min(20, (e.beta || 0) - 45)) / 20;
      if (brand) brand.style.transform = 'translate3d(' + (gx * 12).toFixed(1) + 'px,' + (gy * 6).toFixed(1) + 'px,0)';
      if (headline) headline.style.transform = 'translate3d(' + (gx * -8).toFixed(1) + 'px,' + (gy * -4).toFixed(1) + 'px,0)';
      if (window.__blobTilt) window.__blobTilt(gx, gy);
    }
    window.addEventListener('deviceorientation', onTilt, { passive: true });
  }

  // ─── Lenis smooth scroll ───
  function setupLenis() {
    if (prefersReduced) return;
    if (typeof Lenis === 'undefined') return;
    var lenis = new Lenis({
      duration: 1.1,
      easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); },
      smoothWheel: true,
      smoothTouch: true,
      touchMultiplier: 1.6
    });
    window.lenis = lenis;
    function raf(t) { lenis.raf(t); requestAnimationFrame(raf); }
    requestAnimationFrame(raf);
  }

  // ─── Three.js liquid-blob (ambient, touch-responsive) ───
  function setupBlob() {
    if (prefersReduced) return;
    if (typeof THREE === 'undefined') return;
    var canvas = document.getElementById('blobCanvas');
    if (!canvas) return;
    var cover = document.querySelector('.cover');
    if (!cover) return;

    var scene = new THREE.Scene();
    var rect = cover.getBoundingClientRect();
    var w = rect.width, h = rect.height;
    var camera = new THREE.PerspectiveCamera(50, w / h, 0.1, 100);
    camera.position.z = 3.2;

    var renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(w, h, false);
    renderer.setClearColor(0x000000, 0);

    var uniforms = {
      uTime:   { value: 0 },
      uMouse:  { value: new THREE.Vector2(0, 0) },
      uActive: { value: 1 },
      uColor:  { value: new THREE.Color(0xD2FF00) },
      uIntensity: { value: 1 }
    };

    var vertexShader = [
      'varying vec3 vNormal; varying vec3 vPos;',
      'uniform float uTime; uniform vec2 uMouse; uniform float uActive; uniform float uIntensity;',
      'float hash(vec3 p){p=fract(p*0.3183099+.1);p*=17.0;return fract(p.x*p.y*p.z*(p.x+p.y+p.z));}',
      'float noise(vec3 x){vec3 i=floor(x);vec3 f=fract(x);f=f*f*(3.0-2.0*f);',
      'return mix(mix(mix(hash(i+vec3(0,0,0)),hash(i+vec3(1,0,0)),f.x),',
      'mix(hash(i+vec3(0,1,0)),hash(i+vec3(1,1,0)),f.x),f.y),',
      'mix(mix(hash(i+vec3(0,0,1)),hash(i+vec3(1,0,1)),f.x),',
      'mix(hash(i+vec3(0,1,1)),hash(i+vec3(1,1,1)),f.x),f.y),f.z);}',
      'void main(){',
      '  vec3 p=position;',
      '  float t=uTime*0.42;',
      '  float n=noise(p*1.4+vec3(t,t*0.7,t*0.5));',
      '  p+=normal*(n*0.4*uIntensity);',
      '  vec3 target=vec3(uMouse*1.6,0.4);',
      '  float d=distance(p,target);',
      '  float pull=smoothstep(1.6,0.0,d)*uActive*0.55;',
      '  vec3 dir=normalize(p-target+vec3(0.0001));',
      '  p+=dir*pull;',
      '  vPos=p; vNormal=normal;',
      '  gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0);',
      '}'
    ].join('\n');

    var fragmentShader = [
      'uniform vec3 uColor; varying vec3 vNormal; varying vec3 vPos;',
      'void main(){',
      '  vec3 viewDir=normalize(cameraPosition-vPos);',
      '  float fres=pow(1.0-max(dot(normalize(vNormal),viewDir),0.0),1.6);',
      '  float rim=smoothstep(0.15,1.0,fres);',
      '  vec3 col=mix(vec3(0.02,0.02,0.04),uColor,rim);',
      '  float glow=smoothstep(0.5,1.0,fres);',
      '  col+=uColor*glow*0.7;',
      '  float a=rim*0.9+glow*0.6;',
      '  gl_FragColor=vec4(col,a);',
      '}'
    ].join('\n');

    var geom = new THREE.IcosahedronGeometry(1.1, 48);
    var mat = new THREE.ShaderMaterial({
      uniforms: uniforms, vertexShader: vertexShader, fragmentShader: fragmentShader,
      transparent: true, depthWrite: false, blending: THREE.AdditiveBlending
    });
    var blob = new THREE.Mesh(geom, mat);
    scene.add(blob);

    var targetMouse = new THREE.Vector2(0, 0);
    var autoT = 0;

    window.__blobTilt = function (gx, gy) { targetMouse.set(gx, gy); };

    function pointerFromEvent(clientX, clientY) {
      var r = cover.getBoundingClientRect();
      if (clientY < r.top || clientY > r.bottom) return null;
      var x = ((clientX - r.left) / r.width) * 2 - 1;
      var y = -(((clientY - r.top) / r.height) * 2 - 1);
      return [x, y];
    }
    cover.addEventListener('touchstart', function (e) {
      if (!e.touches[0]) return;
      var p = pointerFromEvent(e.touches[0].clientX, e.touches[0].clientY);
      if (p) targetMouse.set(p[0], p[1]);
    }, { passive: true });
    cover.addEventListener('touchmove', function (e) {
      if (!e.touches[0]) return;
      var p = pointerFromEvent(e.touches[0].clientX, e.touches[0].clientY);
      if (p) targetMouse.set(p[0], p[1]);
    }, { passive: true });
    window.addEventListener('mousemove', function (e) {
      var p = pointerFromEvent(e.clientX, e.clientY);
      if (p) targetMouse.set(p[0], p[1]);
    }, { passive: true });

    function onResize() {
      var r = cover.getBoundingClientRect();
      w = r.width; h = r.height;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h, false);
    }
    window.addEventListener('resize', onResize);
    window.addEventListener('orientationchange', onResize);

    var clock = new THREE.Clock();
    function animate() {
      var dt = clock.getDelta();
      autoT += dt;
      uniforms.uTime.value += dt;
      var ax = Math.sin(autoT * 0.4) * 0.5;
      var ay = Math.cos(autoT * 0.3) * 0.35;
      var wander = new THREE.Vector2(ax, ay);
      var blend = new THREE.Vector2().lerpVectors(wander, targetMouse, 0.55);
      uniforms.uMouse.value.lerp(blend, 0.06);
      blob.rotation.y += dt * 0.14;
      blob.rotation.x += dt * 0.07;
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    }
    animate();
  }

  // ─── Marquee seam ───
  function setupMarquee() {
    document.querySelectorAll('.marquee-track').forEach(function (t) {
      t.innerHTML = t.innerHTML + t.innerHTML;
    });
  }

  onReady(function () {
    setupProgress();
    setupBackToTop();
    setupReveals();
    setupCountUp();
    setupParallax();
    setupNavCardFlash();
    setupMagnetic();
    setupTilt();
    setupLenis();
    setupBlob();
    setupMarquee();
  });
})();
