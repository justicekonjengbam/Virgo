# BrandLogo.tsx

## 1. Purpose
Draws the CabSure logo as a vector picture inside the app. It is used by `BrandMark.tsx` (same folder). A **vector image** (a picture made of shapes and curves, not pixels; *example:* it stays sharp at any size).

## 2. Imports, one by one
- `import Svg, { Defs, LinearGradient, Path, Stop } from 'react-native-svg';` (`BrandLogo.tsx:1`). **react-native-svg** is a library that lets React Native draw SVG (Scalable Vector Graphics, an XML picture format). `Svg` is the canvas. `Defs` holds reusable definitions. `LinearGradient` is a color that fades along a line. `Stop` is one color point on that gradient. `Path` draws a shape from a command string. *Example:* `<Path d="M0 0 L10 10" />` draws a line. It can also draw `Circle`, `Rect`, `Text`.

## 3. Walk through the code
`type BrandLogoProps = { size: number };` (`:3`) one required prop, the width and height in points.

`export function BrandLogo({ size })` (`:6`) returns:
- `<Svg ... height={size} width={size} viewBox="0 0 327 348">` (`:8`). `viewBox` is the inner drawing area (x, y, width, height). The real size is scaled to `size`. `accessibilityLabel="CabSure logo"` lets screen readers say what the image is.
- `<Defs>` (`:9`) with `<LinearGradient id="cabSureGradient" x1 y1 x2 y2>` (`:10`). The `id` is a name used later. The four numbers are the start and end points of the fade.
- Three `<Stop>` tags (`:11-13`) all use `#2563EB` (a blue). So the gradient is really one flat color. Stops at 0, 0.5 and 1 would normally mark places in the fade.
- `<Path d="..." fill="url(#cabSureGradient)" />` (`:16-19`). `d` is a long list of drawing commands (`M` move, `C` curve, `L` line, `Z` close). `fill="url(#id)"` paints the shape with the gradient defined above.

Errors: none expected.

## 4. How data flows
```
BrandMark --size=120--> BrandLogo --> Svg scales viewBox 327x348 to 120x120 --> screen
```

## 5. Try it
Not directly runnable. Render `<BrandLogo size={80} />` inside any screen. Expect a blue taxi-style mark.

## 6. Can it be better?
- Good: vector, accessible label, no image file needed.
- Weak: the gradient has three identical stops, so it adds nothing. The comment says the original is in `assets/brand`; if the logo changes, two copies must be updated. `viewBox` is not square (327x348) but width and height are both `size`, so the picture is fitted with default settings (centered, not stretched).
- Cleaner (opinion): replace the gradient with `fill="#2563EB"` or use `colors.primary` from the theme.
- Security: none.

## 7. Check yourself
1. What does `viewBox` do when `size` changes?
2. Why is the `LinearGradient` here the same as a plain color?
