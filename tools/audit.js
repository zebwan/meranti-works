/* Measurement harness. Paste into the console (or run through the browser tool)
   on any page of the site; returns the numbers that have to match the source
   template at the current viewport width. */
(async () => {
  await new Promise((r) => setTimeout(r, 2500));
  const cs = (e) => getComputedStyle(e);
  const q = (s) => document.querySelector(s);
  const qa = (s) => [...document.querySelectorAll(s)];
  const bb = (e) => {
    if (!e) return null;
    const r = e.getBoundingClientRect();
    return { w: Math.round(r.width), h: Math.round(r.height), t: Math.round(r.top + scrollY) };
  };
  const num = (v) => parseFloat(v);

  const out = {
    viewport: { w: innerWidth, h: innerHeight },
    docHeight: document.documentElement.scrollHeight,
    overflowX: document.documentElement.scrollWidth - innerWidth,
  };

  // chrome
  out.nav = { ...bb(q('.nav')), position: cs(q('.nav')).position, z: cs(q('.nav')).zIndex };
  out.topBar = { ...bb(q('.nav__top')), pad: cs(q('.nav__top')).padding };
  out.mainNav = { ...bb(q('.nav__main')), pad: cs(q('.nav__main')).padding };
  const sn = q('.scrollnav');
  out.scrollNav = sn ? { ...bb(sn), display: cs(sn).display, h: Math.round(parseFloat(cs(sn).height)) } : null;
  out.burgerVisible = !!q('.burger') && cs(q('.burger')).display !== 'none';
  out.desktopLinksVisible = !!q('.nav__links') && cs(q('.nav__links')).display !== 'none';

  // gutter
  const gut = getComputedStyle(document.documentElement).getPropertyValue('--gutter').trim();
  out.gutter = gut;

  // type scale
  const t = (sel) => {
    const e = q(sel);
    if (!e) return null;
    const c = cs(e);
    return { size: c.fontSize, lh: c.lineHeight, ls: c.letterSpacing, weight: c.fontWeight, family: c.fontFamily.split(',')[0] };
  };
  out.type = { h1: t('h1'), h2: t('h2'), h3: t('.t-h3'), body: t('.t-body'), lead: t('.t-lead') };

  // hero
  const hp = q('.hero__panel') || q('.phero__panel');
  out.hero = hp ? { ...bb(hp), pad: cs(hp).padding, radius: cs(hp).borderRadius } : null;
  out.heroIsFullHeight = hp && q('.hero') ? Math.abs(bb(q('.hero')).h - innerHeight) < 2 : null;
  out.heroFloatVisible = q('.hero__float') ? cs(q('.hero__float')).display !== 'none' : null;
  out.heroRatingVisible = q('.hero__rating') ? cs(q('.hero__rating')).display !== 'none' : null;

  // sections
  out.sections = qa('main > *').map((e) => ({
    cls: e.className.split(' ')[0] || e.tagName.toLowerCase(),
    ...bb(e),
    padT: cs(e).paddingTop, padL: cs(e).paddingLeft,
  }));

  // pinning
  out.sticky = qa('*').filter((x) => cs(x).position === 'sticky')
    .map((x) => ({ cls: (x.className || '').toString().split(' ')[0], top: cs(x).top, ...bb(x) }));
  const tr = q('.process__track');
  out.processTrack = tr ? { ...bb(tr), stickyPos: cs(q('.process__sticky')).position } : null;

  // grids
  const grid = (sel) => (q(sel) ? cs(q(sel)).gridTemplateColumns.split(' ').length : null);
  out.cols = { blogs: grid('.blogs__grid'), why: grid('.why__grid'), project: grid('.project'), faq: grid('.faq__split') };

  // slider
  const sl = q('[data-slider]');
  out.slider = sl ? {
    slideW: Math.round(bb(q('.slider__slide')).w),
    visible: Math.round(bb(q('.slider__viewport')).w / (bb(q('.slider__slide')).w + num(cs(q('.slider__track')).gap))),
    snap: cs(q('.slider__viewport')).scrollSnapType,
  } : null;

  // assets
  const imgs = qa('img');
  out.images = {
    total: imgs.length,
    decoded: imgs.filter((i) => i.complete && i.naturalWidth > 0).length,
    broken: imgs.filter((i) => i.complete && i.naturalWidth === 0).map((i) => i.currentSrc.split('/').pop()),
  };
  out.oversizedIcons = qa('svg').filter((s) => {
    const r = s.getBoundingClientRect();
    return (r.width > 48 || r.height > 48) && !s.closest('.map');
  }).length;

  out.fontsLoaded = document.fonts.status;
  out.lang = document.documentElement.lang;
  out.h1Count = qa('h1').length;
  out.imgsMissingAlt = qa('img:not([alt])').length;
  out.imgsMissingDims = qa('img:not([width])').length;

  return out;
})()
