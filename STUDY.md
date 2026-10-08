# BLDR — Framer template teardown
Source: https://bldr.framer.website/ · siteId `vHC7U4Myll4huhatRDjGg`
Method: all 30 SSR pages fetched, full 63-module JS graph downloaded, CSS regexed out of the
module template strings + the SSR `<style>` blocks, `data-framer-name` tree dumped with inline
start-states, live measurement at 1440 / 834 / 390.

Raw artifacts are in `_research/` (pages/, mods/, css/, modcss/, trees/, presets.json).

---

## 1. Routes — 30

| Group | Routes |
|---|---|
| Top level (7) | `/` `/about` `/services` `/projects` `/locations` `/blog` `/contact` |
| Services CMS (6) | general-contracting · residential-construction · commercial-construction · renovation-remodeling · concrete-foundations · roofing-exteriors |
| Projects CMS (4) | maplewood-residential-new-build · westgate-commercial-fit-out · riverside-municipal-renovation · oakhill-custom-home-addition |
| Locations CMS (5) | dallas-tx · fort-worth-tx · austin-tx · houston-tx · san-antonio-tx |
| Blog CMS (8) | renovate-vs-rebuild… · how-much-does-a-home-addition-cost-in-2026 · 5-warning-signs… · the-ultimate-guide-to-sealing… · commercial-property-maintenance-checklist… · how-to-make-a-new-build-last-50-years · why-proper-drainage-is-critical… · foundation-crack-repair-101… |

4 CMS collections. "More Pages" nav also exposes Privacy Policy and Terms & Conditions.

---

## 2. Homepage section list (document order)

| # | `data-framer-name` | Tag | What it is |
|---|---|---|---|
| — | `Desktop` / `Phone` / `Scroll` | `nav` | 3 nav variants, see §5 |
| — | `Page Transition` | div | route-change wipe |
| — | `Loading Screen` | div | full-screen cover, fades to 0.1 and stays (pointer-events:none) |
| 1 | `Hero Section` | header | 100vh, 12px inset image container r=12, H1 + phone pill + floating "repairs" card + trust row + 4.9 star badge |
| 2 | `Service Section` | section | 6-card transform slider, 3-up, progress line + 2 arrows, "Request a Service" glow button |
| 3 | `About us` | section | `// ABOUT US` label + **285-char scroll-scrubbed paragraph**, then dark card (title/body/button) + B&W crane image |
| 4 | `Why Us` | section | bento: big image card w/ 3 logo chips · 4.9 avg rating + avatar stack + 1.5K+ · "Without a single callback for *fixes*" · "Fully covered" · worker image · "500+ Projects Completed" |
| 5 | `Process` | section | **pinned**: `Sticky` panel 100vh top:10px, 4 steps; active step expands, left image swaps per step; sticky orange phone pill |
| 6 | `Projects` | section | **4 stacked sticky cards** top:120px, each a 2-col grid (before/after comparison slider ⟷ meta/title/body/button) |
| 7 | `Reviews` | section | heading + **2-row marquee**, opposite directions |
| 8 | `Areas we Serve` | section | dotted US map + 5 orange pins w/ labels + "View All Locations" glow button |
| 9 | `Blogs` | div | heading + "All Articles" button + 3 blog cards |
| 10 | `FAQ` | section | `FAQ Split` 2-col, 6-item single-open accordion |
| 11 | `CTA` | div | full-bleed image + overlay, heading + **contact form** (name/email/phone/service select/message/Send) |
| 12 | `Desktop`/`Tablet`/`Phone` | footer | 3 columns (Quick Links / Services / Contact Us) + giant `BLDR.` wordmark + newsletter + socials + legal bar |
| — | `Light` | a | floating "Made in Framer"-style pill, appear-animated |

Other pages reuse: nav, CTA, footer, and section components from this set.

---

## 3. Responsive matrix

Breakpoints (from `data-framer-breakpoint-css` + `__framer__breakpoints`):
`≥1440` · `1200–1439.98` · `810–1199.98` · `≤809.98`

