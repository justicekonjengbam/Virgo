# passenger-app/tsconfig.json

## 1. Purpose
This file configures TypeScript (JavaScript with types, checked before running). `tsc` and your editor read it. It is used by `pnpm typecheck` (`package.json:13`).

## 2. Imports, one by one
JSON has no imports. The `extends` key (below) pulls in another config file.

## 3. Walk through the code, top to bottom
- `"extends": "@react-native/typescript-config"` (`tsconfig.json:2`): start from the official React Native settings (strict mode, JSX support, module rules). It is a package in `devDependencies` (`package.json:51`). *Example:* like inheriting a base class.
- `"include": ["App.tsx", "src/**/*.ts", "src/**/*.tsx"]` (`:3`): only these files are checked: the root `App.tsx` and every `.ts`/`.tsx` under `src`. `**` means any depth of folders. Files such as `index.js`, `jest.config.js` and `metro.config.js` are not checked.

## 4. How data flows
```
pnpm typecheck -> tsc reads tsconfig.json -> loads base config
  -> checks included files -> prints errors or nothing
```

## 5. Try it
```sh
cd passenger-app && pnpm typecheck
```
It runs `tsc --noEmit`: `--noEmit` means check only, write no `.js` files. Expected: empty output if all is fine, or lines like `src/x.tsx(10,5): error TS2322`.

## 6. Can it be better?
- Good: minimal, follows the official base.
- Weak: `index.js` is not included, and tests in `src` are checked with the app code (fine). No path aliases.
- Cleaner way (opinion): none needed unless you want aliases like `@/components`.
- Security: none.

## 7. Check yourself
1. What does `extends` do here?
2. Which files does `tsc` skip?
