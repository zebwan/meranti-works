/* ==========================================================================
   scrub-text.js — the About paragraph's per-character scroll reveal.

   Measured on the source: the paragraph is split into word spans, each holding
   one span per character (285 of them on the homepage). As you scroll, each
   character's colour runs from rgba(255,255,255,.2) to #fff, left to right,
   over roughly a 700px window — the first character lights when the block's top
   is about 200px above the fold and the last one lands about 400px later.

   Here the text is split at runtime (so the markup stays readable and
   copy-pasteable) and the scrub is mapped off the element's own position.
   ========================================================================== */

export function initScrubText() {
  const blocks = document.querySelectorAll('[data-scrub]');
  if (!blocks.length) return;

  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

  const all = [];
  blocks.forEach((block) => {
    const text = block.textContent.replace(/\s+/g, ' ').trim();
    block.textContent = '';
    const chars = [];
    text.split(' ').forEach((word, wi, arr) => {
      const w = document.createElement('span');
      w.className = 'w';
      [...(wi < arr.length - 1 ? word + ' ' : word)].forEach((ch) => {
        const c = document.createElement('span');
        c.className = 'c';
        c.textContent = ch;
        w.appendChild(c);
        chars.push(c);
      });
      block.appendChild(w);
    });
    if (reduce) { chars.forEach((c) => c.classList.add('on')); return; }
    all.push({ block, chars });
  });

  if (!all.length) return;

  let ticking = false;
  function update() {
    ticking = false;
    const vh = window.innerHeight;
    for (const { block, chars } of all) {
      const r = block.getBoundingClientRect();
      // start when the block's top is ~75% down the viewport,
      // finish when it has travelled to ~25%.
      const start = vh * 0.78;
      const end = vh * 0.22;
      const progress = Math.max(0, Math.min(1, (start - r.top) / (start - end)));
      const lit = Math.round(progress * chars.length);
      for (let i = 0; i < chars.length; i++) {
        chars[i].classList.toggle('on', i < lit);
      }
    }
  }
  const onScroll = () => {
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(update);
  };

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });
  update();
}
