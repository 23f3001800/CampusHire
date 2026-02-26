"""
Celery background tasks for the placement portal.
Includes daily reminders, monthly reports, and CSV exports.
"""
from celery_app import celery
from flask_mail import Message
from models import Student, PlacementDrive, Application, Company, Placement
from db import db
from datetime import datetime, timedelta
from sqlalchemy import func
import csv
import os

# Single app import — no create_app() inside tasks
from app import app, mail


# ─── Daily Reminder Task ──────────────────────────────────────────────────────


@celery.task(name='tasks.send_daily_reminders')
def send_daily_reminders():
    """
    Send daily reminders to students about upcoming application deadlines.
    Runs daily at 8 AM via Celery Beat.
    """
    with app.app_context():
        now       = datetime.utcnow()
        threshold = now + timedelta(days=3)

        upcoming_drives = PlacementDrive.query.filter(
            PlacementDrive.status == 'Open',
            PlacementDrive.admin_approval_status == 'Approved',
            PlacementDrive.application_deadline.between(now, threshold)
        ).all()

        if not upcoming_drives:
            return {'status': 'no_upcoming_drives'}

        students = Student.query.join(Student.user).filter_by(active=True).all()

        reminders_sent = 0
        for student in students:
            applied_ids = {a.drive_id for a in student.applications}
            eligible    = []

            for drive in upcoming_drives:
                if drive.id in applied_ids:
                    continue
                if drive.min_cgpa and student.cgpa and student.cgpa < drive.min_cgpa:
                    continue
                if drive.eligible_branches and student.branch:
                    allowed = [b.strip().lower() for b in drive.eligible_branches.split(',')]
                    if student.branch.lower() not in allowed:
                        continue
                if drive.eligible_graduation_year and student.graduation_year:
                    if student.graduation_year != drive.eligible_graduation_year:
                        continue
                eligible.append(drive)

            if eligible:
                _send_reminder_email(student, eligible)
                reminders_sent += 1

        return {
            'status':          'success',
            'reminders_sent':  reminders_sent,
            'drives_count':    len(upcoming_drives),
        }


def _send_reminder_email(student, drives):
    """Send deadline reminder email to a student."""
    subject = (
        f"⏰ {len(drives)} Placement Drive"
        f"{'s' if len(drives) > 1 else ''} Closing Soon!"
    )

    drive_rows = ''
    for drive in drives:
        days_left  = (drive.application_deadline - datetime.utcnow()).days
        color      = '#dc3545' if days_left <= 1 else '#ffc107'
        drive_rows += f"""
        <div style="border-left:4px solid #0d6efd;padding:10px;
                    margin:10px 0;background:white;">
            <h3 style="margin:0 0 5px 0">{drive.title}</h3>
            <p style="margin:5px 0;color:#6c757d">
                {drive.company.company_name}
            </p>
            <p style="margin:5px 0">
                <strong style="color:{color}">
                    Deadline: {drive.application_deadline.strftime('%d %b %Y, %I:%M %p')}
                    ({days_left} day{'s' if days_left != 1 else ''} left)
                </strong>
            </p>
        </div>"""

    html = f"""
    <html>
    <body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto">
        <div style="background:#0d6efd;color:white;padding:20px;text-align:center">
            <h1>🎓 CampusHire Reminder</h1>
        </div>
        <div style="padding:20px">
            <p>Hi <strong>{student.user.name}</strong>,</p>
            <p>The following placement drives are closing soon. Don't miss out!</p>
            <div style="background:#f8f9fa;padding:15px;border-radius:8px;margin:20px 0">
                {drive_rows}
            </div>
            <div style="text-align:center;margin:30px 0">
                <a href="http://localhost:5173/student/{student.id}"
                   style="background:#0d6efd;color:white;padding:12px 30px;
                          text-decoration:none;border-radius:5px;display:inline-block">
                    View All Drives
                </a>
            </div>
            <p style="color:#6c757d;font-size:.9rem;margin-top:30px">
                This is an automated reminder from CampusHire Placement Portal.
            </p>
        </div>
    </body>
    </html>"""

    msg = Message(subject, recipients=[student.user.email], html=html)
    mail.send(msg)


# ─── Monthly Report Task ──────────────────────────────────────────────────────


