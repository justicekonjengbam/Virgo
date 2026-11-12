# driver-app/android/settings.gradle

## 1. Purpose
This file tells Gradle which projects ("modules") are part of the Android build and how to find React Native's build plugin. Gradle reads it before `build.gradle`. It is small and mostly copied from the React Native template.

## 2. Imports, one by one
No import lines. The outside things it refers to:
- `../node_modules/@react-native/gradle-plugin` (lines 1 and 6) is a folder installed by `npm install`. It holds React Native's Gradle plugin as source code.
- `com.facebook.react.settings` (line 2) is a plugin id from that folder.
- `com.facebook.react.ReactSettingsExtension` (line 3) is a class from that plugin.

## 3. Walk through the code, top to bottom
- `pluginManagement { includeBuild("../node_modules/@react-native/gradle-plugin") }` (line 1). **includeBuild** (use another folder's build as if it were a library. *Example:* "use this plugin source directly"). This makes the plugin id below findable.
- `plugins { id("com.facebook.react.settings") }` (line 2) turns the plugin on for settings.
- `extensions.configure(com.facebook.react.ReactSettingsExtension){ ex -> ex.autolinkLibrariesFromCommand() }` (line 3). **Autolinking** (React Native finds native libraries in `node_modules` and adds them to the build by itself. *Example:* installing a map library needs no manual Gradle edit). `autolinkLibrariesFromCommand()` runs a command (the React Native CLI) which prints the library list. If node is missing, it fails here.
- `rootProject.name = 'DriverApp'` (line 4) sets the project name.
- `include ':app'` (line 5) adds the `app` folder as a module. That is where the real app code lives.
- `includeBuild('../node_modules/@react-native/gradle-plugin')` (line 6) includes the plugin build again (template convention).

## 4. How data flows
```
./gradlew -> settings.gradle
   |-- includeBuild: finds RN plugin in node_modules
   |-- autolink: runs RN CLI -> list of native libs
   '-- include ':app' -> build.gradle files run
```

## 5. Try it
```zsh
cd driver-app && npm install
cd android && ./gradlew projects
```
`projects` prints the module tree. Expected: `Root project 'DriverApp'` and `Project ':app'`.

## 6. Can it be better?
- Good: standard template, autolinking means little manual work.
- Weak: it fails with unclear errors if `node_modules` is missing. Run `npm install` first.
- Cleaner way: none needed. Do not edit by hand unless upgrading React Native.
- Security: nothing risky.

## 7. Check yourself
1. What does autolinking do for you?
2. Why must `npm install` run before a Gradle build?
