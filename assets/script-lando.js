(function () {
  'use strict';

  var prefersReduced = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var isCoarse = window.matchMedia && window.matchMedia('(pointer: coarse)').matches;
  var isMobile = window.innerWidth < 900;

  // Progress bar
  (function () {
    var bar = document.getElementById('progressBar');
    if (!bar) return;
    var ticking = false;
    function update() {
      var h = document.documentElement;
      var pct = (h.scrollTop / (h.scrollHeight - h.clientHeight)) * 100;
      bar.style.width = Math.min(pct, 100) + '%';
      ticking = false;
    }
    window.addEventListener('scroll', function () {
      if (!ticking) {
        window.requestAnimationFrame(update);
        ticking = true;
      }
    }, { passive: true });
  })();

  // Back to top
  (function () {
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
  })();

  // IntersectionObserver reveals
  (function () {
    var els = document.querySelectorAll('.reveal, .sec, .pull-quote, .entry-stat, .stat-bar, .workout-card, .result-card, .hero-img, .angle, .dyk, .compare-panel, .shelf-item, .nav-card, .radar-row');
    if (!els.length) return;
    if (prefersReduced || !('IntersectionObserver' in window)) {
      els.forEach(function (el) { el.classList.add('visible'); });
      return;
    }
    els.forEach(function (el) { el.classList.add('reveal'); });
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry, i) {
        if (entry.isIntersecting) {
          setTimeout(function () { entry.target.classList.add('visible'); }, i * 40);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.05, rootMargin: '0px 0px 60px 0px' });
    els.forEach(function (el) { observer.observe(el); });
  })();

  // Count-up numbers
  (function () {
    var els = document.querySelectorAll('.count-up, .breather-stat, .stat-num');
    if (!els.length) return;
    if (prefersReduced || !('IntersectionObserver' in window)) return;

    function animateCount(el) {
      var target = el.getAttribute('data-target') || el.textContent.trim();
      if (!target) return;
      var raw = target.replace(/[^0-9.\-]/g, '');
      var num = parseFloat(raw);
      if (isNaN(num)) return;
      var prefix = (target.match(/^[^0-9.\-]*/) || [''])[0];
      var suffix = (target.match(/[^0-9.\-]*$/) || [''])[0];
      var isInt = num === Math.floor(num);
      var duration = 1100;
      var start = performance.now();
      function step(now) {
        var progress = Math.min((now - start) / duration, 1);
        var ease = 1 - Math.pow(1 - progress, 3);
        var current = num * ease;
        el.textContent = prefix + (isInt ? Math.floor(current).toLocaleString() : current.toFixed(1)) + suffix;
        if (progress < 1) requestAnimationFrame(step);
      }
      el.textContent = prefix + '0' + suffix;
      requestAnimationFrame(step);
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          animateCount(entry.target);
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.3 });
    els.forEach(function (el) { observer.observe(el); });
  })();

  // Magnetic hover
  (function () {
    if (prefersReduced || isCoarse) return;
    var targets = document.querySelectorAll('.nav-card, .back-to-top, .tag, .tier-hot');
    targets.forEach(function (el) {
      var strength = el.classList.contains('nav-card') ? 0.15 : 0.35;
      el.addEventListener('mousemove', function (e) {
        var rect = el.getBoundingClientRect();
        var x = e.clientX - rect.left - rect.width / 2;
        var y = e.clientY - rect.top - rect.height / 2;
        el.style.transform = 'translate(' + (x * strength) + 'px, ' + (y * strength) + 'px)';
      });
      el.addEventListener('mouseleave', function () {
        el.style.transform = '';
      });
    });
  })();

  // Lenis smooth scroll
  (function () {
    if (prefersReduced) return;
    if (typeof Lenis === 'undefined') return;
    var lenis = new Lenis({
      duration: 1.15,
      easing: function (t) { return Math.min(1, 1.001 - Math.pow(2, -10 * t)); },
      smoothWheel: true,
      smoothTouch: false
    });
    window.lenis = lenis;
    function raf(time) { lenis.raf(time); requestAnimationFrame(raf); }
    requestAnimationFrame(raf);
  })();

  // Three.js liquid-blob cursor on hero
  (function () {
    if (prefersReduced || isCoarse || isMobile) return;
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
      uTime: { value: 0 },
      uMouse: { value: new THREE.Vector2(0, 0) },
      uMouseActive: { value: 0 },
      uColor: { value: new THREE.Color(0xD2FF00) },
      uAspect: { value: w / h }
    };

    var vertexShader = [
      'varying vec3 vNormal;',
      'varying vec3 vPos;',
      'varying vec2 vUv;',
      'uniform float uTime;',
      'uniform vec2 uMouse;',
      'uniform float uMouseActive;',
      '',
      'float hash(vec3 p) { p = fract(p*0.3183099+.1); p *= 17.0; return fract(p.x*p.y*p.z*(p.x+p.y+p.z)); }',
      'float noise(vec3 x) {',
      '  vec3 i = floor(x); vec3 f = fract(x); f = f*f*(3.0-2.0*f);',
      '  return mix(mix(mix(hash(i+vec3(0,0,0)), hash(i+vec3(1,0,0)),f.x),',
      '                mix(hash(i+vec3(0,1,0)), hash(i+vec3(1,1,0)),f.x),f.y),',
      '            mix(mix(hash(i+vec3(0,0,1)), hash(i+vec3(1,0,1)),f.x),',
      '                mix(hash(i+vec3(0,1,1)), hash(i+vec3(1,1,1)),f.x),f.y),f.z);',
      '}',
      '',
      'void main() {',
      '  vUv = uv;',
      '  vec3 p = position;',
      '  float t = uTime * 0.35;',
      '  float n = noise(p * 1.6 + vec3(t, t*0.7, t*0.5));',
      '  float displace = n * 0.35;',
      '  vec3 mousePos = vec3(uMouse * 1.6, 0.5);',
      '  float d = distance(p, mousePos);',
      '  float pull = smoothstep(1.4, 0.0, d) * uMouseActive * 0.6;',
      '  vec3 dir = normalize(p - mousePos + vec3(0.0001));',
      '  p += dir * pull;',
      '  p += normal * displace;',
      '  vPos = p;',
      '  vNormal = normal;',
      '  gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);',
      '}'
    ].join('\n');

    var fragmentShader = [
      'uniform vec3 uColor;',
      'uniform float uTime;',
      'varying vec3 vNormal;',
      'varying vec3 vPos;',
      'varying vec2 vUv;',
      'void main() {',
      '  vec3 viewDir = normalize(cameraPosition - vPos);',
      '  float fres = pow(1.0 - max(dot(normalize(vNormal), viewDir), 0.0), 1.8);',
      '  float rim = smoothstep(0.2, 1.0, fres);',
      '  vec3 col = mix(vec3(0.02,0.02,0.04), uColor, rim);',
      '  float glow = smoothstep(0.5, 1.0, fres);',
      '  col += uColor * glow * 0.6;',
      '  float alpha = rim * 0.85 + glow * 0.5;',
      '  gl_FragColor = vec4(col, alpha);',
      '}'
    ].join('\n');

    var geom = new THREE.IcosahedronGeometry(1.1, 48);
    var mat = new THREE.ShaderMaterial({
      uniforms: uniforms,
      vertexShader: vertexShader,
      fragmentShader: fragmentShader,
      transparent: true,
      depthWrite: false,
      blending: THREE.AdditiveBlending
    });
    var blob = new THREE.Mesh(geom, mat);
    scene.add(blob);

    var targetMouse = new THREE.Vector2(0, 0);
    var active = 0;

    function onMove(e) {
      var r = cover.getBoundingClientRect();
      if (e.clientY < r.top || e.clientY > r.bottom) { active = 0; return; }
      var x = ((e.clientX - r.left) / r.width) * 2 - 1;
      var y = -(((e.clientY - r.top) / r.height) * 2 - 1);
      targetMouse.set(x, y);
      active = 1;
    }
    window.addEventListener('mousemove', onMove, { passive: true });
    cover.addEventListener('mouseleave', function () { active = 0; });

    function onResize() {
      var r = cover.getBoundingClientRect();
      w = r.width; h = r.height;
      camera.aspect = w / h;
      uniforms.uAspect.value = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h, false);
    }
    window.addEventListener('resize', onResize);

    var clock = new THREE.Clock();
    function animate() {
      var dt = clock.getDelta();
      uniforms.uTime.value += dt;
      uniforms.uMouse.value.lerp(targetMouse, 0.08);
      uniforms.uMouseActive.value += (active - uniforms.uMouseActive.value) * 0.06;
      blob.rotation.y += dt * 0.15;
      blob.rotation.x += dt * 0.08;
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    }
    animate();
  })();

  // Marquee duplication for seamless loop
  (function () {
    var tracks = document.querySelectorAll('.marquee-track');
    tracks.forEach(function (track) {
      var html = track.innerHTML;
      track.innerHTML = html + html;
    });
  })();
})();
