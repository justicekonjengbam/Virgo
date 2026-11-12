# driver-app/react-native.config.js

## 1. Purpose
This one-line file configures the React Native CLI (the `react-native` command). It tells the CLI where custom font files are. The command `npx react-native-asset` (and old `react-native link`) reads it to copy fonts into the Android and iOS projects. Nothing in the repo calls it directly; the CLI loads it.

## 2. Imports, one by one
No imports.

## 3. Walk through the code, top to bottom
`module.exports = { assets: ['./src/assets/fonts'] };` (`driver-app/react-native.config.js:1`)
- `module.exports` is what Node gives to anyone who loads this file.
- `assets` is a list of folders with files to bundle into the native apps. Here it is one folder, `./src/assets/fonts`, which holds the Poppins font files (the passenger README names Poppins in `passenger-app/README.md:14`; for the driver I am not sure, check the folder with `fd . driver-app/src/assets/fonts`).
- Input: none. Output: a settings object.

## 4. How data flows
```
react-native CLI --reads--> this file --> list of asset folders --> copy fonts to android/ios
```

## 5. Try it
```zsh
fd -e ttf . driver-app/src/assets/fonts
```
`fd -e ttf` finds files with the `.ttf` extension. Expect a list of font files if the folder exists.

## 6. Can it be better?
- Good: very small and clear.
- Weak: the passenger app instead copies fonts through Gradle (`assets.srcDirs`, see `passenger-app/android/app/build.gradle:97`). Two apps use two methods.
- Cleaner way: choose one method for both apps.
- Security: none.

## 7. Check yourself
1. Who reads this file?
2. What does the `assets` key hold?
