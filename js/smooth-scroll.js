/* ==========================================================================
   smooth-scroll.js
   The source site ships Lenis (html gets .lenis / .lenis-scrolling). This is a
   compact equivalent: wheel and keyboard input is captured and the real scroll
   position is lerped toward a target each frame, so scroll-linked effects stay
   in sync with native scrollY.

   Touch is left alone — iOS momentum is better than anything we would fake,
   and the source's syncTouch behaves the same way in practice.
   ========================================================================== */

const LERP = 0.1;           // per-frame approach
const WHEEL_MULTIPLIER = 1;
const SNAP = 0.4;           // px below which we land exactly

export function initSmoothScroll() {
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const coarse = matchMedia('(pointer: coarse)').matches;
  if (reduce || coarse) return null;

  const html = document.documentElement;
  html.classList.add('lenis');

  let target = window.scrollY;
  let current = target;
  let running = false;
  let raf = 0;

  const maxScroll = () => html.scrollHeight - window.innerHeight;
  const clamp = (v) => Math.max(0, Math.min(maxScroll(), v));

  function frame() {
    const delta = target - current;
    if (Math.abs(delta) < SNAP) {
      current = target;
      window.scrollTo(0, current);
      running = false;
      html.classList.remove('lenis-scrolling');
      return;
    }
    current += delta * LERP;
    window.scrollTo(0, current);
    raf = requestAnimationFrame(frame);
  }

  function start() {
    if (running) return;
    running = true;
    html.classList.add('lenis-scrolling');
    raf = requestAnimationFrame(frame);
  }

  function onWheel(e) {
    if (e.ctrlKey) return;                       // pinch zoom
    if (e.target.closest('[data-no-smooth]')) return;
    e.preventDefault();
    target = clamp(target + e.deltaY * WHEEL_MULTIPLIER);
    start();
  }

  // If anything else moves the page (anchor jump, find-in-page, resize), adopt it.
  function resync() {
    if (!running) { target = current = window.scrollY; }
  }

  window.addEventListener('wheel', onWheel, { passive: false });
  window.addEventListener('scroll', resync, { passive: true });
  window.addEventListener('resize', () => { target = clamp(target); }, { passive: true });

  // Smooth in-page anchors.
  document.addEventListener('click', (e) => {
    const a = e.target.closest('a[href^="#"]');
    if (!a) return;
    const id = a.getAttribute('href').slice(1);
    if (!id) return;
    const el = document.getElementById(id);
    if (!el) return;
    e.preventDefault();
    target = clamp(el.getBoundingClientRect().top + window.scrollY - 100);
    start();
  });

  return {
    scrollTo(y) { target = clamp(y); start(); },
    stop() { cancelAnimationFrame(raf); running = false; },
  };
}
