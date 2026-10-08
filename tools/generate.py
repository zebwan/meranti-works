#!/usr/bin/env python3
"""Generate every page of the Meranti Works site from data/content.json.

Run from anywhere:   python3 tools/generate.py
Writes 32 HTML files (7 top level + 6 services + 4 projects + 5 locations +
8 blog posts + privacy + terms) into the project root.
"""
import json, os, sys, shutil, html as _html

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

from icons import icon              # noqa: E402
from mapsvg import dotted_map, percent, PLACES   # noqa: E402

C = json.load(open(f'{ROOT}/data/content.json'))
IMG = json.load(open(f'{ROOT}/data/images.json'))
S = C['site']

written = []


# ---------------------------------------------------------------- helpers ----
def e(s):
    return _html.escape(str(s), quote=True)


def up(depth):
    return '../' * depth


def img(slot, cls='cover', depth=0, loading='lazy', sizes=None, extra=''):
    """<img> for a manifest slot, with its real intrinsic size so nothing shifts."""
    from PIL import Image
    path = f'{ROOT}/assets/img/{slot}.jpg'
    w, h = Image.open(path).size
    alt = IMG[slot]['alt']
    attrs = [
        f'src="{up(depth)}assets/img/{slot}.jpg"',
        f'width="{w}"', f'height="{h}"',
        f'alt="{e(alt)}"',
        f'class="{cls}"',
        f'loading="{loading}"',
        'decoding="async"',
    ]
    if loading == 'eager':
        attrs.append('fetchpriority="high"')
    if sizes:
        attrs.append(f'sizes="{sizes}"')
    if extra:
        attrs.append(extra)
    return f'<img {" ".join(attrs)}>'


def label(text):
    return (f'<span class="t-eyebrow label"><span class="slash">//</span>{e(text)}</span>')


def roll(text, reverse=True, stagger=35, duration=0.4):
    """Per-character rolling text, the way the source's RollingTextHover does it.

    One line of characters over a text-shadow copy sitting exactly one
    line-height below; each character rises in turn. Delay per character is
    (duration / length) * index * (stagger / 100), counted from the end for
    buttons and from the start for nav links.
    """
    chars = list(str(text))
    n = max(len(chars), 1)
    step_ms = (duration / n) * (stagger / 100) * 1000
    spans = []
    for i, ch in enumerate(chars):
        idx = (n - 1 - i) if reverse else i
        spans.append(f'<i style="--i:{idx}">{e(ch) if ch != " " else "&#160;"}</i>')
    return (f'<span class="roll" style="--roll-step:{step_ms:.2f}ms" '
            f'aria-label="{e(text)}">{"".join(spans)}</span>')


def btn(text, href, kind='primary', depth=0, glow=False, block=False, icon_name='chevron-right'):
    # `glow` is retained for call-site readability; the glow now comes from the
    # variant itself, exactly as the source's Button component does it.
    cls = f'btn btn--{kind}'
    if glow:
        cls += ' btn--glow'
    if block:
        cls += ' btn--block'
    return (f'<a class="{cls}" href="{up(depth)}{href}">'
            f'<span class="btn__label">{roll(text)}</span>'
            f'{icon(icon_name, 2.2, "btn__icon")}</a>')


def phone_btn(depth=0, glow=True, block=False):
    cls = 'btn btn--phone' + (' btn--glow' if glow else '') + (' btn--block' if block else '')
    return (f'<a class="{cls}" href="tel:{S["phoneHref"]}">'
            f'<span class="btn__avatar">{icon("phone", 2, "")}</span>'
            f'<span class="btn__label">{roll(S["phoneDisplay"])}</span></a>')


def stars(n=5):
    return '<span class="stars">' + icon('star') * n + '</span>'


SOCIAL_ICON = {'fb': 'facebook', 'ig': 'instagram', 'wa': 'whatsapp', 'x': 'x'}


# -------------------------------------------------------------------- head ----
def head(title, description, depth=0, page_css=''):
    u = up(depth)
    return f'''<!doctype html>
<html lang="en-MY">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(description)}">
<meta name="robots" content="noindex, nofollow">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(description)}">
<meta name="theme-color" content="#0C0E0C">
<script>document.documentElement.className+=' js';</script>
<link rel="icon" href="{u}assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="">
<link rel="preload" as="font" type="font/woff2" crossorigin
      href="{u}assets/fonts/{PRELOAD_FONT}">
<link rel="stylesheet" href="{u}css/fonts.css">
<link rel="stylesheet" href="{u}css/tokens.css">
<link rel="stylesheet" href="{u}css/base.css">
<link rel="stylesheet" href="{u}css/components.css">
<link rel="stylesheet" href="{u}css/sections.css">{page_css}
<script type="module" src="{u}js/main.js"></script>
</head>
<body>
<a class="sr-only" href="#main">Skip to content</a>
<div class="loader" aria-hidden="true">
  <div style="text-align:center">
    <div class="loader__mark">MERANTI<b>.</b></div>
    <div class="loader__bar"><i></i></div>
  </div>
</div>
'''


PRELOAD_FONT = 'PfdOpgzFf7N2Uye9JX7xRKYTgSc.woff2'   # Inter Display 600, basic latin


