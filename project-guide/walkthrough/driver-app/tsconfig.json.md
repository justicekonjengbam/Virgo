# driver-app/tsconfig.json

## 1. Purpose
**TypeScript** (JavaScript with types. *Example:* `let n: number = 5`) reads `tsconfig.json` to know how to check the code. This file is read by `tsc` (the `typecheck` script, `driver-app/package.json:14`) and by editors.

## 2. Imports, one by one
No imports. Line 2 uses `extends`, which is similar (see below).

## 3. Walk through the code, top to bottom
- `"extends": "@react-native/typescript-config"` (`driver-app/tsconfig.json:2`). Start from the settings of this package, which React Native provides (strict checks, JSX support, module rules). `extends` means "copy those settings, then apply mine". The package is in devDependencies (`driver-app/package.json:53`).
- `"include": ["App.tsx", "src/**/*.ts", "src/**/*.tsx"]` (line 3). Only these files are checked. `**` means "any depth of folders", `*` means "any name". So all `.ts` and `.tsx` files in `src`, plus `App.tsx`. Files outside, like `metro.config.js`, are not checked.

## 4. How data flows
```
pnpm typecheck -> tsc --noEmit -> reads tsconfig.json -> base config + include list -> errors or silence
```

## 5. Try it
```zsh
pnpm --filter driver-app typecheck
```
`tsc --noEmit` checks types and writes no files. Expect no output on success.

## 6. Can it be better?
- Good: tiny and based on the official config.
- Weak: no `exclude` list (not needed because `include` is narrow). Tests outside `src` (such as a `__tests__` folder) would not be checked (I am not sure whether such a folder exists).
- Cleaner way: add `"__tests__/**/*"` to `include` if tests exist.
- Security: none.

## 7. Check yourself
1. What does `extends` do?
2. Which files does `tsc` check here?
