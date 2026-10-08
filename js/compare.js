/* ==========================================================================
   compare.js — before/after drag slider.

   A direct port of the source template's component, props and all:
     dragMode "drag", initialPosition 50, orientation horizontal,
     divider 4px white + 0 0 8px rgba(0,0,0,.5), handle 40px accent,
     labels BEFORE / AFTER inset 16px,
     keyboard arrows move 2%, shift+arrows move 10%.
   The "before" image is revealed with clip-path: inset(0 (100-p)% 0 0).
   ========================================================================== */

export function initCompare() {
  document.querySelectorAll('.compare').forEach(setup);
}

function setup(el) {
  let p = Number(el.dataset.start ?? 50);
  let dragging = false;

  const set = (next) => {
    p = Math.max(0, Math.min(100, next));
    el.style.setProperty('--p', p.toFixed(2));
    el.setAttribute('aria-valuenow', Math.round(p));
  };

  const fromEvent = (clientX) => {
    const r = el.getBoundingClientRect();
    if (!r.width) return;
    set(((clientX - r.left) / r.width) * 100);
  };

  el.addEventListener('pointerdown', (e) => {
    dragging = true;
    el.setPointerCapture?.(e.pointerId);
    fromEvent(e.clientX);
    e.preventDefault();
  });
  el.addEventListener('pointermove', (e) => { if (dragging) fromEvent(e.clientX); });
  const stop = () => { dragging = false; };
  el.addEventListener('pointerup', stop);
  el.addEventListener('pointercancel', stop);
  el.addEventListener('lostpointercapture', stop);

  el.addEventListener('keydown', (e) => {
    const step = e.shiftKey ? 10 : 2;
    if (e.key === 'ArrowLeft')  { e.preventDefault(); set(p - step); }
    if (e.key === 'ArrowRight') { e.preventDefault(); set(p + step); }
    if (e.key === 'Home')       { e.preventDefault(); set(0); }
    if (e.key === 'End')        { e.preventDefault(); set(100); }
  });

  el.setAttribute('role', 'slider');
  el.setAttribute('tabindex', '0');
  el.setAttribute('aria-label', 'Before and after comparison');
  el.setAttribute('aria-valuemin', '0');
  el.setAttribute('aria-valuemax', '100');
  el.setAttribute('aria-orientation', 'horizontal');
  set(p);
}
