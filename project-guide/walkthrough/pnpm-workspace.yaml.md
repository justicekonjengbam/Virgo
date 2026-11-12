# pnpm-workspace.yaml

## 1. Purpose
This file turns the repo into a pnpm workspace. (**Workspace**: several JavaScript projects in one repo that share one install and one lockfile. *Example:* `pnpm install` at the root installs both apps.) pnpm is the package manager (a tool that downloads libraries). It lives at the repo root and is read by every `pnpm` command.

## 2. Imports, one by one
YAML has no imports. It has three settings.

## 3. Walk through the code, top to bottom
- `packages:` (`pnpm-workspace.yaml:1-3`): the folders that are workspace projects: `passenger-app` and `driver-app`. Note that `admin-app` (plain JS) is not listed, so pnpm treats it as outside the workspace.
- `onlyBuiltDependencies:` (`:5-6`): a safety list. pnpm 10 does not run install scripts (small programs that some packages run after download) unless the package is allowed. Here `unrs-resolver` is allowed, since it builds a native file.
- `allowBuilds:` (`:7-10`): a newer allow-list of the same kind, as a map. `'@firebase/util': true`, `protobufjs: true`, `unrs-resolver: true` mean their install scripts may run. The quotes around `@firebase/util` are needed because `@` is special in YAML. I am not sure why both keys exist at once; check the pnpm docs for your version with `pnpm --version` and the pnpm "settings" page.

## 4. How data flows
```
pnpm install (root) -> reads packages list -> installs passenger-app + driver-app
  -> for each package, runs install scripts only if on the allow-list
```

## 5. Try it
```sh
pnpm install
pnpm -r list --depth 0
```
`-r` means "recursive": run in every workspace project. `--depth 0` shows only top-level packages. Expected: a block for each app.

## 6. Can it be better?
- Good: allow-listing scripts is a good supply-chain safety habit.
- Weak: two overlapping allow-list keys; `admin-app` missing from `packages`; `package.json:7` Windows-only script shows the repo grew on Windows.
- Cleaner way (opinion): keep only the key your pnpm version supports, and add `admin-app` if it has a `package.json`.
- Security: allowing builds for `protobufjs` and `unrs-resolver` runs their code at install time. Only allow packages you trust.

## 7. Check yourself
1. What is the difference between a project listed under `packages` and one that is not?
2. Why does pnpm ask for an allow-list for build scripts?