@celery.task(name='tasks.generate_monthly_report')
def generate_monthly_report():
    """
    Generate and email monthly placement activity report to admin.
    Runs on 1st of every month at 9 AM via Celery Beat.
    """
    with app.app_context():
        from models import User, Role
        admin_role = Role.query.filter_by(name='admin').first()
        if not admin_role or not admin_role.users:
            return {'status': 'no_admin_found'}

        admin = admin_role.users[0]

        today            = datetime.utcnow()
        last_month_start = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
        last_month_end   = today.replace(day=1) - timedelta(seconds=1)

        drives_last_month = PlacementDrive.query.filter(
            PlacementDrive.posted_date.between(last_month_start, last_month_end)
        ).count()

        apps_last_month = Application.query.filter(
            Application.applied_date.between(last_month_start, last_month_end)
        ).count()

        placements_last_month = Placement.query.filter(
            Placement.created_at.between(last_month_start, last_month_end)
        ).count()

        top_companies = db.session.query(
            Company.company_name,
            func.count(Placement.id).label('placement_count')
        ).join(Placement, Company.id == Placement.company_id)\
         .group_by(Company.id)\
         .order_by(func.count(Placement.id).desc())\
         .limit(5).all()

        html = _generate_report_html(
            last_month_start, last_month_end,
            drives_last_month, apps_last_month, placements_last_month,
            Student.query.count(),
            Company.query.count(),
            PlacementDrive.query.count(),
            Application.query.count(),
            Placement.query.count(),
            top_companies,
        )

        subject = f"📊 Monthly Placement Report — {last_month_start.strftime('%B %Y')}"
        msg     = Message(subject, recipients=[admin.email], html=html)
        mail.send(msg)

        return {
            'status':       'success',
            'period':       last_month_start.strftime('%B %Y'),
            'drives':       drives_last_month,
            'applications': apps_last_month,
            'placements':   placements_last_month,
        }


def _generate_report_html(start, end, drives, apps, placements,
                           total_students, total_companies, total_drives,
                           total_apps, total_placements, top_companies):
    rows = ''.join(
        f'<tr><td>{c[0]}</td><td>{c[1]}</td></tr>'
        for c in top_companies
    )
    return f"""
    <html>
    <head>
        <style>
            body      {{ font-family:Arial,sans-serif;max-width:800px;margin:0 auto }}
            .header   {{ background:linear-gradient(135deg,#667eea,#764ba2);
                         color:white;padding:30px;text-align:center }}
            .section  {{ padding:20px;margin:20px 0;background:#f8f9fa;border-radius:8px }}
            .grid     {{ display:grid;grid-template-columns:repeat(3,1fr);gap:15px }}
            .card     {{ background:white;padding:20px;border-radius:8px;text-align:center;
                         box-shadow:0 2px 4px rgba(0,0,0,.1) }}
            .num      {{ font-size:2.5rem;font-weight:bold;color:#0d6efd }}
            .lbl      {{ color:#6c757d;font-size:.9rem;margin-top:5px }}
            table     {{ width:100%;border-collapse:collapse;margin:20px 0 }}
            th,td     {{ padding:12px;text-align:left;border-bottom:1px solid #dee2e6 }}
            th        {{ background:#0d6efd;color:white }}
            tr:hover  {{ background:#f8f9fa }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Monthly Placement Activity Report</h1>
            <p style="font-size:1.2rem;margin-top:10px">
                {start.strftime('%B %Y')}
                ({start.strftime('%d %b')} – {end.strftime('%d %b')})
            </p>
        </div>

        <div class="section">
            <h2>📈 Last Month's Activity</h2>
            <div class="grid">
                <div class="card"><div class="num">{drives}</div>
                    <div class="lbl">Drives Posted</div></div>
                <div class="card"><div class="num">{apps}</div>
                    <div class="lbl">Applications</div></div>
                <div class="card"><div class="num">{placements}</div>
                    <div class="lbl">Students Placed</div></div>
            </div>
        </div>

        <div class="section">
            <h2>🎯 Overall Platform Statistics</h2>
            <table>
                <tr><th>Metric</th><th>Count</th></tr>
                <tr><td>Total Students</td><td>{total_students}</td></tr>
                <tr><td>Total Companies</td><td>{total_companies}</td></tr>
                <tr><td>Total Drives</td><td>{total_drives}</td></tr>
                <tr><td>Total Applications</td><td>{total_apps}</td></tr>
                <tr><td>Total Placements</td><td>{total_placements}</td></tr>
            </table>
        </div>

        <div class="section">
            <h2>🏆 Top 5 Recruiting Companies</h2>
            <table>
                <tr><th>Company</th><th>Placements</th></tr>
                {rows}
            </table>
        </div>

        <div style="text-align:center;margin:40px 0;
                    color:#6c757d;font-size:.9rem">
            <p>Generated on {datetime.utcnow().strftime('%d %B %Y, %I:%M %p UTC')}</p>
            <p>CampusHire Placement Portal — Automated Report</p>
        </div>
    </body>
    </html>"""


# ─── Student CSV Export Task ──────────────────────────────────────────────────


