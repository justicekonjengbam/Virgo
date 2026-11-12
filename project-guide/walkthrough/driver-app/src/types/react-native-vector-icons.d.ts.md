# driver-app/src/types/react-native-vector-icons.d.ts

## 1. Purpose
A one-line declaration so TypeScript accepts imports of the icon library `react-native-vector-icons` (icons drawn from a font. *Example:* `<Icon name="car" />`).

## 2. Imports, one by one
None.

## 3. Walk through the code
`declare module 'react-native-vector-icons/MaterialCommunityIcons';` (`react-native-vector-icons.d.ts:1`). With no body, the module is typed as `any`: every prop is allowed and nothing is checked. Screens then write `import Icon from 'react-native-vector-icons/MaterialCommunityIcons'` without a type error.

## 4. How data flows
```
screen import -> TypeScript reads this file -> "ok, any type"
```

## 5. Try it
Not directly runnable. `pnpm typecheck` in `driver-app` uses it.

## 6. Can it be better?
- Good: shortest way to silence the error.
- Weak: no checking of icon names, so a typo shows a "?" icon at run time. Installing `@types/react-native-vector-icons` would give real types (opinion).
- Security: none.

## 7. Check yourself
1. What type does a body-less `declare module` give?
2. What is one risk of that?
