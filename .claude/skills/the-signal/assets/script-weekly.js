/* The Signal — weekly (Transmission) JavaScript bundle.
 *
 * The weekly is a PAPER OBJECT: it renders complete and beautiful with
 * JavaScript OFF (the paper-and-ink contract). No progress rails, no
 * scroll-triggered reveals, no motion, no bead rail — the reference issue
 * (docs/mockups/reference-issue-transmission.html) proves none are needed.
 *
 * The ONLY script the weekly ships is a defensive, invisible image-error
 * fallback: if a fabricated or expired image URL fails to load, hide the
 * broken <img> (and its caption/figure) so a bad asset never renders a
 * broken-image icon. This is progressive enhancement — with JS off, a
 * broken image is the browser's problem, not a layout break, because the
 * Transmission layout never depends on an image being present.
 */
(function () {
  document.addEventListener(
    'error',
    function (e) {
      var t = e.target;
      if (!t || t.tagName !== 'IMG') return;
      t.style.display = 'none';
      var p = t.parentElement;
      if (!p) return;
      var next = t.nextElementSibling;
      if (next && next.classList && next.classList.contains('plate-cap')) {
        next.style.display = 'none';
      }
      if (p.classList && p.classList.contains('plate-img')) {
        p.style.display = 'none';
      }
      if (p.tagName === 'FIGURE') {
        p.style.display = 'none';
      }
    },
    true
  );
})();