@celery.task(bind=True, name='tasks.export_applications_csv')
def export_applications_csv(self, student_id):
    """Export student's full application history as CSV."""
    with app.app_context():
        student = Student.query.get(student_id)
        if not student:
            raise ValueError('Student not found')

        applications = Application.query.filter_by(student_id=student_id)\
                                        .order_by(Application.applied_date.desc()).all()

        os.makedirs('/tmp/exports', exist_ok=True)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename  = f'applications_{student_id}_{timestamp}.csv'
        filepath  = f'/tmp/exports/{filename}'

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Application ID', 'Company Name', 'Drive Title',
                'Job Type', 'Location', 'Salary',
                'Applied Date', 'Status', 'Reviewed Date', 'Notes',
            ])
            for a in applications:
                writer.writerow([
                    a.id,
                    a.drive.company.company_name if a.drive and a.drive.company else 'N/A',
                    a.drive.title    if a.drive else 'N/A',
                    a.drive.job_type if a.drive else 'N/A',
                    a.drive.location if a.drive else 'N/A',
                    a.drive.salary_max if a.drive else 'N/A',
                    a.applied_date.strftime('%Y-%m-%d %H:%M')   if a.applied_date   else '',
                    a.status,
                    a.reviewed_date.strftime('%Y-%m-%d %H:%M')  if a.reviewed_date  else '',
                    a.notes or '',
                ])

        # Notify student via email
        _send_export_ready_email(student, filename, 'student', student_id)

        return {
            'status':       'SUCCESS',
            'filename':     filename,
            'record_count': len(applications),
        }


# ─── Company CSV Export Task ──────────────────────────────────────────────────


@celery.task(bind=True, name='tasks.export_company_applicants_csv')
def export_company_applicants_csv(self, company_id, drive_id):
    """Export all applicants for a company's drive as CSV."""
    with app.app_context():
        company = Company.query.get(company_id)
        if not company:
            raise ValueError('Company not found')

        drive = PlacementDrive.query.filter_by(
            id=drive_id, company_id=company_id).first()
        if not drive:
            raise ValueError('Drive not found')

        applications = Application.query.filter_by(drive_id=drive_id)\
                                        .order_by(Application.applied_date.desc()).all()

        os.makedirs('/tmp/exports', exist_ok=True)
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename  = f'applicants_{company_id}_drive{drive_id}_{timestamp}.csv'
        filepath  = f'/tmp/exports/{filename}'

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Application ID', 'Student Name', 'Email',
                'Roll Number', 'Branch', 'CGPA',
                'Graduation Year', 'Phone',
                'Applied Date', 'Status', 'Reviewed Date', 'Notes',
            ])
            for a in applications:
                s = a.student
                writer.writerow([
                    a.id,
                    s.user.name  if s and s.user else 'N/A',
                    s.user.email if s and s.user else 'N/A',
                    s.roll_number     if s else 'N/A',
                    s.branch          if s else 'N/A',
                    s.cgpa            if s else 'N/A',
                    s.graduation_year if s else 'N/A',
                    s.phone           if s else 'N/A',
                    a.applied_date.strftime('%Y-%m-%d %H:%M')  if a.applied_date  else '',
                    a.status,
                    a.reviewed_date.strftime('%Y-%m-%d %H:%M') if a.reviewed_date else '',
                    a.notes or '',
                ])

        # Notify HR via email
        _send_export_ready_email(company, filename, 'company', company_id)

        return {
            'status':       'SUCCESS',
            'filename':     filename,
            'record_count': len(applications),
            'drive_title':  drive.title,
        }


def _send_export_ready_email(entity, filename, role, entity_id):
    """Notify user that their CSV export is ready for download."""
    is_company  = role == 'company'
    email       = entity.user.email
    name        = entity.user.name
    download_url = (
        f"http://localhost:5173/company/{entity_id}/export/{filename}"
        if is_company else
        f"http://localhost:5173/student/{entity_id}/export/{filename}"
    )

    html = f"""
    <html>
    <body style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto">
        <div style="background:#0d6efd;color:white;padding:20px;text-align:center">
            <h1>🎓 CampusHire</h1>
        </div>
        <div style="padding:20px">
            <p>Hi <strong>{name}</strong>,</p>
            <p>Your CSV export is ready for download.</p>
            <div style="text-align:center;margin:30px 0">
                <a href="{download_url}"
                   style="background:#28a745;color:white;padding:12px 30px;
                          text-decoration:none;border-radius:5px;
                          display:inline-block">
                    ⬇️ Download CSV
                </a>
            </div>
            <p style="color:#6c757d;font-size:.9rem">
                This link is valid for 24 hours.
            </p>
        </div>
    </body>
    </html>"""

    msg = Message(
        '✅ Your CSV Export is Ready — CampusHire',
        recipients=[email],
        html=html,
    )
    mail.send(msg)
