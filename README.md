# CampusHire — From Classroom to Career

A centralized platform that connects campus talent with hiring companies.
This is check for the first commit


> A full-stack campus placement portal built for the IITM BS Data Science — Application Development II (MAD-2) project.

**Student:** Vikas · **Roll:** 23f3001800 · **Course:** MAD-2, Jan 2026

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)
  - [Running Celery Workers](#running-celery-workers)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Background Jobs](#background-jobs)
- [Caching Strategy](#caching-strategy)
- [Default Credentials](#default-credentials)

---

## Overview

CampusHire digitises the entire campus recruitment lifecycle. Institutes currently rely on spreadsheets and manual email coordination for company approvals, drive management, and application tracking. CampusHire replaces all of that with a role-based web application for three user types:

- **Admin** (Institute Placement Cell) — manages everything
- **Company** — registers, posts drives, manages applicants, Hire student
- **Student** — applies to drives, tracks status, accepts offers, get placed

---

## Features

### Admin
- Dashboard with live counts: students, companies, drives, applications
- Approve or reject company registrations and placement drives
- Block / unblock students and companies (reversible)
- Search across all students and companies
- View all applications, placement statistics, and monthly reports

### Company
- Self-registration with full company profile (logo, industry, recruiter details)
- Create placement drives after admin approval
- View and manage applicants — shortlist, select, or reject with feedback
- Schedule multi-round interviews (in-person or online, with meeting link)
- Generate PDF offer letters; update final placement/selection status

### Student
- Self-registration and profile management (branch, CGPA, resume upload)
- Browse all approved drives with eligibility-based filtering and search
- Apply to drives with cover letter; duplicate applications blocked
- Real-time application status tracking (Applied → Shortlisted → Selected / Rejected)
- Accept or decline offer — **fully reversible** (Offered ↔ Joined ↔ Declined)
- View interview details: round, type, time, venue or meeting link
- Export full application history as CSV (async background job)

### Additional Features (Beyond Core Requirements)
- Interview scheduling with multiple rounds and mode support
- Offer letter PDF upload and in-browser viewing
- Reversible offer decisions (undo accept or decline at any time)
- Monthly HTML activity report email generated on the 1st of each month
- Master-detail admin UI with split-pane layout for students and companies
- Real-time offer banner on student dashboard when a new offer is pending
- Placement history with salary display in LPA format

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | Flask 3.x + Flask-RESTful |
| Authentication | Flask-Security-Too (token-based) |
| Database | SQLite + SQLAlchemy ORM |
| Caching | Redis + Flask-Caching |
| Background Jobs | Celery 5.x + Redis (broker) |
| Email | Flask-Mail |
| Frontend | Vue 3 (Composition API) + Pinia + Vue Router 4 |
| UI Library | Bootstrap 5 + Bootstrap Icons |
| Build Tool | Vite |
| HTTP Client | Axios (with interceptors) |

---

## Project Structure

```
CampusHire-From-Classroom-to-Career-/
│
├── backend/
│   ├── app.py                  # App factory, extension setup, route registration
│   ├── config.py               # DevelopmentConfig, ProductionConfig
│   ├── models.py               # SQLAlchemy models (User, Student, Company, PlacamentDrive, Application, Placement, Interview)
│   ├── extensions.py           # Shared instances: db, cache, mail, security
│   ├── celery_worker.py        # Celery app factory + beat schedule
│   ├── tasks.py                # Celery tasks: reminders, monthly report, CSV export
│   ├── trigger_tasks.py        # Manual task test script (dev only)
│   │
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── api.py              # All Flask-RESTful Resource classes
│   │   └── field_marshal.py    # Marshal field definitions
│   │
│   ├── sripts/
|  │   ├── __init__.py
│   │  ├── init_db.py             # Initialize the database
│   │  └── seed_data.py            # Seed the database with dummy data
│   │
│   ├── services/
│   │   ├── StudentService.py
│   │   ├── CompanyService.py
│   │   └── DriveService.py
│   │
│   ├── uploads/                # Resume and offer letter file storage
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── pages/              # Page-level Vue components
    │   ├── stores/             # Pinia stores (studentStore, adminStore, companyStore, userStore)
    │   ├── router/             # Vue Router with role-based navigation guards 
    │   └── main.js
    ├── index.html
    ├── vite.config.js
    └── package.json
```

---

## Getting Started

### Prerequisites

- Python 3.12+
- Node.js 18+
- Redis (running on `localhost:6379`)

Install Redis:
```bash
# Ubuntu/Debian
sudo apt install redis-server
redis-server --daemonize yes

# macOS
brew install redis
brew services start redis
```

---

### Backend Setup

```bash
# 1. Navigate to backend
cd CampusHire-From-Classroom-to-Career-/backend

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file (see Environment Variables section below)

# 5. Run the app — database and admin user are created automatically on first run
flask run
```

The backend will be available at `http://localhost:5000`.

> The database is created programmatically via SQLAlchemy models. No manual DB setup or DB Browser is needed.

---

### Frontend Setup

```bash
# 1. Navigate to frontend
cd CampusHire-From-Classroom-to-Career-/frontend

# 2. Install dependencies
npm install

# 3. Start dev server
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

### Running Celery Workers

Open two additional terminal tabs inside `backend/` with the venv activated:

```bash
# Terminal 2 — Celery worker
celery -A celery_worker.celery worker --loglevel=info

# Terminal 3 — Celery beat scheduler (for daily/monthly scheduled jobs)
celery -A celery_worker.celery beat --loglevel=info
```

To test tasks manually without Redis:
```bash
python trigger_tasks.py           # runs tasks directly (no Redis needed)
python trigger_tasks.py --async   # dispatches via Celery (Redis + worker required)
```

For local email testing (no real SMTP needed):
```bash
# Install and run Mailpit
mailpit
# Open http://localhost:8025 to view captured emails
```

---

## Environment Variables

Create a `.env` file inside `backend/`:

```env
# Flask
SECRET_KEY=your-secret-key-here
SECURITY_PASSWORD_SALT=your-salt-here
DEBUG=True

# Database
SQLALCHEMY_DATABASE_URI=sqlite:///campushire.db

# Redis & Celery
REDIS_URL=redis://localhost:6379/0

# Mail (use Mailpit for local dev)
MAIL_SERVER=localhost
MAIL_PORT=1025
MAIL_USE_TLS=False
MAIL_DEFAULT_SENDER=noreply@campushire.local

# App
COLLEGE_NAME=Your Institute Name
FRONTEND_URL=http://localhost:5173
ADMIN_EMAIL=admin@college.edu

# File uploads
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=5242880       # 5 MB
```

---

## API Endpoints

### Student
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/student/<id>` | Get student profile |
| `PUT` | `/api/student/<id>` | Update student profile |
| `PATCH` | `/api/student/<id>` | Partial update (block/unblock) |
| `GET` | `/api/student/<id>/applications` | List applications |
| `POST` | `/api/student/<id>/drives/<drive_id>/apply` | Apply to a drive |
| `DELETE` | `/api/student/<id>/applications/<app_id>` | Withdraw application |
| `GET` | `/api/student/<id>/placements` | Placement history |
| `PATCH` | `/api/student/<id>/placements/<p_id>` | Accept / decline / undo offer |
| `POST` | `/api/student/<id>/export-csv` | Trigger async CSV export |

### Company
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/company/<id>` | Get company profile |
| `PUT` | `/api/company/<id>` | Update company profile |
| `PATCH` | `/api/company/<id>` | Partial update (approve/block) |
| `GET` | `/api/company/<id>/drives` | List company drives |
| `POST` | `/api/company/<id>/drives` | Create placement drive |
| `PATCH` | `/api/company/<id>/drives/<drive_id>` | Update drive |
| `GET` | `/api/company/<id>/drives/<drive_id>/applicants` | View applicants |
| `PATCH` | `/api/company/<id>/drives/<drive_id>/applications/<app_id>` | Update application status |
| `POST` | `/api/company/<id>/interviews` | Schedule interview |
| `GET` | `/api/company/<id>/interviews/<app_id>` | Get interview details |

### Admin
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/admin/students` | All students |
| `GET` | `/api/admin/companies` | All companies |
| `GET` | `/api/admin/drives` | All drives |
| `GET` | `/api/admin/placements` | All placements |
| `GET` | `/api/admin/stats` | Dashboard statistics |
| `GET` | `/api/admin/drives/<drive_id>/applicants` | Drive applicants |

### Auth
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/auth/register` | Student / company registration |
| `POST` | `/login` | Flask-Security token login |

> All endpoints except registration and login require an `Authentication-Token` header.

---

## Background Jobs

### Daily Deadline Reminders — `send_deadline_reminders`
- **Schedule:** Every day at 08:00
- Finds all Open drives with deadlines within the next 3 days
- Emails each eligible student who has not yet applied
- Returns `{ sent, drives_checked }`

### Monthly Activity Report — `send_monthly_activity_report`
- **Schedule:** 1st of every month at 06:00
- Auto-calculates the previous full calendar month
- Sends a rich HTML email to all admin users with:
  - KPI banner (total drives, applications, selected, placement rate)
  - Per-drive breakdown table
  - Top 5 companies by applicant count
  - Branch-wise statistics
- Returns `{ sent, month, drives, applications, selected }`

### CSV Export — `export_applications_csv`
- **Trigger:** Student clicks "Export CSV" on their dashboard
- Generates a 13-column CSV with application history
- Saves to `/tmp/exports/` and emails a download link to the student
- Falls back to synchronous execution if Redis is unavailable

---

## Caching Strategy

| Resource | TTL | Invalidated On |
|---|---|---|
| Student / Company profile | 15 min | PUT / PATCH on same resource |
| Application lists | 5 min | Apply, withdraw, status update |
| Admin student / company lists | 5 min | Block/unblock, approve, delete |
| Placement history | 30 min | PATCH on placement status |
| Drive lists / details | 15 min | Admin approval, status change |

---

## Default Credentials

The admin user is created automatically on first run (no registration allowed for admin).

```
Role:     Admin
Email:    admin@campushire.com
Password: admin123          ← change this in config before deploying
```

---

## Notes

- The database (`campushire.db`) is created automatically — never use DB Browser or manual SQL to create tables.
- All file uploads (resumes, offer letters) are stored in `backend/uploads/`.
- Redis must be running for caching and Celery to work. The app degrades gracefully without it (CSV export falls back to sync mode; cache misses result in DB queries).
- Do not run `flask routes` from a parent directory — always `cd backend` first and set `FLASK_APP=app.py`.



### My approach for understadning the application flow 

User enters email/password
 ↓
Login.vue calls userStore.loginWithCredentials()
 ↓
api.js sends POST /api/auth/login
 ↓
Flask verifies credentials
 ↓
Flask returns token + user info
 ↓
Pinia stores token + user
 ↓
api.js uses token automatically
 ↓
User is authenticated



#### Frontend Workflow (Big Picture)

Vue Page
  ↓
Pinia Store
  ↓
api.js (Axios)
  ↓
Flask Backend
  ↓
Response
  ↓
Store updates state
  ↓
Vue auto re-renders


userStore → WHO am I?
studentStore → WHAT can student do?
companyStore → WHAT can company do?
adminStore → WHO controls system?