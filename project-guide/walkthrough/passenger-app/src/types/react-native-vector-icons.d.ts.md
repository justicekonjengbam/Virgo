# passenger-app/src/types/react-native-vector-icons.d.ts

## 1. Purpose
This file adds types for the icon component `react-native-vector-icons/MaterialCommunityIcons`. That library draws icons from a font. This file says which props (settings) the icon component accepts. It has no runtime code.

## 2. Imports, one by one
Both imports are inside the `declare module` block (`passenger-app/src/types/react-native-vector-icons.d.ts:2-3`).
- `import type { ComponentType } from 'react';` **React** is the UI library. `ComponentType<P>` is the type of any component that takes props `P`. *Example:* a function `(props) => <View/>` is a `ComponentType`. `import type` means it is erased at build time.
- `import type { StyleProp, TextStyle } from 'react-native';` **React Native** draws native phone UI. `TextStyle` is the type of text style objects (`{ color: 'red' }`). `StyleProp<T>` also allows arrays, `null` and `false`. Needed to type the `style` prop.

## 3. Walk through the code
`passenger-app/src/types/react-native-vector-icons.d.ts:1-13`
- Line 1: `declare module 'react-native-vector-icons/MaterialCommunityIcons'` (tells TypeScript the shape of this import path. *Example:* it can now be imported without an "implicit any" error.)
- Lines 5-10: `const MaterialCommunityIcons: ComponentType<{ color?, name, size?, style? }>`
  - `name: string` (required) the icon id, e.g. `"chevron-left"`.
  - `color?: string` icon color, e.g. `"#2563EB"`.
  - `size?: number` size in points.
  - `style?: StyleProp<TextStyle>` extra styles (icons are drawn as text characters).
- Line 12: `export default MaterialCommunityIcons;`

Tiny use: `<MaterialCommunityIcons name="help-circle" size={27} color="#2563EB" />`.

## 4. How data flows
```
JSX <MaterialCommunityIcons name="car"/>
   |-- TypeScript checks props against this file
   v
Real library (font glyph) draws the icon at run time
```

## 5. Try it
Not directly runnable. In `passenger-app/`, run `npx tsc --noEmit`. Then change `name` to a number in some component and see the type error.

## 6. Can it be better?
- Good: small and covers the props the app uses.
- Weak: `name` is a plain `string`, so a wrong icon name is not caught. The real library props (like `onPress`) are missing. The newer `@types/react-native-vector-icons` package may already provide full types (I am not sure; check `npm ls`).
- Cleaner way: install the official types package and delete this file.
- Security: none.

## 7. Check yourself
1. What does `import type` change compared to `import`?
2. Which prop is required, and which are optional?
