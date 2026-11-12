# driver-app/src/theme/tokens.ts

## 1. Purpose
It holds the **design tokens** (named values for the look of the app. *Example:* `colors.primary` instead of typing `#2563EB` everywhere). Every Driver screen reads colors, spacing, radius, fonts and shadows from here, via `theme/index.ts`.

## 2. Imports, one by one
None. It is pure data.

## 3. Walk through the code
- `export const colors = {...} as const;` (`tokens.ts:1-28`). `as const` makes TypeScript treat the values as fixed (read-only; `colors.primary` has type `'#2563EB'`, not just `string`). Main groups:
  - Blue brand: `primary` `#2563EB`, `primaryPressed` (darker, when a button is pressed), `primarySoft` (pale background), `primaryShadow` (blue glow, `rgba` = red/green/blue/alpha, 0.20 means 20% visible).
  - Surfaces: `background`, `surface`, `surfaceMuted`.
  - Text: `textPrimary`, `textSecondary`, `textTertiary` (strong to faint).
  - Borders: `border`, `borderStrong`.
  - Status: `success` (green), `warning` (yellow), `error` (red) plus `...Soft` pale versions.
  - `overlay` (dark see-through layer behind pop-ups), `transparent`, `white`, `black`.
  - Lines 24-27 are **aliases** (second names kept so old code works): `text`, `danger`, `dangerSoft` repeat other values.
- `spacing` (`:30`): gaps in pixels, from `xxs` 2 to `massive` 48. *Example:* `padding: spacing.lg` is 16.
- `radius` (`:31`): corner roundness; `pill: 999` makes fully round ends.
- `typography` (`:32-42`): `family` lists the Poppins font file names (`Poppins-Regular` ...). Then styles like `h1 { fontSize: 24, lineHeight: 32 }` (lineHeight is the height of one text line). Spread them: `<Text style={typography.h1}>`.
- `shadows` (`:43-47`): `card`, `raised`, `floating`. Android uses `elevation`; iOS uses `shadowColor/Offset/Opacity/Radius`. They reuse `colors.black` (`:44`).

## 4. How data flows
```
tokens.ts -> index.ts -> screens: style={{ color: colors.textPrimary, padding: spacing.lg }}
```

## 5. Try it
Not directly runnable. Change `primary` to `#16A34A`, reload the app, and buttons turn green.

## 6. Can it be better?
- Good: central look, `as const`, matches the passenger design language (README says shared CabSure design).
- Weak: no dark mode; duplicate aliases (`text` = `textPrimary`, `danger` = `error`); font names must match font files you installed or text falls back silently. The tokens are probably copied in passenger-app (duplication; I am not sure, check with `fd tokens.ts`).
- Cleaner (opinion): put shared tokens in one pnpm workspace package.
- Security: none.

## 7. Check yourself
1. What does `as const` change?
2. Why are there both `text` and `textPrimary`?
