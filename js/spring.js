/* ==========================================================================
   spring.js — turn the template's spring transitions into CSS easings.

   The source bundle expresses its motion as {type:"spring", duration, bounce}.
   Rather than eyeball a cubic-bezier, we simulate the same damped spring and
   sample it into a CSS linear() easing, which is what the Framer runtime does
   internally. Browsers without linear() fall back to a close cubic-bezier.

   The two signatures counted in the bundle:
     SPRING.interaction  duration .4s  bounce .2   (60 uses)
     SPRING.reveal       duration 1.5s bounce 0    (26 uses)
   ========================================================================== */

export const SPRING = {
  interaction: { duration: 0.4, bounce: 0.2 },
  reveal:      { duration: 1.5, bounce: 0 },
  nav:         { duration: 1.0, bounce: 0 },
  quick:       { duration: 0.2, bounce: 0 },
};

const supportsLinear = (() => {
  try { return CSS.supports('transition-timing-function', 'linear(0, 1)'); }
  catch { return false; }
})();

/** Position of a unit damped spring at time t (seconds). */
function springAt(t, omega, zeta) {
  if (zeta < 1) {
    const wd = omega * Math.sqrt(1 - zeta * zeta);
    return 1 - Math.exp(-zeta * omega * t) * (Math.cos(wd * t) + (zeta * omega / wd) * Math.sin(wd * t));
  }
  // critically damped
  return 1 - Math.exp(-omega * t) * (1 + omega * t);
}

const cache = new Map();

/**
 * CSS easing for a {duration, bounce} spring.
 * Mirrors the runtime's visual-duration mapping: w0 = 2pi / (1.2 * T), zeta = 1 - bounce.
 */
export function springEasing({ duration, bounce = 0 }, steps = 40) {
  const key = `${duration}:${bounce}:${steps}`;
  if (cache.has(key)) return cache.get(key);

  let out;
  if (!supportsLinear) {
    out = bounce > 0 ? 'cubic-bezier(.34,1.26,.64,1)' : 'cubic-bezier(.22,1,.36,1)';
  } else {
    const omega = (2 * Math.PI) / (duration * 1.2);
    const zeta = Math.min(1, Math.max(0.05, 1 - bounce));
    const pts = [];
    for (let i = 0; i <= steps; i++) {
      pts.push(Math.round(springAt((i / steps) * duration, omega, zeta) * 1e4) / 1e4);
    }
    pts[pts.length - 1] = 1;
    out = `linear(${pts.join(',')})`;
  }
  cache.set(key, out);
  return out;
}

/** Write the easings onto :root so plain CSS rules can use them too. */
export function installSpringVars() {
  const r = document.documentElement.style;
  r.setProperty('--spring-interaction', springEasing(SPRING.interaction));
  r.setProperty('--spring-reveal', springEasing(SPRING.reveal));
  r.setProperty('--spring-nav', springEasing(SPRING.nav));
}
