# driver-app/src/components/DriverText.tsx

## 1. Purpose
`DriverText` is the one text component for the driver app. It sets font, size, color and line height in one place. `DriverButton`, `DriverTextField`, `DriverPageHeader` and `DriverAuthHeader` all call it. It calls React Native's `Text` and reads `../theme`.

## 2. Imports, one by one
- `import type { PropsWithChildren } from 'react';` (`DriverText.tsx:1`) React is the UI library. `PropsWithChildren<P>` adds a `children` prop to type `P`. *Example:* `<DriverText>Hello</DriverText>`, where "Hello" is `children`. Type-only import.
- `import { Text, type StyleProp, type TextStyle } from 'react-native';` (`:2`) `Text` is the native component that shows words on screen. The two types describe style values. React Native requires all words to be inside `Text`.
- `import { colors, typography } from '../theme';` (`:4`) from `driver-app/src/theme/index.ts`, which re-exports `tokens.ts`. `colors` holds the palette; `typography.family` holds font names (`regular`, `medium`, `semibold`, `bold`).

## 3. Walk through the code
`DriverText.tsx:6`
```ts
type DriverTextProps = PropsWithChildren<{ color?: string; style?: StyleProp<TextStyle>; size?: number; weight?: '400' | '500' | '600' | '700' }>;
```
A **type** (a description of the shape of data; no run-time cost). All props are optional. `weight` can only be one of four strings.

`DriverText.tsx:9-12`
```tsx
export function DriverText({ children, color = colors.textPrimary, size = 14, style, weight = '400' }: DriverTextProps)
```
- **Function component** (a React component is just a function that gets props and returns UI). **Destructuring** pulls props out by name; `= value` sets defaults.
- Line 10: a chain of `? :` (ternary: `a ? b : c`) picks the font family from the weight: 700 bold, 600 semibold, 500 medium, else regular. The names are Poppins font files.
- Line 11: returns `<Text style={[ {...}, style ]}>`. A style **array** merges objects; later items win. So a caller's `style` overrides the defaults. `lineHeight` is `Math.round(size * 1.45)`: for size 16 this gives 23 (`Math.round` rounds to the nearest whole number).

Example: `<DriverText size={16} weight="700" color="#fff">Pay</DriverText>` draws bold white 16-point "Pay" with line height 23.

## 4. How data flows
```
DriverButton --label, color, size, weight--> DriverText
DriverText picks font from typography.family
   --> <Text style=[...]> --> native text on screen
```

## 5. Try it
Not directly runnable alone. Put `<DriverText>Hello</DriverText>` in any screen and run the app (`npx react-native run-android` in `driver-app/`; this starts the Android build and installs it on an emulator).

## 6. Can it be better?
- Good: central text style; typed props; style override works.
- Weak: weight `'400'` and `'500'` use a long ternary chain; the weight type is a string though CSS weights are numbers. Line height fixed at 1.45.
- Cleaner way: a lookup table.
```ts
const family = { '400': f.regular, '500': f.medium, '600': f.semibold, '700': f.bold }[weight];
```
- Security: none.

## 7. Check yourself
1. If you pass `style={{ color: 'red' }}` and `color="blue"`, which wins and why?
2. What line height does size 20 produce?
