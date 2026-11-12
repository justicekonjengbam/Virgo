# driver-app/App.tsx

## 1. Purpose
The root component of the driver app. **Component** (a function that returns what to draw on screen. *Example:* `function Hello(){ return <Text>Hi</Text> }`). It only wraps the navigator in a gesture container. The app entry (`index.js`, not in this batch) registers it under the name `DriverApp` (see `MainActivity.kt:14`). It calls `DriverNavigator` from `src/navigation/DriverNavigator`.

## 2. Imports, one by one
Third party:
- `import 'react-native-gesture-handler';` (`driver-app/App.tsx:1`). A side-effect import: it runs the library's setup code and gives no name. **react-native-gesture-handler** (a library for swipes, taps, drags handled natively). React Navigation needs it for swipe-back and drawers. It must be the first import, which is why a blank line follows. *Example:* swipe from screen edge to go back.
- `import { GestureHandlerRootView } from 'react-native-gesture-handler';` (line 3). A view component that enables gesture handling for everything inside it.

Project:
- `import { DriverNavigator } from './src/navigation/DriverNavigator';` (line 5). The screen-switching setup (Splash, Login, Sign Up, Help), from `driver-app/src/navigation/DriverNavigator`.

## 3. Walk through the code
`export default function App()` (line 7). Takes no inputs; returns **JSX** (HTML-like syntax inside JavaScript. *Example:* `<View />`). `export default` lets another file import it as the main thing from this file.
- Line 9: `<GestureHandlerRootView style={{ flex: 1 }}>`. `style={{ flex: 1 }}`: the outer braces mean "JavaScript here", the inner braces are an object. `flex: 1` means "fill all available space". Without it the view would have zero height and the screen would be blank.
- Line 10: `<DriverNavigator />` draws the navigator. Everything else in the app lives below it.

## 4. How data flows
```
Android starts MainActivity --> React Native loads JS --> runs App()
App --> GestureHandlerRootView --> DriverNavigator --> current screen
```

## 5. Try it
Not directly runnable alone. Run `pnpm start` and `pnpm android` in `driver-app` (see `docs/driver-app-foundation.md`). Expected: the Splash screen.

## 6. Can it be better?
- Good: tiny and correct; gesture import is first.
- Weak: no error boundary (a component that shows a message instead of crashing), no safe-area provider here (it may be in the navigator; I did not check). Inline style object is recreated each render (harmless here).
- Cleaner way: `const styles = StyleSheet.create({ root: { flex: 1 } })` then `style={styles.root}`.
- Security: none.

## 7. Check yourself
1. Why is the gesture-handler import first?
2. What would happen if `flex: 1` were removed?
