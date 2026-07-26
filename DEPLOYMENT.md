# Deploying CampusHire to Render

Five components: Flask API, Vue static site, Postgres, Redis (Key Value), and a
Celery worker. `render.yaml` provisions all of them from one blueprint.

---

## 1. What was broken, and what changed

These were fixed as part of making the project deployable. Several were not
deployment issues at all — they were live bugs or security problems.

### Would have failed the deploy outright

| # | Problem | Fix |
|---|---|---|
| 1 | **The frontend production build failed.** `npm run build` on Node 18 dies with `crypto.hash is not a function` — Vite 7 needs Node 20.19+. | `NODE_VERSION=20.19.5` in `render.yaml`, plus `.nvmrc` at the repo root and in `frontend/`. |
| 2 | **No WSGI server.** `gunicorn` was not in `requirements.txt`; the only entrypoint was `app.run(debug=True)`. | Added `gunicorn`; `startCommand` runs it with 2 workers × 4 threads. |
| 3 | **No production config.** `app.py` hardcoded `DevelopmentConfig`, so `DEBUG=True` and a hardcoded `SECRET_KEY` would have shipped to a public URL. `ProductionConfig` did not exist despite the README claiming it did. | `config.py` rewritten with `Config` / `DevelopmentConfig` / `ProductionConfig`, selected by `APP_ENV`. |
| 4 | **Database was hardcoded to SQLite** and ignored the environment. Render's filesystem is ephemeral, so every deploy would have wiped all data. | `DATABASE_URL` drives the URI. Render's `postgres://` is rewritten to `postgresql+psycopg2://` (SQLAlchemy 2.x dropped the bare alias). Added `psycopg2-binary`. |
| 5 | **CORS was hardcoded to `http://localhost:5173`** — the `CORS_ORIGINS` line was commented out — so the deployed frontend would have been blocked by the browser on every request. | `CORS_ORIGINS` is a required, comma-separated env var in production. |
| 6 | **API URL hardcoded** to `http://localhost:5000/api` in a committed `frontend/.env`. | Renamed to `.env.development`; production reads the build-time `VITE_API_BASE_URL` Render injects. |
| 7 | **`weasyprint` and `reportlab` in requirements but never imported.** WeasyPrint needs `libpango`/`libcairo` system libraries that Render's Python runtime does not ship. | Removed, along with ~10 transitive deps (`pydyf`, `pyphen`, `fonttools`, `pillow`, `tinycss2`, `tinyhtml5`, `cssselect2`, `zopfli`, `brotli`, `webencodings`) and the equally unused `Faker` and `aiosmtpd`. PDF generation is client-side via `html2pdf.js`. |
| 8 | **SPA deep links would 404.** Vue Router uses `createWebHistory`, so `/admin/students` is a real request to the static host. | Rewrite rule `/* → /index.html` in `render.yaml`. |

### Security

| # | Problem | Fix |
|---|---|---|
| 9 | **`SECRET_KEY` and `SECURITY_PASSWORD_SALT` were hardcoded in source** (`"this-is-a-secret-key"`). Anyone with repo access could forge auth tokens. | Read from the environment. `ProductionConfig.validate()` raises at boot if they are missing, so the app can never silently fall back to the dev key. Render generates both. |
| 10 | **`scripts/init_db.py` calls `db.drop_all()`** with nothing stopping it from running against production. | Added an `APP_ENV=production` guard that exits. New `scripts/bootstrap_db.py` is idempotent and destroys nothing. |
| 11 | **No admin user was created automatically**, contradicting the README, and `init_db.py` seeded `password123`. | `bootstrap_db.py` creates the admin from `ADMIN_PASSWORD`, refuses to run in production without it, and enforces a 12-character minimum. |
| 12 | Offer-letter upload accepted **unvalidated `student_id` / `application_id`** straight into a filename. | Both are now checked with `.isdigit()` before use. |

### Correctness

