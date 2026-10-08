/* ==========================================================================
   marquee.js — the review and logo tickers.

   Velocities taken from the source bundle's Ticker props:
     reviews row A/B   gap 16px  velocity 40 px/s   hoverModifier 32 (-> 32% speed)
     reviews on phone  gap 16px  velocity 100 px/s  stackDirection column
     logo strips       gap 21px  velocity 30 px/s   hoverModifier 100 (no change)
   One row runs "default", the other "reverse". Below 810px the reviews switch
   to the column ticker, which is why axis is re-read on every resize.

   Content is duplicated until it is at least twice the viewport width, then the
   transform wraps on one copy's width so the loop is seamless.
   ========================================================================== */

export function initMarquees() {
  document.querySelectorAll('[data-marquee]').forEach(setup);
}

function setup(root) {
  const track = root.querySelector('.marquee__track');
  if (!track) return;

  const hoverMod = Number(root.dataset.hover || 100) / 100;      // 32 -> 0.32
  const dir = root.dataset.direction === 'reverse' ? 1 : -1;
  const colBelow = Number(root.dataset.columnBelow || 0);

  // axis and speed both change at the phone breakpoint
  const vertical = () => colBelow > 0 && window.innerWidth < colBelow;
  const velocity = () => (vertical()
    ? Number(root.dataset.velocityColumn || 100)
    : Number(root.dataset.velocity || 40));

  const originals = [...track.children];
  let unit = 0;
  let offset = 0;
  let last = 0;
  let speedScale = 1;
  let raf = 0;

  function fill() {
    // reset to the original set, then clone until we cover 2x the viewport
    track.querySelectorAll('[data-clone]').forEach((n) => n.remove());
    const vert = vertical();
    root.classList.toggle('marquee--column', vert);
    const gap = parseFloat(getComputedStyle(track).gap) || 0;
    unit = originals.reduce(
      (w, el) => w + (vert ? el.getBoundingClientRect().height : el.getBoundingClientRect().width) + gap, 0);
    if (!unit) return;
    const need = (vert ? root.clientHeight : root.clientWidth) * 2 + unit;
    let have = unit;
    while (have < need) {
      originals.forEach((el) => {
        const c = el.cloneNode(true);
        c.setAttribute('data-clone', '');
        c.setAttribute('aria-hidden', 'true');
        // A cloned lazy <img> can land in a never-loads state; clones are
        // decorative duplicates that have to be painted the moment they scroll
        // in, so load them directly.
        c.querySelectorAll('img[loading="lazy"]').forEach((img) => {
          img.loading = 'eager';
          img.src = img.src;
        });
        track.appendChild(c);
      });
      have += unit;
    }
    if (dir === 1) offset = -unit;
  }

  function frame(now) {
    if (!last) last = now;
    const dt = Math.min((now - last) / 1000, 0.05);   // clamp after a tab switch
    last = now;
    offset += dir * velocity() * speedScale * dt;
    if (dir === -1 && offset <= -unit) offset += unit;
    if (dir === 1 && offset >= 0) offset -= unit;
    track.style.transform = vertical()
      ? `translate3d(0,${offset.toFixed(2)}px,0)`
      : `translate3d(${offset.toFixed(2)}px,0,0)`;
    raf = requestAnimationFrame(frame);
  }

  root.addEventListener('pointerenter', () => { speedScale = hoverMod; });
  root.addEventListener('pointerleave', () => { speedScale = 1; });

  // Pause when off-screen or the tab is hidden; nothing to animate, no cost.
  const io = new IntersectionObserver(([e]) => {
    if (e.isIntersecting) { last = 0; raf ||= requestAnimationFrame(frame); }
    else { cancelAnimationFrame(raf); raf = 0; }
  }, { rootMargin: '200px' });
  io.observe(root);

  document.addEventListener('visibilitychange', () => { last = 0; });

  let resizeTimer = 0;
  let wasVertical = vertical();
  window.addEventListener('resize', () => {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(() => {
      if (vertical() !== wasVertical) { offset = 0; wasVertical = vertical(); }
      fill();
    }, 150);
  }, { passive: true });

  fill();
}
