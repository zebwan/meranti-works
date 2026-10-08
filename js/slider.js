/* ==========================================================================
   slider.js — the services carousel.
   Transform-based, exactly like the source: the viewport is overflow:clip and
   the track is translated. No scroll-snap (which would fight programmatic
   control), no native scrolling. Arrows, drag, and a progress bar.
   ========================================================================== */

import { SPRING, springEasing } from './spring.js';

export function initSliders() {
  document.querySelectorAll('[data-slider]').forEach(setup);
}

function setup(root) {
  const viewport = root.querySelector('.slider__viewport');
  const track = root.querySelector('.slider__track');
  const slides = [...track.children];
  const prev = root.querySelector('[data-slider-prev]');
  const next = root.querySelector('[data-slider-next]');
  const bar = root.querySelector('.slider__progress i');
  if (!slides.length) return;

  let index = 0;
  let perView = 1;
  const easing = springEasing(SPRING.reveal, 24);

  const gap = () => parseFloat(getComputedStyle(track).gap) || 0;
  const slideW = () => slides[0].getBoundingClientRect().width + gap();

  function measure() {
    const w = viewport.clientWidth;
    perView = window.innerWidth >= 1200 ? 3 : window.innerWidth >= 810 ? 2 : 1;
    const g = gap();
    const each = (w - g * (perView - 1)) / perView;
    root.style.setProperty('--slide-w', `${each}px`);
    index = Math.min(index, Math.max(0, slides.length - perView));
    apply(false);
  }

  function apply(animate = true) {
    track.style.transition = animate ? `transform .6s ${easing}` : 'none';
    track.style.transform = `translate3d(${-index * slideW()}px,0,0)`;
    const maxIndex = Math.max(0, slides.length - perView);
    prev && (prev.disabled = index <= 0);
    next && (next.disabled = index >= maxIndex);
    if (bar) {
      const pages = maxIndex + 1;
      bar.style.width = `${100 / pages}%`;
      bar.style.left = `${(index / pages) * 100}%`;
    }
  }

  const go = (i) => {
    index = Math.max(0, Math.min(slides.length - perView, i));
    apply();
  };

  prev?.addEventListener('click', () => go(index - 1));
  next?.addEventListener('click', () => go(index + 1));

  /* drag / swipe */
  let startX = 0, startIdx = 0, dragging = false, moved = 0;
  viewport.addEventListener('pointerdown', (e) => {
    dragging = true; moved = 0;
    startX = e.clientX; startIdx = index;
    viewport.setPointerCapture?.(e.pointerId);
    track.style.transition = 'none';
  });
  viewport.addEventListener('pointermove', (e) => {
    if (!dragging) return;
    moved = e.clientX - startX;
    track.style.transform = `translate3d(${-startIdx * slideW() + moved}px,0,0)`;
  });
  const endDrag = () => {
    if (!dragging) return;
    dragging = false;
    const steps = Math.round(-moved / slideW());
    go(startIdx + steps);
  };
  viewport.addEventListener('pointerup', endDrag);
  viewport.addEventListener('pointercancel', endDrag);
  viewport.addEventListener('lostpointercapture', endDrag);
  viewport.addEventListener('click', (e) => { if (Math.abs(moved) > 6) e.preventDefault(); }, true);

  root.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') { e.preventDefault(); go(index - 1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); go(index + 1); }
  });

  window.addEventListener('resize', measure, { passive: true });
  measure();
}
