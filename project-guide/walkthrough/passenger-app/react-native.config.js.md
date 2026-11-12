# passenger-app/react-native.config.js

## 1. Purpose
This file gives extra settings to the React Native command line tool. Here it says where the custom font files are. When you run `npx react-native-asset`, or the link step, the fonts are copied into the Android and iOS projects.

## 2. Imports, one by one
No imports. `module.exports` hands the config object to the CLI. (*Example:* `module.exports = { a: 1 }` lets a tool `require` this file and read `a`.)

## 3. Walk through the code, top to bottom
- `module.exports = { assets: ['./src/assets/fonts'] };` (`react-native.config.js:1`)
  - `assets` is a list of folders with static files (fonts, sounds) that native apps must include.
  - `./src/assets/fonts` is relative to the app folder. It must exist and hold `.ttf`/`.otf` files.
  - The CLI does not read this at runtime in the phone. It is only used at build or link time.

## 4. How data flows
```
react-native CLI (link/asset command) -> reads this file
  -> copies src/assets/fonts/* into android/ and ios/ resources
  -> app can use the font names in styles
```

## 5. Try it
```sh
cd passenger-app && npx react-native-asset
```
`npx` runs a package without installing it permanently. `react-native-asset` is a separate tool and is not in `package.json`, so npx will download it. Expected: lines saying fonts were linked. I did not run it; check the folder with `fd . src/assets/fonts`.

## 6. Can it be better?
- Good: one line, clear.
- Weak: there is no check that the folder exists. `react-native-vector-icons` fonts need separate handling.
- Security: none.

## 7. Check yourself
1. What does the `assets` key list?
2. Is this file used while the app runs on the phone?
