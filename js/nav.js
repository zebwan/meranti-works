/* ==========================================================================
   nav.js
   Three behaviours, matching the source:
     1. desktop mega menu / dropdown, opened on hover and on keyboard focus
     2. phone drawer that grows inside the nav panel (1px -> content height)
        and closes again on scroll
     3. a second, fixed nav that slides in once you are past the hero —
        1200px and up only; below that the source hides it entirely
   ========================================================================== */

const DESKTOP = '(min-width: 1200px)';

export function initNav() {
  const nav = document.querySelector('.nav');
  if (!nav) return;

  /* ---- 1. desktop menus ---- */
  const items = nav.querySelectorAll('.nav__item[data-menu]');
  let closeTimer = 0;

  const closeAll = (except) => {
    items.forEach((i) => { if (i !== except) i.dataset.open = 'false'; });
  };

  items.forEach((item) => {
    const open = () => {
      if (!matchMedia(DESKTOP).matches) return;
      clearTimeout(closeTimer);
      closeAll(item);
      item.dataset.open = 'true';
    };
    const close = () => {
      closeTimer = setTimeout(() => { item.dataset.open = 'false'; }, 120);
    };
    item.addEventListener('mouseenter', open);
    item.addEventListener('mouseleave', close);
    item.addEventListener('focusin', open);
    item.addEventListener('focusout', (e) => {
      if (!item.contains(e.relatedTarget)) item.dataset.open = 'false';
    });
  });

  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') closeAll(null); });

  /* ---- 2. phone drawer ---- */
  const burger = nav.querySelector('.burger');
  const drawer = nav.querySelector('.drawer');
  const drawerInner = nav.querySelector('.drawer__inner');

  const setDrawer = (open) => {
    if (!drawer) return;
    nav.dataset.drawer = open ? 'open' : 'closed';
    drawer.style.height = open ? `${drawerInner.scrollHeight}px` : '0px';
    burger?.setAttribute('aria-expanded', String(open));
  };

  burger?.addEventListener('click', () => {
    setDrawer(nav.dataset.drawer !== 'open');
  });

  // Nested Services / More Pages groups inside the drawer.
  nav.querySelectorAll('.drawer__group').forEach((group) => {
    const toggle = group.querySelector('.drawer__link');
    const sub = group.querySelector('.drawer__sub');
    toggle?.addEventListener('click', (e) => {
      e.preventDefault();
      const open = group.dataset.open !== 'true';
      group.dataset.open = String(open);
      sub.style.height = open ? `${sub.scrollHeight}px` : '0px';
      // the drawer itself has to grow to fit
      requestAnimationFrame(() => {
        if (nav.dataset.drawer === 'open') drawer.style.height = `${drawerInner.scrollHeight}px`;
      });
    });
  });

  // The source closes the drawer as soon as you scroll.
  let lastY = window.scrollY;
  const onScrollCloseDrawer = () => {
    if (nav.dataset.drawer === 'open' && Math.abs(window.scrollY - lastY) > 12) setDrawer(false);
    lastY = window.scrollY;
  };

  /* ---- 3. fixed scroll nav ---- */
  const scrollnav = document.querySelector('.scrollnav');
  const threshold = () => Math.min(window.innerHeight * 0.6, 520);

  const onScroll = () => {
    onScrollCloseDrawer();
    if (!scrollnav) return;
    scrollnav.dataset.show = String(
      matchMedia(DESKTOP).matches && window.scrollY > threshold(),
    );
  };

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', () => {
    closeAll(null);
    if (nav.dataset.drawer === 'open') drawer.style.height = `${drawerInner.scrollHeight}px`;
    onScroll();
  }, { passive: true });

  onScroll();
}