| | **1440** | **834** | **390** |
|---|---|---|---|
| Active breakpoint | ≥1440 | 810–1199 | ≤809 |
| **Nav variant** | `Desktop` (full links + mega menu) | **`Phone`** (hamburger) | `Phone` |
| Nav height (closed) | 122px | 103px | 103px |
| Top Bar | 30px, `rgba(33,33,33,.7)` + `backdrop-filter:blur(10px)`, pad 0 88px | 30px, pad 0 16px | 30px, pad 0 16px |
| Main nav row | 48px, pad 0 88px | 40px, pad 0 16px | 40px, pad 0 16px |
| Nav side margin | 16px (w=1408) | 16px (w=802) | 16px (w=358) |
| Nav open height | 498px (mega menu) | 593px (drawer) | 593px (drawer) |
| **Sticky scroll nav** | yes, `position:fixed`, **80px** | **none** (`hidden-bqxb5a`) | none |
| **Hero height** | 900 = 100vh | 1112 = 100vh | 844 = 100vh |
| Hero section padding | 12px | 12px | 8px |
| Hero container | pad `0 88px 24px`, r=12 | pad `0 48px 48px`, r=12 | pad `16px`, r=12 |
| **Gutter** | **88px** | **48px** | **20px** |
| Content width | 1264 (1440−2×88) | 738 | 350 |
| **H1** | 56 / lh 100% / ls −.025em | 45 | 36 |
| **H2** | 48 / lh 100% / ls −.02em | 40 | 32 |
| H3 | 32 / lh 110% / ls −.01em | 26 | 20 |
| H4 | 20 / lh 100% | 16 | 16 |
| **Body** | 16 / lh 150% | 16 | 13 / lh 150% |
| Lead | 28 / lh 150% | 22 | 18 |
| Hero: floating card | visible | hidden | hidden |
| Hero: 4.9 star badge | visible | hidden | hidden |
| Hero: trust row | 1 row of 3 | 1 row of 3 | wraps to 2 rows |
| **Process** | pinned, `sticky top:10px height:100vh`, gap 64 | `height:min-content` → effectively unpinned | `position:relative; top:unset`, gap 40 — **fully static** |
| **Projects** | 3× `sticky top:120px`, 2-col grid `repeat(2,minmax(320px,1fr))` gap 24 | still sticky top:120, cards 350 tall | `position:relative; top:unset` — **4 cards stacked** |
| Services slider | 3 cards visible | 2 | 1 |
| Reviews marquee | 2 rows, row direction | 2 rows | **column** ticker (velocity 100) |
| Blogs | 3-up row (650 tall) | stacked (1634) | stacked (1681) |
| FAQ Split | 2-col, `sticky` | 2-col, gap 48 | `flex-direction:column`, gap 32 |
| Doc height | 15128 | 13443 | 15546 |
| Horizontal overflow | 0 | 0 | 0 |

### Section inner-container padding (ground truth from CSS)

| Container | ≥1200 | 810–1199 | ≤809 |
|---|---|---|---|
| Hero Container | `0 88px 24px` | `0 48px 48px` | `16px` |
| Services Container | `0 88px` | `0 48px` | `0 20px` |
| About Content | `64px 88px`, gap 56 | `40px 48px` | `40px 20px` |
| Why Us Content | `0 88px` | `0 48px` | `0 20px`, gap 24 |
| Process Inner | `0 88px` | `0 48px` | `0 20px` |
| Projects Inner | `88px` | `88px 48px` | `48px 16px`, r=8 |
| Reviews Container | `0 88px` | `60px 48px` | `0 20px` |
| Areas Inner | `88px`, gap 40 | `88px 48px 64px` | `40px 20px 56px` |
| Blogs Inner | `0 88px` | `0 48px` | `0 20px` |
| FAQ Content | `0`, gap 16, max-w 1440 | gap 48 | gap 32, column |
| CTA Inner | `88px` | `48px` | `68px 4px 20px` |

