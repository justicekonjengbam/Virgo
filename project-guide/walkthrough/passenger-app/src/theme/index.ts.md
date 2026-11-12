# passenger-app/src/theme/index.ts

## 1. Purpose
A one-line "barrel" file. It lets other files write `from '../../../theme'` instead of `from '../../../theme/tokens'`. Screens such as `SplashScreen.tsx` and `MyRidesScreen.tsx` import from it.

## 2. Imports, one by one
There are no `import` lines. Line 1 is a re-export.

## 3. Walk through the code
`export * from './tokens';` (line 1). **Re-export** (take every exported name from another file and export it again from here). *Example:* `tokens.ts` exports `colors`, `spacing`, `radius`, `typography`, `elevation`, `shadows` and `TypographyVariant`. All of them become available from `theme`.
Input: none. Output: all exports of `./tokens` (see `theme/tokens.ts`).

## 4. How data flows
```
SplashScreen -> import {colors} from 'theme' -> index.ts -> tokens.ts
```

## 5. Try it
Not directly runnable. In any screen: `import { colors } from '../../../theme';` then use `colors.primary`.

## 6. Can it be better?
- Good: short import paths, one place to add more theme files later.
- Weak: `export *` hides where a name comes from. Barrels can slow bundlers a little in big apps. Not a problem at this size.
- Security: none.

## 7. Check yourself
1. What does `export *` do?
2. If you add `theme/dark.ts`, what must you change in this file to share it?
