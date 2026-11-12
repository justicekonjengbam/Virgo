# driver-app/metro.config.js

## 1. Purpose
**Metro** (the JavaScript bundler of React Native. It reads your code and its libraries and packs them into one file the phone can load. *Example:* `App.tsx` plus 800 library files become one `index.bundle`) needs settings for this repo. This file gives Metro those settings for the Driver app. The React Native command `react-native start` (see `driver-app/package.json:6`) loads it. It calls only the `@react-native/metro-config` package, Node's `fs` and `path`.

## 2. Imports, one by one
- `const { getDefaultConfig, mergeConfig } = require('@react-native/metro-config');` (`driver-app/metro.config.js:1`)
  - `require` is the Node way to load a module (*Example:* `require('fs')` gives you file tools).
  - `@react-native/metro-config` is the React Native team's package with the default Metro settings. `getDefaultConfig(dir)` returns the default settings object. `mergeConfig(a, b)` joins two settings objects, with `b` winning.
  - Needed so we only change what is special, not all settings.
- `const fs = require('fs');` (line 2). Node's built-in file system module. *Example:* `fs.existsSync('a.txt')` returns `true` or `false`.
- `const path = require('path');` (line 3). Node's built-in module for file paths. *Example:* `path.join('a','b')` gives `a/b`.

## 3. Walk through the code, top to bottom
- Lines 5-6 are comments. They say pnpm (a package manager that stores libraries once in a shared folder and links to them with symlinks, which are shortcuts to folders) needs the real folder path. The comment mentions a Windows `SUBST` drive (a fake drive letter for a folder). The author seems to work on Windows too.
- `const realProjectRoot = fs.realpathSync.native(__dirname);` (line 7). `__dirname` is the folder of this file (`driver-app`). `fs.realpathSync.native` follows all symlinks and gives the true path. Result example: `/home/rem/projects/CabSure.../driver-app`.
- `const workspaceRoot = path.dirname(realProjectRoot);` (line 8). `path.dirname` removes the last part. So it is the repo root.
- `const workspaceNodeModules = path.join(workspaceRoot, 'node_modules');` (line 9). The shared `node_modules` at the repo root, where pnpm keeps real library files.
- `const babelRuntimeRoot = path.join(realProjectRoot, 'node_modules', '@babel', 'runtime');` (line 10). The path of the `@babel/runtime` helper library inside driver-app.
- `generatedCacheOutputs` (lines 15-19). A list of three **regular expressions** (patterns that match text. *Example:* `/ab/` matches "cab"). They match paths ending in `android/.cxx`, `.pytest_cache` or `.gradle`. These are build or test folders that appear and vanish. The comment (lines 12-14) says watching them caused `ENOENT` (file not found) errors on Windows. `[\\/]` means "a slash or a backslash". `(?:[\\/]|$)` means "followed by a slash or the end".
- `function resolveBabelRuntime(moduleName)` (lines 21-30).
  - Input: the name a file imports, like `@babel/runtime/helpers/extends`. Output: a real file path, or `null`.
  - Line 22: if the name is not `@babel/runtime` and does not start with `@babel/runtime/`, return `null` (not our job).
  - Line 26: remove the `@babel/runtime` prefix and a leading `/`. `@babel/runtime/helpers/extends` becomes `helpers/extends`.
  - Line 27: join it onto `babelRuntimeRoot`.
  - Line 28: three guesses: the path itself, the path plus `.js`, or the path plus `/index.js`.
  - Line 29: `candidates.find(...)` returns the first guess where `fs.existsSync` is true. `?? null` means "if nothing was found, use `null`".
  - Why: it forces Metro to always take Babel's helper code from driver-app's own copy, even from pnpm-linked libraries.
- `const config = getDefaultConfig(__dirname);` (line 32). Default Metro settings for this folder.
- `module.exports = mergeConfig(config, {...})` (line 34). `module.exports` is what Metro reads. The extra settings are:
  - `watchFolders: [workspaceNodeModules]` (line 37). Metro watches changes only here (plus the project). It does not scan the passenger app or the backend.
  - `resolver.blockList: generatedCacheOutputs` (line 39). Metro ignores paths matching those patterns.
  - `unstable_enableSymlinks: true` (line 40). Lets Metro follow symlinks. The word "unstable" means the option may change in future Metro versions.
  - `nodeModulesPaths` (lines 41-45). Folders where Metro looks for libraries, in order. The third one repeats `__dirname` and is nearly the same as the first.
  - `resolveRequest` (lines 46-50). A custom function Metro calls for every import. If `resolveBabelRuntime` finds a file, return `{ type: 'sourceFile', filePath }`. Otherwise call `context.resolveRequest(...)`, which is Metro's normal lookup.

## 4. How data flows
```
file does: import x from '@babel/runtime/helpers/foo'
   |
Metro --> resolveRequest(context, name, platform)
              |-- resolveBabelRuntime(name) -> real path?  yes -> use it
              '-- no -> context.resolveRequest (normal lookup)
```

## 5. Try it
```zsh
cd driver-app && pnpm start
```
`pnpm start` runs `react-native start` and starts Metro on port 8081. Expect a Metro banner. If a library cannot be found, the error comes from this resolver. I am not sure it starts cleanly on Linux, because the `android` script in package.json is Windows only.

## 6. Can it be better?
- Good: comments explain the "why". The watch list is small, so start is faster.
- Weak: the third `nodeModulesPaths` entry duplicates the first. The `.pytest_cache` pattern is a backend folder and is probably useless here. `unstable_enableSymlinks` may be unneeded on newer Metro (opinion; check the Metro docs).
- Cleaner way: remove the duplicate entry.
- Security: nothing risky. It only reads paths.

## 7. Check yourself
1. Why does the file call `fs.realpathSync.native`?
2. What does the custom `resolveRequest` do for the import `react`?