# --------------------------------------------------------------------- nav ----
def nav(active, depth=0):
    u = up(depth)
    links = []
    for item in C['nav']:
        href = item['href']
        is_active = item['href'] == active
        menu = item.get('menu')
        aria = ' aria-current="page"' if is_active else ''
        chev = icon('chevron-down', 2.4, 'chev') if menu else ''
        inner = f'<a class="nav__link" href="{u}{href}"{aria}>{roll(item["label"], reverse=False)}{chev}</a>'
        if menu == 'services':
            inner += mega_services(depth)
        elif menu == 'more':
            inner += dropdown_more(depth)
        attr = ' data-menu="true" data-open="false"' if menu else ''
        cls = 'nav__item nav__item--mega' if menu == 'services' else 'nav__item'
        links.append(f'<div class="{cls}"{attr}>{inner}</div>')

    socials = ''.join(
        f'<a href="{sc["href"]}" aria-label="{e(sc["label"])}">{icon(SOCIAL_ICON[sc["k"]])}</a>'
        for sc in S['social'])

    drawer_links = []
    for item in C['nav']:
        if item.get('menu') == 'services':
            subs = ''.join(f'<a href="{u}services/{s["slug"]}.html">{e(s["name"])}</a>' for s in C['services'])
            drawer_links.append(
                f'<div class="drawer__group" data-open="false">'
                f'<a class="drawer__link" href="{u}services.html">{e(item["label"])}{icon("chevron-down", 2.4, "chev")}</a>'
                f'<div class="drawer__sub">{subs}</div></div>')
        elif item.get('menu') == 'more':
            subs = ''.join(f'<a href="{u}{m["href"]}">{e(m["label"])}</a>' for m in C['morePages'])
            drawer_links.append(
                f'<div class="drawer__group" data-open="false">'
                f'<a class="drawer__link" href="#">{e(item["label"])}{icon("chevron-down", 2.4, "chev")}</a>'
                f'<div class="drawer__sub">{subs}</div></div>')
        else:
            drawer_links.append(f'<a class="drawer__link" href="{u}{item["href"]}">{e(item["label"])}</a>')

    return f'''
<nav class="nav" data-drawer="closed" aria-label="Main">
  <div class="nav__top">
    <div class="nav__topleft">
      {icon('phone', 2)}
      <a href="tel:{S['phoneHref']}">{e(S['phoneDisplay'])}</a>
    </div>
    <div class="nav__social">{socials}</div>
  </div>
  <div class="nav__main">
    <a class="logo" href="{u}index.html" aria-label="{e(S['legalName'])} home">MERANTI<b>.</b></a>
    <div class="nav__links hide-md-dn">{''.join(links)}</div>
    <div class="hide-md-dn">{btn('Request a Quote', 'contact.html', 'primary', depth)}</div>
    <button class="burger hide-lg-up" aria-label="Menu" aria-expanded="false" aria-controls="drawer">
      <span></span><span></span><span></span>
    </button>
  </div>
  <div class="drawer hide-lg-up" id="drawer">
    <div class="drawer__inner">
      {''.join(drawer_links)}
      {btn('Request a Quote', 'contact.html', 'primary', depth, glow=True, block=True)}
    </div>
  </div>
</nav>

<div class="scrollnav" data-show="false" aria-hidden="true">
  <div class="scrollnav__inner">
    <a class="logo" href="{u}index.html" tabindex="-1">MERANTI<b>.</b></a>
    <div class="nav__links">
      {''.join(f'<a class="nav__link" href="{u}{i["href"]}" tabindex="-1">{roll(i["label"], reverse=False)}</a>' for i in C['nav'][:6])}
    </div>
    <a class="btn btn--primary" href="{u}contact.html" tabindex="-1">
      <span class="btn__label">{roll('Request a Quote')}</span>{icon('chevron-right', 2.2, 'btn__icon')}</a>
  </div>
</div>
'''


def mega_services(depth=0):
    u = up(depth)
    items = ''.join(
        f'<a class="mega__item" href="{u}services/{s["slug"]}.html">{icon(s["icon"])}'
        f'<div><h4>{e(s["name"])}</h4><p>{e(s["body"])}</p></div></a>'
        for s in C['services'])
    return f'''<div class="mega">
  <div class="mega__inner">
    <div class="mega__grid">{items}</div>
    <div class="mega__cta">
      {img('mega-quote', 'cover', depth)}
      <h3>Need a quote for your<br>build or renovation?</h3>
      {phone_btn(depth)}
    </div>
  </div>
</div>'''


def dropdown_more(depth=0):
    u = up(depth)
    return ('<div class="dropdown">'
            + ''.join(f'<a href="{u}{m["href"]}">{e(m["label"])}</a>' for m in C['morePages'])
            + '</div>')


# ------------------------------------------------------------------ footer ----
def cta_block(depth=0):
    u = up(depth)
    opts = ''.join(f'<option>{e(o)}</option>' for o in C['contact']['formServices'])
    return f'''
<div class="cta" data-reveal="40">
  <div class="cta__panel">
    {img('cta-home', 'cover', depth)}
    <div class="cta__scrim"></div>
    <div class="cta__content" data-reveal="150">
      {label(C['home']['ctaLabel'])}
      <h2 class="t-h2">{e(C['home']['ctaTitle'])}</h2>
      <p class="t-body">{e(C['home']['ctaIntro'])}</p>
      <div style="display:flex;gap:14px;flex-wrap:wrap;margin-top:6px">
        {phone_btn(depth)}
        <a class="btn btn--ghost" href="mailto:{S['email']}">
          <span class="btn__label">{roll(S['email'])}</span>{icon('mail', 2.2, 'btn__icon')}</a>
      </div>
    </div>
    <div class="cta__form" data-reveal="50">
      <form class="form" data-mock-form data-label="Send message" data-sent="false">
        <div class="form__row">
          <input class="field" name="name" placeholder="Full name" required autocomplete="name">
        </div>
        <div class="form__row">
          <input class="field" type="email" name="email" placeholder="Email address" required autocomplete="email">
          <input class="field" type="tel" name="phone" placeholder="Phone number" required autocomplete="tel">
        </div>
        <div class="form__row"><select class="field" name="service">{opts}</select></div>
        <div class="form__row"><textarea class="field" name="message" placeholder="Tell us about the job — what, where, and roughly when"></textarea></div>
        <button class="btn btn--primary btn--glow btn--block" type="submit">
          <span class="btn__label">Send message</span>{icon('arrow-right', 2.2, 'btn__icon')}</button>
        <p class="form__ok">Thanks — this is a demo site, so nothing was actually sent.</p>
        <p class="form__note">Demo form. Nothing is transmitted or stored.</p>
      </form>
    </div>
  </div>
</div>'''


