# passenger-app/src/types/assets.d.ts

## 1. Purpose
This file teaches TypeScript that `import logo from './logo.png'` is allowed. It has one line and no runtime code. TypeScript only reads it while checking types. The React Native bundler (Metro) is what really loads the image.

## 2. Imports, one by one
None. A file with no `import` or `export` at top level is a "global declaration file", so its `declare module` applies to the whole project.

## 3. Walk through the code
`passenger-app/src/types/assets.d.ts:1`
```ts
declare module '*.png' { const asset: number; export default asset; }
```
- **`.d.ts` file** (a "declaration file": it only describes types, it has no code. *Example:* a label on a box that says what is inside.)
- **`declare module '*.png'`** (tells TypeScript: any import path that ends in `.png` is a module. The `*` is a wildcard. *Example:* `import icon from './icon.png'` now type-checks.)
- **`const asset: number`** declares the default export is a number. In React Native, an imported image is a numeric id that `<Image source={asset} />` understands.
- **`export default asset`** says the module's default export is that value.

Without this line, TypeScript shows error TS2307 "Cannot find module './icon.png'".

## 4. How data flows
```
Component: import logo from '../assets/logo.png'
   |  (type check)            |  (build time)
   v                          v
TypeScript reads assets.d.ts  Metro bundler turns the png into a number id
   "png => number"            <Image source={logo}/> shows it
```

## 5. Try it
Not directly runnable. To see its effect, run in `passenger-app/`:
```zsh
npx tsc --noEmit
```
`npx` runs a tool from node_modules. `tsc` is the TypeScript compiler. `--noEmit` means "check only, write no files". Expected: no output when everything is fine. Delete this file temporarily and any png import will fail the check.

## 6. Can it be better?
- Good: tiny and correct for React Native.
- Weak: only `.png`. Other formats (`.jpg`, `.svg`) would need more lines. The driver app may need a similar file (I did not check).
- Cleaner way: `declare module '*.png' { const asset: number; export default asset; }` plus the same for `*.jpg`.
- Security: none.

## 7. Check yourself
1. Why is the default export typed as `number`?
2. Does this file run on the phone? (No. Only TypeScript uses it.)
