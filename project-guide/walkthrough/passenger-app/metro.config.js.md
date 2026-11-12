# passenger-app/metro.config.js

## 1. Purpose
Metro is the JavaScript bundler of React Native. (**Bundler**: a tool that reads all your source files and packs them into one file the phone can run. *Example:* many `.tsx` files become one `index.bundle`.) This file tunes Metro for this repo: pnpm links, a monorepo layout, and a Windows drive trick. It is read by `pnpm start` (`package.json:6`).

## 2. Imports, one by one
- `const { getDefaultConfig, mergeConfig } = require('@react-native/metro-config');` (`metro.config.js:1`): the official default Metro settings for React Native. `getDefaultConfig(dir)` returns the default config object. `mergeConfig(a, b)` joins two configs, with `b` winning. *Example:* `mergeConfig({a:1},{b:2})` gives `{a:1,b:2}`.
- `const fs = require('fs');` (`:2`): Node's built-in file system module. Used for `realpathSync` and `existsSync`.
- `const path = require('path');` (`:3`): Node's built-in path helper. `path.join('a','b')` gives `a/b`; `path.dirname('/x/y')` gives `/x`.

No project files are imported.

## 3. Walk through the code, top to bottom
- Comment (`:5-7`): says Metro is started from a short `Z:` drive on Windows to avoid path-length limits, and pnpm uses links (symlinks: files that point to other files) outside that drive.
- `realProjectRoot = fs.realpathSync.native(__dirname)` (`:8`): `__dirname` is this file's folder. `realpathSync.native` follows links and returns the true location, e.g. turns `Z:\passenger-app` into the real path.
- `workspaceRoot = path.dirname(realProjectRoot)` (`:9`): the parent folder. This is the repo root where `pnpm-workspace.yaml` lives.
- `babelRuntimeRoot` (`:10-15`): the path `<project>/node_modules/@babel/runtime`. (`@babel/runtime` holds small helper functions that compiled code calls.)
- `function resolveBabelRuntime(moduleName)` (`:17-30`): input is an import name such as `@babel/runtime/helpers/extends`. Output is a real file path or `null`.
  - `:18-23` if the name is not `@babel/runtime` or under it, return `null` (not our job).
  - `:25` removes the `@babel/runtime` prefix and a leading `/`, leaving `helpers/extends`.
  - `:26` joins it to `babelRuntimeRoot`.
  - `:27` tries three candidates: exact, with `.js`, or `index.js` in a folder.
  - `:29` `candidates.find(...)` returns the first one where `fs.existsSync` is true, else `null` (`?? null`; `??` means "if left side is null/undefined use right side").
- `const config = getDefaultConfig(__dirname);` (`:32`): the default settings.
- `module.exports = mergeConfig(config, {...})` (`:34`): adds our changes.
  - `watchFolders: [workspaceRoot]` (`:36`): Metro watches the whole repo root, because pnpm keeps real packages in a `.pnpm` store there.
  - `blockList` (`:40`): regex patterns Metro must ignore: `.pytest_cache`, `.gradle`, `.cxx`. Reason in comment `:38-39`: Windows may lock those folders. `[\\/]` matches `\` or `/`.
  - `nodeModulesPaths` (`:43-47`): extra folders where Metro looks for packages: real project, workspace root, and the plain `__dirname` one.
  - `resolveRequest` (`:48-56`): a function Metro calls for every import. We first try `resolveBabelRuntime`. If it found a file, we return `{type:'sourceFile', filePath}`. Otherwise `context.resolveRequest(...)` does Metro's normal lookup.

## 4. How data flows
```
Metro sees: import x from '@babel/runtime/helpers/foo'
  -> resolveRequest -> resolveBabelRuntime -> real file path
Metro sees: import y from 'react'
  -> resolveBabelRuntime returns null -> default resolver
```

## 5. Try it
```sh
cd passenger-app && pnpm start
```
It runs `react-native start`, which starts Metro on port 8081. Expected: a Metro banner and "Dev server ready". Stop with Ctrl+C.

## 6. Can it be better?
- Good: the comments explain why each hack exists.
- Weak: it is built around Windows (`Z:` drive, `C:\tmp` in `package.json:7`). On Arch Linux the realpath trick is unneeded but harmless. `resolveBabelRuntime` forces the passenger app's own copy of `@babel/runtime`, which can hide version clashes. `workspaceRoot` assumes the app is one level below the root.
- Cleaner way (opinion): if you only work on Linux, delete the custom `resolveRequest` and test that the app still bundles. pnpm's `node-linker=hoisted` is another option.
- Security: none.

## 7. Check yourself
1. What does `mergeConfig` do and which side wins?
2. When does `resolveRequest` hand control back to Metro's default?