| # | Problem | Fix |
|---|---|---|
| 13 | **Uploads resolved three different ways** — `'uploads/resumes'` (CWD-relative), `os.getcwd() + …`, and `current_app.root_path + …`. Under Gunicorn the CWD-relative paths point somewhere different from the app-relative ones, so a resume saved by one code path is invisible to the one that serves it. | New `backend/storage.py` is the single resolver, anchored on an absolute `UPLOAD_FOLDER`. |
| 14 | **`resume_link` was written as `/uploads/resumes/<file>`** but the route is `/api/uploads/resumes/<file>`, so stored links did not resolve. | Corrected to match the registered route. |
| 15 | **`db.create_all()` ran at import time in `create_app()`**, meaning once per Gunicorn worker, racing on a cold database. | Gated behind `AUTO_CREATE_DB` (on in dev, off in prod). Production schema is owned by `bootstrap_db.py`. |
| 16 | **Celery was initialised twice** — once inside `create_app()` and again at `celery_config.py` module level — leaving two instances competing over `set_default()`, making `@shared_task` resolution order-dependent. | `celery_config.py` now reuses `app.extensions["celery"]`. |
| 17 | **CSV export emailed a dead link**: `FRONTEND_URL` + an `/api/...` path that was never registered, and which would have needed an auth token a plain email link cannot carry. It also wrote to `/tmp/exports`, unreadable from the web service. | Links to the in-app applications page; writes under `UPLOAD_FOLDER/exports`. |
| 18 | `FRONTEND_URL` was `'localhost:5173'` — **no scheme**, so every generated email link was malformed. | Defaults now include `http://`, and `.rstrip('/')` prevents double slashes. |
| 19 | `SQLALCHEMY_TRACK_MODIFICATIONS = True` — deprecated, adds per-object overhead. | Set to `False`. Added `pool_pre_ping` / `pool_recycle` so Render's idle-connection drops don't surface as 500s. |
| 20 | **No health check**, so Render could not tell a working deploy from a broken one. | `GET /api/health` verifies the database and reports cache status. Returns 503 if the DB is unreachable. |
| 21 | **No `.gitignore` anywhere** except `frontend/`. `venv/`, `instance/*.sqlite3`, `uploads/` (real student resumes), and `celerybeat-schedule` were all committable. | Root `.gitignore` added. |

### Left alone deliberately

- **`frontend/src/pages/Admin/Dashboard.vue`** is a stale 11-Feb duplicate of
  `pages/admin/Dashboard.vue`. Nothing imports it, and Vite leaves it out of the
  bundle, so it is harmless to the deploy — but the two directories differ only
  by case, which collides on macOS and Windows checkouts. Worth deleting:
  `rm -rf frontend/src/pages/Admin`.
- **`html2pdf.js` is 975 kB**, by far the largest chunk. It is now split into its
  own lazy chunk so it no longer invalidates the rest of the bundle on every
  change, but loading it only on the pages that generate PDFs would be better.

---

## 2. Deploy

### Prerequisites

The project is not currently its own git repository — `git status` here reports
on your home directory. Initialise it first:

```bash
cd CampusHire-From-Classroom-to-Career-
git init
git add .
git status          # confirm no venv/, node_modules/, .env or *.sqlite3 appear
git commit -m "Production hardening and Render deployment config"
git remote add origin git@github.com:<you>/campushire.git
git push -u origin main
```

The `git status` check matters — the new `.gitignore` only helps if you verify
it before the first commit.

### Create the blueprint

1. Render Dashboard → **New → Blueprint** → pick the repo.
2. Render reads `render.yaml` and prompts for every `sync: false` value.
   On this first pass you do not yet know the service URLs, so put placeholders
   in `CORS_ORIGINS`, `FRONTEND_URL` and `VITE_API_BASE_URL` and fix them in
   step 3. Set the real values now for:

   | Variable | Value |
   |---|---|
   | `ADMIN_PASSWORD` | 12+ characters. Creates the admin on first boot. |
   | `MAIL_SERVER` / `MAIL_USERNAME` / `MAIL_PASSWORD` | Your SMTP provider. Leave blank to deploy without email. |

3. After the first deploy Render assigns the URLs. Set the three cross-references
   and redeploy:

   | Service | Variable | Value |
   |---|---|---|
   | `campushire-api` | `CORS_ORIGINS` | `https://campushire-web.onrender.com` |
   | `campushire-api` | `FRONTEND_URL` | `https://campushire-web.onrender.com` |
   | `campushire-web` | `VITE_API_BASE_URL` | `https://campushire-api.onrender.com/api` |

   `VITE_API_BASE_URL` is inlined into the JavaScript at build time, so the
   static site needs a **rebuild**, not a restart, for a change to take effect.

### Verify

```bash
curl https://campushire-api.onrender.com/api/health
# {"status":"ok","env":"production","checks":{"database":"ok","cache":"ok"}}
```

Then log in at the frontend URL as `admin@campushire.edu` with your
`ADMIN_PASSWORD`. If login fails with a CORS error in the browser console,
`CORS_ORIGINS` does not exactly match the site's origin — scheme included, no
trailing slash.

