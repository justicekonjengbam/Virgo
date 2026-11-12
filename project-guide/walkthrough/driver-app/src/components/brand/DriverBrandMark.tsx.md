# driver-app/src/components/brand/DriverBrandMark.tsx

## 1. Purpose
This file draws a small square box that holds the CabSure Driver logo. It gives the logo a fixed size and a text label for screen readers. It is used by splash and header files (`DriverSplashScreen.tsx`, `DriverAuthHeader.tsx`, `DriverPageHeader.tsx`). It calls `DriverBrandLogo` from the same folder.

## 2. Imports, one by one
**Third-party**
- `import { StyleSheet, View } from 'react-native';` (`react-native` is the library that turns React code into real phone screens. *Example:* `<View>` becomes an Android `ViewGroup`.) `View` is an empty box used for layout. `StyleSheet.create` builds a style table. File uses both (`DriverBrandMark.tsx:1`). It can also give `Text`, `Image`, `Pressable`.

**Project**
- `import { DriverBrandLogo } from './DriverBrandLogo';` (`./DriverBrandLogo.tsx`, same folder.) This is the component that draws the actual logo picture (`DriverBrandMark.tsx:2`).

## 3. Walk through the code
**`DriverBrandMark({ size = 60 })`** (`DriverBrandMark.tsx:4`)
- A **component** is a function that returns screen pieces (JSX). *Example:* `<DriverBrandMark size={80}/>` shows an 80 by 80 logo box.
- Input: `size`, a number, default 60. Output: one `View`.
- `accessibilityLabel="CabSure Driver"` is the text a screen reader says for this box.
- `style={[styles.box, { height: size, width: size }]}` is an array of styles. Later items win. So the box is `size` wide and tall.
- `<DriverBrandLogo size={size * 2}/>` draws the logo at twice the box size. The box has `overflow: 'hidden'`, so the extra part is cut off. This is a crop trick, probably to remove empty margin in the image. I am not sure; check `DriverBrandLogo.tsx`.

**`styles`** (`DriverBrandMark.tsx:5`): `alignItems` and `justifyContent` centre the logo. `overflow: 'hidden'` cuts anything outside the box.

## 4. How data flows
```
Parent screen --size=80--> DriverBrandMark --size=160--> DriverBrandLogo
                           (80x80 box, crops)
```

## 5. Try it
Not directly runnable. Use it in a screen: `<DriverBrandMark size={80} />`. Run the app with `cd driver-app && npx react-native run-android`. Expect a logo in a square.

## 6. Can it be better?
- Good: very small, has an accessibility label, size is configurable.
- Weak: whole component is on one line (hard to read). The `size * 2` crop is a hidden magic number with no comment. Label text is hard-coded.
- Cleaner way (opinion):
```tsx
const LOGO_ZOOM = 2; // logo image has empty margin, zoom and crop it
```
- Security: nothing risky.

## 7. Check yourself
1. What size is the logo drawn at if you pass `size={50}`? (100, inside a 50 box.)
2. What does `overflow: 'hidden'` do here?
