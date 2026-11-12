# admin-app/app.js

## 1. Purpose
All the behaviour of the Admin console, in plain JavaScript (no framework). It handles login, keeps the token, builds each page's HTML from API data, and sends admin actions (approve documents, update tickets, assign outstation drivers, change password). It talks to the backend under `/api/v1/admin/...`. It reads and writes elements defined in `index.html` and uses class names from `styles.css`.

## 2. Imports, one by one
There are no `import` lines. It runs as a module (`index.html:42`) and uses **browser built-ins** (tools every browser gives you):
- `document` (the page tree. *Example:* `document.querySelector('#email')` finds the element with id `email`).
- `sessionStorage` (small key-value storage that lasts until the tab closes. *Example:* `sessionStorage.setItem('a','1')`).
- `fetch` (sends an HTTP request. *Example:* `await fetch('/x')`).
- `JSON.parse/stringify` (text to object and back), `Promise.all` (run many async jobs at once), `prompt/confirm/alert` (browser pop-up boxes).

## 3. Walk through the code
**State and element handles** (`:1-5`). `state = { token, admin, page }`. Token and profile are restored from `sessionStorage` (`|| 'null'` so `JSON.parse` never gets `null`). `loginView`, `appView`, `content`, `error` store elements found once.

**`api(path, options)`** (`:7-12`). Calls `fetch('/api/v1' + path)`. Headers: JSON content type, plus `Authorization: Bearer <token>` when logged in (**Bearer token**: a pass string sent in a header, the server checks it), plus any custom headers. `await response.json().catch(() => ({}))` reads the body, or `{}` if it is not JSON. If `!response.ok` (status not 2xx) it builds a message from `body.detail` (FastAPI puts errors there; validation errors are a list, joined by spaces) and `throw new Error(...)`. Returns the parsed body. *Example:* `await api('/admin/drivers')` gives an array of drivers.

**Small helpers** (`:13-16`):
- `esc(value)` replaces `& < > " '` with HTML codes. It stops **XSS** (attacker text running as code in your page). `esc('<b>')` gives `&lt;b&gt;`. `value ?? ''` turns null into empty text.
- `badge(value)` makes `<span class="badge verified">verified</span>`; underscores become spaces.
- `localPhone(v)` keeps digits and the last 10: `'919876543210'` becomes `'9876543210'`.
- `has(permission)` true if the admin's permissions list holds it (`?.` safely stops if null).

**Views** (`:18-28`). `showApp()` hides login, shows app, writes the name and role, hides nav items the admin may not use (`has('documents:review')` etc.), then `render()`. `showLogin()` the reverse. `clearSession()` empties storage and state and shows login.

**Login handler** (`:30-35`). On submit: `preventDefault()` stops the normal page reload. Disables the button, POSTs email and password to `/admin/auth/login`, stores `access_token` and `admin`, calls `showApp()`. `catch` prints the error; `finally` re-enables the button.

**Logout and nav** (`:36-37`). Logout calls `clearSession`. Each `.nav-item` click sets `state.page` from `data-page`, moves the `active` class, and calls `render()`.

**`render()`** (`:39-43`). Sets the page title from a lookup object, shows "Loading...", then awaits the page function for `state.page`. On error it shows the message; if the text matches `/Admin session|authentication|unavailable/i` it logs the admin out (expired session).

**Pages**
- `overview()` (`:44-47`): loads pending documents, drivers, open tickets in parallel with `Promise.all` (permission-less parts become `[]`), then draws 4 count cards.
- `documents()` (`:48-52`) lists pending documents with Approve/Reject buttons; each button carries `data-driver`, `data-document`, `data-review`. `reviewDocument` (`:53`) asks for a reason on reject (`prompt`), then `PUT /admin/drivers/{id}/documents/{type}/review`, then reloads the list.
- `drivers()` (`:54-57`): a table of drivers, city, vehicle, status badges.
- `support()` (`:58-62`) and `updateTicket` (`:63`): list tickets; "Mark in progress" or "Resolve" (needs a note) via `PATCH /admin/support-tickets/{id}`.
- `outstation()` (`:64-68`): lists outstation (out-of-town scheduled) bookings with a 3-step bar (`outstationStage`, `:69`: requested 0, confirmed 1, assigned or completed 2). Buttons depend on status: confirm/reject for `requested`, "Choose eligible driver" for `confirmed`, "Mark completed" for `driver_assigned`.
- `openDriverPicker(bookingId)` (`:70-80`): fetches eligible drivers, builds a modal (popup) overlay, closes on outside click or the x, and on "Assign driver" sends `PATCH` with `driver_phone_number`, then refreshes.
- `updateOutstation(id, action)` (`:81`): confirm uses `confirm()`, reject needs a reason, complete sends status `completed`.
- `account()` (`:82-86`): reloads `/admin/auth/me`, shows ID, email, role, last login, permissions, and a password form.
- `changePassword` (`:87`): checks the two new passwords match, POSTs to `/admin/auth/change-password`, alerts the message, then logs out (the server closes all sessions).
- `labelDocument` (`:88`): friendly names for document codes.

**Start-up** (`:90`). If a token and profile exist, it re-checks `/admin/auth/me` and shows the app, else clears the session; otherwise shows login.

## 4. How data flows
```
admin types email+password --> #login-form submit --> api('/admin/auth/login')
  --> FastAPI returns {access_token, admin} --> sessionStorage + state --> showApp --> render
click "Drivers" --> render --> api('/admin/drivers') (Bearer token) --> JSON --> template string
  --> esc() each value --> content.innerHTML --> browser draws table
click Approve --> PUT review --> server updates --> documents() reloads
```

## 5. Try it
Run the backend, open `/admin`, sign in. In DevTools console: `sessionStorage.getItem('cabsure-admin-profile')` shows the saved profile (the token is stored too; never share it). Watch the Network tab to see `Authorization: Bearer ...` on each call.

## 6. Can it be better?
- Good: every dynamic value goes through `esc()`; permission-based nav; central `api()`; auto logout on expired session.
- Weak: one 90-line file with very long single lines (line 66, 84, 87); HTML built as strings; repeated `try/catch` blocks; `prompt/confirm/alert` are crude; error detection by message text (`:42`) is fragile; `item.document_type` and `item.driver_id` go into attributes without `esc` (`:50`) although likely safe values; token in `sessionStorage` is readable by any XSS bug (an `httpOnly` cookie is safer, opinion); no tests; `esc(driver.phone_number)` in picker shows full number while other places use `localPhone`.
- Cleaner way: split into `api.js`, `pages/*.js`, and format code with Prettier. Before/after for status check: `if (response.status === 401) clearSession()` instead of matching message text.
- Security: UI hiding is only convenience. The server must enforce permissions. Never log the token. Real tokens: `<secret>`.

## 7. Check yourself
1. What does `esc()` protect against, and where is it applied when drawing the drivers table?
2. What triggers an automatic logout in `render()`?