---

## 3. Cost, and what the free tier will not do

| Component | Free | Notes |
|---|---|---|
| Static site | Yes | No limitations that matter here. |
| Web service (API) | Yes | **Sleeps after 15 min idle.** The next request takes ~50s while it wakes. |
| Postgres | Yes | **Render deletes free databases 30 days after creation.** Back up or upgrade before then. |
| Key Value (Redis) | Yes | 25 MB. Enough for this cache + queue. |
| Background worker | **No** | Render has no free tier for workers. |

**The worker is the one thing you cannot run for free.** `render.yaml` sets it to
`starter` (~$7/mo). Delete that block to deploy entirely free — the app still
works, because CSV export already runs synchronously in the request. What stops
is the Celery beat schedule: daily deadline reminders and the monthly activity
report. Nothing else depends on it.

Always-on API without the sleep delay is another ~$7/mo.

### Uploads are ephemeral

Resumes and offer letters are written to the container filesystem, which Render
resets on every deploy and restart. This is fine for a demo and **not fine for
real student data**. Two ways out:

1. **Render Disk** — add to the `campushire-api` service, mount at
   `/opt/render/project/src/backend/uploads`, and set `UPLOAD_FOLDER` to match.
   Costs ~$0.25/GB/mo and disables zero-downtime deploys (a disk attaches to one
   instance at a time).
2. **Object storage** — S3, Cloudflare R2, or Azure Blob. More work, but it is
   the option that survives scaling past one instance.

Until you do one of these, treat every uploaded file as disposable.

---

## 4. Local development

Unchanged from before, except that config now comes from `backend/.env`:

```bash
cd backend
cp .env.example .env
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python -m scripts.init_db      # dev only: DROPS and reseeds
python app.py                  # http://localhost:5000
```

```bash
cd frontend
nvm use                        # reads .nvmrc -> 20.19.5
npm install
npm run dev                    # http://localhost:5173
```

Celery, in two more terminals with the venv active:

```bash
celery -A celery_config.celery_app worker --loglevel=info
celery -A celery_config.celery_app beat   --loglevel=info
```

Local defaults still point at Mailpit (`localhost:1025`); run `mailpit` and open
`http://localhost:8025` to read captured mail.

### Testing the production path locally

Worth doing before you trust a deploy:

```bash
cd backend

# Prompted, not inlined — keeps the credential out of your shell history.
read -rsp 'Admin password (12+ chars): ' ADMIN_PASSWORD && echo
export ADMIN_PASSWORD

APP_ENV=production \
SECRET_KEY=$(python -c 'import secrets;print(secrets.token_urlsafe(32))') \
SECURITY_PASSWORD_SALT=$(python -c 'import secrets;print(secrets.token_urlsafe(32))') \
DATABASE_URL='sqlite:////tmp/prodcheck.sqlite3' \
CORS_ORIGINS='http://localhost:5173' \
  python -m scripts.bootstrap_db

# then serve it the way Render does
APP_ENV=production SECRET_KEY=... SECURITY_PASSWORD_SALT=... \
DATABASE_URL='sqlite:////tmp/prodcheck.sqlite3' CORS_ORIGINS='http://localhost:5173' \
  gunicorn app:app --bind 0.0.0.0:5000 --workers 2 --threads 4
```

Omitting any required variable should abort at boot with a message naming it.
That failure is the feature.

---

## 5. Troubleshooting

| Symptom | Cause |
|---|---|
| Build fails: `crypto.hash is not a function` | Node < 20.19. Check `NODE_VERSION` on the static site. |
| Boot fails: `missing required environment variables` | Working as intended — set the ones it names. |
| Browser: `blocked by CORS policy` | `CORS_ORIGINS` must match the site origin exactly: scheme, no trailing slash, comma-separated for multiple. |
| Frontend calls `localhost:5000` in production | `VITE_API_BASE_URL` was not set at build time. Set it and **rebuild**. |
| First request takes ~50s | Free-tier cold start. |
| Health check: `"database":"error"` | `DATABASE_URL` unset or the free Postgres passed its 30-day expiry. |
| Health check: `"cache":"degraded"` | Redis unreachable. The app still serves requests, reading through to the database. |
| Uploaded resumes vanish | Ephemeral filesystem. See §3. |
| Scheduled emails never arrive | The worker is not deployed (no free tier), or SMTP is unconfigured. |
