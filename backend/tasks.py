"""
tasks.py — Celery tasks for CampusHire
=======================================

Tasks:
  a) send_deadline_reminders       Daily 08:00 IST
  b) send_monthly_activity_report  1st of every month 06:00 IST
  c) export_applications_csv       Student-triggered async job
  d) health_check                  Ping / sanity check
"""

import csv
import os
from datetime import date, datetime, timedelta
from io import StringIO

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

_RETRY = dict(max_retries=3, default_retry_delay=300)


# ---------------------------------------------------------------------------
# Lazy imports — called inside task body after app context is pushed
# ---------------------------------------------------------------------------
def _get_deps():
    from extensions import db, mail
    from models import (
        Application, Company, PlacementDrive,
        Placement, Role, Student, User,
    )
    return mail, db, Student, Company, User, Application, PlacementDrive, Placement, Role


# ---------------------------------------------------------------------------
# Email helper
# ---------------------------------------------------------------------------
def _send_email(mail, *, subject, recipients, html):
    from flask_mail import Message
    mail.send(Message(subject=subject, recipients=recipients, html=html))


# ===========================================================================
# d) HEALTH CHECK
# ===========================================================================

@shared_task(name="tasks.health_check")
def health_check():
    from flask import current_app
    return {
        "status":    "ok",
        "app":       current_app.name,
        "timestamp": datetime.utcnow().isoformat(),
    }


# ===========================================================================
# a) DAILY DEADLINE REMINDER
# ===========================================================================

_REMINDER_SUBJECT = "⏰ Upcoming Placement Deadline — Action Required"