### Mobile menu (recorded open, identical structure at 834 and 390)
- Push-down panel inside the nav — **not** a full-screen overlay, **not** a side drawer.
- Nav 103 → **593px**; `Phone Drawer` animates `height: 1px → 459px`, `overflow:hidden`.
- Top Bar stays visible. Logo becomes `BLDR.`; hamburger ☰ morphs to ✕.
- 7 rows, `gap:18px`, each 35px, hairline divider between, visual order via flex `order`:
  Home(0) · About Us(1) · **Services(2, chevron ⌄)** · Projects(3) · Locations(4) · Blog(5) · **More Pages(6, chevron ⌄)**
- Full-width orange `Request a Quote` button with glow at the bottom.
- **Closes on scroll.**

---

## 4. Motion inventory

### Signature transitions (counted across all 63 modules)
| Uses | Object | Role |
|---|---|---|
| **60** | `spring { duration: .4, bounce: .2, delay: 0 }` | **interaction signature** — hovers, variant swaps, buttons |
| **26** | `spring { duration: 1.5, bounce: 0, delay: 0 }` | **scroll-reveal signature** |
| 12 | `tween { duration: .6, ease: [.44,0,.56,1] }` | secondary reveals / fades |
| 10 | `spring { duration: .4, bounce: 0 }` | nav + misc |
| 10 | `spring { duration: .2, bounce: 0 }` | accordion/toggle micro |
| 9 | `spring { stiffness:168, damping:30, mass:1 }` | **appear-on-load** (nav drop-in) |
| 8 | `spring { duration: 1, bounce: 0 }` | — |
| 6 | `spring { stiffness:300, damping:60, mass:1, duration:.3, ease:[.44,0,.56,1] }` | — |
| 2 | `spring { stiffness:96, damping:43, mass:2.2, duration:.5, durationBasedSpring, ease:[.44,0,.56,1] }` | — |
| 1 each | `stiffness:339/damping:58`, `stiffness:225/damping:45`, `stiffness:57/damping:30` | — |

### Scroll reveals (start states straight from the SSR inline styles)
| Start state | Applied to |
|---|---|
| `opacity:0; translateY(40px); will-change:transform` | every top-level section wrapper + `<main>` |
| `opacity:0; translateY(150px)` | inner `Content` blocks of Projects, Reviews, Areas we Serve, CTA Content, Footer Inner |
| `opacity:0; translateY(50px)` | CTA `Form Column` |
| `opacity:.001; translateY(10px)` | floating `Light` pill |
| `opacity:.001; y:-150; translateX(-50%)` + `spring{stiffness:168,damping:30,mass:1}` | nav drop-in (`__framer__appearAnimationsContent`, id `1x6l547`) |

### Scroll-scrubbed (not triggered — linked to scroll position)
1. **About paragraph** — 285 per-character `<span>`s inside 34 word spans; `color` interpolates `rgba(255,255,255,.2) → #fff` sequentially L→R over a ~700px scroll window (first char lights when the section top is ~200px above the fold; complete ~400px later).
2. **Process** — `Sticky` panel `position:sticky; top:10px; height:100vh` inside a 3454px section → ~2554px of scrub across 4 steps (~638px each). Active step expands (orange icon + orange left rail), left image cross-fades per step.
3. **Projects** — cards 1–3 `position:sticky; top:120px`, 507px pitch (483 card + 24 gap); card 4 scrolls out. Stacked-card effect.

### Continuous
- **Lenis smooth scroll** on `<html>` (`html.lenis.lenis-scrolling`, bundled in `DFDjbk5uqu-*.mjs`).
- **Tickers** (Framer Ticker, px/s):

| Where | gap | velocity | hover | overflow | direction |
|---|---|---|---|---|---|
| Reviews row A | 16px | **40** | **32** (slows to 32%) | clip | default |
| Reviews row B | 16px | 40 | 32 | clip | **reverse** |
| Reviews (mobile) | 16px | 100 | 100 | clip | **column** |
| Logo/trust strips | 21px | 30 | 100 | visible | row |
| Wide strip | 64px | 30 | 100 | visible | row |

