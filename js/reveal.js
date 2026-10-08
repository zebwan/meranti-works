/* ==========================================================================
   reveal.js — the scroll-reveal inventory.

   Start states come straight from the source's server-rendered inline styles:
     [data-reveal]          opacity 0, translateY(40px)    every section wrapper
     [data-reveal="150"]    opacity 0, translateY(150px)   inner content blocks
     [data-reveal="50"]     opacity 0, translateY(50px)    the CTA form column
   all driven by spring{duration:1.5, bounce:0}.

   Children marked [data-stagger] inside a revealed block come in one after the
   other at 80ms apart.

   The hidden start state lives in CSS (scoped to .js), so it has to be
   guaranteed to come off again. IntersectionObserver callbacks are part of the
   rendering lifecycle and do not run in a background tab, so there are two
   safety nets below: reveal on visibilitychange, and an unconditional timeout.
   Without them a page opened in a background tab and never focused would stay
   blank.
   ========================================================================== */

import { SPRING, springEasing } from './spring.js';

const FAILSAFE_MS = 4000;

export function initReveal() {
  const nodes = [...document.querySelectorAll('[data-reveal]')];
  if (!nodes.length) return;

  const reveal = (el, animate, delay = 0) => {
    if (el.hasAttribute('data-revealed')) return;
    el.setAttribute('data-revealed', 'true');
    if (!animate) return;

    const dy = Number(el.dataset.reveal) || 40;
    el.animate(
      [{ opacity: 0, transform: `translateY(${dy}px)` },
       { opacity: 1, transform: 'translateY(0)' }],
      { duration, delay, easing, fill: 'both' },
    );
    el.querySelectorAll('[data-stagger]').forEach((child, i) => {
      child.animate(
        [{ opacity: 0, transform: 'translateY(24px)' },
         { opacity: 1, transform: 'translateY(0)' }],
        { duration, delay: 120 + i * 80, easing, fill: 'both' },
      );
    });
  };

  if (matchMedia('(prefers-reduced-motion: reduce)').matches) {
    nodes.forEach((n) => reveal(n, false));
    return;
  }

  const easing = springEasing(SPRING.reveal);
  const duration = SPRING.reveal.duration * 1000;

  const io = new IntersectionObserver((entries) => {
    for (const entry of entries) {
      if (!entry.isIntersecting) continue;
      io.unobserve(entry.target);
      reveal(entry.target, true);
    }
  }, { rootMargin: '0px 0px -12% 0px', threshold: 0.05 });

  nodes.forEach((n) => io.observe(n));

  // Safety net 1: anything already on screen when the tab becomes visible.
  const catchUp = () => {
    if (document.hidden) return;
    nodes.forEach((n) => {
      if (n.hasAttribute('data-revealed')) return;
      const r = n.getBoundingClientRect();
      if (r.top < window.innerHeight && r.bottom > 0) reveal(n, true);
    });
  };
  document.addEventListener('visibilitychange', catchUp);

  // Safety net 2: never leave content hidden, whatever happens to the observer.
  setTimeout(() => nodes.forEach((n) => reveal(n, false)), FAILSAFE_MS);
}
