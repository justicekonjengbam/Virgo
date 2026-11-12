# admin-app/index.html

## 1. Purpose
The only HTML page of the Admin console. It holds two big blocks: a **login view** and the **app view** (sidebar plus content). `styles.css` makes it pretty and `app.js` fills it with data and switches between views. FastAPI serves it at `/admin` (`backend/app/main.py:36`). It loads `./assets/logo.svg` and fonts from `admin-app/assets/`.

## 2. Imports, one by one
HTML has no import lines, but two tags load files:
- `<link rel="stylesheet" href="./styles.css" />` (`:7`). **Stylesheet** (a file of look rules). `./` means "same folder".
- `<script type="module" src="./app.js"></script>` (`:42`). Loads the JavaScript. `type="module"` makes it an ES module (a file with its own scope that can use `import`/`export`; here it also runs after the page is parsed). It sits at the end of `body` so the elements already exist.

## 3. Walk through the code
- `<!doctype html>` (`:1`) tells the browser this is modern HTML. `<html lang="en">` sets the language for screen readers.
- `<meta charset="UTF-8" />` (`:4`) text encoding. `<meta name="viewport" ...>` (`:5`) makes the page fit phone width. `<title>` (`:6`) is the tab name.
- **Login view** `<main id="login-view" class="login-shell">` (`:10-21`). An `id` is a unique name that JS uses to find the element. Inside, `<form id="login-form">` has an email input (`type="email"`, `required`), a password input (`minlength="8"`), an error line `<p id="login-error" role="alert">` (`role="alert"` makes screen readers read it out), and a submit button. `app.js:30` listens to the form's submit.
- **App view** `<main id="app-view" class="app-shell hidden">` (`:23-41`). Class `hidden` hides it until login succeeds (`styles.css:6`).
  - `<aside class="sidebar">` with brand, a `<nav>` of six buttons. Each has `data-page="..."` (a custom attribute; JS reads it as `button.dataset.page`). Pages: overview, documents, drivers, support, outstation, account (`:27-32`).
  - `<button id="logout">` (`:34`).
  - `<header class="topbar">` with `#page-title`, `#admin-name`, `#admin-role` (`:37`), then `#app-error` (`:38`) and the empty `#page-content` (`:39`) that `app.js` fills.
- Note `Drivers & vehicles` (`:29`) uses a bare `&`; browsers accept it, but `&amp;` is the strict form.

## 4. How data flows
```
Browser GET /admin --> FastAPI StaticFiles --> index.html
   --> loads styles.css, app.js
app.js finds #login-form, #page-content by id and fills/hides them
```

## 5. Try it
Start the backend, open `http://localhost:8000/admin`. In browser DevTools (F12) run `document.querySelector('#app-view').classList` to see `hidden` while logged out.

## 6. Can it be better?
- Good: semantic tags (`main`, `aside`, `nav`, `header`), labels wrapping inputs, `role="alert"`, viewport tag.
- Weak: the nav buttons have no `type="button"` or `aria-current`; the logo `alt=""` is fine for decoration; permission-hidden pages are hidden by JS only; no `<noscript>` text.
- Cleaner way (opinion): add `aria-current="page"` to the active nav item.
- Security: hiding buttons in HTML or JS is not security. The server must check permissions on every `/admin/...` API call.

## 7. Check yourself
1. Why is the script tag at the end of `body`?
2. What does the class `hidden` do on `#app-view`, and who removes it?
