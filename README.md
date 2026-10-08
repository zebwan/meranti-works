# Meranti Works — static site

A 1:1 rebuild of the Framer template at **https://bldr.framer.website/** as a static
HTML/CSS/JS site, rebranded to an invented Malaysian construction company.

The layout, components, effects, animations and responsive behaviour are reproductions
of the source template, measured from its own compiled CSS and JS rather than estimated
by eye. **Only the name and the content differ — the colour palette is the template’s own.**

---

## ⚠️ Everything on this site is placeholder content

**Do not publish this as a real business's website.** There is no such company as
Meranti Works Sdn Bhd. Specifically, all of the following is invented:

| | |
|---|---|
| Company name, registration, CIDB grade | invented |
| Phone `03-7725 4800`, mobile, email `hello@merantiworks.com.my` | invented, not in service |
| Office address in Dataran Prima, Petaling Jaya | invented |
| All four projects, their values, dates and durations | invented |
| All six customer reviews and the people named in them | invented |
| All prices in ringgit, the "480+ projects", "4.9 rating", "1.2K+" | invented |
| All eight blog articles and their authors | invented |
| Everything in the FAQ, including the cost guidance | invented |
| The four team members and their biographies | invented |

The photographs are licensed stock imagery from [Pexels](https://www.pexels.com)
(free to use, no attribution required). **The people in them are models and the
buildings are real buildings elsewhere — none of them have any connection to the
fictional company, and none of the "projects" were built by anyone depicted.** The
before/after pairs are matched on building type and camera angle; they are *not* two
photographs of the same building.

Pages carry `<meta name="robots" content="noindex, nofollow">` and the forms are inert —
nothing is transmitted or stored anywhere.

Before this becomes a real site, replace every value in `data/content.json`, every
photograph in `assets/img/`, and delete this warning.

---

## The brand

**Meranti Works** — meranti is the hardwood Malaysian builders have framed, trussed and
shuttered with for generations, so the name reads like a firm that has been around rather
than something assembled from a thesaurus. Wordmark `MERANTI.` with the full stop in the
accent, the way the source template sets `BLDR.`

The palette is the **source template's own**, unchanged:

```
--accent     #ff8a24      --bg         #0d0d0d
--accent-2   #de8f07      --surface-1  #141414
--accent-3   #c25800      --surface-2  #1a1a1a
                          --surface-3  #262626
                          --surface-4  #292929
                          --surface-5  #2e2e2e
```

Label text on the accent is white, as the template has it. Worth knowing: white on
`#ff8a24` is about a 2.2:1 contrast ratio, which is below the WCAG AA threshold of 4.5:1
for body text. It is the template's own choice and it is reproduced here faithfully; if
this ever becomes a real site, that is the one colour decision to revisit.

Type is unchanged from the source: **Inter Display** for headings, **Inter** for body,
**Fragment Mono** for accents — 122 self-hosted woff2 files, no external requests.

---

## Running it

The site is plain static files with no build step. Any static server works:

```bash
python3 tools/serve.py 9712
```

That mirrors the project to `/tmp/meranti-site` and serves it from there, because macOS
blocks local servers from reading anything under `~/Desktop`. It re-copies each file
when the project copy is newer, so edits show up on reload, and it sends no-cache
headers so ES modules do not go stale.

To deploy, upload the project root as-is minus `tools/`, `_research/` and
`contact-sheet/`. There is nothing to compile.

---

## Layout

```
index.html  about.html  services.html  projects.html
locations.html  blog.html  contact.html  privacy.html  terms.html
services/   6 pages      projects/   4 pages
locations/  5 pages      blog/       8 pages            = 32 pages

css/     fonts · tokens · base · components · sections
js/      spring · smooth-scroll · reveal · nav · slider · compare
         marquee · process · scrub-text · ui · main
assets/  fonts (122 woff2) · img (63) · favicon.svg
data/    content.json   all copy, in one file
         images.json    slot -> Pexels id, width and aspect
tools/   generate.py    writes all 32 pages
         fetch-images.py  downloads and crops every photo
         serve.py       dev server
         check-links.py crawls every page for broken links/assets
         icons.py  mapsvg.py
_research/   the extracted source template: 30 SSR pages, 63 JS modules,
             per-page CSS, the data-framer-name trees, BUILD-SPEC.md
```

Edit `data/content.json`, then:

```bash
python3 tools/generate.py
```

To change a photograph, edit its slot in `data/images.json` and run:

```bash
python3 tools/fetch-images.py --force
```

---

## What was reproduced from the source

Measured from the template's own compiled CSS and JS bundle, not estimated:

**Breakpoints** `≥1440` / `1200–1439.98` / `810–1199.98` / `≤809.98`. The two
thresholds deliberately do not align — the type scale steps down below 1440, the page
gutter below 1200.

**Type scale** h1 56/45/36 · h2 48/40/32 · h3 32/26/20 · h4 20/16/16 · lead 28/22/18 ·
body 16/16/13, with the source's letter-spacing and 100%/110%/150% line heights.

**Geometry** gutter 88/48/20 · nav 122px (103px below 1200) · top bar 30px with
`backdrop-filter: blur(10px)` · fixed scroll nav 80px, desktop only · hero exactly
100vh with a 12px inset panel at radius 12 · project cards 483px, sticky at top 120px ·
radii 3/4/8/12/16/96.

**Vertical rhythm** The gap between sections is a flex `gap` on `<main>` — **128px at
≥1200, 80px below** — not padding on the sections, which carry only their 8/12px shell.
`<main>` is `overflow: clip`, which is what contains the marquee bleed.

**Buttons** The glow is the source's eight stacked `box-shadow` layers, each with
negative spread, recoloured to the lime with the geometry kept byte-for-byte. Primary
carries it and *drops* it on hover; Ghost has none until hover, then becomes a Primary;
Primary Flat has none at all.

**Rolling text** One line of characters over a `text-shadow` duplicate sitting exactly
one line-height (19.2px) below, clipped to one line. Each character is its own span and
rises `0 → -19.2px` on `spring{duration:.4, bounce:0}`, with a per-character delay of
`(duration / length) × index × 0.35` — 35ms per character on a four-letter nav link,
9.3ms on a fifteen-character button. Buttons count the stagger from the end of the word,
nav links from the start.

**Motion** The bundle's two signature springs, resampled into CSS `linear()` easings:
`spring{duration:.4, bounce:.2}` for interactions (60 uses in the source) and
`spring{duration:1.5, bounce:0}` for scroll reveals (26 uses). Reveal start states
(`translateY` of 40 / 150 / 50px) are taken from the source's server-rendered inline
styles. Nav drops in from `y:-150` on `spring{stiffness:168, damping:30, mass:1}`.

**Scroll-linked** Smooth scroll (the source ships Lenis). The About paragraph's
per-character colour scrub, `rgba(255,255,255,.2) → #fff`. The Process section pinned
for 2,560px across four steps with the image cross-fading per step. Projects as stacked
sticky cards.

**Components** Before/after comparison slider ported prop for prop — divider 4px,
handle 40px, labels inset 16px, arrows ±2% and shift ±10%. Review marquee at 40px/s
with rows in opposite directions and hover slowing to 32%, becoming a 100px/s column
ticker below 810px. Transform-based services slider, 3/2/1 up. Single-open FAQ
accordion. Rolling-text hover on every link and button.

## What differs, and why

1. **The source's loading screen settles at opacity 0.1 and never leaves.** That looks
   like a template bug, so this build fades it out properly.
3. **Section heights differ** where the Malaysian copy runs longer or shorter than the
   original's. Every padding, gap and grid value matches; total page height is within
   about 1.5% of the source.
4. **A reveal failsafe was added.** The reveal start state lives in CSS, and
   IntersectionObserver does not run in a background tab, so there is a
   `visibilitychange` catch-up and a 4-second unconditional reveal. Without it a page
   opened in a background tab and never focused would stay blank.
