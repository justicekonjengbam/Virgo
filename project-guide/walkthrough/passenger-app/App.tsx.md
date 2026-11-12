# passenger-app/App.tsx

## 1. Purpose
`App.tsx` is the root component of the Passenger app. **Component** (a function that returns what to draw on screen. *Example:* `function Hi(){ return <Text>Hi</Text> }`). React Native starts here (through `index.js`, which I did not read; check with `fd index.js passenger-app -d 1`). It only shows the navigator, which holds all screens.

## 2. Imports, one by one
- `import { PassengerNavigator } from './src/navigation/PassengerNavigator';` (`passenger-app/App.tsx:1`)
  - A project import from `passenger-app/src/navigation/PassengerNavigator.tsx` (path from the line; file not read here). `{ }` imports a named export.
  - It is the component that sets up screens and moving between them (React Navigation native stack, per `passenger-app/README.md:10`).
  - Other files can export many things; `import { a, b } from` takes several.

## 3. Walk through the code, top to bottom
- The comment on line 3 (`/** ... */`) says navigation and the booking draft live outside single screens. A "booking draft" is the half-filled ride request (pickup, drop). The comment says the navigator owns it; I did not verify that in this file.
- `export default function App() { return <PassengerNavigator />; }` (line 4).
  - `export default` makes this the main thing the file gives out.
  - `<PassengerNavigator />` is **JSX** (HTML-like text inside JavaScript that creates a component. *Example:* `<Text>Hi</Text>`). A self-closing tag with no children.
  - Input: none (no props). Output: the navigator element.
  - Errors: none here. A crash inside the navigator crashes the app, because no error boundary (a React wrapper that catches crashes) is used.

## 4. How data flows
```
Android starts -> index.js registers App -> App() -> <PassengerNavigator /> -> screens
```

## 5. Try it
```zsh
cd passenger-app && pnpm start
```
Starts Metro. Then run the app on an emulator (see `passenger-app/README.md:40-54`). Expect the first screen of the navigator.

## 6. Can it be better?
- Good: very small root.
- Weak: no providers here (Redux store, safe-area, gesture handler). Either the navigator wraps them, or the app uses another state tool; I am not sure. No error boundary. The whole component is on one line, which Prettier would reformat.
- Cleaner way:
```tsx
export default function App() {
  return <PassengerNavigator />;
}
```
- Security: none.

## 7. Check yourself
1. What does `App` return?
2. Where would you add a global wrapper such as a theme provider?
