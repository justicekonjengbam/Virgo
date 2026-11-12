# driver-app/eslint.config.mjs

## 1. Purpose
This configures **ESLint** (a tool that reads your code and warns about bugs and bad style without running it. *Example:* it warns about a variable that is never used). Developers run `npx eslint .` or an editor plugin. It does not affect the built app. The `.mjs` ending means ES module syntax (`import`/`export`) is used.

## 2. Imports, one by one
Third-party:
- `import js from '@eslint/js';` (line 1). ESLint's own base rule sets. Used for `js.configs.recommended`, a list of common-sense rules. *Example:* `no-undef` flags a name that was never defined.
- `import react from 'eslint-plugin-react';` (line 2). Rules about React components. Used for the React recommended rules. *Example:* warns about a missing `key` in a list.
- `import reactHooks from 'eslint-plugin-react-hooks';` (line 3). **Hooks** (React functions like `useState` that must follow rules). The plugin checks them. *Example:* it errors if you call `useState` inside an `if`.
- `import tseslint from 'typescript-eslint';` (line 4). Lets ESLint read TypeScript and adds TypeScript rules. *Example:* flags `any` types.

## 3. Walk through the code, top to bottom
- `export default tseslint.config(...)` (line 6). `tseslint.config` is a helper that merges many config pieces into one flat list. Each argument is one piece, applied in order.
- `js.configs.recommended` (line 7). The base JS rules.
- `...tseslint.configs.recommended` (line 8). The `...` (spread) puts each item of an array inline. This is the TypeScript recommended set.
- Block lines 9-18:
  - `plugins: { react, 'react-hooks': reactHooks }` (line 10) registers the plugins under names.
  - `rules` (lines 11-16): `...react.configs.flat.recommended.rules` copies React's recommended rules. `...reactHooks.configs.recommended.rules` copies hooks rules (`rules-of-hooks`, `exhaustive-deps`). `'react/react-in-jsx-scope': 'off'` (line 14) turns off the old rule that wants `import React`; new React does not need it. `'react/prop-types': 'off'` (line 15) turns off runtime prop checks, since TypeScript checks props.
  - `settings: { react: { version: 'detect' } }` (line 17) reads the React version from `package.json`.
- Block lines 19-29: `ignores` list. Folders and files that ESLint skips: native folders `android/**`, `ios/**`, `node_modules/**`, `coverage/**`, and config files `*.config.js`, `jest.config.js`, `react-native.config.js`. Note `*.config.mjs` (this file) is not in the list, so it is linted too.

## 4. How data flows
```
npx eslint .  -> loads this file -> merges rule sets -> checks each .ts/.tsx/.js
                                                      -> prints warnings/errors
```

## 5. Try it
```zsh
cd driver-app
npx eslint . --max-warnings 0
```
`.` means all files not ignored. `--max-warnings 0` makes any warning fail the command. Expected: no output when clean, else lines like `App.tsx 12:7 error 'x' is assigned a value but never used`.

## 6. Can it be better?
- Good: modern flat config, React and hooks rules on, noisy rules turned off for good reason.
- Weak: no React Native specific rules (for example no inline styles). The `react-hooks` recommended spread may differ by plugin version; not checked. No Prettier.
- Cleaner way: add `'@react-native/eslint-config'` if you want the official rules. (Opinion.)
- Security: nothing risky.

## 7. Check yourself
1. Why is `react/react-in-jsx-scope` off?
2. What does `...` do on line 8?
