# AppText.tsx

## 1. Purpose
A thin wrapper over the design-system text `DsText`. It keeps the older variant names (`title`, `body`, `caption`) and maps them to the design-system names. It sits in `components/foundation/` and calls `DsText` (`design-system/atoms/DsText.tsx`).

## 2. Imports, one by one
- `import type { ReactNode } from 'react';` (`AppText.tsx:1`). **React** builds screens from components. `ReactNode` is the type for anything drawable. Used for `children`. Type-only.
- `import type { StyleProp, TextStyle } from 'react-native';` (`:2`). Types from React Native. `TextStyle` is the shape of a text style object (`{ fontSize: 16 }`). `StyleProp<T>` allows one style, an array, or nothing. Used for the `style` prop.
- `import { DsText } from '../design-system';` (`:4`). Imported through the **barrel file** `design-system/index.ts` (one file that re-exports parts). `DsText` draws styled text.

## 3. Walk through the code
- `type AppTextVariant = 'title' | 'body' | 'caption';` (`:6`). A **union type**: the value must be one of these three strings.
- `AppTextProps` (`:8-12`): `children` (required, the content), `variant` (optional), `style` (optional extra style).
- `export function AppText({ children, variant = 'body', style })` (`:14`). Default variant is `body`.
- `const designSystemVariant = variant === 'title' ? 'h1' : variant;` (`:15`). A **ternary** (`cond ? a : b`). If the variant is `title`, use `h1`. Otherwise keep it. So `body` and `caption` pass unchanged; I assume `DsText` accepts them as `TypographyVariant` (it does, since `DsTextField` uses `caption`, and `body` is the default at `DsText.tsx:16`).
- Line 16 returns `<DsText style={style} variant={designSystemVariant}>{children}</DsText>`.
- *Example:* `<AppText variant="title">Hi</AppText>` draws "Hi" in the `h1` style.

## 4. How data flows
```
Screen --children, variant='title'--> AppText --variant='h1'--> DsText --> Text
```

## 5. Try it
Not directly runnable. `<AppText variant="caption">Small</AppText>` in a screen shows small text.

## 6. Can it be better?
- Good: small; gives a safe name map.
- Weak: it does not pass `color` or `numberOfLines`, so callers lose those. Another layer to learn.
- Cleaner way (opinion): use `DsText` directly; or use a lookup object `{ title: 'h1', body: 'body', caption: 'caption' }` to avoid the ternary.
- Security: none.

## 7. Check yourself
1. What does `variant="title"` become?
2. Why is `children` typed as `ReactNode`?
