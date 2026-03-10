"""
tasks.py — Celery tasks for the Placement Portal
=================================================

Three jobs:
  a) send_deadline_reminders      – Daily @ 08:00: email students whose
                                    drive deadline is within the next 3 days.
  b) send_monthly_activity_report – 1st of every month @ 06:00: HTML
                                    placement report emailed to every admin.
  c) export_applications_csv      – Student-triggered async job: builds a CSV
                                    of the student's application history, saves
                                    it to /tmp/exports/, then emails a download
                                    link back to the student.

Celery beat schedule (add to your celery.py / app factory):
------------------------------------------------------------
    from celery.schedules import crontab

    app.conf.beat_schedule = {
        'daily-deadline-reminders': {
            'task':     'tasks.send_deadline_reminders',
            'schedule': crontab(hour=8, minute=0),          # every day 08:00
        },
        'monthly-activity-report': {
            'task':     'tasks.send_monthly_activity_report',
            'schedule': crontab(hour=6, minute=0, day_of_month=1),  # 1st of month
        },
    }

Required env / config keys:
    MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD
    MAIL_DEFAULT_SENDER   (e.g. "Placement Cell <noreply@college.edu>")
    ADMIN_EMAIL           (fallback if no User with role 'admin' found)
    FRONTEND_URL          (e.g. "https://placement.college.edu")
"""

import csv
import os
from datetime import datetime, timedelta, date
from io import StringIO

from celery import shared_task, current_app as celery_app
from flask import render_template_string
from flask_mail import Message

# ---------------------------------------------------------------------------
# Lazy imports — resolved inside task body so Flask app context is available
# ---------------------------------------------------------------------------
def _get_deps():
    """Return (mail, db, models…) after the app context is pushed."""
    from extensions import mail, db  # noqa: WPS433
    from models import (              # noqa: WPS433
        Student, Company, User, Application, PlacementDrive, Placement, Role,
    )
    return mail, db, Student, Company, User, Application, PlacementDrive, Placement, Role


# ===========================================================================
# a) DAILY DEADLINE REMINDER
# ===========================================================================

REMINDER_SUBJECT = "⏰ Upcoming Placement Deadline — Action Required"

