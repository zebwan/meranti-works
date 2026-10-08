/* ==========================================================================
   main.js — wires everything up.
   Loaded as <script type="module" defer>, so it runs after the HTML is parsed.
   ========================================================================== */

import { installSpringVars } from './spring.js';
import { initSmoothScroll } from './smooth-scroll.js';
import { initReveal } from './reveal.js';
import { initNav } from './nav.js';
import { initSliders } from './slider.js';
import { initCompare } from './compare.js';
import { initMarquees } from './marquee.js';
import { initProcess } from './process.js';
import { initScrubText } from './scrub-text.js';
import { initAccordion, initCounters, initForms, initHoverSprings } from './ui.js';

installSpringVars();
initHoverSprings();

initNav();
initReveal();
initSliders();
initCompare();
initMarquees();
initProcess();
initScrubText();
initAccordion();
initCounters();
initForms();

initSmoothScroll();

// Year in the footer, so nobody has to remember to change it.
document.querySelectorAll('[data-year]').forEach((el) => {
  el.textContent = String(new Date().getFullYear());
});

// Drop the loading screen from the a11y tree once it has faded.
const loader = document.querySelector('.loader');
if (loader) setTimeout(() => loader.remove(), 1800);
