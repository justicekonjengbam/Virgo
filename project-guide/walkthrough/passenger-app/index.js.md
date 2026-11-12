# index.js

## 1. Purpose
The JavaScript entry point of the passenger app. The native side (`MainActivity.kt`) loads the JS bundle, and this file runs first. It registers the root component `App` (from `passenger-app/App`) under the name in `app.json`.

## 2. Imports, one by one
- `import 'react-native-gesture-handler';` (`index.js:1`): a side-effect import (no names taken; just running the file). The library handles touch gestures (swipe, drag) used by navigation. It must be imported **first**, before other code, as its docs say. It can also give `Swipeable` and `Pressable` components.
- `import { AppRegistry } from 'react-native';` (line 2): `react-native` is the main framework. `AppRegistry` is the object where an app announces its root component. *Example:* `AppRegistry.registerComponent('X', () => Comp)`.
- `import App from './App';` (line 3): the project's root React component, from `passenger-app/App.(tsx|js)`. `./` means same folder.
- `import { name as appName } from './app.json';` (line 4): reads the `name` field from `app.json` and renames it `appName`. Result: `"PassengerApp"`.

## 3. Walk through the code
- `AppRegistry.registerComponent(appName, () => App);` (line 6): tells RN: "when native asks to run `PassengerApp`, call this function to get the component". The arrow function `() => App` returns the component (lazy, so it is created only when needed). No return value.
- Errors: if names differ from `MainActivity.getMainComponentName`, you see "Application PassengerApp has not been registered".

## 4. How data flows
```
Native MainActivity -> asks "run PassengerApp" -> AppRegistry (index.js:6) -> () => App -> <App/> renders
```

## 5. Try it
`cd passenger-app && npx react-native start` in one terminal, then `npx react-native run-android` in another. Expected: the app UI shows on the emulator.

## 6. Can it be better?
- Good: standard and short; gesture handler is first.
- Weak: relies on a JSON import for the name; if `App` is TypeScript the import still works. No error boundary here (opinion: add one inside `App`).
- Security: none.

## 7. Check yourself
1. Why must `react-native-gesture-handler` be imported first?
2. Which three names must match for the app to start?