REMINDER_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body { font-family: Arial, sans-serif; background:#f4f6fb; margin:0; padding:0; }
    .wrap { max-width:600px; margin:32px auto; background:#fff;
            border-radius:10px; overflow:hidden;
            box-shadow:0 2px 12px rgba(0,0,0,.08); }
    .header { background:linear-gradient(135deg,#0d6efd,#6610f2);
              padding:28px 32px; color:#fff; }
    .header h1 { margin:0; font-size:22px; }
    .header p  { margin:6px 0 0; opacity:.85; font-size:13px; }
    .body   { padding:28px 32px; }
    .drive-card {
      border:1px solid #dee2e6; border-radius:8px;
      padding:16px 20px; margin-bottom:14px;
    }
    .drive-card h3 { margin:0 0 6px; font-size:16px; color:#0d6efd; }
    .drive-card p  { margin:3px 0; font-size:13px; color:#555; }
    .badge-urgent { display:inline-block; background:#dc3545;
                    color:#fff; border-radius:4px;
                    padding:2px 8px; font-size:11px; margin-left:8px; }
    .badge-soon   { display:inline-block; background:#fd7e14;
                    color:#fff; border-radius:4px;
                    padding:2px 8px; font-size:11px; margin-left:8px; }
    .cta { display:inline-block; margin-top:18px;
           background:#0d6efd; color:#fff; text-decoration:none;
           padding:10px 24px; border-radius:6px; font-size:14px; }
    .footer { background:#f8f9fa; padding:16px 32px;
              font-size:11px; color:#adb5bd; text-align:center; }
  </style>
</head>
<body>
<div class="wrap">
  <div class="header">
    <h1>📋 Placement Deadline Reminder</h1>
    <p>Hi {{ name }}, the following drives close soon — don't miss out!</p>
  </div>
  <div class="body">
    {% for d in drives %}
    <div class="drive-card">
      <h3>
        {{ d.title }}
        {% if d.days_left <= 1 %}
          <span class="badge-urgent">Today!</span>
        {% elif d.days_left <= 2 %}
          <span class="badge-urgent">{{ d.days_left }} days left</span>
        {% else %}
          <span class="badge-soon">{{ d.days_left }} days left</span>
        {% endif %}
      </h3>
      <p><strong>Company:</strong> {{ d.company }}</p>
      <p><strong>Deadline:</strong> {{ d.deadline }}</p>
      {% if d.salary %}
      <p><strong>Package:</strong> {{ d.salary }} {{ d.currency }}</p>
      {% endif %}
    </div>
    {% endfor %}
    <a href="{{ frontend_url }}/drives" class="cta">View &amp; Apply Now →</a>
  </div>
  <div class="footer">
    You received this because you are registered on the Placement Portal.<br>
    {{ college }} · Placement Cell
  </div>
</div>
</body>
</html>
"""


@shared_task(bind=True, name='tasks.send_deadline_reminders',
             max_retries=3, default_retry_delay=300)
def send_deadline_reminders(self):
    """
    Runs daily. For every open drive whose deadline is within the next
    REMINDER_DAYS days, email every eligible student who has NOT yet applied.
    """
    REMINDER_DAYS = 3
    from flask import current_app

    mail, db, Student, Company, User, Application, PlacementDrive, Placement, Role = _get_deps()

    today    = date.today()
    cutoff   = today + timedelta(days=REMINDER_DAYS)
    frontend = current_app.config.get('FRONTEND_URL', 'https://placement.college.edu')
    college  = current_app.config.get('COLLEGE_NAME', 'Our Institute')

    # Drives that are still open and closing within the window
    upcoming_drives = (
        PlacementDrive.query
        .filter(
            PlacementDrive.status == 'Open',
            PlacementDrive.application_deadline >= today,
            PlacementDrive.application_deadline <= cutoff,
        )
        .all()
    )

    if not upcoming_drives:
        return {'sent': 0, 'skipped': 'no upcoming drives'}

    # Build a lookup: drive_id → set of student_ids who already applied
    applied_map = {}
    for drive in upcoming_drives:
        applied_map[drive.id] = {
            a.student_id
            for a in Application.query.filter_by(drive_id=drive.id).all()
        }

    # All active students with an email
    students = (
        Student.query
        .join(Student.user)
        .filter(User.active == True)          # noqa: E712
        .all()
    )

    sent_count = 0

    for student in students:
        if not student.user or not student.user.email:
            continue

        # Which drives is this student eligible for but hasn't applied yet?
        eligible = []
        for drive in upcoming_drives:
            if student.id in applied_map[drive.id]:
                continue                      # already applied
            deadline = drive.application_deadline
            if isinstance(deadline, datetime):
                deadline = deadline.date()
            days_left = (deadline - today).days
            eligible.append({
                'title':    drive.title,
                'company':  drive.company.company_name if drive.company else '—',
                'deadline': deadline.strftime('%d %b %Y'),
                'days_left': days_left,
                'salary':   drive.salary_max,
                'currency': drive.currency or 'INR',
            })

        if not eligible:
            continue

        html_body = render_template_string(
            REMINDER_HTML,
            name=student.user.name,
            drives=eligible,
            frontend_url=frontend,
            college=college,
        )

        msg = Message(
            subject=REMINDER_SUBJECT,
            recipients=[student.user.email],
            html=html_body,
        )
        try:
            mail.send(msg)
            sent_count += 1
        except Exception as exc:
            # Log but don't abort the whole job
            current_app.logger.error(
                f'Reminder email failed for student {student.id}: {exc}'
            )

    return {'sent': sent_count, 'drives_checked': len(upcoming_drives)}


# ===========================================================================
# b) MONTHLY ACTIVITY REPORT  (sent to admin on 1st of every month)
# ===========================================================================

REPORT_SUBJECT = "📊 Monthly Placement Activity Report — {month} {year}"

REPORT_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    * { box-sizing: border-box; }
    body { font-family: Arial, sans-serif; background:#f4f6fb;
           margin:0; padding:0; color:#212529; }
    .wrap { max-width:700px; margin:32px auto; background:#fff;
            border-radius:12px; overflow:hidden;
            box-shadow:0 4px 20px rgba(0,0,0,.1); }

    /* Header */
    .header { background:linear-gradient(135deg,#0d6efd,#6610f2);
              padding:32px 36px; color:#fff; }
    .header h1 { margin:0 0 4px; font-size:24px; }
    .header p  { margin:0; opacity:.85; font-size:13px; }

    /* KPI row */
    .kpi-row { display:flex; gap:0; border-bottom:1px solid #dee2e6; }
    .kpi { flex:1; padding:20px 16px; text-align:center;
           border-right:1px solid #dee2e6; }
    .kpi:last-child { border-right:none; }
    .kpi-val  { font-size:32px; font-weight:700; color:#0d6efd; line-height:1; }
    .kpi-label{ font-size:11px; color:#6c757d; margin-top:4px;
                text-transform:uppercase; letter-spacing:.06em; }

    /* Section */
    .section { padding:24px 36px; }
    .section h2 { font-size:15px; font-weight:700; color:#495057;
                  text-transform:uppercase; letter-spacing:.06em;
                  border-bottom:2px solid #dee2e6; padding-bottom:8px;
                  margin:0 0 16px; }

    /* Table */
    table { width:100%; border-collapse:collapse; font-size:13px; }
    th { background:#f8f9fa; color:#6c757d; font-weight:600;
         text-align:left; padding:8px 12px;
         text-transform:uppercase; font-size:11px; letter-spacing:.05em; }
    td { padding:10px 12px; border-bottom:1px solid #f0f0f0; }
    tr:last-child td { border-bottom:none; }
    .badge { display:inline-block; padding:2px 8px; border-radius:4px;
             font-size:11px; font-weight:600; }
    .badge-success { background:#d1e7dd; color:#0f5132; }
    .badge-warning { background:#fff3cd; color:#664d03; }
    .badge-danger  { background:#f8d7da; color:#842029; }

    /* Progress bar */
    .progress-wrap { background:#e9ecef; border-radius:99px;
                     height:8px; overflow:hidden; margin-top:4px; }
    .progress-bar  { height:100%; background:#0d6efd; border-radius:99px; }

    /* Footer */
    .footer { background:#f8f9fa; padding:16px 36px;
              font-size:11px; color:#adb5bd; text-align:center;
              border-top:1px solid #dee2e6; }
  </style>
</head>
<body>
<div class="wrap">

  <!-- Header -->
  <div class="header">
    <h1>📊 Monthly Placement Report</h1>
    <p>{{ college }} · {{ month }} {{ year }} · Generated {{ generated_on }}</p>
  </div>

  <!-- KPIs -->
  <div class="kpi-row">
    <div class="kpi">
      <div class="kpi-val">{{ stats.drives }}</div>
      <div class="kpi-label">Drives Conducted</div>
    </div>
    <div class="kpi">
      <div class="kpi-val">{{ stats.applications }}</div>
      <div class="kpi-label">Applications</div>
    </div>
    <div class="kpi">
      <div class="kpi-val">{{ stats.selected }}</div>
      <div class="kpi-label">Students Selected</div>
    </div>
    <div class="kpi">
      <div class="kpi-val">{{ stats.placement_rate }}%</div>
      <div class="kpi-label">Placement Rate</div>
    </div>
  </div>

  <!-- Drive breakdown -->
  <div class="section">
    <h2>Drives This Month</h2>
    {% if drives %}
    <table>
      <thead>
        <tr>
          <th>Drive</th>
          <th>Company</th>
          <th>Applied</th>
          <th>Selected</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        {% for d in drives %}
        <tr>
          <td><strong>{{ d.title }}</strong></td>
          <td>{{ d.company }}</td>
          <td>{{ d.applied }}</td>
          <td>{{ d.selected }}</td>
          <td>
            <span class="badge
              {% if d.status == 'Completed' %}badge-success
              {% elif d.status == 'Open' %}badge-warning
              {% else %}badge-danger{% endif %}">
              {{ d.status }}
            </span>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
    {% else %}
    <p style="color:#6c757d;font-size:13px;">No drives were conducted this month.</p>
    {% endif %}
  </div>

  <!-- Top companies -->
  {% if top_companies %}
  <div class="section" style="border-top:1px solid #dee2e6">
    <h2>Top Recruiting Companies</h2>
    <table>
      <thead><tr><th>Company</th><th>Offers Made</th><th>Share</th></tr></thead>
      <tbody>
        {% for c in top_companies %}
        <tr>
          <td>{{ c.name }}</td>
          <td>{{ c.offers }}</td>
          <td style="width:200px">
            <div class="progress-wrap">
              <div class="progress-bar" style="width:{{ c.pct }}%"></div>
            </div>
          </td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
  {% endif %}

  <!-- Branch breakdown -->
  {% if branch_stats %}
  <div class="section" style="border-top:1px solid #dee2e6">
    <h2>Placements by Branch</h2>
    <table>
      <thead><tr><th>Branch</th><th>Selected</th></tr></thead>
      <tbody>
        {% for b in branch_stats %}
        <tr>
          <td>{{ b.branch }}</td>
          <td>{{ b.count }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </div>
  {% endif %}

  <div class="footer">
    This report was auto-generated by the Placement Portal on {{ generated_on }}.<br>
    {{ college }} · Placement Cell · Confidential
  </div>
</div>
</body>
</html>
"""


@shared_task(bind=True, name='tasks.send_monthly_activity_report',
             max_retries=3, default_retry_delay=600)
def send_monthly_activity_report(self):
    """
    Runs on the 1st of every month at 06:00.
    Builds an HTML report covering the previous calendar month and
    emails it to every user who has the 'admin' role.
    """
    from flask import current_app
    from sqlalchemy import func, extract

    mail, db, Student, Company, User, Application, PlacementDrive, Placement, Role = _get_deps()

    today     = date.today()
    # Report window = previous calendar month
    first_of_this  = today.replace(day=1)
    last_of_prev   = first_of_this - timedelta(days=1)
    first_of_prev  = last_of_prev.replace(day=1)

    month_label = first_of_prev.strftime('%B')
    year_label  = first_of_prev.strftime('%Y')
    college     = current_app.config.get('COLLEGE_NAME', 'Our Institute')
    frontend    = current_app.config.get('FRONTEND_URL', 'https://placement.college.edu')

    # ── Drives that started or were active in the previous month ─────────────
    month_drives = (
        PlacementDrive.query
        .filter(
            PlacementDrive.created_at >= datetime.combine(first_of_prev, datetime.min.time()),
            PlacementDrive.created_at <  datetime.combine(first_of_this, datetime.min.time()),
        )
        .all()
    )

    # ── Applications placed in that month ────────────────────────────────────
    month_apps = (
        Application.query
        .filter(
            Application.applied_date >= datetime.combine(first_of_prev, datetime.min.time()),
            Application.applied_date <  datetime.combine(first_of_this, datetime.min.time()),
        )
        .all()
    )

    selected_apps = [a for a in month_apps if a.status == 'Selected']
    total_apps    = len(month_apps)
    total_sel     = len(selected_apps)
    placement_rate = round((total_sel / total_apps * 100) if total_apps else 0, 1)

    # ── Per-drive breakdown ───────────────────────────────────────────────────
    drives_data = []
    for d in month_drives:
        d_apps = [a for a in month_apps if a.drive_id == d.id]
        drives_data.append({
            'title':    d.title,
            'company':  d.company.company_name if d.company else '—',
            'applied':  len(d_apps),
            'selected': sum(1 for a in d_apps if a.status == 'Selected'),
            'status':   d.status,
        })

    # ── Top companies by offers ───────────────────────────────────────────────
    company_offer_map = {}
    for a in selected_apps:
        if a.drive and a.drive.company:
            name = a.drive.company.company_name
            company_offer_map[name] = company_offer_map.get(name, 0) + 1

    sorted_companies = sorted(company_offer_map.items(), key=lambda x: x[1], reverse=True)[:5]
    max_offers = sorted_companies[0][1] if sorted_companies else 1
    top_companies = [
        {'name': name, 'offers': cnt, 'pct': round(cnt / max_offers * 100)}
        for name, cnt in sorted_companies
    ]

    # ── Branch breakdown ──────────────────────────────────────────────────────
    branch_map = {}
    for a in selected_apps:
        if a.student and a.student.branch:
            branch_map[a.student.branch] = branch_map.get(a.student.branch, 0) + 1

    branch_stats = [
        {'branch': b, 'count': c}
        for b, c in sorted(branch_map.items(), key=lambda x: x[1], reverse=True)
    ]

    # ── Render HTML ───────────────────────────────────────────────────────────
    html_body = render_template_string(
        REPORT_HTML,
        college=college,
        month=month_label,
        year=year_label,
        generated_on=today.strftime('%d %b %Y'),
        stats={
            'drives':          len(month_drives),
            'applications':    total_apps,
            'selected':        total_sel,
            'placement_rate':  placement_rate,
        },
        drives=drives_data,
        top_companies=top_companies,
        branch_stats=branch_stats,
        frontend_url=frontend,
    )

    # ── Find admin recipients ─────────────────────────────────────────────────
    admin_role = Role.query.filter_by(name='admin').first()
    if admin_role:
        admin_emails = [u.email for u in admin_role.users if u.email and u.active]
    else:
        fallback = current_app.config.get('ADMIN_EMAIL')
        admin_emails = [fallback] if fallback else []

    if not admin_emails:
        current_app.logger.warning('Monthly report: no admin emails found.')
        return {'sent': 0, 'reason': 'no admin emails'}

    subject = REPORT_SUBJECT.format(month=month_label, year=year_label)

    sent_count = 0
    for email in admin_emails:
        msg = Message(subject=subject, recipients=[email], html=html_body)
        try:
            mail.send(msg)
            sent_count += 1
        except Exception as exc:
            current_app.logger.error(f'Monthly report email failed to {email}: {exc}')

    return {
        'sent':         sent_count,
        'month':        f'{month_label} {year_label}',
        'drives':       len(month_drives),
        'applications': total_apps,
        'selected':     total_sel,
    }


# ===========================================================================
# c) USER-TRIGGERED ASYNC CSV EXPORT
# ===========================================================================

EXPORT_DONE_SUBJECT = "✅ Your Application Export is Ready"

EXPORT_DONE_HTML = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body { font-family: Arial, sans-serif; background:#f4f6fb; margin:0; padding:0; }
    .wrap { max-width:560px; margin:32px auto; background:#fff;
            border-radius:10px; overflow:hidden;
            box-shadow:0 2px 12px rgba(0,0,0,.08); }
    .header { background:linear-gradient(135deg,#198754,#0d6efd);
              padding:28px 32px; color:#fff; }
    .header h1 { margin:0; font-size:20px; }
    .body   { padding:28px 32px; }
    .body p { color:#555; font-size:14px; line-height:1.6; }
    .meta { background:#f8f9fa; border-radius:8px; padding:14px 18px;
            margin:16px 0; font-size:13px; color:#495057; }
    .meta strong { color:#212529; }
    .cta  { display:inline-block; background:#0d6efd; color:#fff;
            text-decoration:none; padding:10px 24px;
            border-radius:6px; font-size:14px; margin-top:8px; }
    .footer { background:#f8f9fa; padding:14px 32px;
              font-size:11px; color:#adb5bd; text-align:center; }
  </style>
</head>
<body>
<div class="wrap">
  <div class="header"><h1>✅ Your CSV Export is Ready!</h1></div>
  <div class="body">
    <p>Hi <strong>{{ name }}</strong>,</p>
    <p>Your placement application history export has been generated successfully.</p>
    <div class="meta">
      <strong>File:</strong> {{ filename }}<br>
      <strong>Records:</strong> {{ record_count }} application(s)<br>
      <strong>Generated:</strong> {{ generated_on }}
    </div>
    <p>Click the button below to download your CSV. The link expires in 24 hours.</p>
    <a href="{{ download_url }}" class="cta">⬇ Download CSV</a>
  </div>
  <div class="footer">
    This export was requested from the Placement Portal student dashboard.<br>
    {{ college }} · Placement Cell
  </div>
</div>
</body>
</html>
"""

# CSV columns
CSV_HEADERS = [
    'Application ID',
    'Student ID',
    'Student Name',
    'Company Name',
    'Drive Title',
    'Drive Location',
    'Salary (Min)',
    'Salary (Max)',
    'Currency',
    'Application Status',
    'Applied Date',
    'Reviewed Date',
    'Cover Letter',
]


@shared_task(bind=True, name='tasks.export_applications_csv',
             max_retries=3, default_retry_delay=60)
def export_applications_csv(self, student_id):
    """
    User-triggered async job.
    1. Fetches all applications for student_id.
    2. Writes a CSV to /tmp/exports/<filename>.
    3. Emails the student a download link.
    4. Returns metadata dict (picked up by the status-polling endpoint).
    """
    from flask import current_app

    mail, db, Student, Company, User, Application, PlacementDrive, Placement, Role = _get_deps()

    student = Student.query.get(student_id)
    if not student or not student.user:
        raise ValueError(f'Student {student_id} not found')

    applications = (
        Application.query
        .filter_by(student_id=student_id)
        .order_by(Application.applied_date.desc())
        .all()
    )

    # ── Build CSV in memory ───────────────────────────────────────────────────
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(CSV_HEADERS)

    for app in applications:
        drive   = app.drive
        company = drive.company if drive else None
        writer.writerow([
            app.id,
            student_id,
            student.user.name,
            company.company_name              if company else '—',
            drive.title                       if drive   else '—',
            drive.location                    if drive   else '—',
            drive.salary_min                  if drive   else '—',
            drive.salary_max                  if drive   else '—',
            drive.currency                    if drive   else '—',
            app.status,
            app.applied_date.strftime('%Y-%m-%d %H:%M') if app.applied_date  else '—',
            app.reviewed_date.strftime('%Y-%m-%d %H:%M') if app.reviewed_date else '—',
            (app.cover_letter or '')[:200],   # truncate very long cover letters
        ])

    csv_content = output.getvalue()

    # ── Persist to disk ───────────────────────────────────────────────────────
    export_dir = '/tmp/exports'
    os.makedirs(export_dir, exist_ok=True)

    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename  = f'applications_student{student_id}_{timestamp}.csv'
    filepath  = os.path.join(export_dir, filename)

    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        f.write(csv_content)

    # ── Email the student ─────────────────────────────────────────────────────
    frontend      = current_app.config.get('FRONTEND_URL', 'https://placement.college.edu')
    college       = current_app.config.get('COLLEGE_NAME', 'Our Institute')
    download_url  = f"{frontend}/api/student/{student_id}/export-csv/{filename}/download"
    generated_on  = datetime.utcnow().strftime('%d %b %Y, %H:%M UTC')
    record_count  = len(applications)

    html_body = render_template_string(
        EXPORT_DONE_HTML,
        name=student.user.name,
        filename=filename,
        record_count=record_count,
        generated_on=generated_on,
        download_url=download_url,
        college=college,
    )

    msg = Message(
        subject=EXPORT_DONE_SUBJECT,
        recipients=[student.user.email],
        html=html_body,
    )
    try:
        mail.send(msg)
    except Exception as exc:
        current_app.logger.error(
            f'Export email failed for student {student_id}: {exc}'
        )
        # Don't re-raise — file was saved, student can still download via polling

    return {
        'filename':     filename,
        'record_count': record_count,
        'download_url': download_url,
    }