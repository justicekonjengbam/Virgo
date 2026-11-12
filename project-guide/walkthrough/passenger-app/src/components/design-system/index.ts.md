# index.ts (design-system)

## 1. Purpose
A **barrel file** (one file that re-exports many files, so other code imports from one place). Instead of `import { DsButton } from '../design-system/atoms/DsButton'`, a screen writes `import { DsButton } from '../design-system'`. Files like `AuthPrompt.tsx` and `RememberMe.tsx` use it.

## 2. Imports, one by one
There are no imports. Each line is `export { X } from 'path'` which reads the file and passes the name on (*example:* `export { a } from './a'` lets others do `import { a } from './index'`).

## 3. Walk through the code
- `index.ts:1` `DsButton` from `./atoms/DsButton`.
- `:2` `export { DsIcon, type IconName } from './atoms/DsIcon';` also exports the type `IconName`. The `type` word marks it as types-only (erased at build).
- `:3` `DsText` from atoms.
- `:4-5` `DsCard`, `DsChip` from molecules.
- `:6` `DsTextField` from `./molecules/DsTextField` (exists in that folder).
- `:7-8` `DsEmptyState`, `DsLoading` from organisms (files exist in `organisms/`).

Layers: atoms (smallest) -> molecules (a few atoms) -> organisms (bigger blocks).

Errors: if a listed file is missing or the name is wrong, the build fails (Metro bundler error "Unable to resolve module").

## 4. How data flows
```
AuthPrompt --import { DsButton }--> index.ts --re-export--> atoms/DsButton.tsx
```

## 5. Try it
From `passenger-app/`: `rg -n "design-system'" src` lists the files that use this barrel. Expect many matches.

## 6. Can it be better?
- Good: short imports, one public list of parts.
- Weak: a barrel can create **circular imports** (A imports B and B imports A) if a design-system file imports from the barrel. Here atoms import `./DsText` directly, which is correct. Also it loads all parts even if one is needed (small cost in an app).
- Cleaner: keep as is; just never import from `'../design-system'` inside the design-system folder.
- Security: none.

## 7. Check yourself
1. What is the benefit of importing from the barrel?
2. Why does `DsButton.tsx` import `./DsText` and not the barrel?
