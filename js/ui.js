/* ==========================================================================
   ui.js — accordion, stat counters, contact form.
   ========================================================================== */

import { SPRING, springEasing } from './spring.js';

/* --------------------------------------------------------------------------
   FAQ accordion. Single open at a time, which is what the source's wrapper
   variant ("All Closed" -> one open) does. Height animates, the + rotates to x.
   -------------------------------------------------------------------------- */
export function initAccordion() {
  document.querySelectorAll('[data-accordion]').forEach((root) => {
    const items = [...root.querySelectorAll('.faq__item')];

    const setOpen = (item, open) => {
      const panel = item.querySelector('.faq__a');
      const btn = item.querySelector('.faq__q');
      item.dataset.open = String(open);
      btn?.setAttribute('aria-expanded', String(open));
      panel.style.height = open ? `${panel.scrollHeight}px` : '0px';
    };

    items.forEach((item) => {
      const btn = item.querySelector('.faq__q');
      setOpen(item, item.dataset.open === 'true');
      btn?.addEventListener('click', () => {
        const willOpen = item.dataset.open !== 'true';
        items.forEach((other) => setOpen(other, other === item && willOpen));
      });
    });

    window.addEventListener('resize', () => {
      items.forEach((item) => {
        if (item.dataset.open === 'true') {
          item.querySelector('.faq__a').style.height = `${item.querySelector('.faq__a').scrollHeight}px`;
        }
      });
    }, { passive: true });
  });
}

/* --------------------------------------------------------------------------
   Stat counters — tick up once, when first scrolled into view.
   -------------------------------------------------------------------------- */
export function initCounters() {
  const nodes = document.querySelectorAll('[data-count]');
  if (!nodes.length) return;

  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const DURATION = 1600;

  const run = (el) => {
    const target = Number(el.dataset.count);
    const suffix = el.dataset.suffix || '';
    if (reduce) { el.textContent = target.toLocaleString('en-MY') + suffix; return; }
    const t0 = performance.now();
    const step = (now) => {
      const p = Math.min(1, (now - t0) / DURATION);
      const eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased).toLocaleString('en-MY') + suffix;
      if (p < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  };

  const io = new IntersectionObserver((entries) => {
    entries.forEach((e) => {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      run(e.target);
    });
  }, { threshold: 0.4 });

  nodes.forEach((n) => { n.textContent = '0'; io.observe(n); });
}

/* --------------------------------------------------------------------------
   Contact + newsletter forms.
   This is a static mock site with no backend, so submission is intercepted and
   acknowledged client-side. Nothing is transmitted anywhere.
   -------------------------------------------------------------------------- */
export function initForms() {
  document.querySelectorAll('form[data-mock-form]').forEach((form) => {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      if (!form.reportValidity()) return;
      form.dataset.sent = 'true';
      const btn = form.querySelector('[type="submit"] .btn__label, [type="submit"]');
      if (btn) btn.textContent = 'Sent';
      form.querySelectorAll('.field').forEach((f) => { f.value = ''; });
      setTimeout(() => {
        form.dataset.sent = 'false';
        if (btn) btn.textContent = form.dataset.label || 'Send message';
      }, 6000);
    });
  });
}

/* --------------------------------------------------------------------------
   Card and image hover polish that the source does with motion springs.
   -------------------------------------------------------------------------- */
export function initHoverSprings() {
  const easing = springEasing(SPRING.interaction);
  document.documentElement.style.setProperty('--ease-spring', easing);
}
