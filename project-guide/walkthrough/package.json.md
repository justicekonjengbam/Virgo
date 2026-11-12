# package.json (repo root)

## 1. Purpose
This is the root `package.json` of the workspace named `cabapp`. It does not hold app code. It gives shortcut commands that run the same task in the passenger app and the driver app. pnpm reads it.

## 2. Imports, one by one
JSON has no imports. Only one library is listed (Prettier, below).

## 3. Walk through the code, top to bottom
- `"name": "cabapp"` (`package.json:2`). The project name. `"private": true` (line 3) stops publishing.
- `"packageManager": "pnpm@11.9.0"` (line 4). Tells **Corepack** (a Node tool that picks the right package manager version. *Example:* `corepack enable`) to use pnpm 11.9.0.
- `scripts` (lines 5-10):
  - `lint`: `pnpm --filter passenger-app lint && pnpm --filter driver-app lint`. `--filter NAME` runs that package's script. `&&` means "run the next one only if the first succeeded".
  - `format`: `prettier --write .` rewrites all files in the repo to one style. `format:check` only checks them.
  - `test`: runs `test` in passenger-app, then driver-app.
- `devDependencies` (lines 11-13): `prettier` `^3.8.2`. Prettier is a code formatter. `^` allows newer minor versions.
- The admin app and the backend are not in these scripts. The admin app is plain JS and the backend uses Python (`uv`). Whether a `pnpm-workspace.yaml` file exists is not shown here; check with `fd pnpm-workspace`.

## 4. How data flows
```
pnpm lint (root)
  |-- pnpm --filter passenger-app lint --> eslint .
  '-- pnpm --filter driver-app lint    --> eslint .
```

## 5. Try it
```zsh
pnpm format:check
```
It runs `prettier --check .`. Expect "All matched files use Prettier code style!" or a list of files to fix.

## 6. Can it be better?
- Good: one command for both mobile apps.
- Weak: no `typecheck` shortcut. `format` runs on the whole repo, including backend and admin files. `&&` stops at the first failure, so driver lint is hidden if passenger lint fails. Use `pnpm -r --if-present lint` to run in all packages (opinion).
- Security: none.

## 7. Check yourself
1. What does `--filter driver-app` do?
2. Why is the package marked `private`?
