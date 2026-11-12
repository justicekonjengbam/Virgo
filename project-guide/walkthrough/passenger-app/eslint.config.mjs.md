# eslint.config.mjs

## 1. Purpose
**ESLint** is a linter: it reads code and warns about likely bugs and style problems without running it. *Example:* it flags a variable you declared but never used. This file is the "flat config" (the new ESLint config format). `.mjs` means an ES module file, so `import`/`export` work.

## 2. Imports, one by one
- `import js from '@eslint/js'` (`eslint.config.mjs:1`): ESLint's own rule sets. Used for `js.configs.recommended`, the basic bug rules (e.g. `no-undef`).
- `import react from 'eslint-plugin-react'` (line 2): rules for React. *Example:* warns about a missing `key` in a list.
- `import reactHooks from 'eslint-plugin-react-hooks'` (line 3): rules for **hooks** (functions like `useState`). *Example:* error if you call a hook inside an `if`.
- `import tseslint from 'typescript-eslint'` (line 4): parser and rules for TypeScript. *Example:* flags `any` overuse.

## 3. Walk through the code
- `export default tseslint.config(...)` (line 6): `tseslint.config` is a helper that merges a list of config objects, in order. Later ones win.
- `js.configs.recommended` (line 7): base JS rules.
- `...tseslint.configs.recommended` (line 8): `...` spreads an array into separate items. TypeScript rules.
- Object at lines 9-18:
  - `plugins: { react, 'react-hooks': reactHooks }` (line 10): registers the plugins under names.
  - `rules` (line 11): `...react.configs.flat.recommended.rules` and `...reactHooks.configs.recommended.rules` copy the recommended rules in (lines 12-13).
  - `'react/react-in-jsx-scope': 'off'` (line 14): newer React does not need `import React` for JSX.
  - `'react/prop-types': 'off'` (line 15): TypeScript types replace prop-types.
  - `settings: { react: { version: 'detect' } }` (line 17): ESLint reads the React version from `package.json`.
- Object at lines 19-29: `ignores` lists paths not to lint: native folders, `node_modules`, coverage, and config JS files.

## 4. How data flows
```
npx eslint . -> loads this config -> for each .ts/.tsx/.js file apply rules -> prints warnings
```

## 5. Try it
`cd passenger-app && npx eslint .` (`npx` runs a local tool; `.` = lint the whole folder). Expected: a list of problems, or no output when clean.

## 6. Can it be better?
- Good: ignores native code, hooks rules are on.
- Weak: no `languageOptions.globals`, so RN globals like `__DEV__` or `fetch` may be flagged by `no-undef` in plain JS files (TS rules turn it off for TS files). Opinion: no formatter rule (Prettier) is present. `'*.config.js'` ignores only root-level matching depends on glob rules; I am not sure it matches nested files.
- Security: none.

## 7. Check yourself
1. What does `...` do before `tseslint.configs.recommended`?
2. Why is `react/react-in-jsx-scope` turned off?
