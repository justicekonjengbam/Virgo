# driver-app/src/components/brand/DriverBrandLogo.tsx

## 1. Purpose
Draws the CabSure logo as a vector picture (SVG) at any size. Vector means it stays sharp at every size. Other brand components can use it (I did not check which ones).

## 2. Imports, one by one
- `import Svg, { Defs, LinearGradient, Path, Stop } from 'react-native-svg';` (`DriverBrandLogo.tsx:1`) **react-native-svg** is a library that draws SVG shapes in React Native. *Example:* `<Svg><Path d="M0 0L10 10"/></Svg>` draws a line.
  - `Svg` the canvas.
  - `Defs` a place for reusable things such as gradients.
  - `LinearGradient` a color blend along a line.
  - `Stop` one color point in a gradient.
  - `Path` a shape from drawing commands.

## 3. Walk through the code
`:3` `DriverBrandLogo({ size })` takes one number and returns an `Svg`.
`:4`:
- `accessibilityLabel="CabSure logo"` for screen readers.
- `height={size} width={size}` the drawn size on screen.
- `viewBox="0 0 327 348"` the inner coordinate system (x, y, width, height). The picture scales from 327x348 units to `size`. Because the box is square but the viewBox is not, the logo is centered with spare space (default SVG behavior; simplified).
- `Defs` holds `LinearGradient id="driverCabSureGradient"` from point (94,104) to (233.998,244.715), with two `Stop`s. Both are `#2563EB`, so the gradient is really one flat blue.
- `Path d="M164.356 104C..."` `d` is a list of commands: `M` move, `C` curve, `L` line, `H`/`V` horizontal/vertical line, `Z` close. Together they draw a ring shape with a car-like cut-out. `fill="url(#driverCabSureGradient)"` fills it using the gradient id.

Example: `<DriverBrandLogo size={64}/>` draws a 64-point blue logo.

## 4. How data flows
```
Caller --size--> DriverBrandLogo --> Svg(viewBox scaled) --> Path filled blue
```

## 5. Try it
Not directly runnable alone. Render `<DriverBrandLogo size={96}/>` in a screen. Ensure `react-native-svg` is installed: `rg '"react-native-svg"' driver-app/package.json`.

## 6. Can it be better?
- Good: no image file, scales well, has an accessibility label.
- Weak: the gradient has two identical colors, so it is useless. The hex color is hard-coded and not from the theme. The `Path` data is a long magic string. The gradient `id` is global; if two logos are drawn, ids repeat (usually harmless since identical).
- Cleaner way: `fill={colors.primary}` and delete `Defs`.
- Security: none.

## 7. Check yourself
1. What does `viewBox` do?
2. Why could the `Defs` block be removed with no visible change?
