# babel.config.js

## 1. Purpose
**Babel** is a tool that rewrites modern JavaScript/JSX/TypeScript into code the phone's JS engine understands. *Example:* it turns `<Text>Hi</Text>` into `React.createElement(Text, null, "Hi")`. This file tells Babel what rules to use. Metro (the RN bundler) reads it automatically.

## 2. Imports, one by one
No import lines. `module.exports = {...}` (`babel.config.js:1`) is the CommonJS way to export an object. *Example:* the older `require`-style module system in Node.

## 3. Walk through the code
- `presets: ['module:@react-native/babel-preset']` (line 2): a **preset** is a bundle of Babel rules. The `module:` prefix means "load this npm package by name". `@react-native/babel-preset` handles JSX, TypeScript, Flow, class properties and RN specifics. It lives in `node_modules`.

## 4. How data flows
```
App.tsx (JSX/TS) -> Metro -> Babel (this config) -> plain JS bundle -> phone
```

## 5. Try it
`cd passenger-app && npx react-native start --reset-cache` (starts Metro and clears its cache, needed after editing this file). Expected: Metro prints a banner and waits.

## 6. Can it be better?
- Good: the default, as RN recommends.
- Weak: no plugins. If you add `react-native-reanimated`, its Babel plugin must be added **last** in `plugins` (I did not check if it is used).
- Security: none.

## 7. Check yourself
1. What does a Babel preset do?
2. Why use `--reset-cache` after changing this file?
