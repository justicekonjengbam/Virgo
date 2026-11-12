# AppButton.tsx

## 1. Purpose
A thin wrapper over the design-system button `DsButton`. It keeps the older prop name `title` and maps it to the new prop `label`. It sits in `components/foundation/`. It calls `DsButton` from `components/design-system`.

## 2. Imports, one by one
- `import { DsButton } from '../design-system';` (`AppButton.tsx:1`). `../design-system` is the **barrel file** `design-system/index.ts` (it re-exports all design-system parts; see `index.ts:1`). `DsButton` is the project button. Needed to draw the button. *Example:* `<DsButton label="Go" onPress={f} />`.

## 3. Walk through the code
- `type AppButtonProps = { title: string; onPress: () => void; disabled?: boolean };` (`:3-7`). `onPress` is a **callback** (a function called when the user taps). `disabled` is optional.
- `export function AppButton({ title, onPress, disabled = false })` (`:9`). `disabled = false` is a default value.
- Line 10 returns `<DsButton disabled={disabled} label={title} onPress={onPress} />`. It renames `title` to `label` and forwards the other two.
- *Example:* `<AppButton title="Book" onPress={() => book()} />` draws a button "Book" that calls `book()` on tap.

## 4. How data flows
```
Screen --title,onPress,disabled--> AppButton --label,onPress,disabled--> DsButton
user tap --> DsButton --> onPress() --> Screen function
```

## 5. Try it
Not directly runnable. Put `<AppButton title="Test" onPress={() => console.log('hi')} />` in a screen; tapping logs "hi".

## 6. Can it be better?
- Good: very small; a clear mapping.
- Weak: it hides `DsButton` options (`size`, variant...). Two button components confuse new people.
- Cleaner way (opinion): use `DsButton` everywhere and remove `AppButton` when old screens are migrated.
- Security: none.

## 7. Check yourself
1. Which prop is renamed, and to what?
2. What is the default of `disabled`?
