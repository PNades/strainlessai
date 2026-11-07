# StrainlessAI Design System: Master

> **How to use:** when building a page, check `design-system/strainless/pages/<page>.md` first.
> If it exists, its rules override this file. Otherwise follow this file exactly.
> Spec Section 8.5 points here; spec Section 1.1 (375 / 768 / 1280 px) applies to everything below.

**Direction:** A · Lagoon (chosen 2026-11-07 from three options: Lagoon, Dusk, Rehearsal Room)
**Generated with:** UI UX Pro Max 2.15.0 (`--design-system`, dials Variance 3 · Motion 2 · Density 4), then curated by hand:
- The palette starts from the database's "Healthcare App" row (calm cyan). The cyan was darkened to `#0B5D73` so white text passes AA, and the green CTA was removed so green only ever means Healthy or Accepted.
- Type comes from the "Wellness Calm" pairing (Lora + Raleway), with Raleway swapped for Source Sans 3. Raleway's default old-style figures make "take 12" and "5 / 16" hard to read, and it is thin at body sizes.
- The generator's "Hero + Features + CTA" landing pattern, GSAP scroll reveals and hover lifts are dropped. StrainlessAI is a task flow, not a marketing page.

---

## 1. Personality

Calm, encouraging, trustworthy, **not clinical**. Think of a voice teacher's quiet studio, not a hospital chart.

- **Calm:** one accent hue, soft cool neutrals, generous line height, no motion that isn't feedback.
- **Encouraging:** the copy does most of the work (see the spec). Visually: rejection is shown in a soft fill with a reason and a next step, never a red screen.
- **Trustworthy:** high contrast (every text pair ≥ 6:1), a steady serif for headings, and the same layout on every screen.
- **Not clinical:** no pure white page, no blue-grey hospital palette, no gauges or dials, no percentages shown as precise truth.

---

## 2. Color

### 2.1 Rule: green, amber and red are reserved

**Green, amber and red mean status only:** Healthy · Borderline · Strained on the result, and Accepted · (warning) · Rejected on the collection site. The brand accent is a blue-teal. Never use the accent for a status, and never use a status colour for decoration or a CTA.

Teal is the nearest brand hue to Healthy green, so every status is also carried by **a label and an icon or shape**, never by colour alone. On the result screen the band card uses status colours only, and the accent appears nowhere inside it.

### 2.2 Light tokens (default)

| Token | Hex | Use | Contrast |
|---|---|---|---|
| `--bg` | `#F5F7F6` | page background | |
| `--surface` | `#FFFFFF` | cards, bars, inputs, header | |
| `--text` | `#14232A` | body text | 15.0:1 on bg |
| `--muted` | `#4B5A62` | secondary text, hints | 6.6:1 on bg, 6.0:1 on `--chip` |
| `--line` | `#CFDADD` | dividers, card borders (decorative) | |
| `--line-strong` | `#7A8B92` | **form control borders** (WCAG 1.4.11) | 3.5:1 on surface, 3.3:1 on bg |
| `--chip` | `#E6EDEE` | neutral fill: empty chips, number discs, meter track | |
| `--accent` | `#0B5D73` | primary buttons, links, selected state, progress | white on it 7.4:1 |
| `--accent-hover` | `#094C5E` | primary hover / pressed | white on it 9.5:1 |
| `--accent-soft` | `#E0EFF2` | selected card fill, info message | accent on it 6.3:1 |
| `--on-accent` | `#FFFFFF` | text on accent | |
| `--focus` | `#1D4ED8` | focus ring (3 px, 2 px offset) | 6.7:1 on surface |
| `--overlay` | `rgba(12, 28, 34, 0.45)` | dialog scrim | |

### 2.3 Status tokens (light)

| Meaning | Text / solid | Soft fill | Border | Text on soft |
|---|---|---|---|---|
| Healthy · Accepted · good | `--ok` `#136B2E` | `--ok-soft` `#E4F3E8` | `--ok-line` `#9FD0AB` | 5.8:1 |
| Borderline · warning | `--warn` `#8A5A00` | `--warn-soft` `#FFF4D6` | `--warn-line` `#B7791F` | 5.4:1 |
| Strained · Rejected · error | `--bad` `#A3221A` | `--bad-soft` `#FBE9E7` | `--bad-line` `#EAB0A9` | 6.4:1 |

Warnings use body text (`--text`) on `--warn-soft` with a 5 px `--warn-line` left border. `--warn` is for short labels only.

### 2.4 Dark tokens (v2 React app only)

The collection site is light-only (`color-scheme: light`). The v2 app (Part 8) supports dark mode with these values:

