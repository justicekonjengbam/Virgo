# BrandMark.tsx

## 1. Purpose
Wraps the logo in a square box of a chosen size and cuts off anything outside it. Login and signup screens use it as the top brand picture. It calls `BrandLogo` (`./BrandLogo.tsx`).

## 2. Imports, one by one
- `import { StyleSheet, View } from 'react-native';` (`BrandMark.tsx:1`). `View` is a layout box. `StyleSheet.create` stores styles. *Example:* `<View style={styles.box}>`.
- `// import { colors } from '../../theme';` (`:2`) is commented out. It is dead code (code that is switched off). It is not run.
- `import { BrandLogo } from './BrandLogo';` (`:3`) the SVG logo, from the same folder.

## 3. Walk through the code
`type BrandMarkProps = { size?: number };` (`:5`) optional size.

`export function BrandMark({ size = 60 })` (`:7`). `size = 60` is a **default value** (used when the caller gives none).
- `:9` `<View accessibilityLabel="CabSure" style={[styles.box, { height: size, width: size }]}>`. A style **array** merges styles; later items win. Here a fixed size box is made.
- `:10` `<BrandLogo size={size * 2} />`. The logo is drawn twice as big as the box. Because the box has `overflow: 'hidden'` the outside part is cut, so this works like a zoom-in on the middle. (My reading; check by changing `size * 2` to `size` and compare.)

`styles.box` (`:15-23`): center the child both ways, `overflow: 'hidden'` cuts anything outside. Lines 17-20 are commented out (a background, border and round corners that were removed).

## 4. How data flows
```
Screen --size(optional)--> BrandMark box(size x size) --size*2--> BrandLogo --> clipped on screen
```

## 5. Try it
Not directly runnable. Use `<BrandMark />` (60 points) or `<BrandMark size={100} />`.

## 6. Can it be better?
- Good: default size, small file, accessibility label.
- Weak: commented-out code and an unused commented import should be deleted (git keeps history). The `* 2` is a magic number with no comment. No docblock.
- Cleaner: `const ZOOM = 2;` with a comment saying why.
- Security: none.

## 7. Check yourself
1. What size is the box when no `size` is passed?
2. Why does `overflow: 'hidden'` matter with `size * 2`?
