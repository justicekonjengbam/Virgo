# driver-app/src/theme/index.ts

## 1. Purpose
A one-line "barrel" file. It lets other files write `from '../theme'` instead of `from '../theme/tokens'`. Screens import colors, spacing and so on from here.

## 2. Imports, one by one
No imports. It uses a re-export.

## 3. Walk through the code
`export * from './tokens';` (`index.ts:1`). **Re-export** (take everything exported by another file and export it again from here. *Example:* if `tokens.ts` exports `colors`, then `import { colors } from '../theme'` works). `./tokens` is `driver-app/src/theme/tokens.ts`. Note `export *` skips a default export; tokens has none.

## 4. How data flows
```
Screen --import { colors }--> theme/index.ts --re-export--> theme/tokens.ts
```

## 5. Try it
Not directly runnable. `rg "from '.*theme'" driver-app/src -g '*.tsx'` lists the files using it.

## 6. Can it be better?
- Good: short, one import path.
- Weak: barrels can hide where a name really lives; fine for a file this small.
- Security: none.

## 7. Check yourself
1. What does `export *` do?
2. Which file really defines `colors`?
