# android/settings.gradle

## 1. Purpose
Gradle reads this file first. It says which modules (sub-projects) exist and where plugins come from. For RN it also turns on **autolinking** (the build finds native libraries from `node_modules` by itself).

## 2. Imports, one by one
No imports. `includeBuild` pulls in another Gradle project.

## 3. Walk through the code
- `pluginManagement { includeBuild("../node_modules/@react-native/gradle-plugin") }` (`settings.gradle:1`): tells Gradle to take plugins from the RN gradle plugin folder in `node_modules`. That is why you run `npm install` before building.
- `plugins { id("com.facebook.react.settings") }` (line 2): applies the RN settings plugin.
- `extensions.configure(com.facebook.react.ReactSettingsExtension){ ex -> ex.autolinkLibrariesFromCommand() }` (line 3): `ex` is the plugin's settings object. `autolinkLibrariesFromCommand()` runs the RN CLI command that lists native libraries (like maps, gesture handler) and adds each as a module. It prints a JSON list; Gradle reads it.
- `rootProject.name = 'PassengerApp'` (line 4): project name.
- `include ':app'` (line 5): adds the `app` folder as a module. `:` marks a Gradle path.
- `includeBuild('../node_modules/@react-native/gradle-plugin')` (line 6): includes the plugin build so it compiles with the project.

## 4. How data flows
```
gradlew -> settings.gradle -> RN CLI "config" -> list of native libs -> modules added -> build.gradle
```

## 5. Try it
`cd passenger-app/android && ./gradlew projects` lists modules: expect `:app` plus one per native library.

## 6. Can it be better?
- Good: standard template.
- Weak: autolink runs a Node command, so Node must be on PATH (mise provides it here). If Gradle fails with "node not found", that is why.
- Security: none.

## 7. Check yourself
1. What does autolinking save you from doing?
2. Why must `npm install` run before a Gradle build?
