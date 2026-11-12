# driver-app/babel.config.js

## 1. Purpose
This configures **Babel** (a tool that rewrites modern JavaScript, JSX and TypeScript into code the phone's JavaScript engine understands. *Example:* `<Text>Hi</Text>` becomes `React.createElement(Text, null, "Hi")`). Metro, the React Native bundler, runs Babel on every source file. Jest runs it too before tests.

## 2. Imports, one by one
No `import` or `require`. It uses CommonJS `module.exports` (line 1), which means "this file's value is this object". Babel loads the file and reads the object.

## 3. Walk through the code, top to bottom
- `module.exports = { ... }` (line 1) exports the config object.
- `presets: ['module:@react-native/babel-preset']` (line 2). A **preset** (a ready-made group of Babel rules. *Example:* one preset handles JSX, TypeScript, async functions and more). The `module:` prefix tells Babel to load the package by its exact name instead of guessing `babel-preset-...`. `@react-native/babel-preset` is the official React Native preset.

Errors: if the package is not installed, Babel stops with "Cannot find module". Run `npm install`.

## 4. How data flows
```
App.tsx (JSX + TS) -> Metro -> Babel (this preset) -> plain JS -> phone
tests (*.test.tsx) -> Jest  -> Babel (this preset) -> plain JS -> run
```

## 5. Try it
```zsh
cd driver-app
npx babel --version
```
If it prints a version, Babel is present. I am not sure `@babel/cli` is a dev dependency here; if not, use `npx react-native start` and watch Metro compile instead.

## 6. Can it be better?
- Good: it is the minimum needed and matches the template.
- Weak: no plugin for path aliases or the Reanimated plugin. If the app uses Reanimated, that would be required (check `package.json`).
- Cleaner way: none for a simple app.
- Security: nothing risky.

## 7. Check yourself
1. What does Babel turn JSX into?
2. Which two tools in this folder run Babel?
