# driver-app/index.js

## 1. Purpose
This is the **entry point** of the driver app (the first JavaScript file that runs). The native shell (Android or iOS) loads the bundle, and this file tells React Native which component is the app. It calls `./App` (the root component, `driver-app/App.tsx` or similar; not read here) and reads `./app.json`.

## 2. Imports, one by one
- `import { AppRegistry } from 'react-native';` (line 1). `react-native` is the framework. **AppRegistry** (a registry where the app's root component is stored under a name. *Example:* `AppRegistry.registerComponent('X', () => App)` means "when native asks for X, give App"). Needed to start the app. Other things in the package: `View`, `Text`, `StyleSheet`.
- `import App from './App';` (line 2). The project's root component. Default import: the file's main export.
- `import { name as appName } from './app.json';` (line 3). Reads the `name` key of `driver-app/app.json:2`. `as appName` renames it locally. Importing JSON works because Metro supports it.

## 3. Walk through the code, top to bottom
- `AppRegistry.registerComponent(appName, () => App);` (line 5). Two inputs: the name string `"DriverApp"`, and a function that returns the component. The function is lazy: React Native calls it only when it needs to render. Output: nothing returned; it saves the pair. Native code later asks for `"DriverApp"` (for iOS at `ios/DriverApp/AppDelegate.swift:27`) and RN runs the function.

Errors: if `./App` is missing, the bundle fails to build. If the names differ, the screen shows "Application DriverApp has not been registered".

## 4. How data flows
```
Native app starts
  -> loads JS bundle (Metro/main.jsbundle)
  -> index.js runs: registerComponent("DriverApp", () => App)
  -> native asks for "DriverApp"
  -> React renders <App/> on screen
```

## 5. Try it
```zsh
cd driver-app
npx react-native start
```
Starts Metro, the bundler server. Then in another terminal `npx react-native run-android`. Expected: the app opens and shows the App component.

## 6. Can it be better?
- Good: exact template; short.
- Weak: no `react-native-gesture-handler` or background task registration here. If the app needs headless tasks (for example for push messages), they would be registered in this file (not checked).
- Cleaner way: none needed.
- Security: nothing risky.

## 7. Check yourself
1. What does `registerComponent` store?
2. Where does `appName` come from?