Marquee mask: `linear-gradient(…, transparent 0%, #000 10%, #000 90%, transparent 100%)`. Track `cursor:e-resize`, draggable on some instances. Card 405px wide.

### Hover
- **`RollingTextHover_Prod`** on every nav link, button label and card link (`.rolling-text-inner-*`): two stacked copies of the label, vertical roll, `spring{duration:.4, bounce:0}`.
- Arrow buttons: 40px window containing 74px of content → arrow slides out / new one slides in.
- Mega menu: `Desktop` → `Dropdown Collapse` variant, nav 122 → 498px, panel `scaleY .55 + translateY(308) → identity`, opacity 0 → 1.

### Components
- **Before/After comparison** (`jlv4AwyV7.adEpFHEW.mjs`) — full source recovered. Instance props on the project cards:
  `dragMode:"drag"`, `initialPosition:50`, `orientation:"horizontal"`, `radius:16`,
  `dividerColor:#FFFFFF`, `dividerWidth:4`, `dividerShadow:true` (`0 0 8px rgba(0,0,0,.5)`),
  `showHandle:true`, `handleColor:#ff8a24`, `handleIconColor:#fff`, `handleSize:40` (`0 2px 8px rgba(0,0,0,.35)`, chevrons at 55%, stroke-width 2.2),
  `showLabels:true`, labels `BEFORE`/`AFTER`, `labelBackground:#1a1a1a`, `labelColor:#fff`
  (label chip: pad `6px 12px`, 12px/600, r=6, `letter-spacing:.04em`, uppercase, inset 16px).
  Before image gets `clip-path: inset(0 {100−p}% 0 0)`. Keyboard: arrows ±2, shift ±10. `cursor:ew-resize`, `touch-action:none`, `role="slider"`.
- **FAQ accordion** — 6 items, wrapper variant `All Closed` → single-open. Answer `height 1px→auto`, `opacity .1→1`, `overflow:hidden`. Toggle icon 19px, `rotate: 0 → 180`.
- **Services slider** — transform-based (`overflow:clip`, **no** scroll-snap), track 2471px, 6 cards ~405px, 3/2/1 visible.
- **Button glow** — a PNG sprite inside the button component (332–812px wide), not a CSS shadow. *See deviation note.*

---

## 5. Navigation (3 separate navs)

| Variant | Position | When |
|---|---|---|
| `Desktop` | `absolute; top:0; left:50%; translateX(-50%); z-index:10` — overlays the hero | ≥1200 |
| `Phone` | same container, hamburger + push-down drawer | ≤1199 |
| `Scroll` | **`position:fixed; top:0; z-index:9; height:80px`** | appears after scroll threshold, **≥1200 only** |

- Mega menu (Services): 1408×356, `#0d0d0d`, r=16, inner 1232 `display:flex gap:24px` → `Services Grid` (6 items, 2 cols × 3 rows, icon + title + description) + `Quote CTA` (image card, r=12, "Need a custom construction quote?" + orange phone button).
- More Pages: plain dropdown — Contact · Blog Detail (CMS) · Service Detail (CMS) · Project Detail (CMS) · Location Detail (CMS) · Privacy Policy · Terms & Conditions.

---

## 6. Tokens

### Colour (all 39 `--token-*` values, deduped by role)
| Role | Hex |
|---|---|
| **Accent** | `#ff8a24` (×2 tokens) |
| Accent dark | `#de8f07`, `#c25800` |
| Page bg | `#0d0d0d` (×2) |
| Surface 1 | `#141414`, `#1a1a1a` (×2) |
| Surface 2 | `#262626` (×2), `#292929`, `#2e2e2e` |
| Top bar bg | `#212121b3` |
| White | `#fff` (×3) |
| White alphas | `#ffffffb3` (×2) · `#ffffff80` (×2) · `#ffffff4d` (×2) · `#fff3` (×2) · `#ffffff1f` · `#ffffff1a` · `#ffffff0a` · `#fff9` · `#fff0` |
| Dark alphas | `#1a1a1acc` · `#1a1a1a80` · `#141414cc` · `#14141440` · `#0d0d0d85` · `#0d0d0d30` · `#0006` |
| Greys | `#828282` · `#969696` · `#c8c8c8` |
| Black | `#000` |

