/* ==========================================================================
   process.js — the pinned, scroll-scrubbed stepper.

   At 1200px and up the source pins a 100vh panel (sticky, top:10px) inside a
   section roughly 3.8x the viewport tall, and walks four steps across the
   remaining scroll. The active step expands, its icon and rail turn accent, and
   the image behind cross-fades.

   Below 1200px the source stops pinning, so this does nothing and every step
   is left open by CSS.
   ========================================================================== */

export function initProcess() {
  const root = document.querySelector('[data-process]');
  if (!root) return;

  const track = root.querySelector('.process__track');
  const sticky = root.querySelector('.process__sticky');
  const steps = [...root.querySelectorAll('.process__step')];
  const images = [...root.querySelectorAll('.process__media img')];
  const railFill = root.querySelector('.process__rail i');
  if (!steps.length) return;

  let active = -1;

  const pinned = () => window.innerWidth >= 1200
    && getComputedStyle(sticky).position === 'sticky';

  function setActive(i) {
    if (i === active) return;
    active = i;
    steps.forEach((s, n) => s.setAttribute('data-active', String(n === i)));
    images.forEach((img, n) => img.setAttribute('data-active', String(n === i)));
    if (railFill) railFill.style.height = `${((i + 1) / steps.length) * 100}%`;
  }

  function update() {
    if (!pinned()) { setActive(steps.length - 1); return; }
    const r = track.getBoundingClientRect();
    const scrollable = r.height - window.innerHeight;
    if (scrollable <= 0) { setActive(0); return; }
    // 0 when the track top reaches the viewport top, 1 when its bottom does
    const progress = Math.max(0, Math.min(1, -r.top / scrollable));
    setActive(Math.min(steps.length - 1, Math.floor(progress * steps.length * 0.999)));
  }

  // Clicking a step jumps the page to that step's slice of the scrub.
  steps.forEach((step, i) => {
    step.addEventListener('click', () => {
      if (!pinned()) return;
      const r = track.getBoundingClientRect();
      const top = r.top + window.scrollY;
      const scrollable = r.height - window.innerHeight;
      window.scrollTo({ top: top + (i / steps.length) * scrollable + 8, behavior: 'smooth' });
    });
  });

  window.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', update, { passive: true });
  update();
}