_REMINDER_HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  body{font-family:Arial,sans-serif;background:#f4f6fb;margin:0;padding:0}
  .wrap{max-width:600px;margin:32px auto;background:#fff;border-radius:10px;
        overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.08)}
  .hdr{background:linear-gradient(135deg,#0d6efd,#6610f2);padding:28px 32px;color:#fff}
  .hdr h1{margin:0;font-size:22px}
  .hdr p{margin:6px 0 0;opacity:.85;font-size:13px}
  .body{padding:28px 32px}
  .card{border:1px solid #dee2e6;border-radius:8px;padding:16px 20px;margin-bottom:14px}
  .card h3{margin:0 0 6px;font-size:16px;color:#0d6efd}
  .card p{margin:3px 0;font-size:13px;color:#555}
  .urgent{display:inline-block;background:#dc3545;color:#fff;border-radius:4px;padding:2px 8px;font-size:11px;margin-left:8px}
  .soon{display:inline-block;background:#fd7e14;color:#fff;border-radius:4px;padding:2px 8px;font-size:11px;margin-left:8px}
  .cta{display:inline-block;margin-top:18px;background:#0d6efd;color:#fff;text-decoration:none;padding:10px 24px;border-radius:6px;font-size:14px}
  .foot{background:#f8f9fa;padding:16px 32px;font-size:11px;color:#adb5bd;text-align:center}
</style></head><body>
<div class="wrap">
  <div class="hdr">
    <h1>📋 Placement Deadline Reminder</h1>
    <p>Hi {{ name }}, the following drives close soon!</p>
  </div>
  <div class="body">
    {% for d in drives %}
    <div class="card">
      <h3>{{ d.title }}
        {% if d.days_left <= 1 %}<span class="urgent">Today!</span>
        {% elif d.days_left <= 2 %}<span class="urgent">{{ d.days_left }} days left</span>
        {% else %}<span class="soon">{{ d.days_left }} days left</span>{% endif %}
      </h3>
      <p><strong>Company:</strong> {{ d.company }}</p>
      <p><strong>Deadline:</strong> {{ d.deadline }}</p>
      {% if d.salary %}<p><strong>Package:</strong> ₹{{ d.salary }} {{ d.currency }}</p>{% endif %}
    </div>
    {% endfor %}
    <a href="{{ frontend_url }}/drives" class="cta">View &amp; Apply Now →</a>
  </div>
  <div class="foot">{{ college }} · Placement Cell</div>
</div></body></html>
"""


@shared_task(bind=True, name="tasks.send_deadline_reminders", **_RETRY)
def send_deadline_reminders(self, reminder_days=3):
    """
    Emails students about drives whose deadline is within `reminder_days` days.
    reminder_days=3 in production. Pass a higher value to test (e.g. 30).

    FIX: application_deadline is a DateTime column — compare using datetime
         objects, not date objects, to avoid silent mismatches.
    """
    from flask import current_app, render_template_string

    mail, db, Student, Company, User, Application, PlacementDrive, Placement, Role = _get_deps()

    # Use datetime boundaries (not date) because application_deadline is DateTime
    now    = datetime.utcnow()
    cutoff = now + timedelta(days=reminder_days)

    frontend = current_app.config.get("FRONTEND_URL", "http://localhost:5173")
    college  = current_app.config.get("COLLEGE_NAME", "Our Institute")

    logger.info("send_deadline_reminders | now=%s cutoff=%s", now.date(), cutoff.date())

    try:
        upcoming = (
            PlacementDrive.query
            .filter(
                PlacementDrive.status == "Open",
                PlacementDrive.application_deadline >= now,      # DateTime >= DateTime ✓
                PlacementDrive.application_deadline <= cutoff,   # DateTime <= DateTime ✓
            )
            .all()
        )
    except Exception as exc:
        logger.exception("DB error fetching drives")
        raise self.retry(exc=exc)

    if not upcoming:
        logger.info("No upcoming drives in next %d days.", reminder_days)
        return {"sent": 0, "reason": f"no drives in next {reminder_days} days"}

    logger.info("Found %d upcoming drive(s).", len(upcoming))

    # Build applied-student lookup per drive
    applied_map = {
        d.id: {a.student_id for a in Application.query.filter_by(drive_id=d.id).all()}
        for d in upcoming
    }

    # Active students with email
    try:
        students = (
            Student.query
            .join(Student.user)
            .filter(User.active == True)    # noqa: E712
            .all()
        )
    except Exception as exc:
        logger.exception("DB error fetching students")
        raise self.retry(exc=exc)

    sent = skipped = errors = 0

    for student in students:
        if not (student.user and student.user.email):
            skipped += 1
            continue

        eligible = []
        for drive in upcoming:
            if student.id in applied_map.get(drive.id, set()):
                continue

            deadline   = drive.application_deadline   # this is a datetime
            days_left  = (deadline.date() - now.date()).days

            eligible.append({
                "title":     drive.title,
                "company":   drive.company.company_name if drive.company else "—",
                "deadline":  deadline.strftime("%d %b %Y"),
                "days_left": days_left,
                "salary":    drive.salary_max,
                "currency":  drive.currency or "INR",
            })

        if not eligible:
            skipped += 1
            continue

        html_body = render_template_string(
            _REMINDER_HTML,
            name=student.user.name,
            drives=eligible,
            frontend_url=frontend,
            college=college,
        )
        try:
            _send_email(mail, subject=_REMINDER_SUBJECT,
                        recipients=[student.user.email], html=html_body)
            sent += 1
            logger.info("Reminder → %s", student.user.email)
        except Exception as exc:
            errors += 1
            logger.error("Reminder FAILED for student %s: %s", student.id, exc)

    result = {"sent": sent, "skipped": skipped, "errors": errors,
              "drives_checked": len(upcoming)}
    logger.info("send_deadline_reminders done | %s", result)
    return result


# ===========================================================================
# b) MONTHLY ACTIVITY REPORT
# ===========================================================================

_REPORT_SUBJECT = "📊 Monthly Placement Activity Report — {month} {year}"

_REPORT_HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  *{box-sizing:border-box}
  body{font-family:Arial,sans-serif;background:#f4f6fb;margin:0;padding:0;color:#212529}
  .wrap{max-width:700px;margin:32px auto;background:#fff;border-radius:12px;
        overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.1)}
  .hdr{background:linear-gradient(135deg,#0d6efd,#6610f2);padding:32px 36px;color:#fff}
  .hdr h1{margin:0 0 4px;font-size:24px}.hdr p{margin:0;opacity:.85;font-size:13px}
  .kpi-row{display:flex;border-bottom:1px solid #dee2e6}
  .kpi{flex:1;padding:20px 16px;text-align:center;border-right:1px solid #dee2e6}
  .kpi:last-child{border-right:none}
  .kv{font-size:32px;font-weight:700;color:#0d6efd;line-height:1}
  .kl{font-size:11px;color:#6c757d;margin-top:4px;text-transform:uppercase;letter-spacing:.06em}
  .sec{padding:24px 36px}
  .sec h2{font-size:15px;font-weight:700;color:#495057;text-transform:uppercase;
          letter-spacing:.06em;border-bottom:2px solid #dee2e6;padding-bottom:8px;margin:0 0 16px}
  table{width:100%;border-collapse:collapse;font-size:13px}
  th{background:#f8f9fa;color:#6c757d;font-weight:600;text-align:left;padding:8px 12px;
     text-transform:uppercase;font-size:11px;letter-spacing:.05em}
  td{padding:10px 12px;border-bottom:1px solid #f0f0f0}
  tr:last-child td{border-bottom:none}
  .badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:11px;font-weight:600}
  .bs{background:#d1e7dd;color:#0f5132}.bw{background:#fff3cd;color:#664d03}.bd{background:#f8d7da;color:#842029}
  .pw{background:#e9ecef;border-radius:99px;height:8px;overflow:hidden;margin-top:4px}
  .pb{height:100%;background:#0d6efd;border-radius:99px}
  .foot{background:#f8f9fa;padding:16px 36px;font-size:11px;
        color:#adb5bd;text-align:center;border-top:1px solid #dee2e6}
</style></head><body>
<div class="wrap">
  <div class="hdr">
    <h1>📊 Monthly Placement Report</h1>
    <p>{{ college }} · {{ month }} {{ year }} · Generated {{ generated_on }}</p>
  </div>
  <div class="kpi-row">
    <div class="kpi"><div class="kv">{{ stats.drives }}</div><div class="kl">Drives</div></div>
    <div class="kpi"><div class="kv">{{ stats.applications }}</div><div class="kl">Applications</div></div>
    <div class="kpi"><div class="kv">{{ stats.selected }}</div><div class="kl">Selected</div></div>
    <div class="kpi"><div class="kv">{{ stats.placement_rate }}%</div><div class="kl">Placement Rate</div></div>
  </div>
  <div class="sec">
    <h2>Drives This Month</h2>
    {% if drives %}
    <table>
      <thead><tr><th>Drive</th><th>Company</th><th>Applied</th><th>Selected</th><th>Status</th></tr></thead>
      <tbody>
        {% for d in drives %}
        <tr>
          <td><strong>{{ d.title }}</strong></td><td>{{ d.company }}</td>
          <td>{{ d.applied }}</td><td>{{ d.selected }}</td>
          <td><span class="badge {% if d.status=='Completed' %}bs{% elif d.status=='Open' %}bw{% else %}bd{% endif %}">{{ d.status }}</span></td>
        </tr>{% endfor %}
      </tbody>
    </table>
    {% else %}<p style="color:#6c757d;font-size:13px">No drives this month.</p>{% endif %}
  </div>
  {% if top_companies %}
  <div class="sec" style="border-top:1px solid #dee2e6">
    <h2>Top Recruiting Companies</h2>
    <table>
      <thead><tr><th>Company</th><th>Offers</th><th>Share</th></tr></thead>
      <tbody>{% for c in top_companies %}
        <tr><td>{{ c.name }}</td><td>{{ c.offers }}</td>
          <td style="width:180px"><div class="pw"><div class="pb" style="width:{{ c.pct }}%"></div></div></td>
        </tr>{% endfor %}
      </tbody>
    </table>
  </div>{% endif %}
  {% if branch_stats %}
  <div class="sec" style="border-top:1px solid #dee2e6">
    <h2>Placements by Branch</h2>
    <table>
      <thead><tr><th>Branch</th><th>Selected</th></tr></thead>
      <tbody>{% for b in branch_stats %}<tr><td>{{ b.branch }}</td><td>{{ b.count }}</td></tr>{% endfor %}</tbody>
    </table>
  </div>{% endif %}
  <div class="foot">
    Auto-generated by the Placement Portal on {{ generated_on }}.<br>
    {{ college }} · Placement Cell · Confidential
  </div>
</div></body></html>
"""


@shared_task(bind=True, name="tasks.send_monthly_activity_report", **_RETRY)
def send_monthly_activity_report(self, month_override=None):
    """
    Runs 1st of every month. Reports on the PREVIOUS calendar month.

    month_override: "YYYY-MM" string to force a specific month.
    Use this to test with your actual data:
        send_monthly_activity_report.delay(month_override="2026-03")

    FIX: PlacementDrive.application_deadline and Application.applied_date
         are both DateTime columns — use datetime boundaries, not date.

    FIX: Role.users is lazy='dynamic' — iterate directly (no .all() needed,
         but filtering works fine).
    """
    from flask import current_app, render_template_string

    mail, db, Student, Company, User, Application, PlacementDrive, Placement, Role = _get_deps()

    today = datetime.utcnow()

    if month_override:
        # e.g. "2026-03" → report for March 2026
        year, month = map(int, month_override.split("-"))
        first_prev  = datetime(year, month, 1)
        # First day of NEXT month = end boundary
        if month == 12:
            first_this = datetime(year + 1, 1, 1)
        else:
            first_this = datetime(year, month + 1, 1)
    else:
        # Default: previous calendar month
        first_this = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        first_prev = (first_this - timedelta(days=1)).replace(day=1)

    month_label = first_prev.strftime("%B")
    year_label  = first_prev.strftime("%Y")
    college     = current_app.config.get("COLLEGE_NAME", "Our Institute")

    logger.info("send_monthly_activity_report | window %s – %s",
                first_prev.date(), (first_this - timedelta(days=1)).date())

    try:
        # FIX: DateTime column — compare against datetime objects, not date
        month_drives = (
            PlacementDrive.query
            .filter(
                PlacementDrive.created_at >= first_prev,
                PlacementDrive.created_at <  first_this,
            )
            .all()
        )
        month_apps = (
            Application.query
            .filter(
                Application.applied_date >= first_prev,
                Application.applied_date <  first_this,
            )
            .all()
        )
    except Exception as exc:
        logger.exception("DB error fetching report data")
        raise self.retry(exc=exc)

    selected_apps  = [a for a in month_apps if a.status == "Selected"]
    total_apps     = len(month_apps)
    total_sel      = len(selected_apps)
    placement_rate = round((total_sel / total_apps * 100) if total_apps else 0, 1)

    # Per-drive breakdown
    drives_data = []
    for d in month_drives:
        d_apps = [a for a in month_apps if a.drive_id == d.id]
        drives_data.append({
            "title":    d.title,
            "company":  d.company.company_name if d.company else "—",
            "applied":  len(d_apps),
            "selected": sum(1 for a in d_apps if a.status == "Selected"),
            "status":   d.status,
        })

    # Top 5 companies by offers
    company_map = {}
    for a in selected_apps:
        if a.drive and a.drive.company:
            n = a.drive.company.company_name
            company_map[n] = company_map.get(n, 0) + 1
    top5 = sorted(company_map.items(), key=lambda x: x[1], reverse=True)[:5]
    max_offers    = top5[0][1] if top5 else 1
    top_companies = [
        {"name": n, "offers": c, "pct": round(c / max_offers * 100)}
        for n, c in top5
    ]

    # Branch breakdown (from selected students)
    branch_map = {}
    for a in selected_apps:
        if a.student and a.student.branch:
            b = a.student.branch
            branch_map[b] = branch_map.get(b, 0) + 1
    branch_stats = [
        {"branch": b, "count": c}
        for b, c in sorted(branch_map.items(), key=lambda x: x[1], reverse=True)
    ]

    html_body = render_template_string(
        _REPORT_HTML,
        college=college,
        month=month_label,
        year=year_label,
        generated_on=today.strftime("%d %b %Y"),
        stats={
            "drives":          len(month_drives),
            "applications":    total_apps,
            "selected":        total_sel,
            "placement_rate":  placement_rate,
        },
        drives=drives_data,
        top_companies=top_companies,
        branch_stats=branch_stats,
    )

    # FIX: Role.users is lazy='dynamic' — iterate directly
    admin_role   = Role.query.filter_by(name="admin").first()
    admin_emails = (
        [u.email for u in admin_role.users if u.email and u.active]
        if admin_role else []
    )
    if not admin_emails:
        fallback = current_app.config.get("ADMIN_EMAIL")
        admin_emails = [fallback] if fallback else []

    if not admin_emails:
        logger.warning("Monthly report: no admin emails found.")
        return {"sent": 0, "reason": "no admin emails"}

    subject = _REPORT_SUBJECT.format(month=month_label, year=year_label)
    sent = errors = 0

    for email in admin_emails:
        try:
            _send_email(mail, subject=subject, recipients=[email], html=html_body)
            sent += 1
            logger.info("Report → %s", email)
        except Exception as exc:
            errors += 1
            logger.error("Report FAILED to %s: %s", email, exc)

    result = {
        "sent":         sent,
        "errors":       errors,
        "month":        f"{month_label} {year_label}",
        "drives":       len(month_drives),
        "applications": total_apps,
        "selected":     total_sel,
    }
    logger.info("send_monthly_activity_report done | %s", result)
    return result


# ===========================================================================
# c) STUDENT-TRIGGERED CSV EXPORT
# ===========================================================================

_EXPORT_SUBJECT = "✅ Your Application Export is Ready"

_EXPORT_HTML = """
<!DOCTYPE html><html><head><meta charset="utf-8">
<style>
  body{font-family:Arial,sans-serif;background:#f4f6fb;margin:0;padding:0}
  .wrap{max-width:560px;margin:32px auto;background:#fff;border-radius:10px;
        overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,.08)}
  .hdr{background:linear-gradient(135deg,#198754,#0d6efd);padding:28px 32px;color:#fff}
  .hdr h1{margin:0;font-size:20px}
  .body{padding:28px 32px}.body p{color:#555;font-size:14px;line-height:1.6}
  .meta{background:#f8f9fa;border-radius:8px;padding:14px 18px;margin:16px 0;font-size:13px;color:#495057}
  .meta strong{color:#212529}
  .cta{display:inline-block;background:#0d6efd;color:#fff;text-decoration:none;
       padding:10px 24px;border-radius:6px;font-size:14px;margin-top:8px}
  .foot{background:#f8f9fa;padding:14px 32px;font-size:11px;color:#adb5bd;text-align:center}
</style></head><body>
<div class="wrap">
  <div class="hdr"><h1>✅ Your CSV Export is Ready!</h1></div>
  <div class="body">
    <p>Hi <strong>{{ name }}</strong>,</p>
    <p>Your application history has been exported successfully.</p>
    <div class="meta">
      <strong>File:</strong> {{ filename }}<br>
      <strong>Records:</strong> {{ record_count }} application(s)<br>
      <strong>Generated:</strong> {{ generated_on }}
    </div>
    <p>Click below to download. Link expires in 24 hours.</p>
    <a href="{{ download_url }}" class="cta">⬇ Download CSV</a>
  </div>
  <div class="foot">{{ college }} · Placement Cell</div>
</div></body></html>
"""

_CSV_HEADERS = [
    "Application ID", "Student ID", "Student Name",
    "Company Name", "Drive Title", "Drive Location",
    "Salary (Min)", "Salary (Max)", "Currency",
    "Application Status", "Applied Date", "Reviewed Date", "Cover Letter",
]


@shared_task(bind=True, name="tasks.export_applications_csv", **_RETRY)
def export_applications_csv(self, student_id):
    from flask import current_app, render_template_string

    mail, db, Student, Company, User, Application, PlacementDrive, Placement, Role = _get_deps()

    logger.info("export_applications_csv | student_id=%s", student_id)

    student = Student.query.get(student_id)
    if not student or not student.user:
        raise ValueError(f"Student {student_id} not found")

    try:
        applications = (
            Application.query
            .filter_by(student_id=student_id)
            .order_by(Application.applied_date.desc())
            .all()
        )
    except Exception as exc:
        logger.exception("DB error fetching applications")
        raise self.retry(exc=exc)

    buf    = StringIO()
    writer = csv.writer(buf)
    writer.writerow(_CSV_HEADERS)

    for app in applications:
        drive   = app.drive
        company = drive.company if drive else None
        writer.writerow([
            app.id, student_id, student.user.name,
            company.company_name                          if company else "—",
            drive.title                                   if drive   else "—",
            drive.location                                if drive   else "—",
            drive.salary_min                              if drive   else "—",
            drive.salary_max                              if drive   else "—",
            drive.currency                                if drive   else "—",
            app.status,
            app.applied_date.strftime("%Y-%m-%d %H:%M")  if app.applied_date  else "—",
            app.reviewed_date.strftime("%Y-%m-%d %H:%M") if app.reviewed_date else "—",
            (app.cover_letter or "")[:200],
        ])

    export_dir = "/tmp/exports"
    os.makedirs(export_dir, exist_ok=True)

    ts       = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"applications_student{student_id}_{ts}.csv"
    filepath = os.path.join(export_dir, filename)

    try:
        with open(filepath, "w", newline="", encoding="utf-8") as fh:
            fh.write(buf.getvalue())
        logger.info("CSV saved: %s (%d rows)", filepath, len(applications))
    except OSError as exc:
        logger.exception("Failed to write CSV")
        raise self.retry(exc=exc)

    frontend     = current_app.config.get("FRONTEND_URL", "http://localhost:5173")
    college      = current_app.config.get("COLLEGE_NAME", "Our Institute")
    download_url = f"{frontend}/api/student/{student_id}/export-csv/{filename}/download"
    generated_on = datetime.utcnow().strftime("%d %b %Y, %H:%M UTC")

    html_body = render_template_string(
        _EXPORT_HTML,
        name=student.user.name,
        filename=filename,
        record_count=len(applications),
        generated_on=generated_on,
        download_url=download_url,
        college=college,
    )

    try:
        _send_email(mail, subject=_EXPORT_SUBJECT,
                    recipients=[student.user.email], html=html_body)
        logger.info("Export email → %s", student.user.email)
    except Exception as exc:
        # Don't retry — CSV is saved, student can still poll for it
        logger.error("Export email FAILED for student %s: %s", student_id, exc)

    result = {
        "filename":     filename,
        "record_count": len(applications),
        "download_url": download_url,
    }
    logger.info("export_applications_csv done | %s", result)
    return result