### Type
- **Inter Display** — all headings, weights 400/500/600/700 (+ italics). Headings use 600.
  OpenType features on H2: `"blwf" on, "cv03" on, "cv04" on, "cv09" on, "cv11" on`.
- **Inter** — body/UI, 400/500/600/700/900 (+ italics).
- **Fragment Mono** 400 — accent/mono bits.
- 119 woff2 files, all downloaded to `assets/fonts/`.

### Type scale (10 presets, responsive)
| Preset | Tag | ≥1440 | 810–1439 | ≤809 | lh | ls | weight | colour |
|---|---|---|---|---|---|---|---|---|
| `1766wuf` | h1 | 56 | 45 | 36 | 100% | −.025em | 600 | `#000` (overridden to #fff in use) |
| `20opp4` | h2 | 48 | 40 | 32 | 100% | −.02em | 600 | `#fff` |
| `1dvtnw0` | h3 | 32 | 26 | 20 | 110% | −.01em | 600 | `#fff` |
| `1k09btx` | h3 | 24 | 20 (≤1199) | 20 | 100% | 0 | 600 | `#fff` |
| `1090b09` | h4 | 20 | 16 | 16 | 100% | 0 | 600 | `#fff` |
| `1xmsk7z` | p (lead) | 28 | 22 | 18 | 150% | 0 | 400 | `#ffffff80` |
| `im68uy` | p (body) | 16 | 16 | 13 | 150% | 0 | 400 | `#ffffff80` |
| `1c7dfye` | p (eyebrow) | 14 | — | — | 100% | **1.11px** | 500 | `#ffffff4d`, **uppercase** |
| `1j5ezk5` | p (micro) | 12 | — | — | 100% | **1px** | 600 | `#fff`, **uppercase** |
| `38g6gk` | p (micro, Inter) | 12 | — | — | 100% | 0 | 600 | `#fff` |

### Radii
`3px · 4px · 8px · 12px · 16px · 96px` (pills). Dominant: **12px** (cards/containers), **16px** (mega menu, project cards), **8px** (small), **96px** (buttons/pills).

### Gaps (frequency)
`16px` (56) · `10px` (38) · `24px` (21) · `32px` (14) · `48px` (10) · `56px` (9) · `8px`/`4px` (8) · `64px` (4) · `12px` (4) · `20px` (3) · `18px` (3) · `14px` (3) · `40px` (3)

### Effects
- `backdrop-filter: blur(10px)` top bar · `blur(45px)` bordered cards · `blur(94px)` · `blur(100px)` CTA form panel
- Hairline borders `1.5px solid #ffffff0d`
- Form panel: `background:#0006`, `backdrop-filter:blur(100px)`, r=16, gap 24, max-width 688px

---

## 7. Assets
- **112 distinct images** site-wide, **48 on the homepage**. No `<video>`, no Lottie.
- 4 before/after pairs (PNG "Before" ~1536w + JPG "After" 4000–5000w).
- 6 avatar JPGs @160w, 2 testimonial portraits @200w, 3 logo-chip PNGs.
- 6 button-glow PNG sprites (332–812w).
- **221 inline SVG `<path>`s**, 8 `<use>` symbol refs — service icons, process icons, social icons, chevrons, stars, calendar/pin, hamburger.
- 119 woff2 font files.

---

## 8. Deviations I'd flag (building to match first)

1. **Button glow is a baked orange PNG.** A recoloured brand can't reuse it. I'll build the glow as a blurred radial element in the accent colour — pixel-equivalent and themeable.
2. **`Loading Screen` settles at opacity 0.1 and never leaves** (pointer-events:none, so harmless). Looks like a template bug; I'll match it unless told otherwise.
3. **H1 preset colour is `#000`**, overridden to white at every usage site. I'll set the preset to the final colour.
4. A `data-framer-name="Contaienr"` typo on the Reviews wrapper — I'll spell it correctly in the rebuild.
