# LoadingState.tsx

## 1. Purpose
A thin wrapper. `LoadingState` just calls `DsLoading` with a label. It keeps an older app-level name working while the real design lives in the design system. It sits in `components/feedback/`. It calls `DsLoading` (`design-system/organisms/DsLoading.tsx`). I did not find other callers needed to understand it; check with `rg LoadingState passenger-app/src`.

## 2. Imports, one by one
- `import { DsLoading } from '../design-system';` (`LoadingState.tsx:1`). `../design-system` resolves to `design-system/index.ts`, a **barrel file** (one file that re-exports many things so you import from one place. *Example:* `export { DsLoading } from './organisms/DsLoading'`). Used to draw the spinner.

## 3. Walk through the code
- `type LoadingStateProps = { label: string };` (`:3-5`): one required prop, the text.
- `export function LoadingState({ label }: LoadingStateProps)` (`:7`): takes the props object, pulls out `label` (destructuring), and returns `<DsLoading label={label} />` (`:8`). `DsLoading` draws a spinner and the text.
- *Example:* `<LoadingState label="Wait" />` shows a spinner and "Wait".

## 4. How data flows
```
Screen --label--> LoadingState --label--> DsLoading --> spinner
```

## 5. Try it
Not directly runnable. Use `<LoadingState label="Loading rides…" />` inside a screen.

## 6. Can it be better?
- Good: tiny, no logic to break.
- Weak: it adds nothing over `DsLoading`; it hides the `fullScreen` option; two names for one thing confuse readers.
- Cleaner way (opinion): replace uses with `DsLoading` and delete this file, or re-export: `export { DsLoading as LoadingState } from '../design-system';`.
- Security: none.

## 7. Check yourself
1. What does a barrel file do?
2. Why might this wrapper be removed later?