def footer(depth=0):
    u = up(depth)
    svc = ''.join(f'<li><a href="{u}services/{s["slug"]}.html">{e(s["name"])}</a></li>' for s in C['services'][:4])
    quick = ''.join(f'<li><a href="{u}{i["href"]}">{e(i["label"])}</a></li>'
                    for i in C['nav'] if i.get('menu') is None)
    hours = ''.join(f'<li><p>{e(h["d"])} · {e(h["t"])}</p></li>' for h in S['hours'])
    socials = ''.join(
        f'<a href="{sc["href"]}" aria-label="{e(sc["label"])}">{icon(SOCIAL_ICON[sc["k"]])}</a>'
        for sc in S['social'])
    return f'''
<footer class="footer">
  <div class="wrap">
    <div class="footer__cols" data-reveal="150">
      <div class="footer__col">
        <h5>Quick links</h5>
        <ul>{quick}<li><a href="{u}contact.html">Contact</a></li></ul>
      </div>
      <div class="footer__col">
        <h5>Services</h5>
        <ul>{svc}</ul>
      </div>
      <div class="footer__col">
        <h5>Contact us</h5>
        <ul>
          <li><a href="mailto:{S['email']}">{e(S['email'])}</a></li>
          <li><a href="tel:{S['phoneHref']}">{e(S['phoneDisplay'])}</a></li>
          <li><p>{'<br>'.join(e(l) for l in S['addressLines'])}</p></li>
          {hours}
        </ul>
      </div>
    </div>

    <div style="display:flex;align-items:flex-end;justify-content:space-between;gap:48px;flex-wrap:wrap;margin-top:72px">
      <div class="footer__wordmark">MERANTI<b>.</b></div>
      <div style="display:flex;flex-direction:column;gap:18px;min-width:280px;flex:1 1 280px">
        <h5 style="font-family:var(--font-display);font-size:15px;font-weight:600">Get occasional build tips</h5>
        <form class="newsletter" data-mock-form data-label="Subscribe" data-sent="false">
          <input class="field" type="email" placeholder="Enter your email" required aria-label="Email address">
          <button type="submit">Subscribe</button>
        </form>
        <div>
          <h5>Follow us</h5>
          <div class="socials">{socials}</div>
        </div>
      </div>
    </div>

    <div class="footer__legal">
      <p>&copy; <span data-year>2026</span> {e(S['legalName'])}. Demo site — all content is placeholder.</p>
      <p style="display:flex;gap:20px">
        <a href="{u}privacy.html">Privacy Policy</a>
        <a href="{u}terms.html">Terms &amp; Conditions</a>
      </p>
    </div>
  </div>
</footer>
</body>
</html>'''


def shell(title, desc, body, depth=0, active='', with_cta=True):
    return (head(title, desc, depth)
            + nav(active, depth)
            + f'<main id="main" class="sections">{body}</main>'
            + (cta_block(depth) if with_cta else '')
            + footer(depth))