| Token | Hex | Contrast |
|---|---|---|
| `--bg` | `#0F1A1E` | |
| `--surface` | `#16242A` | |
| `--text` | `#E6EEF0` | 15.0:1 on bg |
| `--muted` | `#A3B3B9` | 7.4:1 on surface |
| `--line` | `#2B3D44` | |
| `--line-strong` | `#5D737B` | 3.2:1 on surface |
| `--chip` | `#203239` | |
| `--accent` | `#5BC0D6` | 7.5:1 on surface |
| `--accent-hover` | `#7FD0E2` | |
| `--accent-soft` | `#143640` | |
| `--on-accent` | `#06262E` | 7.5:1 on accent |
| `--focus` | `#8AB4F8` | 8.4:1 on bg |
| `--ok` / `--warn` / `--bad` | `#5FCB85` / `#E8B65A` / `#F28B82` | 7.9 / 8.5 / 6.7:1 on surface |

Dark soft fills are the status hue at about 14% over `--surface`. Check each new pair at ≥ 4.5:1 before shipping.

---

## 3. Typography

| Role | Face | Weights shipped | Fallback |
|---|---|---|---|
| Headings, brand, big recorder cue | **Lora** | 600 | `Georgia, "Times New Roman", serif` |
| Body, labels, buttons, chips | **Source Sans 3** | 400, 600 | `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif` |
| Completion code | system monospace | (system) | `ui-monospace, "SF Mono", Consolas, monospace` |

