# admin-app/styles.css

## 1. Purpose
**CSS** (rules that say how HTML looks. *Example:* `.error { color: red; }` makes every element with class `error` red). This file styles the whole Admin console: fonts, login card, sidebar, tables, badges, buttons, the driver picker popup and the phone layout. It is 12 lines, but lines 7-11 are very long because many rules sit on one line. `index.html:7` loads it; `app.js` uses its class names inside generated HTML.

## 2. Imports, one by one
No `@import`. It loads font files with `src:url(...)` (see below). Files are `admin-app/assets/Poppins-*.ttf` (Poppins is a font family).

## 3. Walk through the code
- `@font-face` x4 (`:1-4`). Teaches the browser a font: name `Poppins`, weights 400, 500, 600 and 700-900, from local `.ttf` files (`format('truetype')`).
- `:root { --blue:#2563eb; ... }` (`:5`). `:root` is the top of the page. `--name` values are **CSS variables** (named values reused with `var(--blue)`). Defines blue, ink, muted grey, line, surface, bg, green, red, amber. It also sets the default font and text colour.
- `* { box-sizing:border-box }` (`:6`) makes width include padding and border. `body{margin:0;background}` removes default gap. `button,input,textarea { font:inherit }` makes controls use the page font. `.hidden { display:none !important }` hides an element for sure (`!important` beats other rules). `app.js` toggles this class.
- Line 7, login and base form pieces: `.login-shell` centres the card with **flexbox** (a layout mode that lines items up, `align-items`, `justify-content`) and a blue-white gradient. `.login-card` is a **grid** (rows and columns layout) with `gap:16px`. `.eyebrow`, `.muted`, input style, `:focus` outline, `.primary` button, `.primary:disabled` (wait cursor while logging in), `.error`.
- Line 8, shell: `.app-shell` is a grid with a 252px sidebar and a `1fr` (all the rest) content column. `.sidebar`, `.brand`, `.nav-item` (`.active`/`:hover` get blue-soft background), `.logout`, `.content-shell`, `.topbar`, `.admin-identity`.
- Line 9, content: `.metrics` 4-column grid of cards; `.panel`, `.item`; `.badge` pill shape; colour classes `.pending,.open`, `.verified,.resolved`, `.rejected,.closed`, `.in_progress` match status words that `app.js` puts in `badge()` (`app.js:14`); `.actions` and buttons `.approve/.reject/.secondary`; `.table`, `.table-wrap` (scrolls sideways).
- Line 10: `.account-grid`, `.account-form`, `.detail-row`, `.permission-list`.
- Line 11: `.booking-flow` step bar (three numbered circles; `::after` pseudo-elements draw the connecting line), `.assigned-driver`, `.modal-overlay` (full-screen dim background, `position:fixed; inset:0; z-index:100`), `.driver-picker`, `.driver-option`.
- Line 12: `@media (max-width:760px) { ... }` a **media query** (rules that apply only on narrow screens). The sidebar becomes a top row, metrics become 2 columns.

## 4. How data flows
```
app.js writes HTML with class="badge verified" --> browser matches .badge and .verified --> green pill
screen narrower than 760px --> @media block wins --> one-column layout
```

## 5. Try it
Open `/admin` and in DevTools change `--blue` on `:root` to `#dc2626`. The whole console turns red. That shows variables at work.

## 6. Can it be better?
- Good: variables for colours, responsive block, focus outlines, disabled state.
- Weak: lines 7-11 are minified-style single lines, hard to read and to review in git. Light-only (no dark mode). Hard-coded colours like `#b9c9e7`, `#fff7ed` bypass the variables. `.modal-overlay` has no focus trap (that is JS work).
- Cleaner way: one rule per line, or run Prettier (`npx prettier --write admin-app/styles.css`).
- Security: none; CSS holds no secrets.

## 7. Check yourself
1. How does `.hidden` keep an element hidden even if another rule sets `display:grid`?
2. Which line makes the layout single-column on phones?