def write(path, content):
    full = os.path.join(ROOT, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    open(full, 'w', encoding='utf-8').write(content)
    written.append((path, len(content)))


# ============================================================ page builders ===
def service_card(s, depth=0, slide=False):
    return f'''<a class="card svc-card" href="{up(depth)}services/{s['slug']}.html">
  <div class="svc-card__media">
    {img(s['img'], 'cover', depth)}
    <div class="svc-card__icon">{icon(s['icon'])}</div>
  </div>
  <div class="svc-card__body">
    <h3 class="t-h3sm">{e(s['name'])}</h3>
    <p class="t-body">{e(s['excerpt'])}</p>
  </div>
</a>'''


def blog_card(b, depth=0):
    return f'''<a class="card blog-card" href="{up(depth)}blog/{b['slug']}.html">
  <div class="blog-card__media">{img(b['img'], 'cover', depth)}</div>
  <div class="blog-card__body">
    <span class="tag">{e(b['cat'])}</span>
    <h3 class="t-h3sm">{e(b['title'])}</h3>
    <div class="blog-card__meta"><span>{e(b['author'])}</span><span>·</span><span>{e(b['date'])}</span></div>
  </div>
</a>'''


def compare_block(p, depth=0):
    return f'''<div class="compare" data-start="50">
  {img(p['after'], 'compare__after', depth)}
  {img(p['before'], 'compare__before', depth)}
  <span class="compare__label compare__label--before">Before</span>
  <span class="compare__label compare__label--after">After</span>
  <div class="compare__divider"></div>
  <div class="compare__handle">{icon('chevrons', 2.2)}</div>
</div>'''


def project_block(p, depth=0):
    return f'''<article class="project">
  <div class="project__media">{compare_block(p, depth)}</div>
  <div class="project__body">
    <div class="project__meta">
      {icon('calendar')}<span>{e(p['date'])}</span><span class="dot">•</span>
      {icon('pin')}<span>{e(p['location'])}</span>
    </div>
    <h3 class="t-h3">{e(p['name'])}</h3>
    <p class="t-body">{e(p['excerpt'])}</p>
    <div>{btn('Project details', f"projects/{p['slug']}.html", 'ghost', depth)}</div>
  </div>
</article>'''


def review_card(r, depth=0):
    return f'''<figure class="review">
  <div class="review__quote">{icon('quote')}</div>
  <blockquote class="review__text">“{e(r['text'])}”</blockquote>
  <figcaption class="review__who">
    {img(r['avatar'], '', depth)}
    <div>
      <div style="font-family:var(--font-display);font-weight:600">{e(r['name'])}</div>
      <div style="font-size:13px;color:var(--w-40)">{e(r['where'])}</div>
    </div>
  </figcaption>
</figure>'''


def faq_block(depth=0):
    items = ''
    for i, f in enumerate(C['faqs']):
        items += f'''<div class="faq__item" data-open="{'true' if i == 0 else 'false'}">
  <button class="faq__q" aria-expanded="{'true' if i == 0 else 'false'}">
    <span>{e(f['q'])}</span><span class="faq__toggle"></span>
  </button>
  <div class="faq__a"><p class="t-body">{e(f['a'])}</p></div>
</div>'''
    return items


def map_block(depth=0):
    pins = ''
    for loc in C['locations']:
        lon, lat = PLACES[loc['slug']]
        x, y = percent(lon, lat)
        pins += (f'<a class="map__pin" data-pos="{loc.get("labelPos", "n")}" '
                 f'style="left:{x}%;top:{y}%" '
                 f'href="{up(depth)}locations/{loc["slug"]}.html">'
                 f'<span>{e(loc["name"])}</span><i></i></a>')
    return f'<div class="map">{dotted_map()}{pins}</div>'


# ------------------------------------------------------------------- home ----
def build_home():
    h = C['home']
    slides = ''.join(f'<div class="slider__slide">{service_card(s)}</div>' for s in C['services'])
    steps = ''
    for i, p in enumerate(C['process']):
        steps += f'''<div class="process__step" data-active="{'true' if i == 0 else 'false'}">
  <div class="process__stephead">{icon(p['icon'])}<h3>{e(p['title'])}</h3></div>
  <p class="t-body">{e(p['body'])}</p>
</div>'''
    step_imgs = ''.join(img(p['img'], 'cover', 0, extra=f'data-active="{"true" if i == 0 else "false"}"')
                        for i, p in enumerate(C['process']))
    projects = ''.join(project_block(p) for p in C['projects'])
    row_a = ''.join(review_card(r) for r in C['reviews'])
    row_b = ''.join(review_card(r) for r in list(reversed(C['reviews'])))
    blogs = ''.join(blog_card(b) for b in C['blog'][:3])
    chips = ''.join(f'<span class="why__chip">{icon("check")}{e(c)}</span>' for c in h['whyChips'])
    avs = ''.join(img(f'av-{i}', '', 0) for i in (1, 2, 3))

    body = f'''
<header class="hero" data-reveal="40">
  <div class="hero__panel">
    {img('hero-home', 'cover', 0, loading='eager', sizes='100vw')}
    <div class="hero__scrim"></div>
    <div class="hero__content">
      <h1 class="t-h1 hero__title">{e(h['heroTitle'])}</h1>
      <div>{phone_btn()}</div>
      <ul class="hero__trust">
        {''.join(f'<li>{icon("check-circle")}{e(t)}</li>' for t in h['heroTrust'])}
      </ul>
    </div>
    <div class="hero__float">
      {img('hero-card-thumb', '', 0)}
      <div>
        <h4>{e(h['floatCard']['title'])}</h4>
        <a href="{h['floatCard']['href']}">{e(h['floatCard']['cta'])}{icon('chevron-right', 2.4)}</a>
      </div>
    </div>
    <div class="hero__rating">{stars()}<span>{e(S['ratingLabel'])}</span></div>
  </div>
</header>

<section class="services" data-reveal="40">
  <div class="services__inner">
    <div class="sechead sechead--center">
      {label(h['servicesLabel'])}
      <h2 class="t-h2">{e(h['servicesTitle'])}</h2>
      <p class="t-body">{e(h['servicesIntro'])}</p>
    </div>
    <div class="slider" data-slider tabindex="0">
      <div class="slider__viewport"><div class="slider__track">{slides}</div></div>
      <div class="slider__controls">
        <button class="iconbtn" data-slider-prev aria-label="Previous services">
          <span class="iconbtn__slide">{icon('arrow-left', 2)}{icon('arrow-left', 2)}</span></button>
        <div class="slider__progress"><i></i></div>
        <button class="iconbtn" data-slider-next aria-label="Next services">
          <span class="iconbtn__slide">{icon('arrow-right', 2)}{icon('arrow-right', 2)}</span></button>
      </div>
    </div>
    <div class="services__cta">{btn('Request a service', 'contact.html', 'primary', glow=True)}</div>
  </div>
</section>

<section class="about" data-reveal="40">
  <div class="about__inner">
    <div class="about__intro">
      {label(h['aboutLabel'])}
      <p class="scrub" data-scrub>{e(h['aboutScrub'])}</p>
    </div>
    <div class="about__split">
      <div class="about__card">
        <h3 class="t-h3">{e(h['aboutCardTitle'])}</h3>
        <div>
          <p class="t-body" style="margin-bottom:24px">{e(h['aboutCardBody'])}</p>
          {btn(h['aboutCta'], 'about.html', 'primary')}
        </div>
      </div>
      <div class="about__media">{img('about-bw', 'cover')}</div>
    </div>
  </div>
</section>

<section class="why" data-reveal="40">
  <div class="why__inner">
    <div class="sechead sechead--center">
      {label(h['whyLabel'])}
      <h2 class="t-h2">{e(h['whyTitle'])}</h2>
    </div>
    <div class="why__grid">
      <div class="why__cell why__cell--media">
        {img('why-main', 'cover')}
        <div class="why__cellbody">
          <h3 class="t-h3sm" style="max-width:18ch">{e(h['whyMediaTitle'])}</h3>
          <div class="why__chips">{chips}</div>
        </div>
      </div>
      <div class="why__cell">
        <div>
          <div class="why__stat">{S['rating']}<span style="color:var(--accent)">+</span></div>
          <p class="t-body" style="margin-top:10px">{e(h['whyRatingLabel'])}</p>
        </div>
        <div class="avatars">{avs}<span class="more">{e(h['whyAvatarsMore'])}</span></div>
      </div>
      <div class="why__cell why__cell--quote">
        <p class="why__quote">{h['whyQuote']}</p>
      </div>
      <div class="why__cell">
        <h3 class="t-h3sm">{e(h['whyCoveredTitle'])}</h3>
        <p class="t-body">{e(h['whyCoveredBody'])}</p>
      </div>
      <div class="why__cell why__cell--photo">{img('why-worker', 'cover')}</div>
      <div class="why__cell">
        <div class="why__stat"><span data-count="{h['whyStat']}" data-suffix="{h['whyStatSuffix']}">0</span></div>
        <p class="t-body">{e(h['whyStatLabel'])}</p>
      </div>
    </div>
  </div>
</section>

<section class="process" data-process data-reveal="40">
  <div class="process__inner">
    <div class="process__head sechead sechead--center">
      {label(h['processLabel'])}
      <h2 class="t-h2">{e(h['processTitle'])}</h2>
      <p class="t-body">{e(h['processIntro'])}</p>
    </div>
    <div class="process__track" style="--steps:{len(C['process'])}">
      <div class="process__sticky">
        <div class="process__media">{step_imgs}</div>
        <div class="process__steps">
          <div class="process__rail"><i></i></div>
          {steps}
        </div>
      </div>
    </div>
    <div class="process__cta">{phone_btn()}</div>
  </div>
</section>

<section class="projects" data-reveal="40">
  <div class="projects__inner">
    <div class="sechead sechead--center" data-reveal="150">
      {label(h['projectsLabel'])}
      <h2 class="t-h2">{e(h['projectsTitle'])}</h2>
      <p class="t-body">{e(h['projectsIntro'])}</p>
    </div>
    <div class="projects__list">{projects}</div>
  </div>
</section>

<section class="reviews" data-reveal="40">
  <div class="reviews__inner">
    <div class="sechead sechead--center" data-reveal="150">
      <div class="reviews__badge">{stars()}<span class="t-micro" style="color:var(--w-40)">{e(S['ratingLabel'])}</span></div>
      <h2 class="t-h2">{e(h['reviewsTitle'])}</h2>
      <p class="t-body">{e(h['reviewsIntro'])}</p>
    </div>
  </div>
  <div class="reviews__rows">
    <div class="marquee" data-marquee data-velocity="40" data-velocity-column="100" data-column-below="810" data-hover="32" data-direction="default">
      <div class="marquee__track">{row_a}</div>
    </div>
    <div class="marquee" data-marquee data-velocity="40" data-velocity-column="100" data-column-below="810" data-hover="32" data-direction="reverse">
      <div class="marquee__track">{row_b}</div>
    </div>
  </div>
</section>

<section class="areas" data-reveal="40">
  <div class="areas__inner">
    <div class="sechead sechead--center" data-reveal="150">
      {label(h['areasLabel'])}
      <h2 class="t-h2">{e(h['areasTitle'])}</h2>
      <p class="t-body">{e(h['areasIntro'])}</p>
    </div>
    {map_block()}
    {btn(h['areasCta'], 'locations.html', 'primary', glow=True)}
  </div>
</section>

<div class="blogs" data-reveal="40">
  <div class="blogs__inner">
    <div class="blogs__head">
      <div class="sechead">
        {label(h['blogsLabel'])}
        <h2 class="t-h2">{e(h['blogsTitle'])}</h2>
        <p class="t-body">{e(h['blogsIntro'])}</p>
      </div>
      {btn(h['blogsCta'], 'blog.html', 'primary', glow=True)}
    </div>
    <div class="blogs__grid">{blogs}</div>
  </div>
</div>

<section class="faq" data-reveal="40">
  <div class="faq__split">
    <div class="faq__left">
      <h2 class="t-h2">{e(h['faqTitle'])}</h2>
      <p class="t-body">{e(h['faqIntro'])}</p>
      <div style="margin-top:8px">{phone_btn()}</div>
    </div>
    <div data-accordion>{faq_block()}</div>
  </div>
</section>
'''
    write('index.html', shell(h['title'], h['description'], body, 0, 'index.html'))


# ----------------------------------------------------- inner page scaffold ----
def phero(title, intro, slot, crumbs, depth=0):
    crumb_html = ' '.join(
        (f'<a href="{up(depth)}{href}">{e(txt)}</a>' if href else f'<span>{e(txt)}</span>')
        + ('<span>/</span>' if i < len(crumbs) - 1 else '')
        for i, (txt, href) in enumerate(crumbs))
    return f'''<header class="phero" data-reveal="40">
  <div class="phero__panel">
    {img(slot, 'cover', depth, loading='eager', sizes='100vw')}
    <div class="phero__scrim"></div>
    <div class="phero__content">
      <nav class="crumbs" aria-label="Breadcrumb">{crumb_html}</nav>
      <h1 class="t-h1">{e(title)}</h1>
      <p class="t-lead">{e(intro)}</p>
    </div>
  </div>
</header>'''


# ------------------------------------------------------------------ about ----
def build_about():
    a = C['about']
    stats = ''.join(f'''<div class="stat" data-stagger>
  <div class="stat__n"><span data-count="{s['n']}" data-suffix="{e(s['suffix'])}">0</span></div>
  <p class="t-body">{e(s['label'])}</p></div>''' for s in a['stats'])
    values = ''.join(f'''<div class="card" style="padding:28px;gap:10px" data-stagger>
  <h3 class="t-h3sm">{e(v['t'])}</h3><p class="t-body">{e(v['b'])}</p></div>''' for v in a['values'])
    team = ''.join(f'''<div data-stagger>
  <div style="border-radius:var(--r-md);overflow:hidden;aspect-ratio:4/3">{img(t['img'], 'cover')}</div>
  <h3 class="t-h3sm" style="margin-top:16px">{e(t['name'])}</h3>
  <p class="t-micro" style="color:var(--accent);margin-top:8px">{e(t['role'])}</p>
  <p class="t-body" style="margin-top:10px">{e(t['bio'])}</p></div>''' for t in C['team'])

    body = f'''
{phero(a['heroTitle'], a['intro'], 'page-about', [('Home', 'index.html'), ('About', None)])}

<section class="section" data-reveal="40">
  <div class="grid-2" style="gap:48px;align-items:center">
    <div class="sechead">
      {label('Our mission')}
      <h2 class="t-h2">{e(a['missionTitle'])}</h2>
      <p class="t-body">{e(a['missionBody'])}</p>
      <div style="margin-top:12px">{btn('Talk to us', 'contact.html', 'primary')}</div>
    </div>
    <div style="border-radius:var(--r-md);overflow:hidden;aspect-ratio:3/2">{img('about-crane', 'cover')}</div>
  </div>
</section>

<section class="section--tight" style="padding-inline:var(--gutter)" data-reveal="40">
  <div class="stats">{stats}</div>
</section>

<section class="section" data-reveal="40">
  <div class="sechead" style="margin-bottom:40px">
    {label('How we work')}
    <h2 class="t-h2">{e(a['valuesTitle'])}</h2>
  </div>
  <div class="grid-4">{values}</div>
</section>

<section class="section" data-reveal="40">
  <div class="sechead" style="margin-bottom:40px">
    {label('The team')}
    <h2 class="t-h2">The People Who Will Be on Your Site</h2>
  </div>
  <div class="grid-4">{team}</div>
</section>

<section class="section" data-reveal="40">
  <div style="border-radius:var(--r-md);overflow:hidden;aspect-ratio:21/9">{img('about-team', 'cover')}</div>
</section>
'''
    write('about.html', shell('About | ' + S['legalName'],
                              a['intro'][:155], body, 0, 'about.html'))


# --------------------------------------------------------------- services ----
def build_services():
    cards = ''.join(f'<div data-stagger>{service_card(s)}</div>' for s in C['services'])
    body = f'''
{phero('Construction Services Built for Malaysian Weather',
       'Main contracting, residential and commercial builds, renovation, foundations and roofing across the Klang Valley.',
       'page-services', [('Home', 'index.html'), ('Services', None)])}

<section class="section" data-reveal="40">
  <div class="sechead" style="margin-bottom:40px">
    {label('What we do')}
    <h2 class="t-h2">Six Things We Do Properly</h2>
    <p class="t-body">Each one gets a written scope, a fixed price and a named supervisor.</p>
  </div>
  <div class="grid-3">{cards}</div>
</section>

<section class="section" data-reveal="40">
  <div class="sechead sechead--center" style="margin-bottom:40px">
    {label('Process')}
    <h2 class="t-h2">{e(C['home']['processTitle'])}</h2>
  </div>
  <div class="grid-4">
    {''.join(f"""<div class="card" style="padding:28px;gap:12px" data-stagger>
      <div style="color:var(--accent);width:24px">{icon(p['icon'])}</div>
      <h3 class="t-h3sm">{e(p['title'])}</h3>
      <p class="t-body">{e(p['body'])}</p></div>""" for p in C['process'])}
  </div>
</section>

<section class="faq" data-reveal="40" style="padding-top:0">
  <div class="faq__split">
    <div class="faq__left">
      <h2 class="t-h2">{e(C['home']['faqTitle'])}</h2>
      <p class="t-body">{e(C['home']['faqIntro'])}</p>
    </div>
    <div data-accordion>{faq_block()}</div>
  </div>
</section>
'''
    write('services.html', shell('Services | ' + S['legalName'],
                                 'Main contracting, residential and commercial construction, renovation, piling and roofing in the Klang Valley.',
                                 body, 0, 'services.html'))


def build_service_detail(s):
    d = 1
    others = [x for x in C['services'] if x['slug'] != s['slug']][:3]
    inc = ''.join(f'<li>{e(i)}</li>' for i in s['includes'])
    rel = ''.join(f'<div data-stagger>{service_card(o, d)}</div>' for o in others)
    body = f'''
{phero(s['heroTitle'], s['excerpt'], s['img'],
       [('Home', 'index.html'), ('Services', 'services.html'), (s['name'], None)], d)}

<section class="section" data-reveal="40">
  <div class="grid-2" style="gap:48px;align-items:start">
    <div class="prose">
      <h2>{e(s['name'])} in the Klang Valley</h2>
      <p>{e(s['intro'])}</p>
      <h3>What the job includes</h3>
      <ul>{inc}</ul>
      <p>Every quote is written, itemised and fixed before work starts. If the scope changes on site, we price the change and get it approved before we build it — no silent variation orders.</p>
    </div>
    <div style="display:flex;flex-direction:column;gap:24px">
      <div style="border-radius:var(--r-md);overflow:hidden;aspect-ratio:3/2">{img(s['bodyImg'], 'cover', d)}</div>
      <dl class="facts">
        <div><dt>Indicative price</dt><dd>{e(s['price'])}</dd></div>
        <div><dt>Typical duration</dt><dd>{e(s['duration'])}</dd></div>
      </dl>
      <div class="card" style="padding:28px;gap:16px">
        <h3 class="t-h3sm">Want this priced?</h3>
        <p class="t-body">Free site visit and written quote anywhere in the Klang Valley.</p>
        {phone_btn(d, block=True)}
      </div>
    </div>
  </div>
</section>

<section class="section" data-reveal="40">
  <div class="sechead" style="margin-bottom:40px">
    {label('More services')}
    <h2 class="t-h2">Other Things We Build</h2>
  </div>
  <div class="grid-3">{rel}</div>
</section>
'''
    write(f'services/{s["slug"]}.html',
          shell(f'{s["name"]} | {S["legalName"]}', s['excerpt'][:155], body, d, 'services.html'))


# --------------------------------------------------------------- projects ----
def build_projects():
    items = ''.join(project_block(p) for p in C['projects'])
    body = f'''
{phero('Work We Have Finished',
       'Drag the handle on any photo to see what the building looked like before we started.',
       'page-projects', [('Home', 'index.html'), ('Projects', None)])}

<section class="projects" data-reveal="40">
  <div class="projects__inner">
    <div class="projects__list">{items}</div>
  </div>
</section>
'''
    write('projects.html', shell('Projects | ' + S['legalName'],
                                 'Recent construction, fit-out and restoration projects across Kuala Lumpur and Selangor.',
                                 body, 0, 'projects.html'))


def build_project_detail(p):
    d = 1
    others = [x for x in C['projects'] if x['slug'] != p['slug']][:2]
    paras = ''.join(f'<p>{e(x)}</p>' for x in p['body'].split('\n\n'))
    rel = ''.join(f'''<a class="card blog-card" href="{up(d)}projects/{o['slug']}.html" data-stagger>
      <div class="blog-card__media">{img(o['after'], 'cover', d)}</div>
      <div class="blog-card__body"><span class="tag">{e(o['type'])}</span>
      <h3 class="t-h3sm">{e(o['name'])}</h3>
      <div class="blog-card__meta"><span>{e(o['location'])}</span></div></div></a>''' for o in others)
    body = f'''
{phero(p['name'], p['excerpt'], p['after'],
       [('Home', 'index.html'), ('Projects', 'projects.html'), (p['name'], None)], d)}

<section class="section" data-reveal="40">
  <dl class="facts" style="margin-bottom:48px">
    <div><dt>Location</dt><dd>{e(p['location'])}</dd></div>
    <div><dt>Completed</dt><dd>{e(p['date'])}</dd></div>
    <div><dt>Type</dt><dd>{e(p['type'])}</dd></div>
    <div><dt>Contract value</dt><dd>{e(p['value'])}</dd></div>
    <div><dt>Duration</dt><dd>{e(p['duration'])}</dd></div>
  </dl>
  <div class="grid-2" style="gap:48px;align-items:start">
    <div class="prose">
      <h2>About this project</h2>
      {paras}
    </div>
    <div style="border-radius:var(--r-lg);overflow:hidden;aspect-ratio:4/3;position:relative">
      {compare_block(p, d)}
    </div>
  </div>
</section>

<section class="section" data-reveal="40">
  <div class="sechead" style="margin-bottom:40px">
    {label('More work')}
    <h2 class="t-h2">Other Projects</h2>
  </div>
  <div class="grid-2">{rel}</div>
</section>
'''
    write(f'projects/{p["slug"]}.html',
          shell(f'{p["name"]} | {S["legalName"]}', p['excerpt'][:155], body, d, 'projects.html'))


# -------------------------------------------------------------- locations ----
def build_locations():
    cards = ''.join(f'''<a class="card blog-card" href="locations/{l['slug']}.html" data-stagger>
  <div class="blog-card__media">{img(l['img'], 'cover')}</div>
  <div class="blog-card__body">
    <span class="tag">{e(l['state'])}</span>
    <h3 class="t-h3sm">{e(l['name'])}</h3>
    <p class="t-body">{e(l['blurb'])}</p>
  </div></a>''' for l in C['locations'])
    body = f'''
{phero('Where We Work',
       'Five Klang Valley bases, with selected work further south on request.',
       'page-locations', [('Home', 'index.html'), ('Locations', None)])}

<section class="areas" data-reveal="40">
  <div class="areas__inner">{map_block()}</div>
</section>

<section class="section" data-reveal="40">
  <div class="sechead" style="margin-bottom:40px">
    {label('Service areas')}
    <h2 class="t-h2">Pick Your Area</h2>
  </div>
  <div class="grid-3">{cards}</div>
</section>
'''
    write('locations.html', shell('Locations | ' + S['legalName'],
                                  'Construction and renovation across Kuala Lumpur, Petaling Jaya, Shah Alam, Subang Jaya and Klang.',
                                  body, 0, 'locations.html'))


def build_location_detail(l):
    d = 1
    areas = ''.join(f'<li>{e(a)}</li>' for a in l['areas'])
    svc = ''.join(f'<div data-stagger>{service_card(s, d)}</div>' for s in C['services'][:3])
    body = f'''
{phero(f'Contractor in {l["name"]}', l['blurb'], l['img'],
       [('Home', 'index.html'), ('Locations', 'locations.html'), (l['name'], None)], d)}

<section class="section" data-reveal="40">
  <div class="grid-2" style="gap:48px;align-items:start">
    <div class="prose">
      <h2>Building and renovating in {e(l['name'])}</h2>
      <p>{e(l['blurb'])}</p>
      <p>Most of the housing stock here was built between the 1980s and the early 2000s, which means the two jobs we are called out for most are roof and gutter work, and extensions onto structures that were never designed to carry them. Both are worth checking properly before anyone starts quoting on finishes.</p>
      <h3>Neighbourhoods we cover</h3>
      <ul>{areas}</ul>
    </div>
    <div style="display:flex;flex-direction:column;gap:24px">
      <div class="card" style="padding:28px;gap:16px">
        <h3 class="t-h3sm">Free site visit in {e(l['name'])}</h3>
        <p class="t-body">We will come out, measure up and quote in writing. No charge.</p>
        {phone_btn(d, block=True)}
        {btn('Send a message', 'contact.html', 'ghost', d, block=True)}
      </div>
      <dl class="facts">
        <div><dt>Office</dt><dd style="font-size:15px;line-height:150%">{'<br>'.join(e(x) for x in S['addressLines'])}</dd></div>
        <div><dt>Hours</dt><dd style="font-size:15px;line-height:150%">{'<br>'.join(e(h['d']) + ' &middot; ' + e(h['t']) for h in S['hours'])}</dd></div>
      </dl>
    </div>
  </div>
</section>

<section class="section" data-reveal="40">
  <div class="sechead" style="margin-bottom:40px">
    {label('Services here')}
    <h2 class="t-h2">What We Do in {e(l['name'])}</h2>
  </div>
  <div class="grid-3">{svc}</div>
</section>
'''
    write(f'locations/{l["slug"]}.html',
          shell(f'Contractor in {l["name"]} | {S["legalName"]}', l['blurb'][:155], body, d, 'locations.html'))


# ------------------------------------------------------------------- blog ----
def build_blog():
    cards = ''.join(f'<div data-stagger>{blog_card(b)}</div>' for b in C['blog'])
    body = f'''
{phero('Your Construction Knowledge Hub',
       'Practical advice on building, renovating and maintaining property in Malaysia.',
       'page-blog', [('Home', 'index.html'), ('Blog', None)])}

<section class="section" data-reveal="40">
  <div class="grid-3">{cards}</div>
</section>
'''
    write('blog.html', shell('Blog | ' + S['legalName'],
                             'Construction and renovation advice for Malaysian property owners.',
                             body, 0, 'blog.html'))


ARTICLE_BODY = """<p>{excerpt}</p>
<h2>Why this comes up so often</h2>
<p>Malaysia gets somewhere around 2,400&nbsp;mm of rain a year and rarely drops below 23&nbsp;&deg;C. That combination is hard on buildings in a way that temperate-climate detailing simply does not account for, and most of the problems we are called out to trace back to a decision someone made to save a few thousand ringgit at the start.</p>
<h2>What to look at first</h2>
<ul>
<li><strong>Water paths.</strong> Follow where rain actually goes — roof, gutter, downpipe, apron drain, perimeter drain. Any break in that chain shows up inside the building within two monsoons.</li>
<li><strong>Structure before finishes.</strong> Beams, columns and slabs decide what you can do. Tiles and paint do not.</li>
<li><strong>What the original builder did.</strong> On a house older than fifteen years, assume nothing. Open it up and look.</li>
</ul>
<h2>Rough costs in 2026</h2>
<p>As a guide for the Klang Valley: a bathroom strip-out and rebuild runs <strong>RM&nbsp;18,000 to RM&nbsp;35,000</strong>; a wet and dry kitchen reconfiguration <strong>RM&nbsp;45,000 to RM&nbsp;90,000</strong>; re-roofing a standard double-storey terrace <strong>RM&nbsp;28,000 to RM&nbsp;55,000</strong> depending on material and access. Treat these as starting points — your quote should be specific to your building.</p>
<h2>When to call someone</h2>
<p>If you can see daylight through a roof, if a crack is wider than a two-ringgit coin, or if a stain keeps coming back after you have painted over it twice, stop patching and get it looked at. Those three are all symptoms of something structural or something that is still letting water in.</p>
<p>We give free written quotes anywhere in the Klang Valley — call <strong>{phone}</strong> or send us the details.</p>"""


def build_blog_detail(b):
    d = 1
    others = [x for x in C['blog'] if x['slug'] != b['slug']][:3]
    rel = ''.join(f'<div data-stagger>{blog_card(o, d)}</div>' for o in others)
    article = ARTICLE_BODY.format(excerpt=e(b['excerpt']), phone=e(S['phoneDisplay']))
    body = f'''
{phero(b['title'], b['excerpt'], b['img'],
       [('Home', 'index.html'), ('Blog', 'blog.html'), (b['cat'], None)], d)}

<section class="section" data-reveal="40">
  <div class="grid-2" style="gap:48px;align-items:start">
    <article class="prose">
      <div class="blog-card__meta" style="margin-bottom:8px">
        <span class="tag">{e(b['cat'])}</span><span>{e(b['author'])}</span><span>·</span><span>{e(b['date'])}</span>
      </div>
      {article}
    </article>
    <aside style="display:flex;flex-direction:column;gap:24px;position:sticky;top:120px">
      <div class="card" style="padding:28px;gap:16px">
        <h3 class="t-h3sm">Need this done?</h3>
        <p class="t-body">Free site visit and a written, itemised quote.</p>
        {phone_btn(d, block=True)}
      </div>
      <div style="border-radius:var(--r-md);overflow:hidden;aspect-ratio:4/3">{img('why-worker', 'cover', d)}</div>
    </aside>
  </div>
</section>

<section class="section" data-reveal="40">
  <div class="sechead" style="margin-bottom:40px">
    {label('Keep reading')}
    <h2 class="t-h2">More Articles</h2>
  </div>
  <div class="grid-3">{rel}</div>
</section>
'''
    write(f'blog/{b["slug"]}.html',
          shell(f'{b["title"]} | {S["legalName"]}', b['excerpt'][:155], body, d, 'blog.html'))


# ---------------------------------------------------------------- contact ----
def build_contact():
    c = C['contact']
    hours = ''.join(f'<li style="display:flex;justify-content:space-between;gap:24px;padding:12px 0;border-bottom:1px solid var(--line-soft)">'
                    f'<span class="t-body">{e(h["d"])}</span><span style="color:var(--white)">{e(h["t"])}</span></li>'
                    for h in S['hours'])
    body = f'''
{phero(c['heroTitle'], c['intro'], 'page-contact', [('Home', 'index.html'), ('Contact', None)])}

<section class="section" data-reveal="40">
  <div class="grid-2" style="gap:48px;align-items:start">
    <div style="display:flex;flex-direction:column;gap:32px">
      <div class="sechead">
        {label('Get in touch')}
        <h2 class="t-h2">Three Ways to Reach Us</h2>
      </div>
      <div style="display:flex;flex-direction:column;gap:16px">
        <a class="card" style="flex-direction:row;align-items:center;gap:16px;padding:22px" href="tel:{S['phoneHref']}">
          <span style="color:var(--accent);width:22px">{icon('phone')}</span>
          <span><span class="t-micro" style="color:var(--w-40)">Phone</span><br>
          <strong style="font-family:var(--font-display);font-size:18px">{e(S['phoneDisplay'])}</strong></span></a>
        <a class="card" style="flex-direction:row;align-items:center;gap:16px;padding:22px" href="mailto:{S['email']}">
          <span style="color:var(--accent);width:22px">{icon('mail')}</span>
          <span><span class="t-micro" style="color:var(--w-40)">Email</span><br>
          <strong style="font-family:var(--font-display);font-size:18px">{e(S['email'])}</strong></span></a>
        <div class="card" style="flex-direction:row;align-items:flex-start;gap:16px;padding:22px">
          <span style="color:var(--accent);width:22px;margin-top:2px">{icon('pin')}</span>
          <span><span class="t-micro" style="color:var(--w-40)">Office</span><br>
          <span class="t-body" style="color:var(--white)">{'<br>'.join(e(x) for x in S['addressLines'])}</span></span></div>
      </div>
      <div>
        <h3 class="t-h3sm" style="margin-bottom:8px">Opening hours</h3>
        <ul>{hours}</ul>
      </div>
    </div>
    <div style="display:flex;flex-direction:column;gap:24px">
      <div class="areas__inner" style="padding:28px;background:var(--surface-1);border-radius:var(--r-md)">
        {map_block()}
      </div>
    </div>
  </div>
</section>

<section class="faq" data-reveal="40">
  <div class="faq__split">
    <div class="faq__left">
      <h2 class="t-h2">{e(C['home']['faqTitle'])}</h2>
      <p class="t-body">{e(C['home']['faqIntro'])}</p>
    </div>
    <div data-accordion>{faq_block()}</div>
  </div>
</section>
'''
    write('contact.html', shell('Contact | ' + S['legalName'], c['intro'][:155], body, 0, 'contact.html'))


# ------------------------------------------------------------------ legal ----
LEGAL = {
    'privacy': ('Privacy Policy', [
        ('About this page', 'This is a demonstration website. It is not operated by a real business, it does not collect, store or transmit any personal data, and the forms on it do nothing beyond showing a confirmation message in your browser.'),
        ('If this were a real site', 'A live version of this policy would set out what data is collected through the enquiry form, how long it is kept, who it is shared with, and how to request its deletion — as required under Malaysia’s Personal Data Protection Act 2010.'),
        ('Cookies', 'This site sets no cookies and runs no analytics.'),
    ]),
    'terms': ('Terms & Conditions', [
        ('About this page', 'This is a demonstration website built as a design exercise. The company, people, projects, reviews, prices and contact details shown on it are invented. Nothing here is an offer, a quotation or a contract.'),
        ('Content', 'All text and figures are placeholder content and should not be relied on. Photography is licensed stock imagery used for layout purposes only; the people and buildings shown have no connection to the fictional company.'),
        ('If this were a real site', 'A live version would cover quotation validity, payment schedules, variation orders, warranty terms and dispute resolution under Malaysian law.'),
    ]),
}


def build_legal(key):
    title, blocks = LEGAL[key]
    prose = ''.join(f'<h2>{e(h)}</h2><p>{e(p)}</p>' for h, p in blocks)
    body = f'''
{phero(title, 'Placeholder legal text for a demonstration site.', 'page-contact',
       [('Home', 'index.html'), (title, None)])}
<section class="section" data-reveal="40">
  <div class="prose">{prose}</div>
</section>
'''
    write(f'{key}.html', shell(f'{title} | {S["legalName"]}',
                               'Placeholder legal text for a demonstration site.', body, 0, '', with_cta=False))


# ------------------------------------------------------------------- main ----
def build_favicon():
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
           '<rect width="64" height="64" rx="14" fill="#0C0E0C"/>'
           '<path d="M14 48V16h8.6l9.4 19.3L41.4 16H50v32h-6.6V27.4L35.3 44h-6.6L20.6 27.4V48z" fill="#ff8a24"/>'
           '</svg>')
    write('assets/favicon.svg', svg)


def main():
    build_favicon()
    build_home()
    build_about()
    build_services()
    for s in C['services']:
        build_service_detail(s)
    build_projects()
    for p in C['projects']:
        build_project_detail(p)
    build_locations()
    for l in C['locations']:
        build_location_detail(l)
    build_blog()
    for b in C['blog']:
        build_blog_detail(b)
    build_contact()
    for k in LEGAL:
        build_legal(k)

    pages = [w for w in written if w[0].endswith('.html')]
    total = sum(n for _, n in pages)
    print(f'{len(pages)} pages, {total/1024:.0f} KB total')
    for p, n in pages:
        print(f'  {n/1024:6.1f} KB  {p}')


if __name__ == '__main__':
    main()