- **Only these three files ship.** Bold text (`strong`, `b`, labels, buttons) is **600**, never 700, so the browser never fakes a bold.
- Self-hosted woff2, **Latin subset** (Google's latin `unicode-range`), `font-display: swap`. Glyphs outside it (▶ ✓ ✕, IPA ɑ) fall back to the system font. Files live next to each app's CSS (collection site: `ml/collect/static/fonts/`), with each font's OFL licence beside it. No Google Fonts requests: the CSPs are `'self'` only and singers' IPs stay off third-party servers.

### Scale

| Token | Phone (< 768) | ≥ 768 px | Line height | Face |
|---|---|---|---|---|
| body | 17 px | 18 px | 1.5 | Source Sans 3 400 |
| `--fs-small` | 0.95rem | 0.95rem | 1.5 | Source Sans 3 400 |
| `--fs-tiny` | 0.9rem (chips, meter label; never below 14 px) | same | 1.4 | Source Sans 3 600 |
| h1 | 1.6rem | 1.95rem | 1.2 | Lora 600 |
| h2 | 1.3rem | 1.3rem | 1.3 | Lora 600 |
| h3 / group heading | 1.12rem | 1.12rem | 1.3 | Lora 600 |
| recorder cue ("Sing now") | 1.7rem | 1.7rem | 1.3 | Lora 600 |

Running text max 62ch. Headings use `text-wrap: balance`. Digits in progress counters use `tabular-nums`.

---

## 4. Spacing, radius, elevation

**4 px base.** Use only these steps:

| Token | Value | Typical use |
|---|---|---|
| `--s1` | 4px | hairline gaps, chip padding |
| `--s2` | 8px | list gaps, between related lines |
| `--s3` | 12px | button-row gaps, bar padding, inside messages |
| `--s4` | 16px | **side gutter**, card padding, field spacing |
| `--s5` | 24px | between groups / sections |
| `--s6` | 32px | above a new screen section |
| `--s7` | 48px | large desktop breathing room |

| Token | Value | Use |
|---|---|---|
| `--radius-sm` | 8px | messages, warnings, inputs |
| `--radius` | 12px | buttons, cards, slots |
| `--radius-lg` | 16px | sheets and dialogs |
| `--radius-pill` | 999px | chips |

Elevation is mostly borders, not shadows. Two shadows only:
- `--shadow-bar: 0 -1px 0 var(--line), 0 -4px 12px rgba(20, 35, 42, 0.06)` for the sticky bottom bar.
- `--shadow-sheet: 0 12px 32px rgba(20, 35, 42, 0.18)` for dialogs from 768 px.

---

## 5. Layout and responsiveness (spec 1.1)

- **Mobile first.** Breakpoints: **600 px** (bar buttons go side by side) and **768 px** (bigger type, 2-column voice grid, centred dialogs). Check at **375 / 768 / 1280**.
- One centred content column, `--col: 728px`, with a 16 px gutter. No horizontal scroll at any width.
- **Primary action lives in a sticky bottom bar** with `env(safe-area-inset-bottom)` padding. It is full width on phones and 320 px centred from 600 px.
- Tap targets ≥ 48 px tall (56 px for the main action), ≥ 8 px apart. Nothing is hover-only.
- Overlays are full-screen sheets on phones and centred dialogs (max 600 px; 480 px for small confirms) from 768 px.

---

## 6. Components

All values come from the tokens. Names match the collection site's classes. The React app maps them to shadcn/ui variants with the same tokens.

| Component | Spec |
|---|---|
| **Primary button** | `--accent` fill, `--on-accent` text, 600, `--radius`, min-height 48 (56 for `.big`). Hover/pressed `--accent-hover`. Disabled: opacity 0.45, `not-allowed`. |
| **Secondary button** | `--surface` fill, `--accent` text, 2 px `--accent` border. Hover: `--accent-soft` fill. |
| **Danger button** | `--surface` fill, `--bad` text and border. Hover: `--bad-soft` fill. Only for delete or stop actions, never for a result. |
| **Icon button** | transparent, `--text`, 48 × 48, needs `aria-label`. |
| **Input / select** | `--surface`, 2 px `--line-strong` border, `--radius-sm`, min-height 48, **17 px font** (stops iOS zoom). Focus: border `--accent` plus the focus ring. |
| **Checkbox** | 26 px, `accent-color: var(--accent)`, whole label is the 48 px target. |
| **Card / slot** | `--surface`, 2 px `--line` border, `--radius`. Selected: `--accent` border + `--accent-soft` fill. Accepted: `--ok-line` border. Rejected: `--bad-line` border with the reason in `--bad` underneath. |
| **Chip** | pill, `--fs-tiny`, 600. Empty `--chip`/`--muted` · Checking `--accent-soft`/`--accent` · Accepted `--ok-soft`/`--ok` with ✓ · Rejected `--bad-soft`/`--bad`. |
| **Message** | `--radius-sm`, `--s3` padding. Info `--accent-soft`, error `--bad-soft` + `--bad` 600, ok `--ok-soft` + `--ok` 600. Errors say what happened and what to do next. |
| **Warning** | `--warn-soft`, 5 px `--warn-line` left border, `--text` 600. |
| **Recorder** | `--surface` card, cue in Lora 600 1.7rem: "Sing now" `--ok`, "Wait…" `--muted`. Level meter 14 px track in `--chip`, fill `--accent`, `--bad` when clipping. |
| **Sticky bar** | `--surface`, top border `--line`, `--shadow-bar`. |
| **Sheet / dialog** | body `--bg`, head `--surface` with `--line` divider, `--radius-lg` from 768 px, `--shadow-sheet`. |
| **Result band (v2 app)** | One card per result. Healthy `--ok-soft` + `--ok-line` + check icon; Borderline `--warn-soft` + `--warn-line` + half-circle icon; Strained `--bad-soft` + `--bad-line` + alert icon. Label in Lora 600, the coaching text below in body. No accent colour inside. |

Icons in the v2 app: **Lucide** SVG, 20–24 px, `currentColor`, `aria-hidden` when next to text. Don't use emoji as icons. The collection site keeps its current ▶ ✓ ✕ text glyphs until it is next rebuilt.

---

## 7. Motion

Motion is feedback only. There are no scroll reveals or decorative animation.

- Colour, border and background transitions: **150 ms ease-out** on buttons, cards and inputs.
- Meter: `width 60ms linear` (it tracks live input level).
- Dialog enter: 200 ms fade + 8 px rise; exit 150 ms.
- `@media (prefers-reduced-motion: reduce)`: all transitions and animations off.
- Never animate layout (width or height of containers), and never use hover transforms that move things.

---

## 8. Anti-patterns

- ❌ Accent teal used to mean "good", or green/amber/red used as decoration or CTA
- ❌ Status shown by colour alone
- ❌ Clinical look: pure-white page, gauges, dials, precise percentages, hospital blue
- ❌ Fonts from Google's CDN (blocked by CSP; privacy) or any weight beyond the three files
- ❌ Body text under 16 px; form text under 17 px on phones
- ❌ Hover-only help or definitions
- ❌ Primary action scrolled out of view on a phone
- ❌ Input borders below 3:1 contrast
- ❌ Raw hex values in component CSS (use tokens)

---

## 9. Pre-delivery checklist

- [ ] Every colour is a token from this file; contrast pairs re-checked for any new pair
- [ ] Green/amber/red appear only as status, each with a label and icon or shape
- [ ] Lora 600 + Source Sans 3 400/600 only; `font-display: swap`; Latin subset; self-hosted
- [ ] Spacing uses `--s1`…`--s7` only
- [ ] 375 / 768 / 1280 px: nothing cut off, overlapping, or scrolling sideways
- [ ] Main action visible without scrolling on a phone; targets ≥ 48 px
- [ ] Visible focus ring on every interactive element
- [ ] `prefers-reduced-motion` respected
